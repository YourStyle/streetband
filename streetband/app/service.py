from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from typing import Union

from aiogram.utils.emoji import emojize

from app.callback_datas import choice_callback, user_reg_callback, action_callback, groups_callback
from config import GENRES
from database import database as db, cache
from app.dialogs import msg

# Профиль юзера
MAIN_KB = ReplyKeyboardMarkup(
    resize_keyboard=True,
    row_width=2,
    keyboard=[
        [
            KeyboardButton(msg.favourite),
            KeyboardButton(msg.fav_genres),
        ],
        [
            KeyboardButton(msg.nearby)
        ],
        [
            KeyboardButton(msg.name_lc),
            KeyboardButton(msg.balance)
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
                text="Назад",
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


async def get_genre_ids(user_id: str) -> list:
    """Функция получает id лиг пользователя в базе данных"""
    genres = cache.lrange(f"{user_id}", 0, -1)
    if genres is None:
        genres = await db.select_users(user_id)
        if genres is not None:
            genres = genres.split(',')
            [cache.lpush(f"{user_id}", ge_id) for ge_id in genres]
        else:
            return []
    return genres


CONFIG_KB = InlineKeyboardMarkup().row(
    InlineKeyboardButton(msg.btn_back, callback_data='main_window'),
    InlineKeyboardButton(msg.config_btn_edit, callback_data='edit_config#')
).add(InlineKeyboardButton(msg.config_btn_delete, callback_data='delete_config'))


def genres_kb(active_genres: list, offset: int = 0):
    kb = InlineKeyboardMarkup()
    genres_keys = list(GENRES.keys())[0 + offset:5 + offset]
    for genres_id in genres_keys:
        if genres_id in active_genres:
            kb.add(InlineKeyboardButton(
                f"{'✅'} {GENRES[genres_id]}",
                callback_data=f'del_ge_#{offset}#{genres_id}'
            ))
        else:
            kb.add(InlineKeyboardButton(
                GENRES[genres_id],
                callback_data=f'add_ge_#{offset}#{genres_id}'
            ))
    kb.row(
        InlineKeyboardButton(
            msg.btn_back if offset else msg.btn_go,
            callback_data="edit_config#0" if offset else "edit_config#5"),
        InlineKeyboardButton(msg.btn_save, callback_data="save_config")
    )
    return kb


async def get_genres_names(ids: list) -> str:
    """Функция собирает сообщение с названиями лиг из id"""
    genres_text = ""
    for i, genre_id in enumerate(ids, start=1):
        if i != 1:
            genres_text += '\n'
        genres_text += msg.genre_row.format(
            i=i,
            name=GENRES.get(genre_id, '-')
        )
    return genres_text


def update_genres(user_id: str, data: str):
    """Функция добавляет или удаляет id лиги для юзера"""
    genre_id = data.split("#")[-1]  # data ~ add_league_#5#345
    if data.startswith("add"):
        cache.lpush(f"{user_id}", genre_id)
    else:
        cache.lrem(f"{user_id}", 0, genre_id)
