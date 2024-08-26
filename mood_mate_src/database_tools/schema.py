from enum import Enum
from pydantic import BaseModel

default_reminder_time = "19:00"

class Language(Enum):
    ENG = "en"
    RU = "ru"

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
    reminder_enabled: bool = True
    username: str | None = None

    class ConfigDict:
        orm_mode = True


class User(BaseModel):
    user_id: int
    chat_id: int
    settings: UserSettings  # Dictionary to store JSON settings
    class ConfigDict:
        orm_mode = True  # Enable ORM mode for easy conversion
