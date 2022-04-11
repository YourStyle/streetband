import asyncio
from aiogram import Dispatcher, types
from aiogram.dispatcher import filters, FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from io import BytesIO
from gadgets import service as s
from gadgets.callback_datas import info_callback, add_callback, fav_callback, delete_callback
from gadgets.dialogs import msg
from gadgets.service import create_group_action_kb
from gadgets.states import EditingProfile

from database import database as db, cache


async def open_profile(message: types.Message):
    await message.answer(text="Вы открыли ваш личный кабинет", reply_markup=s.MAIN_KB)


async def group_info(call: CallbackQuery, callback_data: dict):
    await call.answer()
    groups = cache.jget("musicians")
    group = groups[int(callback_data["db_number"])]
    group_id = group["musician_id"]
    group_name = group["musician_name"]
    group_picture = group["group_pic"]
    genres = await s.get_genres_names(group["group_genre"], False)
    group_description = group["group_description"]
    group_leader = group["group_leader"]
    caption = f"Название: {group_name} \nЛидер группы: {group_leader}\nЖанр: {genres}\nОписание :{group_description}"

    '''проверка на нахождение исполнителя в избранном'''
    fav_groups = db.get_user(str(call.from_user.id))["fav_groups"]
    if cache.jget("musicians") is None:
        db.get_musicians()
    groups = cache.jget("musicians")
    print(fav_groups)
    flag = False
    if fav_groups:
        for group in fav_groups:
            for info in groups:
                if info["musician_id"] == group:
                    flag = True
    await call.message.answer_photo(group_picture, caption,
                                    reply_markup=create_group_action_kb(group_id, callback_data["db_number"], fav=flag))


async def add_to_favourite(call: CallbackQuery, callback_data: dict):
    await call.answer()
    db.to_fav(str(call.from_user.id), callback_data["id"])
    if callback_data["id"] in db.get_user(str(call.from_user.id))["fav_groups"]:
        fav = True
    else:
        fav = False
    print(callback_data["db_number"])
    await call.message.edit_reply_markup(
        s.create_group_action_kb(callback_data["id"], callback_data["db_number"], fav=fav))
    temp = await call.message.answer(text="Исполнитель добавлен в избранное")
    await asyncio.sleep(2)
    await temp.delete()


async def donate(call: CallbackQuery):
    await call.answer()
    await call.message.answer(text="Спасибо, мы получили ваш платёж")


async def set_mus_location(message: types.Message):
    print("?")
    db.set_group_current_location(str(message.from_user.id), dict(message.location))
    await message.answer(text="Местоположение установлено")


async def answer_qr(message: types.Message):
    bio = BytesIO()
    mus_id = str(message.from_user.id)
    bio.name = f'logo_{mus_id}.png'
    image = s.create_qr(mus_id)
    image.save(bio, 'PNG')
    bio.seek(0)
    await message.answer_photo(bio)
    bio = BytesIO()
    bio.name = f'logo_{mus_id}.png'
    image = s.create_qr(mus_id)
    image.save(bio, 'PNG')
    bio.seek(0)
    await message.answer_document(bio)


async def return_fav(message: types.Message):
    fav_kb = InlineKeyboardMarkup()
    fav_groups = db.get_user(str(message.from_user.id))["fav_groups"]
    if cache.jget("musicians") is None:
        db.get_musicians()
    groups = cache.jget("musicians")
    print(fav_groups)
    if fav_groups:
        for group in fav_groups:
            for info in groups:
                if info["musician_id"] == group:
                    fav_kb.row(InlineKeyboardButton(text=info["musician_name"],
                                                    callback_data=fav_callback.new(id=info["musician_id"])))
        fav_kb.row(InlineKeyboardButton(text="Назад", callback_data="back"))
        await message.answer(text="Ваши избранные исполнители", reply_markup=fav_kb)
    else:
        # fav_kb.row(InlineKeyboardButton(text="Назад", callback_data="back"))
        await message.answer(
            text="У вас ещё нет любимых исполнителей 😭 \nНажмите на кнопку Музыканты рядом, чтобы найти лучших музыкантов поблизости 😍")


async def back_form_fav(call: CallbackQuery):
    await call.answer()
    await call.message.answer("Меню", reply_markup=s.MAIN_KB)


