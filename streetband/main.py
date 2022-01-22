from aiogram import executor
from aiogram.types import Update

from app import bot


executor.start_polling(bot.dp, on_shutdown=bot.on_shutdown)
