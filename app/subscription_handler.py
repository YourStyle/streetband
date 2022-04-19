from aiogram import Dispatcher, types
from aiogram.dispatcher import filters, FSMContext
from aiogram.types import CallbackQuery, LabeledPrice, ContentTypes

from app.paymnet_handler import Item
from app.states import Subscribing
from database import database as db
from app import service as s


async def subscription(message: types.Message, state: FSMContext):
    subscribed = db.get_subscription(str(message.from_user.id))
    free = db.get_free_subscription(str(message.from_user.id))
    sub_active = db.get_musician(str(message.from_user.id))["active_subscription"]

    if (subscribed or free) is not None and sub_active:
        if free:
            time = 90 - free.days
            if time <= 0:
                await message.answer(
                    f"Ваша пробная подписка закончилась! Сейчас пользователи не смогут найти вас на картах, "
                    f"отсканировать ваш QR-код"
                    f"и прослушать ваши песни",
                    reply_markup=s.SUBSC_KB)
                db.end_subscription(str(message.from_user.id))
                musician = Item(
                    title="Оплата подписки",
                    description=f"С вашей карты будет списано 100 рублей и подписка будет доступна в течение месяца с "
                                f"момента оплаты",
                    currency="RUB",
                    prices=[
                        LabeledPrice(
                            label="Подписка",
                            amount=100_00
                        )
                    ],
                    start_parameter="create_invoice_donate",
                    photo_url="https://i.ibb.co/5LwRm3P/logo.png",
                    photo_size=200,
                    is_flexible=False
                )
                await message.bot.send_invoice(chat_id=message.from_user.id,
                                               **musician.generate_invoice(),
                                               payload=f"{message.from_user.id}")
                await state.set_state(Subscribing.MusicianSubscribing)
            else:
                await message.answer(
                    f"Ваша пробная подписка действует ещё {time} дней. Через {time} дней мы автоматически спишем "
                    f"ежемесячную плату",
                    reply_markup=s.CAN_KB)
        else:
            time = 30 - subscribed.days
            if time <= 0:
                await message.answer(
                    f"Ваша подписка закончилась! Сейчас пользователи не смогут найти вас на картах, отсканировать ваш "
                    f"QR-код "
                    f"и прослушать ваши песни",
                    reply_markup=s.SUBSC_KB)
                db.end_subscription(str(message.from_user.id))
                musician = Item(
                    title="Оплата подписки",
                    description=f"С вашей карты будет списано 100 рублей и подписка будет доступна в течение месяца с "
                                f"момента оплаты",
                    currency="RUB",
                    prices=[
                        LabeledPrice(
                            label="Подписка",
                            amount=100_00
                        )
                    ],
                    start_parameter="create_invoice_donate",
                    photo_url="https://i.ibb.co/5LwRm3P/logo.png",
                    photo_size=200,
                    is_flexible=False
                )
                await message.bot.send_invoice(chat_id=message.from_user.id,
                                               **musician.generate_invoice(),
                                               payload=f"{message.from_user.id}")
                await state.set_state(Subscribing.MusicianSubscribing)
            else:
                await message.answer(
                    f"Ваша подписка действует ещё {time} дней. Через {time} дней мы автоматически спишем ежемесячную "
                    f"плату",
                    reply_markup=s.CAN_KB)
    elif sub_active is not None:
        await message.answer(
            f"Ваша подписка не активна",
            reply_markup=s.SUB_KB)
    else:
        await message.answer(
            f"Активировать пробную подписку",
            reply_markup=s.FREE_KB)


async def cancel_subscription(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer("Вы отменили подписку 😪")
    db.cancel_subscription(str(call.from_user.id))
    await call.message.answer(
        f"Ваша подписка не активна! Сейчас пользователи не смогут найти вас на картах, отсканировать ваш "
        f"QR-код "
        f"и прослушать ваши песни",
        reply_markup=s.SUBSC_KB)
    musician = Item(
        title="Оплата подписки",
        description=f"С вашей карты будет списано 100 рублей и подписка будет доступна в течение месяца с "
                    f"момента оплаты",
        currency="RUB",
        prices=[
            LabeledPrice(
                label="Подписка",
                amount=100_00
            )
        ],
        start_parameter="create_invoice_donate",
        photo_url="https://i.ibb.co/5LwRm3P/logo.png",
        photo_size=200,
        is_flexible=False
    )
    await call.bot.send_invoice(chat_id=call.from_user.id,
                                **musician.generate_invoice(),
                                payload=f"{call.from_user.id}")
    await state.set_state(Subscribing.MusicianSubscribing)


async def activate_free_subscription(call: CallbackQuery):
    await call.answer()
    await call.message.answer("Вы активировали пробную подписку 😎")
    db.free_subscription(str(call.from_user.id))


async def activate_subscription(call: CallbackQuery, state: FSMContext):
    await call.answer()
    musician = Item(
        title="Оплата подписки",
        description=f"С вашей карты будет списано 100 рублей и подписка будет доступна в течение месяца с момента оплаты",
        currency="RUB",
        prices=[
            LabeledPrice(
                label="Подписка",
                amount=100_00
            )
        ],
        start_parameter="create_invoice_donate",
        photo_url="https://i.ibb.co/5LwRm3P/logo.png",
        photo_size=200,
        is_flexible=False
    )
    await call.bot.send_invoice(chat_id=call.from_user.id,
                                **musician.generate_invoice(),
                                payload=f"{call.from_user.id}")
    await state.set_state(Subscribing.MusicianSubscribing)


async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery, state: FSMContext):
    await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query_id=pre_checkout_query.id, ok=True)
    await state.set_state(Subscribing.MusicianPaid)


async def all_good(message: types.Message, state: FSMContext):
    await message.answer(text="Вы возобновили подписку 😎", reply_markup=s.MUSICIAN_LC_KB)
    db.activate_subscription(str(message.from_user.id))
    await state.reset_state()


def subscribe_user(dp: Dispatcher):
    dp.register_message_handler(subscription, filters.Text(contains="Подписка"), state="*")
    dp.register_callback_query_handler(cancel_subscription,
                                       lambda call: call.data and call.data == 'cancel_subscription',
                                       state="*")
    dp.register_callback_query_handler(activate_free_subscription,
                                       lambda call: call.data and call.data == 'free',
                                       state="*")
    dp.register_callback_query_handler(activate_subscription,
                                       lambda call: call.data and call.data == 'activate_subscription',
                                       state="*")
    dp.register_pre_checkout_query_handler(process_pre_checkout_query, state=Subscribing.MusicianSubscribing)
    dp.register_message_handler(all_good, content_types=ContentTypes.SUCCESSFUL_PAYMENT, state=Subscribing.MusicianPaid)
