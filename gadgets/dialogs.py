from dataclasses import dataclass


@dataclass(frozen=True)
class Messages():
    genre_row: str = "{i}. {name}"
    genre_rows: str = "{i}"
    greeting: str = "Хэллоу 😎 ! \n "
    config: str = "Сейчас выбраны:\n{genres}"
    greeting_musician: str = "Хэллоу 😎 ! Давай добавим немного музыки в эти серые будни"
    greeting_user: str = "Хэллоу 😎 ! \n Я помогу тебе найти лучших музыкантов твоего города"
    text_placeholder: str = "⏳Год основания: 1973 \n" \
                            "🎸Жанр: хард-рок\n" \
                            "🤴Состав: Малколм Янг, Ангус Янг, Бон Скотт, Клифф Уильямс, Фил Рудд"
    send_location: str = "Если вы хотите получать данные о ближайших музыкантах каждые 15 минут " \
                         "во време прогулки отправьте нам вашу live локацию.\n" \
                         "А если хотите просто увидеть ближайщих музыкантов отправьте обычную геолокацию"
    online: str = "📍 Отправить локацию"
    donate: str = "💵 Задонатить"
    set_genres: str = "Выбери ваши любимые жанры.\nВыбраны:\n{genres}"
    donate_fun: str = "Заплатить ведьмаку чеканной монетой"
    nearby: str = "📍 Музыканты рядом"
    lc: str = "👨 Профиль"
    favourite: str = "❤️ Избранное"
    btn_back: str = "<- Назад"
    btn_go: str = "Вперед ->"
    btn_save: str = "Сохранить"
    config_btn_edit: str = "Изменить"
    config_btn_delete: str = "Удалить данные"
    data_delete: str = "Данные успешно удалены"
    choice: str = "Выберите:"
    policy: str = "Условия пользования ботом"
    add_musician: str = "❤️ В избранное"
    delete_musician: str = "💔 Удалить"
    name_lc: str = "Никнейм"
    name: str = "Отправьте название группы (если вы исполняете в соло можете отправить своё имя)"
    requisites: str = "Отправьте ваш номер счёта, чтобы вы смогли получать на него донаты от пользователей"
    picture: str = "Отправьте фото группы (если вы исполняете в соло можете отправить своё фото)"
    genres: str = "Введите жанры, в которых вы исполняете (через запятую). Сейчас бот поддерживает: рок, джаз, рэп, поп, классика, народное, кантри"
    description: str = "Отправьте описание"
    riba: str = "Спасибо! Мы получили вашу заявку. Менеджер проверит договор и отправит вам пробный платёж (в размере 1 ₽) на указанные в договоре реквизиты"
    exit: str = "Вы отменили регистрацию группы ! Хотите продолжить регистрацию как пользователь?"
    lc_mus: str = "🕺 Профиль группы"
    info_mus: str = "🕺 О группе"
    fav_genres: str = "❤️‍🔥Любимые жанры"
    finish: str = "Let`s rock😎!"
    play_local: str = "🗺Местоположение"
    songs: str = "🎸 Песни"
    balance: str = "💵 Баланс"
    bonuses: str = "🎁 Бонусы"
    reg_complete: str = "Регистрация заверешена! Let`s rock😎!"
    wellcome: str = "С возвращением! Let`s rock😎!"
    save: str = "Измения сохранены!"
    no_genres: str = "Вы не выбрали ни одного жанра!"
    qr: str = "🔁 QR-код"
    edit_name: str = "Отправьте новое название"
    edit_pic: str = "Отправьте новое фото"
    edit_desc: str = "Отправьте новое описание"
    edit_leader: str = "Отправьте нового лидера (его юзернейм без знака @)"
    cb_not_saved: str = "Вы не добавили ни одного жанра!"
    done: str = "Изменения сохранены"
    bad_chars: str = "Мы не можете сохранить такие символы, введите что-то другое"
    subscription: str = "✉️Подписка"
    subscription_con: str = "😯 Отменить подписку"
    subscription_ref: str = "😎 Возобновить подписку"


msg = Messages()
