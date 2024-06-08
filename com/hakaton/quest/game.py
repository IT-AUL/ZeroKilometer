from aiogram.types import FSInputFile, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from com.hakaton.quest.dialogue import Translate
from com.hakaton.quest.player import Player
from quest_manager import load_chapters

quest_managers = {}
translate = Translate()

CHAPTERS = load_chapters()


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


async def send_photo_or_video_note(user_id, message: Message):
    if quest_managers[user_id].current_chapter.video_path != "":
        cat = FSInputFile(quest_managers[user_id].current_chapter.video_path)
        if quest_managers[user_id].current_chapter.video_path.endswith(".mp4"):
            await message.answer_video_note(cat, length=360)
        else:
            await message.answer_photo(photo=cat)
