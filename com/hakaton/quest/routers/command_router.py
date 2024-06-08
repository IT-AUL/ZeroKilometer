from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import InputMediaPhoto
from com.hakaton.quest.game import *
from com.hakaton.quest.quest_manager import QuestManager

command_router = Router(name="command")


@command_router.message(CommandStart())
async def start_quest(message: Message) -> None:
    user_id = message.from_user.id
    if message.from_user.id not in quest_managers.keys():
        quest_managers[user_id] = QuestManager(CHAPTERS)
        await message.answer(text=f"Глава: <b>{quest_managers[user_id].current_chapter.title}</b>")
    if not quest_managers[user_id].player.changed_location:
        quest_managers[user_id].is_talking_with_npc = False
        quest_description, markup = quest_managers[user_id].get_quest_desc_and_choices()
        await send_photo_or_video_note(user_id, message)
        await message.answer(text=quest_description, reply_markup=markup)


@command_router.message(Command("no_fight"))
async def no_fight(message: Message) -> None:
    user_id = message.from_user.id
    if not quest_managers[user_id].player.changed:
        quest_managers[user_id].player.will_fight = 0
        quest_managers[user_id].player.changed = True
        await message.answer(text="Вы включили мирное прохождение")
    else:
        await message.answer(text="Вы не можете поменять режим.")


@command_router.message(Command("clear"))
async def clear(message: Message) -> None:
    user_id = message.from_user.id
    quest_managers[user_id] = QuestManager(CHAPTERS)
    await message.answer(text=f"Глава: <b>{quest_managers[user_id].current_chapter.title}</b>")
    quest_description, markup = quest_managers[user_id].get_quest_desc_and_choices()
    await message.answer(text=quest_description, reply_markup=markup)


@command_router.message(Command("cards"))
async def view_cards(message: Message) -> None:
    user_id = message.from_user.id
    media = []
    for it in quest_managers[user_id].player.items:
        print(it)
        if str(it["type"]) == "ally":
            media.append(
                InputMediaPhoto(
                    media=FSInputFile(fr'C:\Users\galee\PycharmProjects\Hakaton\cards\{str(it['id'])}.png')))
    if len(media) > 0:
        await message.answer_media_group(media=media)
    else:
        await message.answer(text="У Вас нет карточек.")


@command_router.message(Command("path"))
async def view_path(message: Message) -> None:
    await message.answer(text="https://yandex.ru/maps/-/CDbHVY~n")
