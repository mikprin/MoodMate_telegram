import json
import os
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from aiogram.types import Message
from mood_mate_src.mate_logger import logger

from mood_mate_src.database_tools.locks import user_db_lock
from mood_mate_src.database_tools.query import execute_query_with_lock, DB_PATH, execute_query

USERS_DB_TABLE = "users"
default_reminder_time = "19:00"

class Language(Enum):
    ENG = "en"
    RU = "ru"

default_dopings_list = {
    Language.ENG.value: [
                        "Coffee/caffeine: ☕",
                        "Smoking: 🚬",
                        "Alcohol: 🍺 or 🍷",
                        "Weed: 🌿",
                        "Mushrooms: 🍄",
                        # "LSD: 🌈",
                        "Pills?: 💊",
                        ],
    Language.RU.value: [
                        "Кофе/кофеин: ☕",
                        "Курение: 🚬",
                        "Алкоголь: 🍺 или 🍷",
                        "Трава: 🌿",
                        "Грибы: 🍄",
                        # "ЛСД: 🌈",
                        "Таблетки?: 💊",
                        ]
}


class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"

class UserSettings(BaseModel):
    name: str
    created_at: int
    language: str = Language.ENG.value
    dopings_list: list = list()  # List to store JSON dopings
    gender: Gender | None = None
    periods_are_tracked: bool = False
    reminder_time: str = default_reminder_time
    reminder_enabled: bool = False
    username: str | None = None

    class ConfigDict:
        orm_mode = True


class User(BaseModel):
    user_id: int
    chat_id: int
    settings: UserSettings  # Dictionary to store JSON settings
    class ConfigDict:
        orm_mode = True  # Enable ORM mode for easy conversion


def create_user_from_telegram_message(message: Message) -> User:
    lang_code = message.from_user.language_code

    if lang_code in [lang.value for lang in Language]:
        language = Language(lang_code)
    else:
        language = Language.ENG
    
    return User(
        user_id=message.from_user.id,
        chat_id=message.chat.id,
        settings=UserSettings(
            name = message.from_user.full_name,
            username=message.from_user.username,
            dopings_list=default_dopings_list[language.value],
            created_at = int(datetime.now().timestamp()),
            language=language.value,
        )
    )


# Function to insert a user into the database
async def add_user_to_db(user: User):

    # Serialize settings to JSON string if present
    settings_json = json.dumps(user.settings.model_dump()) if user.settings else None

    # Insert the user into the database
    await execute_query_with_lock(
        db_path=DB_PATH,
        db_lock=user_db_lock,
        query=f'''
        INSERT INTO {USERS_DB_TABLE} (user_id, chat_id, settings)
        VALUES (?, ?, ?)
        ''',
        params=(user.user_id, user.chat_id, settings_json))
    logger.info(f"User {user.settings.username} added to the database.")


async def update_user_in_db(user: User):
    
    # Serialize settings to JSON string if present
    settings_json = json.dumps(user.settings.model_dump()) if user.settings else None

    # Insert the user into the database
    await execute_query_with_lock(
        db_path=DB_PATH,
        db_lock=user_db_lock,
        query=f'''
        UPDATE {USERS_DB_TABLE} SET chat_id = ?, settings = ?
        WHERE user_id = ?
        ''',
        params=(user.chat_id, settings_json, user.user_id))
    logger.info(f"User {user.settings.username} updated in the database.")


# def transfrom_raw_user_data(raw_user_data: tuple) -> User:
#     # Deserialize the settings JSON
#     # raw_user_data = list(raw_user_data)
#     raw_user_data[2] = json.loads(raw_user_data[2])
#     return User(*raw_user_data)


def get_user_from_db(user_id: int) -> User:
    # Get the user from the database
    user_data = execute_query(
        db_path=DB_PATH,
        query=f'''
        SELECT * FROM {USERS_DB_TABLE} WHERE user_id = ?
        ''',
        params=(user_id,),
        return_result=True,
        dict_result=True
        )
    
    # If the user is not found, return None
    if not user_data:
        return None
    
    # Deserialize the settings JSON
    for user in user_data:
        user['settings'] = json.loads(user['settings'])
        user_res = User(**user)
    
    # Return the User object
    return user_res

def get_all_users_from_db() -> list[User]:
    # Get all users from the database
    users_data = execute_query(
        db_path=DB_PATH,
        query=f'''
        SELECT * FROM {USERS_DB_TABLE}
        ''',
        return_result=True,
        dict_result=True
        )
    
    # Process case with no users
    if not users_data:
        return list()
    
    users = list()
    
    for user_data in users_data:
        # Deserialize the settings JSON
        user_data['settings'] = json.loads(user_data['settings'])
        user = User(**user_data)
        users.append(user)
    return users


async def process_user_db(message: Message):
    """Process the user database when new msg arrives
    Effectively creates or retrieves the user from the database
    """
    user = get_user_from_db(message.from_user.id)
    if user is None:
        user = create_user_from_telegram_message(message)
        await add_user_to_db(user)
    return user