async def fav_group_info(call: CallbackQuery, callback_data: dict):
    await call.answer()
    if cache.jget("musicians") is None:
        db.get_musicians()
    groups = cache.jget("musicians")
    for info in groups:
        if info["musician_id"] == callback_data["id"]:
            group = info
    group_id = group["musician_id"]
    group_name = group["musician_name"]
    group_picture = group["group_pic"]
    genres = await s.get_genres_names(group["group_genre"], False)
    group_description = group["group_description"]
    group_leader = group["group_leader"]
    caption = f"Название: {group_name} \nЛидер группы: {group_leader}\nЖанр: {genres}\nОписание :{group_description}"

    await call.message.answer_photo(group_picture, caption,
                                    reply_markup=create_group_action_kb(group_id, callback_data["id"], fav=True,
                                                                        location=False))


async def delete_from_fav(call: CallbackQuery, callback_data: dict):
    await call.answer()
    print(callback_data)
    await call.message.edit_reply_markup(create_group_action_kb(callback_data["id"], callback_data["id"], fav=False,
                                                                location=False))
    temp = await call.message.answer(text="Музыкант удалён из избранного")
    db.from_fav(str(call.from_user.id), callback_data["id"])
    await asyncio.sleep(2)
    await temp.delete()


async def return_fav_groups(call: CallbackQuery):
    await call.answer()
    fav_kb = InlineKeyboardMarkup()
    fav_groups = db.get_user(str(call.from_user.id))["fav_groups"]
    if cache.jget("musicians") is None:
        db.get_musicians()
    groups = cache.jget("musicians")
    for group in fav_groups:
        for info in groups:
            if info["musician_id"] == group:
                fav_kb.row(InlineKeyboardButton(text=info["musician_name"],
                                                callback_data=fav_callback.new(id=info["musician_id"])))
    fav_kb.row(InlineKeyboardButton(text="Назад", callback_data="back_to_menu"))
    await call.message.answer(text="Ваши избранные исполнители", reply_markup=fav_kb)


async def edit_group(message: types.Message):
    await message.answer(text="Информация о группе", reply_markup=s.EDIT_PROFILE_KB)
    buffer = db.get_musician(str(message.from_user.id))
    subbuffer = {k: buffer[k] for k in
                 ('musician_id', 'musician_name', 'group_pic', 'group_genre', 'group_description', 'group_leader',
                  'current_location')}
    cache.jset(f"musician_{str(message.from_user.id)}", subbuffer)


async def set_edit_name(call: CallbackQuery, state: FSMContext):
    await state.reset_state()
    await call.answer()
    name = cache.jget(f"musician_{str(call.from_user.id)}")["musician_name"]
    current_name = "Текущее название: " + name + "\n"
    await call.message.answer((current_name + msg.edit_name))
    await state.set_state(EditingProfile.EditingName)


async def set_edit_pic(call: CallbackQuery, state: FSMContext):
    await state.reset_state()
    await call.answer()
    photo = cache.jget(f"musician_{str(call.from_user.id)}")["group_pic"]
    current_name = "Текущее фото: \n"
    await call.message.answer_photo(photo=photo, caption=current_name + msg.edit_pic)
    await state.set_state(EditingProfile.EditingPic)


async def set_edit_desc(call: CallbackQuery, state: FSMContext):
    await state.reset_state()
    await call.answer()
    desc = cache.jget(f"musician_{str(call.from_user.id)}")["group_description"]
    current_desc = "Текущее описание: " + desc + "\n"
    await call.message.answer(current_desc + msg.edit_desc)
    await state.set_state(EditingProfile.EditingDesc)


async def set_edit_leader(call: CallbackQuery, state: FSMContext):
    await state.reset_state()
    await call.answer()
    leader = cache.jget(f"musician_{str(call.from_user.id)}")["group_leader"]
    if call.from_user.username is None:
        current_leader = "Текущий лидер: " + leader + "\n"
    else:
        current_leader = "Текущий лидер: @" + leader + "\n"
    await call.message.answer(current_leader + msg.edit_leader)
    await state.set_state(EditingProfile.EditingLeader)


# async def set_edit_genres(call: CallbackQuery, state: FSMContext):
#     await call.answer()
#     genres_id = cache.jget(f"musician_{str(call.from_user.id)}")["group_genre"]
#     genres = await s.get_genres_names(genres_id)
#     current_genres = "Текущий жанры:\n" + genres + "\n"
#     await call.message.answer(current_genres + msg.genres)
#     await state.set_state(EditingProfile.EditingGenres)


async def edit_name(message: types.Message, state: FSMContext):
    '''Запись в бд'''
    db.set_m_name(str(message.from_user.id), message.text)

    '''Запись в кэш'''
    info = cache.jget(f"musician_{str(message.from_user.id)}")
    info["musician_name"] = message.text
    cache.jset(f"musician_{str(message.from_user.id)}", info)

    await state.reset_state()
    await message.answer(msg.done)


