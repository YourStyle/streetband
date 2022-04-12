from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from typing import Union
from PIL import Image, ImageDraw
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import VerticalGradiantColorMask
from gadgets.callback_datas import groups_callback, user_reg_callback, choice_callback, action_callback, \
    info_callback, add_callback, delete_callback, review_callback, donate_callback, songs_callback, user_songs_callback
from gadgets.dialogs import msg
from config import GENRES
from database import cache, database

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
        ]
    ]
)

# DONATE_KB = InlineKeyboardMarkup(
#     inline_keyboard=[
#         [
#             InlineKeyboardButton(
#                 text=msg.donate,
#                 callback_data=donate_callback.new(id=artist_id)
#             )
#         ]
#     ]
# )

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


def create_group_caption_kb(artist_id, number):
    GROUP_CAPTIONS_KB = InlineKeyboardMarkup(
        row_width=2,
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=msg.info_mus,
                    callback_data=info_callback.new(id=artist_id, db_number=number)
                )
            ],
            [
                InlineKeyboardButton(
                    text=msg.donate,
                    callback_data=donate_callback.new(id=artist_id)
                )
            ],
            [
                InlineKeyboardButton(
                    text="Назад",
                    callback_data=groups_callback.new(location="back")
                )
            ]
        ]
    )
    return GROUP_CAPTIONS_KB


EDIT_PROFILE_KB = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="📝Название",
            callback_data="edit_name"
        ),
        InlineKeyboardButton(
            text="📝Описание",
            callback_data="edit_description"
        )
    ],
    [
        InlineKeyboardButton(
            text="📝Фото",
            callback_data="edit_picture"
        ),
        InlineKeyboardButton(
            text="📝Лидер",
            callback_data="edit_leader"
        )
    ],
    [
        InlineKeyboardButton(
            text="📝Жанры",
            callback_data="edit_genres"
        )
    ]
]
)


def create_group_action_kb(artist_id, number, fav=False, location=True):
    if not fav:
        GROUP_CAPTIONS_KB = InlineKeyboardMarkup(
            row_width=2,
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=msg.add_musician,
                        callback_data=add_callback.new(id=artist_id, db_number=number)
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=msg.donate,
                        callback_data=donate_callback.new(id=artist_id)
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=msg.songs,
                        callback_data=user_songs_callback.new(id=artist_id)
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Назад",
                        callback_data=groups_callback.new(location="back")
                    )
                ]
            ]
        )
    elif location:
        GROUP_CAPTIONS_KB = InlineKeyboardMarkup(
            row_width=2,
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=msg.delete_musician,
                        callback_data=delete_callback.new(id=artist_id)
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=msg.donate,
                        callback_data=donate_callback.new(id=artist_id)
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=msg.songs,
                        callback_data=user_songs_callback.new(id=artist_id)
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Назад",
                        callback_data=groups_callback.new(location="back")
                    )
                ]
            ]
        )
    else:
        GROUP_CAPTIONS_KB = InlineKeyboardMarkup(
            row_width=2,
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=msg.delete_musician,
                        callback_data=delete_callback.new(id=artist_id)
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=msg.donate,
                        callback_data=donate_callback.new(id=artist_id)
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=msg.songs,
                        callback_data=user_songs_callback.new(id=artist_id)
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Назад",
                        callback_data="back_to_fav"
                    )
                ]
            ]
        )
    return GROUP_CAPTIONS_KB


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


MEM_KB = InlineKeyboardMarkup().row(InlineKeyboardButton(msg.finish, callback_data="finish"))

CAN_KB = InlineKeyboardMarkup().row(InlineKeyboardButton(msg.subscription_con, callback_data="cancel_subscription"))
SUB_KB = InlineKeyboardMarkup().row(InlineKeyboardButton(msg.subscription_ref, callback_data="activate_subscription"))

FREE_KB = InlineKeyboardMarkup().row(InlineKeyboardButton("😎 Активировать", callback_data="free"))

SUBSC_KB = ReplyKeyboardMarkup(
    resize_keyboard=True,
    row_width=2,
    keyboard=[
        [
            KeyboardButton(msg.subscription)
        ]
    ]
)

