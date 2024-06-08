from aiogram import Router
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, CallbackQuery
from com.hakaton.quest.game import *

choice_router = Router(name="choice_router")

next_chapter_button_markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text="Двигаться дальше", request_location=True)]])


@choice_router.callback_query()
async def apply_choice(callback: CallbackQuery):
    print(callback.data)
    user_id = callback.from_user.id
    user = quest_managers[user_id]
    for choice in user.current_quest.choices:
        quest_managers[user_id].is_talking_with_npc = False

        # i compare unique combination of current chapter, quest and choice id with current choice
        compare_data = user.current_chapter_id + ";" + user.current_quest_id + ";" + choice.choice_id
        if compare_data == callback.data:
            if choice.to_quest.startswith("ch"):
                quest_managers[user_id].player.changed_location = True

                user.current_chapter_id = choice.to_quest
                user.current_chapter = user.chapters[user.current_chapter_id]
                user.current_quest_id = "q0"
                user.current_quest = user.current_chapter.quests[user.current_quest_id]

                await send_photo_or_video_note(user_id, callback.message)
                await callback.message.answer(text="<b>Новая локация</b>", reply_markup=next_chapter_button_markup)
                await callback.message.edit_reply_markup(reply_markup=None)
            else:
                user.current_quest_id = choice.to_quest
                quest_description, markup = user.get_quest_desc_and_choices()
                if len(choice.result) > 0:
                    quest_managers[user_id].player.apply_changes(**choice.result)

                await send_photo_or_video_note(user_id, callback.message)
                await callback.message.edit_reply_markup(reply_markup=None)
                await callback.message.answer(text=choice.text)
                await callback.message.answer(text=quest_description, reply_markup=markup)
            break
    else:
        await callback.message.delete()
