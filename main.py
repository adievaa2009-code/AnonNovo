import asyncio
import logging

from aiogram.fsm.storage.redis import RedisStorage, Redis
from aiogram import Bot, Dispatcher

from bot.config import config, bot
from bot.handlers import *
from database.initdb import init_db
from database.manager import basedatabase
from database.models import Base

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


# redis = Redis(host=config.redis.host)
# storage = RedisStorage(redis=redis)
# dp = Dispatcher(storage=storage)
dp = Dispatcher()

dp.include_routers(commands_router, menu_router, callback_router)


async def main():
    logging.info("Starting bot")
    await init_db()
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Error occurred: {e}")

async def init_models(engine=None):
    async with basedatabase.db() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(main())
