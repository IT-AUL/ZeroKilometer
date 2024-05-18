# Standard library imports
import asyncio
import logging
import sys
import json
import urllib.parse

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
    CallbackQuery, FSInputFile, WebAppInfo, InputMediaPhoto
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from geopy.distance import geodesic

# Local application/library specific imports
from dialogue import Translate
from npc_manager import ask_question
from player import Player
from quest_manager import QuestManager
from config import *

DISTANCE = 50

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
    print(quest_managers[user_id].current_chapter.title, quest_managers[user_id].current_chapter.video_path)
    if quest_managers[user_id].current_chapter.video_path != "":
        cat = FSInputFile(quest_managers[user_id].current_chapter.video_path)
        await bot.send_video_note(message.chat.id, cat, length=360)
    await message.answer(text=quest_description, reply_markup=markup)


@dp.message(Command("no_fight"))
async def no_fight(message: Message) -> None:
    user_id = message.from_user.id
    if not players[user_id].changed:
        players[user_id].will_fight = 0
        players[user_id].changed = True
        await message.answer(text="Вы включили мирное прохождение")
    else:
        await message.answer(text="Вы не можете поменять режим.")


@dp.message(Command("clear"))
async def clear(message: Message) -> None:
    user_id = message.from_user.id
    players[user_id] = Player()
    quest_managers[user_id] = QuestManager(player=players[user_id])
    await message.answer(text=f"Глава: <b>{quest_managers[user_id].current_chapter.title}</b>")
    is_talking_with_npc[user_id] = False
    quest_description, markup = quest_managers[user_id].get_quest_desc_and_choices()
    await message.answer(text=quest_description, reply_markup=markup)


@dp.message(Command("cards"))
async def view_cards(message: Message) -> None:
    user_id = message.from_user.id
    media = []
    for it in players[user_id].items:
        if it["type"] == "ally":
            media.append(
                InputMediaPhoto(media=FSInputFile(fr'C:\Users\galee\PycharmProjects\Hakaton\cards\{it['id']}.png')))
    if len(media) > 0:
        await bot.send_media_group(chat_id=user_id, media=media)
    else:
        await message.answer(text="У Вас нет карточек.")


@dp.message(Command("path"))
async def view_path(message: Message) -> None:
    user_id = message.from_user.id
    media = FSInputFile(r'C:\Users\galee\PycharmProjects\Hakaton\path.png')
    await bot.send_photo(chat_id=user_id, photo=media)


@dp.message(F.location)
async def check_location(message: Message) -> None:  # check if player near right place
    _location = (message.location.latitude, message.location.longitude)
    print(message.from_user.id, _location)
    user_id = message.from_user.id
    user = quest_managers[user_id]
    if players[user_id].changed_location and geodesic(_location,
                                                      user.current_chapter.geo_position).meters <= DISTANCE:
        players[user_id].changed_location = False
        quest_description, markup = user.get_quest_desc_and_choices()

        await message.answer(text=f"Глава: <b>{user.current_chapter.title}</b>", reply_markup=ReplyKeyboardRemove())

        if quest_managers[user_id].current_chapter.video_path != "":
            cat = FSInputFile(quest_managers[user_id].current_chapter.video_path)
            await bot.send_video_note(message.chat.id, cat, length=360)

        await message.answer(text=quest_description, reply_markup=markup)
    elif geodesic(_location, user.current_chapter.geo_position).meters > DISTANCE:
        await bot.send_venue(message.chat.id, latitude=user.current_chapter.geo_position[0],
                             longitude=user.current_chapter.geo_position[1], title="Вы слишком далеко.",
                             address="Следующая точка здесь.")
        await message.answer("<i>Подойдите не меньше, чем на 50 метров.</i>")


@dp.message()
async def managing_player_responses(message: Message):
    if is_talking_with_npc[message.from_user.id]:
        # translation = translate.tat_to_rus(message.text)
        answer = ask_question(message.text, players[message.from_user.id].npc)
        await message.answer(text=answer)


