import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

import config
from handlers import router, setup_router, setup_router_2, setup_router_3
from premium import start_dp
from admin import setup_router_admin


async def main():
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    await setup_router(dp, bot)
    await setup_router_2(dp, bot)
    await setup_router_3(dp, bot)
    await setup_router_admin(dp, bot)
    await start_dp(dp, bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
