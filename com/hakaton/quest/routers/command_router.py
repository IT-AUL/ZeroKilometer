from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InputMediaPhoto, FSInputFile

from com.hakaton.quest.main import players, quest_managers, is_talking_with_npc, send_photo_or_video_note, bot
from com.hakaton.quest.player import Player
from com.hakaton.quest.quest_manager import QuestManager

r = Router(name="command")


@r.message(CommandStart())
async def start_quest(message: Message) -> None:
    user_id = message.from_user.id
    if message.from_user.id not in players.keys():
        players[user_id] = Player()
        quest_managers[user_id] = QuestManager(player=players[user_id])
        await message.answer(text=f"Глава: <b>{quest_managers[user_id].current_chapter.title}</b>")
    if not players[user_id].changed_location:
        is_talking_with_npc[user_id] = False
        quest_description, markup = quest_managers[user_id].get_quest_desc_and_choices()
        await send_photo_or_video_note(user_id, message)
        await message.answer(text=quest_description, reply_markup=markup)


@r.message(Command("no_fight"))
async def no_fight(message: Message) -> None:
    user_id = message.from_user.id
    if not players[user_id].changed:
        players[user_id].will_fight = 0
        players[user_id].changed = True
        await message.answer(text="Вы включили мирное прохождение")
    else:
        await message.answer(text="Вы не можете поменять режим.")


@r.message(Command("clear"))
async def clear(message: Message) -> None:
    user_id = message.from_user.id
    players[user_id] = Player()
    quest_managers[user_id] = QuestManager(player=players[user_id])
    await message.answer(text=f"Глава: <b>{quest_managers[user_id].current_chapter.title}</b>")
    is_talking_with_npc[user_id] = False
    quest_description, markup = quest_managers[user_id].get_quest_desc_and_choices()
    await message.answer(text=quest_description, reply_markup=markup)


@r.message(Command("cards"))
async def view_cards(message: Message) -> None:
    user_id = message.from_user.id
    media = []
    for it in players[user_id].items:
        print(it)
        if str(it["type"]) == "ally":
            media.append(
                InputMediaPhoto(
                    media=FSInputFile(fr'C:\Users\galee\PycharmProjects\Hakaton\cards\{str(it['id'])}.png')))
    if len(media) > 0:
        await bot.send_media_group(chat_id=user_id, media=media)
    else:
        await message.answer(text="У Вас нет карточек.")


@r.message(Command("path"))
async def view_path(message: Message) -> None:
    await message.answer(text="https://yandex.ru/maps/-/CDbHVY~n")