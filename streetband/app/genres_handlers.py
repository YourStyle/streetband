from aiogram import Dispatcher, types
from aiogram.types import CallbackQuery

from streetband.app import service as s
from streetband.app.dialogs import msg
from streetband.config import YEAR
from streetband.database import cache, database as db


async def get_config(message: types.Message):
    user_genre_ids = await s.get_genre_ids(message.from_user.id)
    if user_genre_ids:
        cache.setex(f"last_msg_{message.from_user.id}", YEAR, message.message_id + 2)
        genres = await s.get_genres_names(user_genre_ids)
        await message.answer(msg.config.format(genres=genres),
                             reply_markup=s.CONFIG_KB)
    else:
        cache.setex(f"last_msg_{message.from_user.id}", YEAR, message.message_id + 1)
        await set_or_update_config(user_id=message.from_user.id)


async def delete_config(call: CallbackQuery):
    await db.delete_users(call.from_user.id)
    cache.delete(f"{call.from_user.id}")
    await call.answer()
    cache.incr(f"last_msg_{call.from_user.id}")
    await call.bot.send_message(call.from_user.id,
                                msg.data_delete,
                                reply_markup=s.MAIN_KB)


async def set_or_update_config(call: CallbackQuery = None,
                               user_id=None, offset=""):
    # если пришел callback, получим данные
    if call is not None:
        user_id = call.from_user.id
        offset = call.data.split("#")[-1]

    genres_ids = await s.get_genre_ids(user_id)
    genres = await s.get_genres_names(genres_ids)

    # если это первый вызов функции, отправим сообщение
    # если нет, отредактируем сообщение и клавиатуру
    if offset == "":
        await call.bot.send_message(
            user_id,
            msg.set_genres.format(genres=genres),
            reply_markup=s.genres_kb(genres_ids)
        )
    else:
        msg_id = cache.get(f"last_msg_{user_id}")
        await call.bot.edit_message_text(
            msg.set_genres.format(genres=genres),
            user_id,
            message_id=msg_id
        )
        await call.bot.edit_message_reply_markup(
            user_id,
            message_id=msg_id,
            reply_markup=s.genres_kb(genres_ids, int(offset))
        )


async def update_genres_info(callback_query: types.CallbackQuery):
    offset = callback_query.data.split("#")[-2]
    s.update_genres(callback_query.from_user.id, callback_query.data)
    await set_or_update_config(user_id=callback_query.from_user.id, offset=offset)
    await callback_query.answer()


async def save_config(call: CallbackQuery):
    genres_list = await s.get_genre_ids(call.from_user.id)
    if genres_list:
        db.insert_or_update_users(
            call.from_user.id,
            ",".join(genres_list)
        )
        await call.answer()
        await call.bot.send_message(
            call.from_user.id,
            msg.save,
            reply_markup=s.MAIN_KB
        )
    else:
        # не сохраняем если список пустой
        await call.answer(msg.cb_not_saved)


def choose_genres(dp: Dispatcher):
    dp.register_message_handler(get_config, lambda message: message.text == msg.fav_genres)
    dp.register_callback_query_handler(delete_config, lambda call: call.data == 'delete_config')
    dp.register_callback_query_handler(set_or_update_config, lambda call: call.data.startswith('edit_config'),
                                       state="*")
    dp.register_callback_query_handler(update_genres_info, lambda call: call.data[:6] in ['del_ge', 'add_ge'])
    dp.register_callback_query_handler(save_config, lambda call: call.data == 'save_config')