# Профиль музыканта
MUSICIAN_LC_KB = ReplyKeyboardMarkup(
    resize_keyboard=True,
    row_width=2,
    keyboard=[
        [
            KeyboardButton(text=msg.play_local, request_location=True),
            KeyboardButton(msg.songs)
        ],
        [
            KeyboardButton(msg.qr),
            KeyboardButton(msg.subscription)
        ],
        [
            KeyboardButton(msg.lc_mus)
        ]
    ]
)


async def get_genre_ids(user_id: str, musician: bool) -> list:
    """Функция получает id жанров пользователя в базе данных"""
    genres = cache.lrange(f"{user_id}", 0, -1)
    if not musician:
        if not genres:
            if cache.jget(f"{user_id}_gen") != "editing":
                try:
                    genres = database.get_user(user_id)["fav_genres"]
                except TypeError:
                    return []
            if genres is not None:
                [cache.lpush(f"{user_id}", ge_id) for ge_id in genres]
            else:
                return []
    else:
        if not genres:
            if cache.jget(f"{user_id}_gen") != "editing":
                try:
                    genres = database.get_musician(user_id)["group_genre"]
                except TypeError:
                    return []
            if genres is not None:
                [cache.lpush(f"{user_id}", ge_id) for ge_id in genres]
            else:
                return []
    return genres


CONFIG_KB = InlineKeyboardMarkup().row(
    InlineKeyboardButton(msg.btn_back, callback_data='main_window'),
    InlineKeyboardButton(msg.config_btn_edit, callback_data='edit_config#')
).add(InlineKeyboardButton(msg.config_btn_delete, callback_data='delete_config'))

CONFIG_M_KB = InlineKeyboardMarkup().row(
    InlineKeyboardButton(msg.config_btn_edit, callback_data='edit_config#')
).add(InlineKeyboardButton(msg.config_btn_delete, callback_data='delete_config'))

ADD_SONG_KB = InlineKeyboardMarkup().row(InlineKeyboardButton(msg.add_song, callback_data="add_song"))

SONGS_KB = InlineKeyboardMarkup().row(
    InlineKeyboardButton(msg.add_song, callback_data='add_song'),
    InlineKeyboardButton(msg.delete_song, callback_data='delete_song')
).add(InlineKeyboardButton(msg.delete_all_songs, callback_data='delete_all_songs'))


def delete_cancel_kb(song_id):
    kb = InlineKeyboardMarkup().row(
        InlineKeyboardButton(msg.btn_back, callback_data='back_to_songs'),
        InlineKeyboardButton(msg.delete_song, callback_data=f'delete_song_{song_id}')
    )
    return kb


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


async def get_genres_names(ids: list, sep: bool = True) -> str:
    genres_text = ""
    if sep:
        for i, genre_id in enumerate(ids, start=1):
            if i != 1:
                genres_text += '\n'
            genres_text += msg.genre_row.format(
                i=i,
                name=GENRES.get(genre_id, '-')
            )
    else:
        for i, genre_id in enumerate(ids, start=1):
            if i != 1:
                genres_text += ','
            genres_text += msg.genre_rows.format(i=GENRES.get(genre_id, '-'))
    return genres_text


def update_genres(user_id: str, data: str):
    genre_id = data.split("#")[-1]  # data ~ add_league_#5#345
    if data.startswith("add"):
        cache.lpush(f"{user_id}", genre_id)
    else:
        cache.lrem(f"{user_id}", 0, genre_id)


def create_qr(musician_id):
    data = "https://t.me/streetband_bot?start=mus_" + musician_id
    Logo_link = 'logo.png'

    logo = Image.open(Logo_link)
    basewidth = 100
    draw = ImageDraw.Draw(logo)

    # adjust image size
    wpercent = (basewidth / float(logo.size[0]))
    hsize = int((float(logo.size[1]) * float(wpercent)))
    logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)
    # mus_qr = musician_id + ".png"
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(data)

    img = qr.make_image(image_factory=StyledPilImage, module_drawer=RoundedModuleDrawer(radius_ratio=0.5),
                        color_mask=VerticalGradiantColorMask(bottom_color=(192, 0, 32)))
    pos = ((img.size[0] - logo.size[0]) // 2,
           (img.size[1] - logo.size[1]) // 2)
    img.paste(logo, pos, logo)
    return img


def review_kb():
    kb = InlineKeyboardMarkup(row_width=5)
    buf = []
    for i in range(1, 6):
        kb.insert(InlineKeyboardButton(f"⭐️{i}", callback_data=review_callback.new(score=str(i))))
    return kb
