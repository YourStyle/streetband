import asyncio

import aioschedule
from aiogram import Bot
from aiogram.dispatcher import FSMContext
from aiogram.types import LabeledPrice
from aiogram.utils.exceptions import BotBlocked

import config
from app.paymnet_handler import Item
from database import database as db, cache
from gadgets import service as s
from gadgets.service import cancel_mailing_kb
from gadgets.states import Subscribing


async def send_mailing_test():
    bot = Bot(token=config.TOKEN, parse_mode="HTML")
    db.get_musicians()
    arr = cache.jget("musicians")
    for user_id in arr:
        if user_id["active_subscription"] is True:
            try:
                subscribed = db.get_subscription(user_id["musician_id"])
                if subscribed.days == 15:
                    await bot.send_message(chat_id=user_id["musician_id"],
                                           text=f"До конца вашей подписки {subscribed.days} дней")
                elif subscribed.days == 1:
                    await bot.send_message(chat_id=user_id["musician_id"],
                                           text=f"До конца вашей подписки {subscribed.days} день")
                elif subscribed.days == 0:
                    await bot.send_message(user_id["musician_id"],
                                           f"Ваша подписка закончилась! Сейчас пользователи не смогут найти вас на картах, отсканировать ваш "
                                           f"QR-код "
                                           f"и прослушать ваши песни",
                                           reply_markup=s.SUBSC_KB)
                    db.end_subscription(user_id["musician_id"])
                    musician = Item(
                        title="Оплата подписки",
                        description=f"С вашей карты будет списано 100 рублей и подписка будет доступна в течение "
                                    f"месяца с "
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
                    await bot.send_invoice(chat_id=user_id["musician_id"],
                                           **musician.generate_invoice(),
                                           payload=f"{user_id['musician_id']}")
                    # await state.set_state(Subscribing.MusicianSubscribing)
            except BotBlocked:
                await asyncio.sleep(1)
    db.get_users()
    arr_user = cache.jget("users_data")
    users = arr_user
    counter = len(users)
    for i in range(counter):
        try:
            if db.check_mail_status(str(users[i]["user_id"])):
                await bot.send_message(chat_id=users[i]["user_id"],
                                       text="Если вы больше не хотите получать уведомления, нажмите на кнопку ниже! На данный момент он полностью работает ! Извинямся за спам !(",
                                       reply_markup=cancel_mailing_kb(str(arr_user[i]["user_id"])))
            else:
                pass
        except BotBlocked:
            await asyncio.sleep(1)


async def scheduler():
    # print("test")
    aioschedule.every().day.at("16:40").do(send_mailing_test)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)
