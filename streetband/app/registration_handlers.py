from io import BytesIO

from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InputFile

from streetband.database import database as db
from streetband.app import service as s
from streetband.app.callback_datas import user_reg_callback, choice_callback, action_callback
from streetband.app.dialogs import msg
from streetband.app.states import Registration_Musician, Registration_User


async def register_musician(call: CallbackQuery):
    await call.answer()
    await call.message.answer(msg.policy, reply_markup=s.AGREEMENT_KB)
    await Registration_Musician.first()


async def musician_agreed_policy(call: CallbackQuery):
    await call.answer()
    await call.message.answer(msg.name)
    await Registration_Musician.next()


async def user_agreed_policy(call: CallbackQuery, state: FSMContext):
    if not db.user_exists(call.from_user.id):
        user = db.add_user(call.from_user.id, call.from_user.username, call.from_user.language_code)
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
    await Registration_Musician.previous()


async def get_name(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(group_name=name)
    await message.answer(msg.requisites, reply_markup=s.BACK_OR_CANCEL_KB)

    await Registration_Musician.next()


async def get_requisites(message: types.Message, state: FSMContext):
    requisites = message.text
    await state.update_data(group_requisites=requisites)
    await message.answer(msg.picture, reply_markup=s.BACK_OR_CANCEL_KB)

    await Registration_Musician.next()


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


async def get_desc(message: types.Message, state: FSMContext):
    description = message.text
    current_info = await state.get_data()
    await state.update_data(group_description=description)
    await state.update_data(group_leader=message.from_user.url)
    name = current_info.get('group_name')
    requisites = current_info.get('group_requisites')
    data = "Название группы: {}\nРеквизиты: {}\nОписание: {}".format(name, requisites, description)
    reg_data = await message.answer_photo(photo=current_info.get('group_pic'), caption=data,
                                          reply_markup=s.BACK_OR_APPROVE_KB)
    await state.update_data(group_pic=reg_data.photo[-1].file_id)
    await Registration_Musician.next()


async def register_musician_info(call: CallbackQuery, state: FSMContext):
    current_info = await state.get_data()
    name = current_info.get('group_name')
    photo = current_info.get('group_pic')
    requisites = current_info.get('group_requisites')
    description = current_info.get('group_description')
    await call.answer()
    creator_username = current_info.get('group_leader')
    userid = call.from_user.id
    await call.message.answer(
        "Спасибо {}! Мы получили вашу заявку. В ближайшее время мы пришлём ответ и договор".format(
            call.from_user.first_name))
    await call.bot.send_photo(chat_id=-1001374281612, photo=photo,
                              caption="Название группы: {}\nРеквизиты: {}\nОписание: {}\nUsername: {}\nUser_id: {}".format(
                                  name,
                                  requisites,
                                  description,
                                  creator_username,
                                  userid),
                              reply_markup=s.create_approvement_kb(message=call.from_user.id))


async def send_approved_data(call: CallbackQuery, callback_data: dict):
    await call.answer()
    await call.bot.send_document(chat_id=callback_data["id"], document=InputFile("bot/kxm.docx"),
                                 caption="Спасибо за ожидание! Менеджер подтвердил регистрацию вашей группы. Заполните "
                                         "договор и отпрвьте его в этот чат.")
    state = Dispatcher.current_state(chat=callback_data["id"], user=callback_data["id"])
    await state.set_state(Registration_Musician.Uploading_agreement)
    await call.message.delete()


async def send_declined_data(call: CallbackQuery, callback_data: dict):
    await call.answer()
    await call.bot.send_message(chat_id=callback_data["id"],
                                text="Спасибо за ожидание! Менеджер отклонил регистрацию вашей группы.В скором времени он "
                                     "свяжется с вами и расскажет какие правки нужно внести. Данные придётся ввести "
                                     "повторно")
    state = Dispatcher.current_state(chat=callback_data["id"], user=callback_data["id"])
    await state.reset_state()
    await call.message.delete()


async def get_agreement(message: types.Message, state: FSMContext):
    agreement_doc = message.document.file_id
    current_info = await state.get_data()
    await message.answer(msg.riba)
    await message.bot.send_document(chat_id=-1001374281612, document=agreement_doc,
                                    reply_markup=s.create_final_approvement_kb(message=message.from_user.id))
    await Registration_Musician.next()


async def send_approved_data_fin(call: CallbackQuery, callback_data: dict):
    await call.answer()
    await call.message.delete()
    await call.bot.send_message(chat_id=callback_data["id"],
                                text="Спасибо за ожидание! Ваша группа добавлена в нашу базу ! Теперь вы можете управлять "
                                     "всем из своего личного кабинета",
                                reply_markup=s.MEM_KB)


async def register_musician_final(call: CallbackQuery, state: FSMContext):
    current_info = await state.get_data()
    # нужно переписать под музыканта
    # сейчас вот это лежит в current_info
    # {'group_name': 'Кек',
    # 'group_requisites': '4276 6600 3705 5514',
    # 'group_pic': 'AgACAgIAAxkDAAIF5mH1MMAf1G9P_mwRyk5avg34Kmq5AAIutzEbibypSx8OsdsjZRVeAQADAgADeQADIwQ',
    # 'group_description': 'Мом',
    # 'group_leader': 'tg://user?id=602172928'}
    if not db.user_exists(call.from_user.id):
        user = db.add_user(call.from_user.id, call.from_user.username, call.from_user.language_code)
    await call.answer()
    await Bot.send_message(chat_id=call.from_user.id,
                           text="Ниже ваш личный кабинет",
                           reply_markup=s.MUSICIAN_LC_KB)


async def register_user(call: CallbackQuery):
    await call.answer()
    await call.message.answer(msg.policy, reply_markup=s.AGREEMENT_KB)
    await Registration_User.first()


def register_users(dp: Dispatcher):
    dp.register_callback_query_handler(register_musician, user_reg_callback.filter(user="musician"))
    dp.register_callback_query_handler(musician_agreed_policy, choice_callback.filter(decision="agree"),
                                       state=Registration_Musician.Agreeing_terms)
    dp.register_callback_query_handler(user_agreed_policy, choice_callback.filter(decision="agree"),
                                       state=Registration_User.Agreeing_terms)
    dp.register_callback_query_handler(exit_reg, action_callback.filter(action="exit"), state='*')
    dp.register_callback_query_handler(back, action_callback.filter(action="back"), state='*')
    dp.register_message_handler(get_name, state=Registration_Musician.Group_name)
    dp.register_message_handler(get_requisites, state=Registration_Musician.Requisites)
    dp.register_message_handler(get_pic, state=Registration_Musician.Group_pic,
                                content_types=types.ContentTypes.PHOTO | types.ContentTypes.DOCUMENT)
    dp.register_message_handler(get_desc, state=Registration_Musician.Group_desc)
    dp.register_callback_query_handler(register_musician_info, action_callback.filter(action="approve"),
                                       state=Registration_Musician.Waiting_first_approve)
    dp.register_callback_query_handler(send_approved_data, action_callback.filter(action="approve_data"),
                                       state="*")
    dp.register_callback_query_handler(send_declined_data, action_callback.filter(action="decline_data"),
                                       state="*")
    dp.register_message_handler(get_agreement, state=Registration_Musician.Uploading_agreement,
                                content_types=types.ContentTypes.DOCUMENT)
    dp.register_callback_query_handler(send_approved_data_fin, action_callback.filter(action="approve_final_data"),
                                       state="*")
    dp.register_callback_query_handler(register_musician_final, lambda call: call.data and call.data == 'finish',
                                       state=Registration_Musician.Waiting_final_approve)
    dp.register_callback_query_handler(register_user, user_reg_callback.filter(user="user"))

