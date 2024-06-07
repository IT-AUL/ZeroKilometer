from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from com.hakaton.quest.game import *
from com.hakaton.quest.npc_manager import ask_question

speech_router = Router(name="speech_router")


@speech_router.message()
async def managing_player_responses(message: Message):
    if is_talking_with_npc[message.from_user.id]:
        # translation = translate.tat_to_rus(message.text)
        answer = ask_question(message.text, players[message.from_user.id].npc)
        await message.answer(text=answer)


@speech_router.callback_query(F.data.contains("ask_"))
async def handle_ask_question(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_talking_with_npc[user_id] = True
    players[user_id].npc = str(callback.data).split(";")[-1]
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(text="Ну, спрашивай")
