# Standard library imports
import asyncio
import logging
import sys

# Third-party library imports
from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    CallbackQuery, WebAppInfo
)
from geopy.distance import geodesic

# Local application/library specific imports
from dialogue import Translate
from npc_manager import ask_question
from player import Player
from quest_manager import QuestManager
from config import *

dp = Dispatcher()

players = {}
quest_managers = {}
is_talking_with_npc = {}
translate = Translate()

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

next_chapter_button_markup = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Двигаться дальше", request_location=True)]])


@dp.message(CommandStart())
async def start_quest(message: Message) -> None:
    user_id = message.from_user.id
    if message.from_user.id not in players.keys():
        players[user_id] = Player()
        quest_managers[user_id] = QuestManager(player=players[user_id])
        await message.answer(text=f"Глава: <b>{quest_managers[user_id].current_chapter.title}</b>")
    is_talking_with_npc[user_id] = False
    quest_description, markup = quest_managers[user_id].get_quest_desc_and_choices()
    m = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(web_app=WebAppInfo(url="https://danisgaleev.github.io/"),
                        text="rkjey")]])
    await message.answer(text=quest_description, reply_markup=m)


@dp.message(Command("clear"))
async def clear(message: Message) -> None:
    user_id = message.from_user.id
    players[user_id] = Player()
    quest_managers[user_id] = QuestManager(player=players[user_id])
    await message.answer(text=f"Глава: <b>{quest_managers[user_id].current_chapter.title}</b>")
    is_talking_with_npc[user_id] = False
    quest_description, markup = quest_managers[user_id].get_quest_desc_and_choices()
    await message.answer(text=quest_description, reply_markup=markup)


@dp.message(F.location)
async def check_location(message: Message) -> None:  # check if player near right place
    _location = (message.location.latitude, message.location.longitude)
    print(message.from_user.id, _location)
    user_id = message.from_user.id
    user = quest_managers[user_id]
    if players[user_id].changed_location and geodesic(_location, user.current_chapter.geo_position).meters <= 50:
        players[user_id].changed_location = False
        quest_description, markup = user.get_quest_desc_and_choices()

        await message.answer(text=f"Глава: <b>{user.current_chapter.title}</b>", reply_markup=ReplyKeyboardRemove())
        await message.answer(text=quest_description, reply_markup=markup)
    elif geodesic(_location, user.current_chapter.geo_position).meters > 50:
        await bot.send_venue(message.chat.id, latitude=user.current_chapter.geo_position[0],
                             longitude=user.current_chapter.geo_position[1], title="Вы слишком далеко.",
                             address="Следующая точка здесь.")
        await message.answer("<i>Подойдите не меньше, чем на 50 метров.</i>")


@dp.message()
async def managing_player_responses(message: Message):
    if is_talking_with_npc[message.from_user.id]:
        translation = translate.tat_to_rus(message.text)
        answer = ask_question(translation)
        await message.answer(text=answer)


@dp.callback_query(F.data.endswith("ask"))
async def handle_ask_question(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_talking_with_npc[user_id] = True
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(text="Ну, спрашивай")


@dp.callback_query()
async def apply_choice(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = quest_managers[user_id]
    for choice in user.current_quest.choices:
        is_talking_with_npc[user_id] = False

        # i compare unique combination of current chapter, quest and choice id with current choice
        compare_data = user.current_chapter_id + ";" + user.current_quest_id + ";" + choice.choice_id
        if compare_data == callback.data:
            if choice.to_quest.startswith("ch"):
                players[user_id].changed_location = True

                user.current_chapter_id = choice.to_quest
                user.current_chapter = user.chapters[user.current_chapter_id]
                user.current_quest_id = "q0"
                user.current_quest = user.current_chapter.quests[user.current_quest_id]

                await callback.message.answer(text="<b>Новая локация</b>", reply_markup=next_chapter_button_markup)
                await callback.message.edit_reply_markup(reply_markup=None)
            else:
                user.current_quest_id = choice.to_quest
                quest_description, markup = user.get_quest_desc_and_choices()
                players[user_id].apply_changes(**choice.result)

                await callback.message.edit_reply_markup(reply_markup=None)
                await callback.message.answer(text=choice.text)
                await callback.message.answer(text=quest_description, reply_markup=markup)
            break
    else:
        await callback.message.delete()


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
