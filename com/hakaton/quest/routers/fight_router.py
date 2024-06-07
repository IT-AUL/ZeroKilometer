import json
import urllib

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto, KeyboardButton, WebAppInfo, ReplyKeyboardMarkup

from com.hakaton.quest.game import *
import urllib.parse

# from com.hakaton.quest.main import bot

fight_router = Router(name="fight_router")


# (ally/opponent)_id_name
@fight_router.callback_query(F.data.endswith("fight"))
async def handle_fight(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.edit_reply_markup(reply_markup=None)
    ally_markup = ally_deck(players[user_id])
    # await bot.send_photo(chat_id=callback.message.chat.id,
    #                      photo=FSInputFile(r"C:\Users\galee\PycharmProjects\Hakaton\cards\default_card.png"),
    #                      caption="Ваша колода",
    #                      reply_markup=ally_markup)
    await callback.message.answer_photo(
        photo=FSInputFile(r"C:\Users\galee\PycharmProjects\Hakaton\cards\default_card.png"),
        caption="Ваша колода",
        reply_markup=ally_markup)


@fight_router.callback_query(F.data.startswith("id_"))
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


@fight_router.callback_query(F.data == "start_fighting")
async def handle_fighters(callback: CallbackQuery):
    user_id = callback.from_user.id
    player = players[user_id]
    if len(player.deck) == 3:
        opponents = []
        for item in player.items:
            if item['type'] == "opponent":
                opponents.append(item['id'])

        wep_app_url = 'https://poitzero.netlify.app/?data={data}'
        data = player.deck + opponents
        encoded_data = urllib.parse.quote(json.dumps(data))
        url = wep_app_url.format(data=encoded_data)

        fight_markup = KeyboardButton(text="Начать бой", web_app=WebAppInfo(url=url))
        print(url)
        await callback.message.answer(text="Перейти", reply_markup=ReplyKeyboardMarkup(keyboard=[[fight_markup]]))
    else:
        await callback.answer("У Вас должно быть выбрано три карты")
