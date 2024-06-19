import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message
from aiogram.utils.deep_linking import create_start_link
from aiogram.utils.payload import decode_payload

from config import *

dp = Dispatcher()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

link = None


@dp.message(CommandStart(deep_link=True))
async def start_with_sponsor(message: Message, command: CommandObject):
    args = command.args
    try:
        payload = decode_payload(args)
        await message.answer(payload)
        await message.answer("ans")
    except Exception as e:
        await message.answer("error")


@dp.message(CommandStart())
async def start_without_sponsor(message: Message):
    await message.answer("ans")


async def main() -> None:
    global link
    link = await create_start_link(bot, 'dvizheniye_pervih', encode=True)
    print(link)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
