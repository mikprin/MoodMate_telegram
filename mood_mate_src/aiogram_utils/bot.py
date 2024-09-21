from aiogram import Bot
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from os import getenv


def get_bot() -> Bot:
    token = getenv("TELEGRAM_BOT_TOKEN")
    bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    return bot