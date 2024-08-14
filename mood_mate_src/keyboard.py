from aiogram.types.keyboard_button import KeyboardButton
from aiogram import types
from mood_mate_src.database_tools.users import Language, User


BUTTONS_TEXT = {
    "go_back": "🔙",
    "settings": "⚙️",
    "track_mood": "Track mood",
}

BUTTONS_TEXT_LANG = {
    Language.RU.value: {
    "go_back": "Назад! 🔙",
    "settings": "⚙️",
    "track_mood": "Записать настроение",
    "help": "Помощь",
    "change_language": "🌐",
    },
    
    Language.ENG.value: {
    "go_back": "Go back! 🔙",
    "settings": "⚙️",
    "track_mood": "Track mood",
    "help": "Help",
    "change_language": "🌐",
    }
}


def get_all_buttons_text(button_text: str) -> list[str]:
    langs = [lang.value for lang in Language]
    return [BUTTONS_TEXT_LANG[lang][button_text] for lang in langs]
    

def get_lang(user: User | None = None) -> str:
    if user is None:
        return Language.ENG.value
    return user.settings.language
    

def get_start_keyboard(user: User | None = None):
    
    language = get_lang(user)
    
    keyboard_buttons = [
        [
            KeyboardButton(text=BUTTONS_TEXT_LANG[language]["track_mood"]),
            KeyboardButton(text="Show mood history"),

            KeyboardButton(text=BUTTONS_TEXT_LANG[language]["settings"]),
            KeyboardButton(text=BUTTONS_TEXT_LANG[language]["help"]),
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=keyboard_buttons,
        resize_keyboard=True,
        input_field_placeholder="ТЫК"
    )
    return keyboard


def get_settings_keyboard(user: User | None = None):
    
    language = get_lang(user)
    
    keyboard_buttons = [
        [
            KeyboardButton(text=BUTTONS_TEXT_LANG[language]["change_language"]),
            KeyboardButton(text=BUTTONS_TEXT_LANG[language]["go_back"]),
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=keyboard_buttons,
        resize_keyboard=True,
        input_field_placeholder="ТЫК"
    )
    return keyboard