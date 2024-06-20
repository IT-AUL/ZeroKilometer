import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.deep_linking import create_start_link
from aiogram.utils.payload import decode_payload

from config import *

dp = Dispatcher()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

link = None

wep_app_url = "https://site.com?dvizheniye_pervih={dvizheniye_pervih}"


@dp.message(CommandStart(deep_link=True))
async def start_with_sponsor(message: Message, command: CommandObject):
    args = command.args
    try:
        payload = decode_payload(args)
        if payload == "dvizheniye_pervih":
            wep_app_url.format(dvizheniye_pervih=True)
        else:
            wep_app_url.format(dvizheniye_pervih=False)
        await handle(wep_app_url, message)

    except Exception as e:
        await message.answer(f"error {str(e)}")


@dp.message(CommandStart())
async def start_without_sponsor(message: Message):
    wep_app_url.format(dvizheniye_pervih=False)
    await handle(wep_app_url, message)


async def handle(url: str, message: Message) -> None:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Погнали", web_app=WebAppInfo(url=url))]])
    await message.answer(text="Начать игру", reply_markup=keyboard)


async def main() -> None:
    global link
    link = await create_start_link(bot, 'dvizheniye_pervih', encode=True)
    print(link)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
