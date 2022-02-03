from aiogram import Dispatcher, types
from aiogram.dispatcher import filters
from aiogram.types import CallbackQuery

from streetband.app import service as s
from streetband.app.callback_datas import info_callback, add_callback
from streetband.config import GENRES
from streetband.database import database as db, cache


async def open_profile(message: types.Message):
    await message.answer(text="Вы открыли ваш личный кабинет", reply_markup=s.MAIN_KB)


async def group_info(call: CallbackQuery, callback_data: dict):
    groups = cache.jget("musicians")
    group = groups[int(callback_data["db_loc"])]
    group_name = group["musician_name"]
    group_picture = group["group_pic"]
    genres = await s.get_genres_names(group["group_genre"], False)
    group_description = group["group_description"]
    group_leader = group["group_leader"]
    caption = f"Название: {group_name} \nЛидер группы: {group_leader}\nЖанр: {genres}\nОписание :{group_description}"
    await call.message.answer_photo(group_picture, caption)


async def add_to_favourite(call: CallbackQuery, callback_data: dict):
    await call.answer()
    db.to_fav(str(call.from_user.id), callback_data["id"])
    print("Чел добавил группу в избранное")


async def show_menu(message: types.Message):
    await message.answer(text="Вы перешли в личный кабинет", reply_markup=s.MAIN_KB)


async def donate(call: CallbackQuery):
    await call.answer()
    print("У чела много денег")


def use_buttons(dp: Dispatcher):
    dp.register_message_handler(open_profile, filters.Text(contains="Профиль"))
    dp.register_callback_query_handler(group_info, info_callback.filter(), state="*")
    dp.register_callback_query_handler(add_to_favourite, add_callback.filter(), state="*")
    dp.register_message_handler(show_menu, commands="show_menu", state="*")
    dp.register_callback_query_handler(donate, lambda call: call.data and call.data == 'donate', state="*")
