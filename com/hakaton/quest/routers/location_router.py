from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from geopy.distance import geodesic

from com.hakaton.quest.game import *

# from com.hakaton.quest.main import bot

location_router = Router(name="location_router")

DISTANCE = 5000000000


@location_router.message(F.location)
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

        await send_photo_or_video_note(user_id, message)

        await message.answer(text=quest_description, reply_markup=markup)
    elif geodesic(_location, user.current_chapter.geo_position).meters > DISTANCE:
        # await bot.send_venue(message.chat.id, latitude=user.current_chapter.geo_position[0],
        #                      longitude=user.current_chapter.geo_position[1], title="Вы слишком далеко.",
        #                      address="Следующая точка здесь.")
        await message.answer_venue(latitude=user.current_chapter.geo_position[0],
                                   longitude=user.current_chapter.geo_position[1], title="Вы слишком далеко.",
                                   address="Следующая точка здесь.")
        await message.answer("<i>Подойдите не меньше, чем на 50 метров.</i>")
