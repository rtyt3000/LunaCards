from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from database.user import get_user, create_user
from database.group import get_group, create_group


class RegisterMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        event: Message = event
        if await get_user(event.from_user.id) is None:
            await create_user(event.from_user.id, event.from_user.username)
        if event.chat.type in ["group", "supergroup"] and await get_group(event.chat.id) is None:
            await create_group(event.chat.id, event.chat.title)

        return await handler(event, data)
