from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db
from models import Bot
from services.bots import get_bot_by_token


bot_token_scheme = APIKeyHeader(
    name="Authorization",
    scheme_name="BotToken",
    description=(
        "Enter the complete value: Bot lsg_YOUR_TOKEN"
    ),
    auto_error=False,
)


def invalid_bot_token() -> HTTPException:
    return HTTPException(
        status_code=401,
        detail="Invalid bot token",
    )


async def get_current_bot(
    authorization: str | None = Security(bot_token_scheme),
    db: AsyncSession = Depends(get_db),
) -> Bot:
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing bot token",
        )

    scheme, separator, token = authorization.partition(" ")

    if (
        scheme != "Bot"
        or not separator
        or not token
        or any(char.isspace() for char in token)
    ):
        raise invalid_bot_token()

    bot = await get_bot_by_token(db, token)

    if bot is None:
        raise invalid_bot_token()

    return bot
