from os import getenv
from abc import ABC, abstractmethod
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, KeyboardButton
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, BaseFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

from mood_mate_src.mate_logger import logger
from mood_mate_src.database_tools.users import (
    create_user_from_telegram_message,
    User,
    UserSettings,
    get_user_from_db,
    add_user_to_db,
    update_user_in_db,
    Language,
)
from mood_mate_src.database_tools.redis_tools import RedisDB
from mood_mate_src.database_tools.db_init import init_db
from mood_mate_src.keyboard import (
    get_start_keyboard,
    get_settings_keyboard,
    get_all_buttons_text,
    BUTTONS_TEXT,
    BUTTONS_TEXT_LANG,
)
from mood_mate_src.states_machine import AddRecord
from mood_mate_src.messaging.states_text import mood_record_states_messages
from mood_mate_src import additional_routers

dp = Dispatcher()
dp.include_router(additional_routers.router)

token = getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token, parse_mode=ParseMode.HTML)

admin_ids_users = getenv("ADMIN_CHATS")
ADMIN_LOG_MSG_TXT = "Mood bot admin update:"

if admin_ids_users:
    if "," in admin_ids_users:
        admin_ids_users = admin_ids_users.split(",")
    else:
        admin_ids_users = [admin_ids_users]


class ButtonTextFilter(BaseFilter):
    """
    Filter for checking if the message text is in the list of button texts
    """
    def __init__(self, button_texts: list[str]):
        self.button_texts = button_texts
        logger.debug(f"ButtonTextFilter initialized with button_texts: {button_texts}")

    async def __call__(self, message: Message) -> bool:
        logger.debug(f"Checking if message.text is in button_texts: {message.text} in {self.button_texts}")
        return message.text in self.button_texts

async def run_bot():
    """Dont forget to load the .env file BEFORE running the bot"""
    logger.debug("Initializing the database")
    init_db()
    
    logger.info("Starting the bot")
    await dp.start_polling(bot)


@dp.message(ButtonTextFilter(get_all_buttons_text("go_back")))
async def go_back_handler(message: Message):
    user = process_user_db(message)
    new_keyboard = get_start_keyboard(user=user)
    await bot.edit_message_reply_markup(
        chat_id=message.chat.id,
        message_id=message.message_id,
        reply_markup=new_keyboard
    )


@dp.message(ButtonTextFilter(get_all_buttons_text("settings")))
async def settings_handler(message: Message):
    user = process_user_db(message)
    await message.answer("Settings placeholder", reply_markup=get_settings_keyboard(user=user))


@dp.message(ButtonTextFilter(get_all_buttons_text("change_language")))
async def change_language_handler(message: Message):
    user = process_user_db(message)
    new_lang = Language.RU.value if user.settings.language == Language.ENG.value else Language.ENG.value
    user.settings.language = new_lang
    await update_user_in_db(user)
    await message.answer(f"{mood_record_states_messages[new_lang]['lang_changed']}", reply_markup=get_settings_keyboard(user=user))

def process_user_db(message: Message):
    """Process the user database"""
    user = get_user_from_db(message.from_user.id)
    if user is None:
        user = create_user_from_telegram_message(message)
        add_user_to_db(user)
    return user


# Start command handler
@dp.message(CommandStart())
async def start_command_handler(message: Message):
    logger.info(f"User {message.from_user.username} started the bot")
    
    user = process_user_db(message)
    greetings_msg = mood_record_states_messages[user.settings.language]["greetings"]
    await message.answer(greetings_msg,
                         reply_markup=get_start_keyboard(user=user))

    
@dp.message(ButtonTextFilter(get_all_buttons_text("track_mood")))
async def track_mood_handler(message: Message, state: FSMContext):
    """Enter in AddRecord state handler"""
    
    user =  process_user_db(message)
    await state.update_data(user=user)
    await state.set_state(AddRecord.sleep)
    await message.answer("Please enter your mood data in the following format:\n"
                         "Mood level: 1-5\n")
    
@dp.message(AddRecord.sleep)
async def add_mood_handler(message: Message, state: FSMContext):
    """Add mood level to the state"""
    await state.update_data(mood=message.text)
    await state.set_state(AddRecord.horny)
    await message.answer(f"You entered: {message.text}\n Please enter the number of hours you slept last night:")
    
@dp.message(AddRecord.horny)
async def add_sleep_handler(message: Message, state: FSMContext):
    """Add sleep hours to the state"""
    user = await state.get_data("user")
    await state.update_data(sleep=message.text)
    await state.set_state(AddRecord.horny)
    await message.answer(f"You entered: {message.text}\n Please enter your level of horniness:")
    
@dp.message(AddRecord.horny)
async def add_horny_handler(message: Message, state: FSMContext):
    """Add horny level to the state"""
    user = await state.get_data("user")
    await state.update_data(horny=message.text)
    await state.set_state(AddRecord.exercise)
    await message.answer(f"You entered: {message.text}\n Please enter the number of hours you exercised today:")

@dp.message(AddRecord.exercise)
async def add_exercise_handler(message: Message, state: FSMContext):
    """Add exercise hours to the state"""
    user = await state.get_data("user")
    await state.update_data(exercise=message.text)
    await state.set_state(AddRecord.doping)
    await message.answer(f"You entered: {message.text}\n Please enter the doping you took today:")
    