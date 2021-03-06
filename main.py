import asyncio

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.types import BotCommand, BotCommandScopeDefault
import logging
import config
from app.button_handlers import use_buttons
from app.feedback_handlers import send_feedback
from app.genres_handlers import choose_genres
from filters.musician import MusicianFilter
from app.registration_handlers import register_users
from app.start_handlers import start_bot
from app.streets_handlers import check_streets
from app.paymnet_handler import pay_bot
from app.subscription_handler import subscribe_user

# from app.utils import check_subscription
# from scripts.post import scheduler
from scripts.post import scheduler

logger = logging.getLogger(__name__)


def register_all_filters(dp):
    dp.filters_factory.bind(MusicianFilter)


def register_all_handlers(dp):
    start_bot(dp)
    pay_bot(dp)
    register_users(dp)
    choose_genres(dp)
    subscribe_user(dp)
    use_buttons(dp)
    check_streets(dp)
    send_feedback(dp)


async def set_bot_commands(bot: Bot):
    data = [
        (
            [
                BotCommand(command="start", description="Запуск бота"),
                BotCommand(command="feedback", description="Отправить отзыв о боте")
            ],
            BotCommandScopeDefault(),
            None
        )
    ]
    for commands_list, commands_scope, language in data:
        await bot.set_my_commands(commands=commands_list, scope=commands_scope, language_code=language)



# async def on_startup(_):
#     asyncio.create_task(scheduler())


async def bot_main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    bot = Bot(token=config.TOKEN, parse_mode="HTML")
    dp = Dispatcher(bot, storage=RedisStorage2(config.REDIS_HOST))

    await set_bot_commands(bot)

    register_all_filters(dp)
    register_all_handlers(dp)

    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


async def main():
    await asyncio.gather(
        bot_main(),
        scheduler(),
    )


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
