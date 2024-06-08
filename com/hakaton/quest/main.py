import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import routers.choice_router
import routers.command_router
import routers.fight_router
import routers.location_router
import routers.speech_router
import routers.web_app_router
from config import *

dp = Dispatcher()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def main() -> None:
    dp.include_router(routers.command_router.command_router)
    dp.include_router(routers.web_app_router.web_app_router)
    dp.include_router(routers.location_router.location_router)
    dp.include_router(routers.speech_router.speech_router)
    dp.include_router(routers.fight_router.fight_router)
    dp.include_router(routers.choice_router.choice_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
