import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from dotenv import load_dotenv

load_dotenv()

dp = Dispatcher()
bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))

wep_app_url = ""

keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Погнали", web_app=WebAppInfo(url=wep_app_url))]])


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(text="Начать игру", reply_markup=keyboard)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
