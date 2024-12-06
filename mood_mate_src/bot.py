from os import getenv

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from mood_mate_src import additional_routers, mood_survey_router, settings
from mood_mate_src.aiogram_utils.bot import get_bot
from mood_mate_src.analytics import analytics_routers
from mood_mate_src.database_tools.db_init import init_db
from mood_mate_src.database_tools.users import (
    Language, User, UserSettings, create_user_from_telegram_message,
    process_user_db, process_user_from_id, update_user_in_db)
from mood_mate_src.filters import ButtonTextFilter, CallbackDataFilter
from mood_mate_src.keyboard import (BUTTONS_TEXT_LANG, emotional_emoji_sets,
                                    get_all_buttons_text,
                                    get_inline_settings_keyboard,
                                    get_settings_keyboard, get_start_keyboard)
from mood_mate_src.mate_logger import logger
from mood_mate_src.messaging.states_text import (get_state_msg,
                                                 mood_record_states_messages)

dp = Dispatcher()
dp.include_router(additional_routers.router)
# In mood_survey_router.py I collected all the handlers related to the mood survey to get MoodRecord from the user
dp.include_router(mood_survey_router.router)
# Handlers for analytics
dp.include_router(analytics_routers.router)
# Settings handlers
dp.include_router(settings.router)

bot = get_bot()

admin_ids_users = getenv("ADMIN_CHATS")
ADMIN_LOG_MSG_TXT = "Mood bot admin update:"

if admin_ids_users:
    if "," in admin_ids_users:
        admin_ids_users = admin_ids_users.split(",")
    else:
        admin_ids_users = [admin_ids_users]


async def run_bot():
    """Dont forget to load the .env file BEFORE running the bot"""
    init_db()

    logger.info("Starting the bot")
    await dp.start_polling(bot)


@dp.message(ButtonTextFilter(get_all_buttons_text("go_back")))
async def go_back_handler(message: Message):
    user = await process_user_db(message)
    new_keyboard = get_start_keyboard(user=user)
    # await bot.edit_message_reply_markup(
    #     chat_id=message.chat.id,
    #     message_id=message.message_id,
    #     reply_markup=new_keyboard
    # )
    await message.answer("Menu",reply_markup=new_keyboard)


# Start command handler
@dp.message(CommandStart())
async def start_command_handler(message: Message):
    logger.info(f"User {message.from_user.username} with id {message.from_user.id} and chat_id {message.chat.id} started the bot")

    user = await process_user_db(message)

    if user.chat_id != message.chat.id:
        user.chat_id = message.chat.id
        await update_user_in_db(user)

    greetings_msg = get_state_msg("greetings", user)
    await message.answer(greetings_msg,
                         reply_markup=get_start_keyboard(user=user))


@dp.callback_query(CallbackDataFilter("main_menu"))
async def main_menu_callback_handler(query: types.CallbackQuery):
    user = await process_user_db(query.message)
    await query.message.edit_text("Menu", reply_markup=get_start_keyboard(user=user))
    await query.answer()
