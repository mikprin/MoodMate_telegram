from os import getenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, KeyboardButton
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from mood_mate_src.mate_logger import logger
from mood_mate_src.database_tools.db_init import init_db

from mood_mate_src.messaging.states_text import mood_record_states_messages, get_state_msg
from mood_mate_src import additional_routers, mood_survey_router
from mood_mate_src.analytics import analytics_routers
from mood_mate_src.filters import ButtonTextFilter, CallbackDataFilter

from mood_mate_src.database_tools.users import (
    create_user_from_telegram_message,
    User,
    UserSettings,
    update_user_in_db,
    process_user_db,
    process_user_from_id,
    Language,
)
from mood_mate_src.keyboard import (
    get_start_keyboard,
    get_settings_keyboard,
    get_inline_settings_keyboard,
    get_all_buttons_text,
    BUTTONS_TEXT_LANG,
    emotional_emoji_sets
)

dp = Dispatcher()
dp.include_router(additional_routers.router)
# In mood_survey_router.py I collected all the handlers related to the mood survey to get MoodRecord from the user
dp.include_router(mood_survey_router.router)
# Handlers for analytics
dp.include_router(analytics_routers.router)

token = getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token, parse_mode=ParseMode.HTML)

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

@dp.message(ButtonTextFilter(get_all_buttons_text("settings")))
async def settings_handler(message: Message):
    user = await process_user_db(message)
    await message.answer("Settings", reply_markup=get_inline_settings_keyboard(user=user))

# Add settings callbacks:

@dp.callback_query(CallbackDataFilter("change_language"))
async def change_language_callback_handler(query: types.CallbackQuery):
    user = await process_user_from_id(query.from_user.id)
    new_lang = Language.RU.value if user.settings.language == Language.ENG.value else Language.ENG.value
    user.settings.language = new_lang
    await update_user_in_db(user)
    await query.answer()
    await query.message.edit_text(f"{get_state_msg('lang_changed', user)}",
                                  reply_markup=get_inline_settings_keyboard(user=user))


@dp.callback_query(CallbackDataFilter("toggle_reminder"))
async def toggle_reminder_callback_handler(query: types.CallbackQuery):
    user = await process_user_from_id(query.from_user.id)
    user.settings.reminder_enabled = not user.settings.reminder_enabled
    await update_user_in_db(user)
    await query.answer()
    reminder_state = "on" if user.settings.reminder_enabled else "off"
    await query.message.edit_text(f"{get_state_msg('toggle_reminder_' + reminder_state, user)}",
                                  reply_markup=get_inline_settings_keyboard(user=user))

@dp.message(ButtonTextFilter(get_all_buttons_text("toggle_reminder")))
async def toggle_reminder_handler(message: Message):
    user = await process_user_db(message)
    user.settings.reminder_enabled = not user.settings.reminder_enabled
    await update_user_in_db(user)
    reminder_state = "on" if user.settings.reminder_enabled else "off"
    await message.answer(f"{get_state_msg('toggle_reminder_' + reminder_state, user)}",
                         reply_markup=get_settings_keyboard(user=user))

@dp.message(ButtonTextFilter(get_all_buttons_text("change_language")))
async def change_language_handler(message: Message):
    user = await process_user_db(message)
    new_lang = Language.RU.value if user.settings.language == Language.ENG.value else Language.ENG.value
    user.settings.language = new_lang
    await update_user_in_db(user)
    await message.answer(f"{get_state_msg('lang_changed', user)}", reply_markup=get_settings_keyboard(user=user))

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