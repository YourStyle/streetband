from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from gadgets import service as s
from gadgets.callback_datas import review_callback
from gadgets.states import Feedback
from database import database as db


async def feedback(message: types.Message, state: FSMContext):
    await message.answer("Поделитесь своми впечатлениям после работы с ботом. Если вы заметили какие-то баги ("
                         "странное поведение) или у вас есть идея, как можно улучшить бота, напишите в ответ на это "
                         "сообщение. Если вам всё понравилось можете отправить любой смайлик")
    await state.set_state(Feedback.Reviewing)


async def review(message: types.Message):
    db.add_feedback_text(str(message.from_user.id), comment=message.text)
    await message.answer("Спасибо за отзыв. Оцените бота пожалуйста, нажав на звёздочки с цифирками от 1 до 5",
                         reply_markup=s.review_kb())


async def thanks(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer()
    db.add_feedback_rate(str(call.from_user.id), rate=callback_data['score'])
    await call.message.answer("Мы получили ваш отзыв! Спасибо 👍")
    print(callback_data)
    await state.reset_state(with_data=True)


def send_feedback(dp: Dispatcher):
    dp.register_message_handler(feedback, commands=['feedback'])
    dp.register_message_handler(review, state=Feedback.Reviewing)
    dp.register_callback_query_handler(thanks, review_callback.filter(), state=Feedback.Reviewing)
