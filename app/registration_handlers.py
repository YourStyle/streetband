from io import BytesIO

from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InputFile

from database import database as db
from app import service as s
from app.callback_datas import user_reg_callback, choice_callback, action_callback
from app.dialogs import msg
from app.states import RegistrationMusician, RegistrationUser


async def register_musician(call: CallbackQuery):
    await call.answer()
    await call.message.answer(msg.policy, reply_markup=s.AGREEMENT_KB)
    await RegistrationMusician.first()


async def musician_agreed_policy(call: CallbackQuery):
    await call.answer()
    await call.message.answer(msg.name)
    await RegistrationMusician.next()


async def user_agreed_policy(call: CallbackQuery, state: FSMContext):
    if not db.user_exists(str(call.from_user.id)):
        db.add_user(str(call.from_user.id), call.from_user.username, call.from_user.language_code)
    await call.answer()
    await call.message.answer(msg.reg_complete, reply_markup=s.MAIN_KB)
    await state.reset_state()


async def exit_reg(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer(text=msg.exit,
                              reply_markup=s.CHOICE_KB)
    await state.reset_state()


async def back(call: CallbackQuery):
    await call.answer()
    await call.message.answer("Введите данные повторно")
    await RegistrationMusician.previous()


async def get_name(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(group_name=name)
    await message.answer(msg.requisites, reply_markup=s.BACK_OR_CANCEL_KB)
    await RegistrationMusician.next()


async def get_requisites(message: types.Message, state: FSMContext):
    requisites = message.text
    await state.update_data(group_requisites=requisites)
    await message.answer(msg.picture, reply_markup=s.BACK_OR_CANCEL_KB)
    await RegistrationMusician.next()


async def get_pic(message: types.Message, state: FSMContext):
    if message.document:
        pic_io = BytesIO()
        await message.document.download(destination=pic_io)
        await state.update_data(group_pic=InputFile(pic_io))
    else:
        pic = message.photo[-1].file_id
        await state.update_data(group_pic=pic)
    await message.answer(msg.genres, reply_markup=s.BACK_OR_CANCEL_KB)
    await RegistrationMusician.next()


async def get_genres(message: types.Message, state: FSMContext):
    genres = message.text.lower()
    await state.update_data(group_genres=genres)
    await message.answer(msg.description, reply_markup=s.BACK_OR_CANCEL_KB)
    await RegistrationMusician.next()


async def get_desc(message: types.Message, state: FSMContext):
    description = message.text
    current_info = await state.get_data()
    await state.update_data(group_description=description)
    if message.from_user.username is None:
        leader = message.from_user.first_name
    else:
        leader = message.from_user.username
    await state.update_data(group_leader=leader)
    name = current_info.get('group_name')
    requisites = current_info.get('group_requisites')
    genres = current_info.get('group_genres')
    data = "Название группы: {}\nРеквизиты: {}\nЖанры: {}\nОписание: {}".format(name, requisites, genres,
                                                                                description)
    reg_data = await message.answer_photo(photo=current_info.get('group_pic'), caption=data,
                                          reply_markup=s.BACK_OR_APPROVE_KB)
    await state.update_data(group_pic=reg_data.photo[-1].file_id)
    await RegistrationMusician.next()


async def register_musician_info(call: CallbackQuery, state: FSMContext):
    current_info = await state.get_data()
    name = current_info.get('group_name')
    photo = current_info.get('group_pic')
    requisites = current_info.get('group_requisites')
    genres = current_info.get('group_genres')
    description = current_info.get('group_description')
    await call.answer()
    creator_username = current_info.get('group_leader')
    userid = call.from_user.id
    await call.message.answer(
        "Спасибо {}! Мы получили вашу заявку. В ближайшее время мы пришлём ответ и договор".format(
            call.from_user.first_name))
    await call.bot.send_photo(chat_id=-1001374281612, photo=photo,
                              caption="Название группы: {}\nРеквизиты: {}\nЖанры: {}\nОписание: {}\nUsername: {}\nUser_id: {}".format(
                                  name,
                                  requisites,
                                  genres,
                                  description,
                                  creator_username,
                                  userid),
                              reply_markup=s.create_approvement_kb(message=call.from_user.id))


async def send_approved_data(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer()
    await call.bot.send_document(chat_id=callback_data["id"], document=InputFile("app/kxm.docx"),
                                 caption="Спасибо за ожидание! Менеджер подтвердил регистрацию вашей группы. Заполните "
                                         "договор и отпрвьте его в этот чат.")
    await state.storage.set_state(chat=callback_data["id"], user=callback_data["id"],
                                  state=RegistrationMusician.Uploading_agreement)
    await call.message.delete()


async def send_declined_data(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer()
    await call.bot.send_message(chat_id=callback_data["id"],
                                text="Спасибо за ожидание! Менеджер отклонил регистрацию вашей группы.В скором времени он "
                                     "свяжется с вами и расскажет какие правки нужно внести. Данные придётся ввести "
                                     "повторно")
    # state.(Dispatcher, chat=callback_data["id"], user=callback_data["id"])
    await state.storage.reset_state(chat=callback_data["id"], user=callback_data["id"])
    await call.message.delete()


async def get_agreement(message: types.Message, state: FSMContext):
    agreement_doc = message.document.file_id
    current_info = await state.get_data()
    await message.answer(msg.riba)
    await message.bot.send_document(chat_id=-1001374281612, document=agreement_doc,
                                    reply_markup=s.create_final_approvement_kb(message=message.from_user.id))
    await RegistrationMusician.next()


async def send_approved_data_fin(call: CallbackQuery, callback_data: dict):
    await call.answer()
    await call.message.delete()
    await call.bot.send_message(chat_id=callback_data["id"],
                                text="Спасибо за ожидание! Ваша группа добавлена в нашу базу ! Теперь вы можете управлять "
                                     "всем из своего личного кабинета. Нажмите на кнопку ниже, чтобы открыть личный кабинет",
                                reply_markup=s.MEM_KB)


async def register_musician_final(call: CallbackQuery, state: FSMContext):
    current_info = await state.get_data()
    muser_id = str(call.from_user.id)
    db.add_musician(muser_id)
    db.set_m_name(muser_id, str(current_info['group_name']))
    db.set_group_pic(muser_id, str(current_info['group_pic']))
    db.set_group_description(muser_id, str(current_info['group_description']))
    db.set_group_leader(muser_id, str(current_info['group_leader']))
    db.set_group_genre(muser_id, current_info['group_genres'].capitalize().split(','))
    db.set_group_current_location(muser_id, None)
    db.free_subscription(muser_id)
    db.get_musicians()
    await call.answer()
    await call.bot.send_message(chat_id=call.from_user.id,
                                text="Ниже ваш личный кабинет",
                                reply_markup=s.MUSICIAN_LC_KB)
    await state.reset_state(with_data=True)
    print(await state.get_state())


async def register_user(call: CallbackQuery):
    await call.answer()
    await call.message.answer(msg.policy, reply_markup=s.AGREEMENT_KB)
    await RegistrationUser.first()


def register_users(dp: Dispatcher):
    dp.register_callback_query_handler(register_musician, user_reg_callback.filter(user="musician"))
    dp.register_callback_query_handler(musician_agreed_policy, choice_callback.filter(decision="agree"),
                                       state=RegistrationMusician.Agreeing_terms)
    dp.register_callback_query_handler(user_agreed_policy, choice_callback.filter(decision="agree"),
                                       state=RegistrationUser.Agreeing_terms)
    dp.register_callback_query_handler(exit_reg, action_callback.filter(action="exit"), state='*')
    dp.register_callback_query_handler(back, action_callback.filter(action="back"), state='*')

    dp.register_message_handler(get_name, state=RegistrationMusician.Group_name)
    dp.register_message_handler(get_requisites, state=RegistrationMusician.Requisites)
    dp.register_message_handler(get_pic, state=RegistrationMusician.Group_pic,
                                content_types=types.ContentTypes.PHOTO | types.ContentTypes.DOCUMENT)
    dp.register_message_handler(get_genres, state=RegistrationMusician.Group_genres)
    dp.register_message_handler(get_desc, state=RegistrationMusician.Group_desc)

    dp.register_callback_query_handler(register_musician_info, action_callback.filter(action="approve"),
                                       state=RegistrationMusician.Waiting_first_approve)
    dp.register_callback_query_handler(send_approved_data, action_callback.filter(action="approve_data"),
                                       state="*")
    dp.register_callback_query_handler(send_declined_data, action_callback.filter(action="decline_data"),
                                       state="*")
    dp.register_message_handler(get_agreement, state=RegistrationMusician.Uploading_agreement,
                                content_types=types.ContentTypes.DOCUMENT)
    dp.register_callback_query_handler(send_approved_data_fin, action_callback.filter(action="approve_final_data"),
                                       state="*")
    dp.register_callback_query_handler(register_musician_final, lambda call: call.data and call.data == 'finish',
                                       state=RegistrationMusician.Waiting_final_approve)
    dp.register_callback_query_handler(register_user, user_reg_callback.filter(user="user"))
