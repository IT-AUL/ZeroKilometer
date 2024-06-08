import json

from aiogram import Router, types, F

from com.hakaton.quest.cards import cards
from com.hakaton.quest.game import *

web_app_router = Router(name="wep_app_router")


@web_app_router.message(F.web_app_data)
async def handle_web_app_data(message: types.Message):
    ch_id = "ch" + str(int(str(quest_managers[message.from_user.id].current_chapter_id)[2:]) + 1)
    quest_managers[message.from_user.id].current_chapter_id = ch_id
    quest_managers[message.from_user.id].current_quest_id = 'q0'
    quest_managers[message.from_user.id].current_chapter = quest_managers[message.from_user.id].chapters[ch_id]
    quest_managers[message.from_user.id].current_quest = quest_managers[message.from_user.id].current_chapter['q0']

    data = json.loads(message.web_app_data.data)
    if data['data'] != 'lose':
        defeated_enemies = list(data['data'])
        item = []
        for enemy in defeated_enemies:
            item.append(cards[enemy])
        quest_managers[message.from_user.id].player.items += item
        print(quest_managers[message.from_user.id].player.items)
        await message.answer("Новые карточки добавлены")
    else:
        await message.answer("Вы проиграли")
