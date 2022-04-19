import asyncio
import aioschedule
from aiogram import Dispatcher
from database import database as db, cache


async def check_subscription():
    db.get_musicians()
    ids = cache.jget("musicians")
    checker = []
    for i in ids:
        checker.append(i["musician_id"])
    print(ids)


async def scheduler():
    aioschedule.every().day.at("15:09").do(check_subscription)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)
