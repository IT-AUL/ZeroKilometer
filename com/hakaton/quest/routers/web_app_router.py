import json

from aiogram import Router, types, F

from com.hakaton.quest.cards import cards
from com.hakaton.quest.game import *

web_app_router = Router(name="wep_app_router")


@web_app_router.message(F.web_app_data)
async def handle_web_app_data(message: types.Message):
    data = json.loads(message.web_app_data.data)
    if data['data'] != 'lose':
        defeated_enemies = list(data['data'])
        item = []
        for enemy in defeated_enemies:
            item.append(cards[enemy])
        players[message.from_user.id].items += item
        print(players[message.from_user.id].items)
        await message.answer("Новые карточки добавлены")
