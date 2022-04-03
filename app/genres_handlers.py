import asyncio

from aiogram import Dispatcher, types
from aiogram.types import CallbackQuery

from gadgets import service as s
from gadgets.dialogs import msg
from config import YEAR
from database import cache, database as db


async def get_config(message: types.Message):
    # print(db.get_user(str(message.from_user.id))["fav_genres"])
    is_musician = db.get_user(str(message.from_user.id))["musician"]
    user_genre_ids = await s.get_genre_ids(str(message.from_user.id), is_musician)
    if user_genre_ids:
        cache.setex(f"last_msg_{message.from_user.id}", YEAR, message.message_id + 2)
        genres = await s.get_genres_names(user_genre_ids)
        await message.answer(msg.config.format(genres=genres),
                             reply_markup=s.CONFIG_KB)
    else:
        cache.setex(f"last_msg_{message.from_user.id}", YEAR, message.message_id + 1)
        await message.answer(
            msg.no_genres,
            reply_markup=s.genres_kb(db.get_user(str(message.from_user.id))["fav_genres"])
        )


async def get_config_musician(call: CallbackQuery):
    await call.answer()
    # print(db.get_musician(str(call.from_user.id))["group_genre"])
    is_musician = db.get_user(str(call.from_user.id))["musician"]
    user_genre_ids = await s.get_genre_ids(str(call.from_user.id), is_musician)
    if user_genre_ids:
        cache.setex(f"last_msg_{str(call.from_user.id)}", YEAR, int(call.id) + 2)
        genres = await s.get_genres_names(user_genre_ids)
        await call.message.answer(msg.config.format(genres=genres),
                                  reply_markup=s.CONFIG_M_KB)
    else:
        cache.setex(f"last_msg_{call.from_user.id}", YEAR, int(call.id) + 1)
        await call.message.answer(
            msg.no_genres,
            reply_markup=s.genres_kb(db.get_musician(str(call.from_user.id))["group_genre"])
        )


async def delete_config(call: CallbackQuery):
    # genres_list = await s.get_genre_ids(str(call.from_user.id))
    is_musician = db.get_user(str(call.from_user.id))["musician"]
    cache.delete(f"{call.from_user.id}")

    await call.answer()
    cache.incr(f"last_msg_{call.from_user.id}")
    if is_musician:
        db.delete_m_genres(str(call.from_user.id))
        await call.bot.send_message(call.from_user.id,
                                    msg.data_delete,
                                    reply_markup=s.MUSICIAN_LC_KB)
    else:
        db.delete_genres(str(call.from_user.id))
        await call.bot.send_message(call.from_user.id,
                                    msg.data_delete,
                                    reply_markup=s.MAIN_KB)
    cache.delete(f"{str(call.from_user.id)}_gen")


async def set_or_update_config(call: CallbackQuery, offset=""):
    is_musician = db.get_user(str(call.from_user.id))["musician"]

    user_id = str(call.from_user.id)
    if cache.jget(f"{user_id}_gen") is None:
        cache.jset(f"{user_id}_gen", "editing")

    # если нет, отредактируем сообщение и клавиатуру
    if not is_musician:
        genres_ids = await s.get_genre_ids(user_id, is_musician)
        genres = await s.get_genres_names(genres_ids)
        if offset == "":
            if (call.data.split("#")[-1] == "0") or (call.data.split("#")[-1] == "5"):
                await set_or_update_config(call, offset=call.data.split("#")[-1])
            else:
                await call.message.answer(
                    msg.set_genres.format(genres=genres),
                    reply_markup=s.genres_kb(genres_ids)
                )
        else:
            await call.message.edit_text(
                msg.set_genres.format(genres=genres)
            )
            await call.message.edit_reply_markup(
                reply_markup=s.genres_kb(genres_ids, int(offset))
            )
    else:
        m_genre_ids = await s.get_genre_ids(str(call.from_user.id), is_musician)
        genres = await s.get_genres_names(m_genre_ids)
        if offset == "":
            if (call.data.split("#")[-1] == "0") or (call.data.split("#")[-1] == "5"):
                await set_or_update_config(call, offset=call.data.split("#")[-1])
            else:
                await call.message.answer(
                    msg.set_genres.format(genres=genres),
                    reply_markup=s.genres_kb(m_genre_ids)
                )
        else:
            await call.message.edit_text(
                msg.set_genres.format(genres=genres)
            )
            await call.message.edit_reply_markup(
                reply_markup=s.genres_kb(m_genre_ids, int(offset))
            )
    await call.answer()


async def update_genres_info(call: CallbackQuery):
    offset = call.data.split("#")[-2]
    s.update_genres(call.from_user.id, call.data)
    await set_or_update_config(call, offset=offset)
    await call.answer()


async def save_config(call: CallbackQuery):
    is_musician = db.get_user(str(call.from_user.id))["musician"]
    genres_list = await s.get_genre_ids(str(call.from_user.id), is_musician)
    if genres_list:
        if is_musician:
            db.add_m_genre(
                str(call.from_user.id),
                genres_list
            )
            await call.answer()
            await call.bot.send_message(
                call.from_user.id,
                msg.save,
                reply_markup=s.MUSICIAN_LC_KB
            )
        else:
            db.add_genre(
                str(call.from_user.id),
                genres_list
            )
            await call.answer()
            await call.bot.send_message(
                call.from_user.id,
                msg.save,
                reply_markup=s.MAIN_KB
            )
    else:
        # не сохраняем если список пустой
        await call.answer()
        no_genres = await call.message.answer(msg.cb_not_saved)
        await asyncio.sleep(3)
        await no_genres.delete()
    cache.delete(f"{str(call.from_user.id)}_gen")


def choose_genres(dp: Dispatcher):
    dp.register_message_handler(get_config, lambda message: message.text == msg.fav_genres, state="*")
    dp.register_callback_query_handler(get_config_musician, lambda call: call.data and call.data == 'edit_genres',
                                       state="*")
    dp.register_callback_query_handler(delete_config, lambda call: call.data == 'delete_config', state="*")
    dp.register_callback_query_handler(set_or_update_config, lambda call: call.data.startswith('edit_config'),
                                       state="*")
    dp.register_callback_query_handler(update_genres_info, lambda call: call.data[:6] in ['del_ge', 'add_ge'],
                                       state="*")
    dp.register_callback_query_handler(save_config, lambda call: call.data == 'save_config', state="*")
