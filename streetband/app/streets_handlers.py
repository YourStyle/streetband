from aiogram import types, Dispatcher
from aiogram.dispatcher import filters, FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from streetband.app import service as s
from streetband.app.calculate_distance import choose_shortest
from streetband.app.callback_datas import groups_callback, location_callback, info_callback
from streetband.app.dialogs import msg
from streetband.app.states import ChoosingMusician
from streetband.database import database as db, cache

location_kb = InlineKeyboardMarkup()


async def show_musiacians(message: types.Message, state: FSMContext):
    await message.answer(text=msg.send_location, reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ChoosingMusician.Choosing_musician)


async def get_location(message: types.Message):
    location = message.location
    closest_musicians = choose_shortest(location)
    inc = 0
    for artist_name, distance, artist_id in closest_musicians:
        text = f"{artist_name} в {distance}км от вас"
        location_kb.row(
            InlineKeyboardButton(text=text, callback_data=location_callback.new(location=inc,
                                                                                artist_id=artist_id)))
        inc += 1
    await message.answer(text="Список ближайших артистов", reply_markup=location_kb)


async def get_group(call: CallbackQuery, callback_data: dict):
    await call.answer()

    counter = 0
    groups = cache.jget("musicians")
    for i in groups:
        if i["musician_id"] == callback_data["artist_id"]:
            break
        counter += 1
    group = groups[counter]
    artist_id = group["musician_id"]
    artist_name = group["musician_name"]
    artist_location = group["current_location"]
    artist_genre = group["group_genre"]

    if artist_location is not None:
        await call.message.answer_venue(latitude=artist_location["lat"], longitude=artist_location["lon"],
                                        title=artist_name,
                                        address="жанр: " + await s.get_genres_names(artist_genre, False),
                                        foursquare_type="arts_entertainment/default",
                                        reply_markup=s.create_group_caption_kb(artist_id, counter))
    else:
        arctic = {"lat": -79.474655, "lon": 29.507431}
        await call.message.answer_venue(latitude=arctic["lat"], longitude=arctic["lon"],
                                        title=artist_name,
                                        address="жанр: " + await s.get_genres_names(artist_genre, False),
                                        foursquare_type="arts_entertainment/default",
                                        reply_markup=s.create_group_caption_kb(artist_id, counter))


async def show_groups(call: CallbackQuery):
    await call.answer()
    await call.message.answer(text="Список ближайших артистов", reply_markup=location_kb)


async def whaat(call: CallbackQuery):
    print(call)


def check_streets(dp: Dispatcher):
    dp.register_message_handler(show_musiacians, filters.Text(contains="Музыканты"))
    dp.register_message_handler(get_location,
                                content_types=types.ContentTypes.LOCATION, state=ChoosingMusician.Choosing_musician)
    dp.register_callback_query_handler(get_group, location_callback.filter(), state=ChoosingMusician.Choosing_musician)
    dp.register_callback_query_handler(show_groups, groups_callback.filter(location="group_locations"),
                                       state=ChoosingMusician.Choosing_musician)
    dp.register_callback_query_handler(whaat, state="*")
