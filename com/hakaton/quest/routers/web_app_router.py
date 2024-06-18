import json

from aiogram import Router, types, F

from com.hakaton.quest.cards import cards
from com.hakaton.quest.game import *
from com.hakaton.quest.routers.choice_router import next_chapter_button_markup

web_app_router = Router(name="wep_app_router")


@web_app_router.message(F.web_app_data)
async def handle_web_app_data(message: types.Message):
    user_id = message.from_user.id
    data = json.loads(message.web_app_data.data)
    print("data", data)
    info = str(data['info'])

    quest_managers[message.from_user.id].player.apply_changes(clear="True")
    quest_managers[user_id].player.deck = []
    if data['data'] != 'lose':
        defeated_enemies = list(data['data'])
        print("defeated_enemies", defeated_enemies)
        item = []
        for enemy in defeated_enemies:
            item.append(cards[enemy])
        quest_managers[message.from_user.id].player.items += item
        quest_managers[message.from_user.id].player.apply_changes(clear=True)
        await message.answer("Новые карточки добавлены")
    else:
        await message.answer("Вы проиграли")

    if info.startswith('c'):
        quest_managers[message.from_user.id].player.changed_location = True

        quest_managers[message.from_user.id].current_chapter_id = info
        quest_managers[message.from_user.id].current_quest_id = 'q0'
        quest_managers[message.from_user.id].current_chapter = quest_managers[message.from_user.id].chapters[info]
        quest_managers[message.from_user.id].current_quest = \
            quest_managers[message.from_user.id].current_chapter.quests['q0']

        await send_photo_or_video_note(user_id, message)
        await message.answer(text="<b>Новая локация</b>", reply_markup=next_chapter_button_markup)
    else:
        quest_managers[message.from_user.id].current_quest_id = info
        quest_managers[message.from_user.id].current_quest = \
            quest_managers[message.from_user.id].current_chapter.quests[info]