async def edit_pic(message: types.Message, state: FSMContext):
    if message.document:

        '''Запись в бд'''
        pic_io = BytesIO()
        await message.document.download(destination=pic_io)
        db.set_group_pic(str(message.from_user.id), InputFile(pic_io))

        '''Запись в кэш'''
        info = cache.jget(f"musician_{str(message.from_user.id)}")
        info["group_pic"] = InputFile(pic_io)
        cache.jset(f"musician_{str(message.from_user.id)}", info)

    else:
        '''Запись в бд'''
        pic = message.photo[-1].file_id
        db.set_group_pic(str(message.from_user.id), pic)

        '''Запись в кэш'''
        info = cache.jget(f"musician_{str(message.from_user.id)}")
        info["group_pic"] = pic
        cache.jset(f"musician_{str(message.from_user.id)}", info)

    await state.reset_state()
    await message.answer(msg.done)


async def edit_desc(message: types.Message, state: FSMContext):
    '''Запись в бд'''
    db.set_group_description(str(message.from_user.id), message.text)

    '''Запись в кэш'''
    info = cache.jget(f"musician_{str(message.from_user.id)}")
    info["group_description"] = message.text
    cache.jset(f"musician_{str(message.from_user.id)}", info)

    await state.reset_state()

    await message.answer(msg.done)


async def edit_leader(message: types.Message, state: FSMContext):
    '''Запись в бд'''
    db.set_group_leader(str(message.from_user.id), message.text)

    '''Запись в кэш'''
    info = cache.jget(f"musician_{str(message.from_user.id)}")
    info["group_leader"] = message.text
    cache.jset(f"musician_{str(message.from_user.id)}", info)
    await state.reset_state()
    await message.answer(msg.done)




async def songs(message: types.Message):
    '''Реализовать после запуска'''
    await message.answer("⚠️Этот раздел находится в разработке ⚠️")



async def whaat(message: types.Message):
    await message.answer("Лох")


async def whaat_mus(message: types.Message):
    await message.answer("Музыкант")


def use_buttons(dp: Dispatcher):
    dp.register_message_handler(answer_qr, filters.Text(contains=msg.qr),state="*")
    dp.register_message_handler(set_mus_location, is_musician=True, content_types=types.ContentTypes.LOCATION,
                                state="*")
    dp.register_message_handler(return_fav, filters.Text(contains="Избранное"), state="*")
    dp.register_message_handler(edit_group, filters.Text(contains="Профиль"), state="*")
    dp.register_message_handler(songs, filters.Text(contains="Песни"), state="*")
    dp.register_callback_query_handler(group_info, info_callback.filter(), state="*")
    '''Раздел с избранным'''
    dp.register_callback_query_handler(add_to_favourite, add_callback.filter(), state="*")
    dp.register_callback_query_handler(delete_from_fav, delete_callback.filter(), state="*")

    dp.register_callback_query_handler(back_form_fav, lambda call: call.data and call.data == 'back_to_menu', state="*")
    dp.register_callback_query_handler(return_fav_groups, lambda call: call.data and call.data == 'back_to_fav',
                                       state="*")

    '''Редактор профиля группы'''
    dp.register_callback_query_handler(set_edit_name, lambda call: call.data and call.data == 'edit_name', state="*")
    dp.register_callback_query_handler(set_edit_desc, lambda call: call.data and call.data == 'edit_description',
                                       state="*")
    dp.register_callback_query_handler(set_edit_pic, lambda call: call.data and call.data == 'edit_picture', state="*")
    dp.register_callback_query_handler(set_edit_leader, lambda call: call.data and call.data == 'edit_leader',
                                       state="*")
    # dp.register_callback_query_handler(set_edit_genres, lambda call: call.data and call.data == 'edit_genres',
    #                                    state="*")

    dp.register_message_handler(edit_name, state=EditingProfile.EditingName)
    dp.register_message_handler(edit_desc, state=EditingProfile.EditingDesc)
    dp.register_message_handler(edit_pic, state=EditingProfile.EditingPic,
                                content_types=types.ContentTypes.PHOTO | types.ContentTypes.DOCUMENT)
    dp.register_message_handler(edit_leader, state=EditingProfile.EditingLeader)
    # dp.register_message_handler(edit_genres, state=EditingProfile.EditingGenres)

    dp.register_callback_query_handler(fav_group_info, fav_callback.filter(), state="*")

    '''Тестовый хендлер'''
    # dp.register_message_handler(whaat_mus, is_musician=True, content_types=types.ContentTypes.LOCATION, state="*")
    # dp.register_message_handler(whaat, content_types=types.ContentTypes.LOCATION, state="*")

