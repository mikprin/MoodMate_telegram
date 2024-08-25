import os
from aiogram import exceptions
import asyncio
from aiogram import Bot
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, KeyboardButton
from aiogram.enums import ParseMode

from mood_mate_src.mate_logger import logger



token = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token, parse_mode=ParseMode.HTML)


async def send_message_to_user(chat_id: int, text: str, disable_notification: bool = False) -> bool:
    try:
        await bot.send_message(chat_id, text, disable_notification=disable_notification)
    # except exceptions.BotBlocked:
    #     logger.error(f"Target [ID:{user_id}]: blocked by user")
    # except exceptions.ChatNotFound:
    #     logger.error(f"Target [ID:{user_id}]: invalid user ID")
    # except exceptions.RetryAfter as e:
    #     logger.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
    #     await asyncio.sleep(e.timeout)
    #     return await send_message_to_user(user_id, text)  # Recursive call
    # except exceptions.UserDeactivated:
    #     logger.error(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramRetryAfter as e:
        logger.exception(f"Target [ID:{chat_id}]: retry after")
        asyncio.sleep(e.timeout)
        return await send_message_to_user(chat_id, text)
    except exceptions.TelegramBadRequest:
        logger.exception(f"Target [ID:{chat_id}]: bad request")
        await bot.session.close()
    except exceptions.TelegramAPIError:
        logger.exception(f"Target [ID:{chat_id}]: failed")


    except Exception as e:
        logger.exception(f"Target [ID:{chat_id}]: failed with exception {e}")
    else:
        logger.info(f"Send message: Target [ID:{chat_id}]: success")
        await bot.session.close()
        return True
    return False

async def send_file_to_user(chat_id: int, file: str, caption: str = None, disable_notification: bool = False) -> bool:
    
    file_obj = types.FSInputFile(file)
    
    try:
        await bot.send_document(chat_id, file_obj, caption=caption, disable_notification=disable_notification)
    except exceptions.TelegramRetryAfter as e:
        logger.exception(f"Target [ID:{chat_id}]: retry after")
        asyncio.sleep(e.timeout)
        return await send_file_to_user(chat_id, file, caption, disable_notification)
    except exceptions.TelegramBadRequest:
        logger.exception(f"Target [ID:{chat_id}]: bad request")
        await bot.session.close()
    except exceptions.TelegramAPIError:
        logger.exception(f"Target [ID:{chat_id}]: failed")
    except Exception as e:
        logger.exception(f"Target [ID:{chat_id}]: failed with exception {e}")
    else:
        logger.info(f"Send file: Target [ID:{chat_id}]: success")
        await bot.session.close()
        return True
    return False