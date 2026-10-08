from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from api.bot_deps import get_current_bot
from api.deps import get_db
from models import Bot, User


router = APIRouter(
    prefix="/bot",
    tags=["Bot API"],
)


class BotProfile(BaseModel):
    id: int
    bot_id: int
    is_bot: bool
    username: str
    display_name: str | None
    description: str | None


class GetMeResponse(BaseModel):
    ok: bool
    result: BotProfile


@router.get(
    "/getMe",
    response_model=GetMeResponse,
)
async def get_me(
    response: Response,
    bot: Bot = Depends(get_current_bot),
    db: AsyncSession = Depends(get_db),
):
    response.headers["Cache-Control"] = "no-store"

    bot_user = await db.get(User, bot.user_id)

    if bot_user is None or not bot_user.is_bot:
        raise HTTPException(
            status_code=401,
            detail="Invalid bot token",
        )

    return {
        "ok": True,
        "result": {
            "id": bot_user.id,
            "bot_id": bot.id,
            "is_bot": True,
            "username": bot_user.username,
            "display_name": bot_user.display_name,
            "description": bot_user.bio,
        },
    }
