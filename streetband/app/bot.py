import asyncio
import logging
import re
from io import BytesIO
from typing import List

from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher, filters, FSMContext
from aiogram.types import InputFile, Update, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from loguru import logger
import app.service as s
from app.callback_datas import location_callback, choice_callback, user_reg_callback, action_callback, groups_callback
from app.states import Registration_Musician, Registration_User, Choosing_Musician
from database import database as db
from app.calculate_distance import choose_shortest

from app.dialogs import msg
from config import TOKEN

storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)
dp.middleware.setup(LoggingMiddleware())
location_kb = InlineKeyboardMarkup()


@dp.message_handler(filters.CommandStart(deep_link=re.compile("mus_[1-9]{5}")))
async def start_qr(message: types.Message):
    # закидываем пользователя в дб по его user_id и добавляем user_name
    user_name = message.from_user.first_name
    language = message.from_user.language_code
    if not db.user_exists():
        user = db.add_user(message.from_user.id, user_name, language)
    get_musician = db.get_musician(message.text.split()[-1])
    photo = InputFile("app/acdc.jpg")
    await message.answer_photo(photo=photo, caption=msg.text_placeholder, reply_markup=s.DONATE_KB)
    await message.answer(reply_markup=s.MAIN_KB)


@dp.message_handler(filters.CommandStart())
async def start_normal(message: types.Message):
    user_name = message.from_user.first_name
    language = message.from_user.language_code
    user_id = message.from_user.id
    if not db.user_exists(user_id):
        user = db.add_user(user_id, user_name, language)
        await message.answer(msg.choice, reply_markup=s.CHOICE_KB)


@dp.callback_query_handler(user_reg_callback.filter(user="musician"))
async def register_musician(call: CallbackQuery, callback_data: dict):
    await call.answer()
    await call.message.answer(msg.policy, reply_markup=s.AGREEMENT_KB)
    await Registration_Musician.first()


