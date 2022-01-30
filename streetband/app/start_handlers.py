import re

from aiogram import Dispatcher, types
from aiogram.dispatcher import filters, FSMContext
from aiogram.types import InputFile

from streetband.app.dialogs import msg
from streetband.database import database as db
from streetband.app import service as s


async def start_qr(message: types.Message):
    # закидываем пользователя в дб по его user_id и добавляем user_name
    user_name = message.from_user.first_name
    language = message.from_user.language_code
    if not db.user_exists():
        user = db.add_user(message.from_user.id, user_name, language)
    get_musician = db.get_musician(message.text.split()[-1])
    photo = InputFile("bot/acdc.jpg")
    await message.answer_photo(photo=photo, caption=msg.text_placeholder, reply_markup=s.DONATE_KB)
    await message.answer(reply_markup=s.MAIN_KB)


async def start_normal(message: types.Message, state: FSMContext):
    await state.reset_state()
    user_id = message.from_user.id
    if db.user_exists(user_id):
        await message.answer(msg.wellcome, reply_markup=s.MAIN_KB)
    else:
        await message.answer(msg.choice, reply_markup=s.CHOICE_KB)


def start_bot(dp: Dispatcher):
    dp.register_message_handler(start_qr, filters.CommandStart(deep_link=re.compile("mus_[1-9]{5}")))
    dp.register_message_handler(start_normal, filters.CommandStart(), state="*")
