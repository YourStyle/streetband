from dataclasses import dataclass
from typing import List
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import LabeledPrice, CallbackQuery

import config
from app.callback_datas import donate_callback
from app.states import Donating
from database import database as db


@dataclass
class Item:
    title: str
    description: str
    start_parameter: str
    currency: str
    prices: List[LabeledPrice]
    max_tip_amount: int = None
    photo_url: str = None
    photo_size: int = None
    photo_width: int = None
    photo_height: int = None
    send_phone_number_to_provider: bool = False
    send_email_to_provider: bool = False
    is_flexible: bool = False
    suggested_tip_amounts: List[int] = None

    provider_token: str = config.PROVIDER_TOKEN

    def generate_invoice(self):
        return self.__dict__


async def show_invoices(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer()
    buffer = db.get_musician(str(callback_data["id"]))
    # print(buffer)
    musician = Item(
        title="Поддержка музыканта",
        description=f"Перевод будет отправлен группе {buffer['musician_name']}  ",
        currency="RUB",
        prices=[
            LabeledPrice(
                label="Донат",
                amount=20_00
            )
        ],
        max_tip_amount=10000_00,
        start_parameter="create_invoice_donate",
        photo_url="https://i.ibb.co/5LwRm3P/logo.png",
        photo_size=200,
        suggested_tip_amounts=[10_00, 20_00, 50_00, 100_00],
        is_flexible=False
    )
    await call.bot.send_invoice(chat_id=call.from_user.id,
                                **musician.generate_invoice(),
                                payload=f"{buffer['musician_id']}")
    await state.set_state(Donating.UserDonating)


async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery, state: FSMContext):
    await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query_id=pre_checkout_query.id, ok=True)
    await pre_checkout_query.bot.send_message(chat_id=pre_checkout_query.from_user.id,
                                              text="Спасибо за поддержку музыканта 😎")
    await state.reset_state()



def pay_bot(dp: Dispatcher):
    dp.register_callback_query_handler(show_invoices, donate_callback.filter(), state="*")
    dp.register_pre_checkout_query_handler(process_pre_checkout_query, state=Donating.UserDonating)
