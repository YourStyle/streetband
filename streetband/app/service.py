from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from typing import Union

from app.callback_datas import choice_callback, user_reg_callback, action_callback, groups_callback
from database import database as db
from app.dialogs import msg

# Профиль юзера
MAIN_KB = ReplyKeyboardMarkup(
    resize_keyboard=True,
    row_width=2,
    keyboard=[
        [
            KeyboardButton(msg.favourite),
            KeyboardButton(msg.lc)
        ],
        [
            KeyboardButton(msg.nearby)
        ]
    ]
)

DONATE_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=msg.donate,
                callback_data="donate"
            )
        ]
    ]
)



GROUP_CAPTIONS_KB = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=msg.add_musician,
                callback_data="add"
            ),
            InlineKeyboardButton(
                text=msg.info_mus,
                callback_data="info"
            )
        ],
        [
            InlineKeyboardButton(
                text=msg.donate,
                callback_data="donate"
            )
        ],
        [
            InlineKeyboardButton(
                text="Все группы",
                callback_data=groups_callback.new(location="group_locations")
            )
        ]
    ]
)

CHOICE_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="исполнитель",
                callback_data=user_reg_callback.new(user="musician")
            ),
            InlineKeyboardButton(
                text="пользователь",
                callback_data=user_reg_callback.new(user="user")
            )
        ]
    ]
)

AGREEMENT_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅",
                callback_data=choice_callback.new(decision="agree")
            )
        ]
    ]
)

BACK_OR_CANCEL_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Вернуться",
                callback_data=action_callback.new(action="back", id="1")
            )
        ],
        [
            InlineKeyboardButton(
                text="Отменить регистрацию группы",
                callback_data=action_callback.new(action="exit", id="1")
            )
        ]
    ]
)

BACK_OR_APPROVE_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Вернуться",
                callback_data=action_callback.new(action="back", id="1")
            )
        ],
        [
            InlineKeyboardButton(
                text="Подтвердить",
                callback_data=action_callback.new(action="approve", id="1")
            )
        ]
    ]
)


def create_approvement_kb(message: Union[str, int]):
    DECLINE_OR_APPROVE = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅",
                    callback_data=action_callback.new(action="approve_data", id=message)
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌",
                    callback_data=action_callback.new(action="decline_data", id=message)
                )
            ]
        ]
    )
    return DECLINE_OR_APPROVE


def create_final_approvement_kb(message: Union[str, int]):
    DECLINE_OR_APPROVE = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅",
                    callback_data=action_callback.new(action="approve_final_data", id=message)
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌",
                    callback_data=action_callback.new(action="decline_final_data", id=message)
                )
            ]
        ]
    )
    return DECLINE_OR_APPROVE


# Профиль музыканта
MUSICIAN_LC_KB = ReplyKeyboardMarkup(
    resize_keyboard=True,
    row_width=2,
    keyboard=[
        [
            KeyboardButton(msg.play_local),
            KeyboardButton(msg.songs)
        ],
        [
            KeyboardButton(msg.balance),
            KeyboardButton(msg.bonuses)
        ],
        [
            KeyboardButton(msg.lc)
        ],
        [
            KeyboardButton(msg.lc_mus)
        ]
    ]
)
