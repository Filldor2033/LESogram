import hashlib
import re
import secrets

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth import hash_password
from models import Bot, User
from utils.time import utc_now


BOT_USERNAME_RE = re.compile(
    r"[a-z][a-z0-9_]{2,45}_bot"
)
BOT_TOKEN_RE = re.compile(
    r"lsg_[A-Za-z0-9_-]{43}"
)


class BotUsernameTaken(Exception):
    pass


def generate_bot_token() -> str:
    return "lsg_" + secrets.token_urlsafe(32)


def hash_bot_token(token: str) -> str:
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


async def get_bot_by_token(
    db: AsyncSession,
    token: str,
) -> Bot | None:
    if not BOT_TOKEN_RE.fullmatch(token):
        return None

    result = await db.execute(
        select(Bot).where(
            Bot.token_hash == hash_bot_token(token),
            Bot.is_active.is_(True),
        )
    )
    return result.scalar_one_or_none()


async def create_bot(
    db: AsyncSession,
    *,
    owner: User,
    username: str,
    display_name: str,
    description: str | None = None,
) -> tuple[Bot, str]:
    if owner.is_bot:
        raise ValueError("Bot accounts cannot create bots")

    username = username.strip().lower()
    display_name = display_name.strip()
    description = description.strip() if description else None

    if not BOT_USERNAME_RE.fullmatch(username):
        raise ValueError(
            "Username must end in _bot and use "
            "lowercase letters, digits or _"
        )

    if not 1 <= len(display_name) <= 50:
        raise ValueError(
            "Display name must contain 1-50 characters"
        )

    if description is not None and len(description) > 200:
        raise ValueError("Description is too long")

    exists = await db.scalar(
        select(User.id).where(
            func.lower(User.username) == username
        )
    )
    if exists is not None:
        raise BotUsernameTaken(username)

    token = generate_bot_token()

    bot_user = User(
        username=username,
        hashed_password=hash_password(
            secrets.token_urlsafe(32)
        ),
        is_admin=False,
        is_bot=True,
        display_name=display_name,
        bio=description,
    )
    db.add(bot_user)

    try:
        await db.flush()

        bot = Bot(
            user_id=bot_user.id,
            owner_id=owner.id,
            token_hash=hash_bot_token(token),
        )
        db.add(bot)

        await db.commit()
        await db.refresh(bot)

    except IntegrityError as exc:
        await db.rollback()

        exists = await db.scalar(
            select(User.id).where(
                func.lower(User.username) == username
            )
        )
        if exists is not None:
            raise BotUsernameTaken(username) from exc

        raise

    return bot, token


async def list_owned_bots(
    db: AsyncSession,
    owner_id: int,
):
    result = await db.execute(
        select(Bot, User)
        .join(User, Bot.user_id == User.id)
        .where(Bot.owner_id == owner_id)
        .order_by(Bot.id.desc())
    )
    return result.all()


async def get_owned_bot(
    db: AsyncSession,
    owner_id: int,
    bot_id: int,
) -> Bot | None:
    return await db.scalar(
        select(Bot).where(
            Bot.id == bot_id,
            Bot.owner_id == owner_id,
        )
    )


async def rotate_bot_token(
    db: AsyncSession,
    *,
    owner_id: int,
    bot_id: int,
) -> str | None:
    bot = await get_owned_bot(db, owner_id, bot_id)
    if bot is None:
        return None

    token = generate_bot_token()

    bot.token_hash = hash_bot_token(token)
    bot.token_rotated_at = utc_now()

    await db.commit()
    return token


async def set_bot_active(
    db: AsyncSession,
    *,
    owner_id: int,
    bot_id: int,
    enabled: bool,
) -> bool:
    bot = await get_owned_bot(db, owner_id, bot_id)
    if bot is None:
        return False

    bot.is_active = enabled
    await db.commit()
    return True
