from aiogram import types, Dispatcher
from aiogram.dispatcher import filters, FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from streetband.app.calculate_distance import choose_shortest
from streetband.app.callback_datas import groups_callback, location_callback
from streetband.app.dialogs import msg
from streetband.app.states import Choosing_Musician

location_kb = InlineKeyboardMarkup()

async def show_musiacians(message: types.Message):
    await message.answer(text=msg.send_location, reply_markup=types.ReplyKeyboardRemove())
    await Choosing_Musician.first()


async def get_location(message: types.Message):
    location = message.location
    latitude = location.latitude
    longitude = location.longitude
    closest_musicians = choose_shortest(location)
    inc = 0
    for artist_name, distance, url, artist_location, artist_id in closest_musicians:
        text = f"{artist_name} в {distance}км от вас"
        location_kb.row(
            InlineKeyboardButton(text=text, callback_data=location_callback.new(location=inc,
                                                                                artist_id=artist_id, distance=distance,
                                                                                name=artist_name)))
        inc += 1
    await message.answer(text="Список ближайших артистов", reply_markup=location_kb)


async def get_group(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer()
    print(call)
    # logger.info(f"callback_data = {call.data}")
    # logger.info(f"callback_data dict = {callback_data}")
    # artist_id = callback_data.get("artist_id")
    print(callback_data)
    await call.message.answer_venue(latitude=55.757784, longitude=37.633295, title="Александр Машин",
                                    address="жанр: джаз",
                                    foursquare_type="food",
                                    reply_markup=s.GROUP_CAPTIONS_KB)
    await state.reset_state()


async def show_groups(call: CallbackQuery):
    print(location_kb)
    await call.message.answer(text="Ближайшие группы", reply_markup=location_kb)
    await Choosing_Musician.first()


def check_streets(dp: Dispatcher):
    dp.register_message_handler(show_musiacians, filters.Text(contains="Музыканты"))
    dp.register_message_handler(get_location, state=Choosing_Musician.Choosing_musician,
                                content_types=types.ContentTypes.LOCATION)
    dp.register_message_handler(get_group, location_callback.filter(), state=Choosing_Musician.Choosing_musician)
    dp.register_message_handler(show_groups, groups_callback.filter(location="group_locations"))
