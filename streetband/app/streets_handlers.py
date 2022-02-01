from aiogram import types, Dispatcher
from aiogram.dispatcher import filters, FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from streetband.app import service as s
from streetband.app.calculate_distance import choose_shortest
from streetband.app.callback_datas import groups_callback, location_callback
from streetband.app.dialogs import msg
from streetband.app.states import Choosing_Musician
from streetband.data.locations import artists
from streetband.database import database as db

location_kb = InlineKeyboardMarkup()


async def show_musiacians(message: types.Message):
    await message.answer(text=msg.send_location, reply_markup=types.ReplyKeyboardRemove())
    await Choosing_Musician.Choosing_musician


async def get_location(message: types.Message):
    location = message.location
    closest_musicians = choose_shortest(location)
    inc = 0
    print(closest_musicians)
    for artist_name, distance, latitude, longitude, genre, artist_id in closest_musicians:
        text = f"{artist_name} в {distance}км от вас"
        location_kb.row(
            InlineKeyboardButton(text=text, callback_data=location_callback.new(location=inc,
                                                                                artist_id=artist_id)))
        inc += 1
    await message.answer(text="Список ближайших артистов", reply_markup=location_kb)


async def get_group(call: CallbackQuery, callback_data: dict):
    await call.answer()
    print(call)
    print(callback_data)
    # Допилить получение музыканта из бд, что на выход мы получали локу (лат, лонг), название группы, жанр
    db.get_musician(callback_data["artist_id"])
    # Реализации без бд
    group = [i for i in artists if i[3]["artist_id"] == callback_data["artist_id"]][0]
    print(group)
    await call.message.answer_venue(latitude=group[1]["lat"], longitude=group[1]["lon"],
                                    title=group[0],
                                    address="жанр: " + group[2]["genre"],
                                    foursquare_type="food",
                                    reply_markup=s.GROUP_CAPTIONS_KB)


async def show_groups(call: CallbackQuery):
    await call.answer()
    await call.message.answer(text="Список ближайших артистов", reply_markup=location_kb)


async def whaat(call: CallbackQuery):
    print(call)


def check_streets(dp: Dispatcher):
    dp.register_message_handler(show_musiacians, filters.Text(contains="Музыканты"))
    dp.register_message_handler(get_location,
                                content_types=types.ContentTypes.LOCATION)
    dp.register_callback_query_handler(get_group, location_callback.filter())
    dp.register_callback_query_handler(show_groups, groups_callback.filter(location="group_locations"))
    dp.register_callback_query_handler(whaat, state="*")
