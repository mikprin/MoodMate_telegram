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

class AssistantRole(BaseModel):
    role_name_short: str
    role_name: str
    role_description: str | None = None


DEFAULT_ASSISTANT_ROLE = AssistantRole(
    role_name_short="rick_sanchez",
    role_name="Rick Sanchez",
    role_description="A genius scientist with a cynical and reckless personality."
)

class UserSettings(BaseModel):
    name: str
    created_at: int
    language: str = Language.ENG.value
    dopings_list: list = list()  # List to store JSON dopings
    periods_are_tracked: bool = False
    reminder_time: str = default_reminder_time
    reminder_enabled: bool = True
    gender: Gender | None = None
    recommended_sleep: float | None = None
    username: str | None = None
    weekly_report_enabled: bool | None = None
    assistant_custom_role: AssistantRole | None = DEFAULT_ASSISTANT_ROLE

    class ConfigDict:
        orm_mode = True


class User(BaseModel):
    user_id: int
    chat_id: int
    settings: UserSettings  # Dictionary to store JSON settings
    class ConfigDict:
        orm_mode = True  # Enable ORM mode for easy conversion


class Doping(BaseModel):
    """Doping model to store user's dopings.
    Not used yet, but will be used in the future."""
    names: dict[str, str] # For multi-language support
    emoji: str | None = None
    image: str | None = None

    class ConfigDict:
        orm_mode = True  # Enable ORM mode for easy conversion
        
    def __str__(self):
        return f"{self.names[Language.ENG.value]} {self.emoji}"
    
    def get_name_by_lang(self, lang: str) -> str:
        return f"{self.names[lang]} {self.emoji}"


class UserFeedbackRecord(BaseModel):
    """Model to store user feedback"""
    user_id: int
    created_at: int
    feedback: str

    class ConfigDict:
        orm_mode = True  # Enable ORM mode for easy conversion
    def __str__(self):
        return f"Feedback from user_id {self.user_id}: {self.feedback}"