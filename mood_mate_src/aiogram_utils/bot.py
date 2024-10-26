from aiogram import Bot
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from os import getenv


def get_bot(parse_mode="html") -> Bot:
    token = getenv("TELEGRAM_BOT_TOKEN")
    
    if parse_mode == "markdown":
        default_parse_mode = DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2)
    else:
        default_parse_mode = DefaultBotProperties(parse_mode=ParseMode.HTML)

    bot = Bot(token, default=default_parse_mode)
    return bot