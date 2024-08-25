from aiogram.filters import BaseFilter
from aiogram.types import Message


class ProfileFilter(BaseFilter):

    async def __call__(self, message: Message) -> bool:
        if message.text is not None:
            if message.text.casefold() in \
                    ["кпрофиль".casefold(), "профиль".casefold(), "комару профиль".casefold(),
                     "камара профиль".casefold()]:
                return True
            else:
                return False
        else:
            return False
