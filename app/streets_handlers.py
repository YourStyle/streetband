from aiogram import types, Dispatcher
from aiogram.dispatcher import filters, FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from gadgets import service as s
from scripts.calculate_distance import choose_shortest, calc_distance
from gadgets.callback_datas import groups_callback, location_callback
from gadgets.dialogs import msg
from gadgets.states import ChoosingMusician
from database import database as db, cache

location_kb = InlineKeyboardMarkup([])


async def show_musiacians(message: types.Message, state: FSMContext):
    await message.answer(text=msg.send_location)
    await state.set_state(ChoosingMusician.Choosing_musician)


async def get_location(message: types.Message):
    if location_kb == InlineKeyboardMarkup([]):
        pass
    else:
        location_kb.inline_keyboard.clear()

    location = message.location
    coordinates = {"latitude": location["latitude"], "longitude": location["longitude"]}
    cache.jset(f"{str(message.from_user.id)}_loc", coordinates)

    closest_musicians = choose_shortest(location)
    flag = closest_musicians[1]
    closest_musicians = closest_musicians[0]
    inc = 0
    counter = 0
    for artist_name, distance, artist_id in closest_musicians:
        if counter < flag:
            text = f"{artist_name} в {distance} м. от вас"
        else:
            text = f"{artist_name} в {distance} км. от вас"
        location_kb.row(
            InlineKeyboardButton(text=text, callback_data=location_callback.new(location=inc,
                                                                                artist_id=artist_id)))
        inc += 1
        counter += 1
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
        await call.message.answer_venue(latitude=artist_location["latitude"], longitude=artist_location["longitude"],
                                        title=artist_name,
                                        address="жанр: " + await s.get_genres_names(artist_genre, False),
                                        foursquare_type="arts_entertainment/default",
                                        reply_markup=s.create_group_caption_kb(artist_id, counter))
    else:
        arctic = {"latitude": -79.474655, "longitude": 29.507431}
        await call.message.answer_venue(latitude=arctic["latitude"], longitude=arctic["longitude"],
                                        title=artist_name,
                                        address="жанр: " + await s.get_genres_names(artist_genre, False, ),
                                        foursquare_type="arts_entertainment/default",
                                        reply_markup=s.create_group_caption_kb(artist_id, counter))


async def rephresh_nearby_groups(message: types.Message):
    location = message.location
    coordinates = {"latitude": location["latitude"], "longitude": location["longitude"]}
    cache_cor: dict = cache.jget(f"{str(message.from_user.id)}_loc")
    if cache_cor is None:
        db.get_musicians()
    delta_dist = calc_distance(coordinates["latitude"], coordinates["longitude"], cache_cor["latitude"],
                               cache_cor["longitude"])
    if float(delta_dist) > 500:
        cache.jset(f"{str(message.from_user.id)}_loc", coordinates)
        if location_kb == InlineKeyboardMarkup([]):
            pass
        else:
            location_kb.inline_keyboard.clear()

        location = message.location
        closest_musicians = choose_shortest(location)

        flag = closest_musicians[1]

        closest_musicians = closest_musicians[0]
        inc = 0
        counter = 0
        for artist_name, distance, artist_id in closest_musicians:
            if counter < flag:
                text = f"{artist_name} в {distance} м. от вас"
            else:
                text = f"{artist_name} в {distance} км. от вас"
            location_kb.row(
                InlineKeyboardButton(text=text, callback_data=location_callback.new(location=inc,
                                                                                    artist_id=artist_id)))
            inc += 1
            counter += 1
        await message.answer(text="Вы прошли 500м! Новый список ближайших артистов", reply_markup=location_kb)


async def show_groups(call: CallbackQuery, state: FSMContext):
    await call.answer()
    if not location_kb["inline_keyboard"]:
        await state.set_state(ChoosingMusician.Choosing_musician)
        await call.message.answer(text="Отправьте ваше местоложение заново")
    else:
        await call.message.answer(text="Список ближайших артистов", reply_markup=location_kb)


def check_streets(dp: Dispatcher):
    dp.register_message_handler(show_musiacians, filters.Text(contains="Музыканты"), state="*")
    dp.register_message_handler(get_location,
                                content_types=types.ContentTypes.LOCATION, state=ChoosingMusician.Choosing_musician)
    dp.register_edited_message_handler(rephresh_nearby_groups,
                                       content_types=types.ContentTypes.LOCATION,
                                       state=ChoosingMusician.Choosing_musician)
    dp.register_callback_query_handler(get_group, location_callback.filter(), state=ChoosingMusician.Choosing_musician)
    dp.register_callback_query_handler(show_groups, groups_callback.filter(location="back"),
                                       state=ChoosingMusician.Choosing_musician)
