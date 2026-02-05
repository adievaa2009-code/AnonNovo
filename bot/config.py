from dataclasses import dataclass
from typing import List

from environs import Env
from aiogram import Bot, Dispatcher

@dataclass
class TgBotConfig:
    token: str
    admin_ids: List[int]


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str
    port: str


@dataclass
class RedisConfig:
    host: str
@dataclass
class Ai:
    token: str
    team_id: str


@dataclass
class Config:
    tg_bot: TgBotConfig
    ai: Ai
    # db: DbConfig
    # redis: RedisConfig


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBotConfig(
            token=env.str("BOT_TOKEN"), admin_ids=list(map(int, env.list("ADMINS")))
        ),
        ai=Ai(token=env.str("API_TOKEN"), team_id=env.str("TEAM_ID"))
              )
        # db=DbConfig(
        #     host=env.str("DB_HOST"),
        #     password=env.str("DB_PASS"),
        #     user=env.str("DB_USER"),
        #     database=env.str("DB_NAME"),
        #     port=env.str("DB_PORT"),
        # ),
        # redis=RedisConfig(host=env.str("REDIS_HOST")),



config = load_config(".env")
BOT_TOKEN = config.tg_bot.token

bot = Bot(BOT_TOKEN, parse_mode="HTML")