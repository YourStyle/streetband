from aiogram import Dispatcher, types
from aiogram.dispatcher import filters
from aiogram.types import CallbackQuery

from streetband.app import service as s


async def open_profile(message: types.Message):
    await message.answer(text="Вы открыли ваш личный кабинет", reply_markup=s.MAIN_KB)


async def group_info(call: CallbackQuery):
    await call.answer()
    print("Чел чекнул инфо")


async def add_to_favourite(call: CallbackQuery):
    await call.answer()
    print("Чел добавил группу в избранное")


async def show_menu(message: types.Message):
    await message.answer(text="Вы перешли в личный кабинет", reply_markup=s.MAIN_KB)


async def donate(call: CallbackQuery):
    await call.answer()
    print("У чела много денег")


def use_buttons(dp: Dispatcher):
    dp.register_message_handler(open_profile, filters.Text(contains="Профиль"))
    dp.register_callback_query_handler(group_info, lambda call: call.data and call.data == 'info', state="*")
    dp.register_callback_query_handler(add_to_favourite, lambda call: call.data and call.data == 'add', state="*")
    dp.register_message_handler(show_menu, commands="show_menu", state="*")
    dp.register_callback_query_handler(donate, lambda call: call.data and call.data == 'donate', state="*")
