import re

from aiogram import Dispatcher, types
from aiogram.dispatcher import filters, FSMContext
from aiogram.types import InputFile

from app.dialogs import msg
from database import database as db
from app import service as s


async def start_qr(message: types.Message):
    # закидываем пользователя в дб по его user_id и добавляем user_name
    user_name = message.from_user.first_name
    language = message.from_user.language_code
    if not db.user_exists(message.from_user.id):
        user = db.add_user(str(message.from_user.id), user_name, language)
    musician = db.get_musician(str(message.text.split()[-1][4::]))
    print(musician)
    print(message.text.split()[-1][4::])
    info = []

    genre = "🎸Жанр:" + await s.get_genres_names(musician["group_genre"], False)
    info.append(genre)
    desc = "📝Описание:" + musician["group_description"]
    info.append(desc)
    leader = "🤴Лидер: " + musician["group_leader"]
    info.append(leader)

    caption = "\n".join(info)
    await message.answer_photo(photo=musician["group_pic"], caption=caption, reply_markup=s.DONATE_KB)
    await message.answer(msg.wellcome, reply_markup=s.MAIN_KB)


async def start_normal(message: types.Message, state: FSMContext):
    await state.reset_state()
    temp = await message.answer(text="м", reply_markup=types.ReplyKeyboardRemove())
    await temp.delete()
    user_id = str(message.from_user.id)
    if db.user_exists(user_id) and (not db.get_user(user_id)["musician"]):
        await message.answer(msg.wellcome, reply_markup=s.MAIN_KB)
    elif db.user_exists(user_id) and (db.get_user(user_id)["musician"]):
        await message.answer(msg.wellcome, reply_markup=s.MUSICIAN_LC_KB)
    else:
        await message.answer(msg.choice, reply_markup=s.CHOICE_KB)


def start_bot(dp: Dispatcher):
    dp.register_message_handler(start_qr, filters.CommandStart(deep_link=re.compile("mus_[0-9]{9}")))
    dp.register_message_handler(start_normal, filters.CommandStart(), state="*")