@dp.callback_query_handler(choice_callback.filter(decision="agree"), state=Registration_Musician.Agreeing_terms)
async def musician_agreed_policy(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer()
    await call.message.answer(msg.name)
    await Registration_Musician.next()


@dp.callback_query_handler(choice_callback.filter(decision="agree"), state=Registration_User.Agreeing_terms)
async def user_agreed_policy(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer()
    await call.message.answer(msg.reg_complete, reply_markup=s.MAIN_KB)
    await state.reset_state()


@dp.callback_query_handler(action_callback.filter(action="back"), state='*')
async def back(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer()
    await call.message.answer("Введите данные повторно")
    await Registration_Musician.previous()


@dp.callback_query_handler(action_callback.filter(action="exit"), state='*')
async def exit_reg(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer(text=msg.exit,
                              reply_markup=s.CHOICE_KB)
    await state.reset_state()


@dp.message_handler(state=Registration_Musician.Group_name)
async def get_name(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(group_name=name)
    await message.answer(msg.requisites, reply_markup=s.BACK_OR_CANCEL_KB)

    await Registration_Musician.next()


@dp.message_handler(state=Registration_Musician.Requisites)
async def get_name(message: types.Message, state: FSMContext):
    requisites = message.text
    print(requisites)
    await state.update_data(group_requisites=requisites)
    await message.answer(msg.picture, reply_markup=s.BACK_OR_CANCEL_KB)

    await Registration_Musician.next()


@dp.message_handler(state=Registration_Musician.Group_pic,
                    content_types=types.ContentTypes.PHOTO | types.ContentTypes.DOCUMENT)
async def get_pic(message: types.Message, state: FSMContext):
    if message.document:
        pic_io = BytesIO()
        await message.document.download(destination=pic_io)
        await state.update_data(group_pic=InputFile(pic_io))
    else:
        pic = message.photo[-1].file_id
        await state.update_data(group_pic=pic)
    await message.answer(msg.description, reply_markup=s.BACK_OR_CANCEL_KB)

    await Registration_Musician.next()


@dp.message_handler(state=Registration_Musician.Group_desc)
async def get_desc(message: types.Message, state: FSMContext):
    description = message.text
    current_info = await state.get_data()
    await state.update_data(group_description=description)
    name = current_info.get('group_name')
    requisites = current_info.get('group_requisites')
    data = "Название группы: {}\nРеквизиты: {}\nОписание: {}".format(name, requisites, description)
    reg_data = await message.answer_photo(photo=current_info.get('group_pic'), caption=data,
                                          reply_markup=s.BACK_OR_APPROVE_KB)
    await state.update_data(group_pic=reg_data.photo[-1].file_id)
    await Registration_Musician.next()


@dp.callback_query_handler(action_callback.filter(action="approve"), state=Registration_Musician.Waiting_first_approve)
async def register_musician(call: CallbackQuery, callback_data: dict, state: FSMContext):
    current_info = await state.get_data()
    name = current_info.get('group_name')
    photo = current_info.get('group_pic')
    requisites = current_info.get('requisites')
    description = current_info.get('group_description')
    await call.answer()
    creator_username = call.from_user.username
    userid = call.from_user.id
    await call.message.answer(
        "Спасибо {}! Мы получили вашу заявку. В ближайшее время мы пришлём ответ и договор".format(
            call.from_user.first_name))
    await bot.send_photo(chat_id=-1001374281612, photo=photo,
                         caption="Название группы: {}\nРеквизиты: {}\nОписание: {}\nUsername: {}\nUser_id: {}".format(
                             name,
                             requisites,
                             description,
                             creator_username,
                             userid),
                         reply_markup=s.create_approvement_kb(message=call.from_user.id))


@dp.callback_query_handler(action_callback.filter(action="approve_data"),
                           state="*")
async def send_approved_data(call: CallbackQuery, callback_data: dict):
    await call.answer()
    await bot.send_document(chat_id=callback_data["id"], document=InputFile("app/kxm.docx"),
                            caption="Спасибо за ожидание! Менеджер подтвердил регистрацию вашей группы. Заполните договор и отпрвьте его в этот чат.")
    state = dp.current_state(chat=callback_data["id"], user=callback_data["id"])
    await state.set_state(Registration_Musician.Uploading_agreement)
    await call.message.delete()


@dp.callback_query_handler(action_callback.filter(action="declined_data"),
                           state="*")
async def send_declined_data(call: CallbackQuery, callback_data: dict):
    await call.answer()
    await bot.send_message(chat_id=callback_data["id"],
                           text="Спасибо за ожидание! Менеджер отклонил регистрацию вашей группы.В скором времени он свяжется с вами и расскажет какие правки нужно внести. Данные придётся ввести повторно")
    state = dp.current_state(chat=callback_data["id"], user=callback_data["id"])
    await state.reset_state()
    await call.message.delete()


@dp.message_handler(state=Registration_Musician.Uploading_agreement,
                    content_types=types.ContentTypes.DOCUMENT)
async def get_agreement(message: types.Message, state: FSMContext):
    agreement_doc = message.document.file_id
    await message.answer(msg.riba)

    await bot.send_document(chat_id=-1001374281612, document=agreement_doc,
                            reply_markup=s.create_final_approvement_kb(message=message.from_user.id))
    await Registration_Musician.next()


@dp.callback_query_handler(action_callback.filter(action="approve_final_data"),
                           state="*")
async def send_approved_data(call: CallbackQuery, callback_data: dict):
    await call.answer()
    await call.message.delete()
    await bot.send_message(chat_id=callback_data["id"],
                           text="Спасибо за ожидание! Ваша группа добавлена в нашу базу ! Теперь вы можете управлять всем из своего личного кабинета",
                           reply_markup=s.MUSICIAN_LC_KB)


@dp.callback_query_handler(user_reg_callback.filter(user="user"))
async def register_musician(call: CallbackQuery, callback_data: dict):
    await call.answer()
    await call.message.answer(msg.policy, reply_markup=s.AGREEMENT_KB)
    await Registration_User.first()

    # @dp.message_handler(Command("show_musicians"))


# choosen_musician = ""

@dp.message_handler(filters.Text(contains="Музыканты рядом"))
async def show_musiacians(message: types.Message):
    await message.answer(text=msg.send_location, reply_markup=types.ReplyKeyboardRemove())
    await Choosing_Musician.first()


@dp.message_handler(state=Choosing_Musician.Choosing_musician, content_types=types.ContentTypes.LOCATION)
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


@dp.callback_query_handler(location_callback.filter(), state=Choosing_Musician.Choosing_musician)
async def get_group(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer()
    print(call)
    logger.info(f"callback_data = {call.data}")
    logger.info(f"callback_data dict = {callback_data}")
    # artist_id = callback_data.get("artist_id")
    print(callback_data)
    await call.message.answer_venue(latitude=55.757784, longitude=37.633295, title="Александр Машин",
                                    address="жанр: джаз",
                                    foursquare_type="food",
                                    reply_markup=s.GROUP_CAPTIONS_KB)
    # answer_photo(photo=InputFile("app/animals.jpg"),
    #              caption=f"Вы выбрали группу {callback_data['name']}. Расстояние до неё {callback_data['distance']}км",
    #              reply_markup=s.GROUP_CAPTIONS_KB)
    await state.reset_state()


# @dp.message_handler(content_types=types.ContentTypes.LOCATION, state=Choosing_Musician.Choosing_musician)
# async def what(message: types.Message, state: FSMContext):
#     await message.answer_venue(latitude=55.757784, longitude=37.633295, title="Александр Машин", address="жанр: джаз",
#                                foursquare_type="food",
#                                reply_markup=s.GROUP_CAPTIONS_KB)


@dp.callback_query_handler(groups_callback.filter(location="group_locations"))
async def show_groups(call: CallbackQuery):
    print(location_kb)
    await call.message.answer(text="Ближайшие группы", reply_markup=location_kb)
    await Choosing_Musician.first()
# ! Для обновления групп рядом, раскомментить потом
# @dp.edited_message_handler(content_types=types.ContentTypes.LOCATION)
# async def what(message: types.Message):
#     await asyncio.sleep()
#     print(message)
#     location = message.location
#     latitude = location.latitude
#     longitude = location.longitude
#     await message.answer(f"Ваша текущая геолокация\n"
#                          f"Latitude = {latitude}\n"
#                          f"Longitude = {longitude}\n\n"
#                          )

# @dp.callback_query_handler(location_callback.filter(location="location_0"))
# async def show_artist(call: CallbackQuery, callback_data: dict):
#     await call.answer()
#     logger.info(f"callback_data = {call.data}")
#     logger.info(f"callback_data dict = {callback_data}")
#     artist_id = callback_data.get("artist_id")
#
#     await call.message.answer_photo(photo=InputFile("app/animals.jpg"),
#                                     caption="Вы выбрали группу The Animals. Расстояние до неё 2км",
#                                     reply_markup=s.GROUP_CATIONS_KB)

@dp.message_handler(filters.Text(contains="Профиль"))
async def open_profile(message: types.Message):
    await message.answer(text="Вы открыли ваш личный кабинет", reply_markup=s.MAIN_KB)


async def on_shutdown(dp):
    logger.warning('Shutting down..')
    # закрытие соединения с БД
    pass
    logger.warning("DB Connection closed")