@dp.callback_query(F.data.contains("ask_"))
async def handle_ask_question(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_talking_with_npc[user_id] = True
    players[user_id].npc = str(callback.data).split(";")[-1]
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(text="Ну, спрашивай")


# (ally/opponent)_id_name
@dp.callback_query(F.data.endswith("fight"))
async def handle_fight(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.edit_reply_markup(reply_markup=None)
    ally_markup = ally_deck(players[user_id])
    await bot.send_photo(chat_id=callback.message.chat.id,
                         photo=FSInputFile(r"C:\Users\galee\PycharmProjects\Hakaton\cards\default_card.png"),
                         caption="Ваша колода",
                         reply_markup=ally_markup)


@dp.callback_query(F.data.startswith("id_"))
async def handle_fighters(callback: CallbackQuery):
    user_id = callback.from_user.id
    player = players[user_id]
    if str(callback.data[3:]) in player.deck:
        player.deck.remove(str(callback.data[3:]))

        ally_markup = ally_deck(player)
        await callback.message.edit_media(
            media=InputMediaPhoto(media=FSInputFile(fr"C:\Users\galee\PycharmProjects\Hakaton\cards\default_card.png"),
                                  caption="Выбрано: " + str(len(player.deck))), reply_markup=ally_markup)
    else:
        player.deck.append(str(callback.data[3:]))
        ally_markup = ally_deck(player)
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=FSInputFile(fr"C:\Users\galee\PycharmProjects\Hakaton\cards\{str(callback.data[3:])}.png"),
                caption="Выбрано: " + str(len(player.deck))), reply_markup=ally_markup)


@dp.callback_query(F.data == "start_fighting")
async def handle_fighters(callback: CallbackQuery):
    user_id = callback.from_user.id
    player = players[user_id]
    if len(player.deck) == 3:
        opponents = []
        for item in player.items:
            if item['type'] == "opponent":
                opponents.append(item['id'])

        wep_app_url = 'https://your-webapp-url.com/?data={data}'
        data = player.deck + opponents
        encoded_data = urllib.parse.quote(json.dumps(data))
        url = wep_app_url.format(data=encoded_data)

        fight_markup = InlineKeyboardBuilder()
        fight_markup.button(text="Перейти", web_app=WebAppInfo(url=url))
        print(url)
        await callback.message.answer(text="Перейти", reply_markup=fight_markup.as_markup())
    else:
        await callback.answer("У Вас должно быть выбрано три карты")


@dp.callback_query()
async def apply_choice(callback: types.CallbackQuery):
    print(callback.data)
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

                if quest_managers[user_id].current_chapter.video_path != "":
                    cat = FSInputFile(quest_managers[user_id].current_chapter.video_path)
                    await bot.send_video_note(callback.message.chat.id, cat, length=360)
                await callback.message.answer(text="<b>Новая локация</b>", reply_markup=next_chapter_button_markup)
                await callback.message.edit_reply_markup(reply_markup=None)
            else:
                user.current_quest_id = choice.to_quest
                quest_description, markup = user.get_quest_desc_and_choices()
                if len(choice.result) > 0:
                    players[user_id].apply_changes(**choice.result)
                if quest_managers[user_id].current_chapter.video_path != "":
                    cat = FSInputFile(quest_managers[user_id].current_chapter.video_path)
                    await bot.send_video_note(callback.message.chat.id, cat, length=360)
                await callback.message.edit_reply_markup(reply_markup=None)
                await callback.message.answer(text=choice.text)
                await callback.message.answer(text=quest_description, reply_markup=markup)
            break
    else:
        await callback.message.delete()


def ally_deck(player: Player):
    ally_keyboard = InlineKeyboardBuilder()
    for item in player.items:
        if item['type'] == "ally" and item['id'] in player.deck:
            ally_keyboard.button(text=item["name"] + " ✅", callback_data=f"id_{item['id']}")
        elif item['type'] == "ally":
            ally_keyboard.button(text=item["name"] + " ☑️", callback_data=f"id_{item['id']}")
    ally_keyboard.button(text="⚔️ Начать ⚔️", callback_data="start_fighting")
    ally_keyboard.adjust(1, True)
    return ally_keyboard.as_markup()


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
