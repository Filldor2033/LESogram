"""
Profile ("personal cabinet") API: self profile CRUD, avatar
upload/serve/delete, password change, public profile cards,
user stats, and the admin panel endpoints.
"""

import secrets
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_current_user_model, get_db
from auth import hash_password, verify_password
from core.config import UPLOADS_DIR
from core.rate_limit import enforce_http_rate_limit
from models import User
from schemas import PasswordChangeRequest, ProfileUpdateRequest
from services.messages import normalize_message_text
from services.users import (
    MAX_BIO_LENGTH,
    MAX_DISPLAY_NAME_LENGTH,
    get_user_by_username,
    get_user_stats,
    list_rooms_for_admin,
    list_users_for_admin,
    serialize_user_private,
    serialize_user_public,
)

router = APIRouter()

AVATARS_DIR = UPLOADS_DIR / "avatars"
MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5 MB pre-check; client resizes to ~256px
ALLOWED_AVATAR_TYPES = {"image/png", "image/jpeg", "image/webp", "image/gif"}
ALLOWED_AVATAR_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def _validate_avatar_ext(filename: str) -> str:
    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_AVATAR_EXTS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported avatar format",
        )

    return ext


@router.get("/me")
async def get_me(
    current_user: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    """
    Full self-profile (includes the registration date).
    """
    del db
    return serialize_user_private(current_user)


@router.get("/me/stats")
async def get_my_stats(
    current_user: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    return await get_user_stats(db, current_user.username)


@router.patch("/me")
async def update_me(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    """
    Updates display name / bio. The username is an identity —
    it is never editable.
    """
    data: dict = {}

    if payload.display_name is not None:
        name = payload.display_name.strip()

        if name == "":
            data["display_name"] = None
        else:
            if len(name) > MAX_DISPLAY_NAME_LENGTH:
                raise HTTPException(
                    status_code=422,
                    detail="Display name is too long",
                )

            data["display_name"] = name

    if payload.bio is not None:
        bio = payload.bio.strip()

        if bio == "":
            data["bio"] = None
        else:
            if len(bio) > MAX_BIO_LENGTH:
                raise HTTPException(
                    status_code=422,
                    detail="Bio is too long",
                )

            data["bio"] = bio

    if not data:
        return serialize_user_private(current_user)

    for field, value in data.items():
        setattr(current_user, field, value)

    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)

    return serialize_user_private(current_user)


@router.post("/me/password")
async def change_password(
    payload: PasswordChangeRequest,
    request: Request,
    current_user: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    await enforce_http_rate_limit(request, "change_password", 5, 300)

    if not verify_password(
        payload.current_password, current_user.hashed_password
    ):
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect",
        )

    current_user.hashed_password = hash_password(payload.new_password)

    db.add(current_user)
    await db.commit()

    return {"ok": True}


@router.post("/me/avatar")
async def upload_avatar(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    await enforce_http_rate_limit(request, "upload_avatar", 10, 300)

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Avatar file is missing a name",
        )

    ext = _validate_avatar_ext(file.filename)

    declared = (file.content_type or "").lower()

    if declared and declared not in ALLOWED_AVATAR_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported avatar format",
        )

    AVATARS_DIR.mkdir(parents=True, exist_ok=True)

    name = f"avatar_{secrets.token_hex(8)}{ext}"
    stored_path = AVATARS_DIR / name

    total = 0

    try:
        with open(stored_path, "wb") as out:
            while chunk := await file.read(64 * 1024):
                total += len(chunk)

                if total > MAX_AVATAR_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="Avatar is too large",
                    )

                out.write(chunk)
    except HTTPException:
        stored_path.unlink(missing_ok=True)
        raise

    finally:
        await file.close()

    # remove the previous avatar file
    old_url = current_user.avatar_url

    if old_url:
        old_name = old_url.rsplit("/", 1)[-1]
        (AVATARS_DIR / old_name).unlink(missing_ok=True)

    current_user.avatar_url = f"/api/avatars/{name}"

    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)

    return {"avatar_url": current_user.avatar_url}


@router.delete("/me/avatar")
async def delete_avatar(
    current_user: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    old_url = current_user.avatar_url

    if old_url:
        old_name = old_url.rsplit("/", 1)[-1]
        (AVATARS_DIR / old_name).unlink(missing_ok=True)

    current_user.avatar_url = None

    db.add(current_user)
    await db.commit()

    return {"ok": True}


@router.get("/avatars/{filename}")
async def get_avatar(filename: str):
    """
    Serves avatar files. Avatars are public within the app (every
    logged-in user can see them in chat), so no room token is
    required — but the path is strictly validated.
    """
    safe = Path(filename).name

    if not safe or safe != filename:
        raise HTTPException(status_code=400, detail="Invalid avatar name")

    candidate = (AVATARS_DIR / safe).resolve()

    try:
        candidate.relative_to(AVATARS_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid avatar name")

    if not candidate.exists() or not candidate.is_file():
        raise HTTPException(status_code=404, detail="Avatar not found")

    return FileResponse(candidate)


@router.get("/users/{username}/profile")
async def get_user_profile(
    username: str,
    current_username: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Public profile card. No registration date here.
    """
    user = await get_user_by_username(db, username.strip())

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # the owner's full profile comes from /me
    return serialize_user_public(user)


# --- admin ---

async def _require_admin(
    current_user: User = Depends(get_current_user_model),
) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    return current_user


@router.get("/admin/users")
async def admin_list_users(
    admin: User = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    del admin
    return {"users": await list_users_for_admin(db)}


@router.get("/admin/rooms")
async def admin_list_rooms(
    admin: User = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    del admin
    return {"rooms": await list_rooms_for_admin(db)}


@router.post("/admin/users/{username}/role")
async def admin_set_role(
    username: str,
    is_admin: bool = Form(...),
    admin: User = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    if username == admin.username:
        raise HTTPException(
            status_code=400,
            detail="You cannot change your own role",
        )

    user = await get_user_by_username(db, username.strip())

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_admin = bool(is_admin)

    db.add(user)
    await db.commit()

    return {"username": user.username, "is_admin": bool(user.is_admin)}

