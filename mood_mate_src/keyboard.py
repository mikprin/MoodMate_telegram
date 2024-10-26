from aiogram.types.keyboard_button import KeyboardButton
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
import emoji
from mood_mate_src.database_tools.users import Language, User
from mood_mate_src.messaging.lang_support import get_msg_from_dict

BUTTONS_TEXT_LANG = {
    Language.RU.value: {
    "go_back": "Назад! 🔙",
    "settings": "⚙️",
    "track_mood": "Записать настроение",
    "help": "Помощь",
    "change_language": "🌐, Eng/Ru",
    "toggle_reminder": "Напоминания от бота",
    "mood_data": "Аналитика настроения",
    "pick_emoji": "Выберите пиктограмму",
    "accept": "Принять",
    "track_periods_on": "Включить ведение месячных",
    "track_periods_off": "Выключить ведение месячных",
    "cancel": "Отмена",
    "do_not_save": "Не сохранять запись",
    "get_csv": "Скачать мои данные как CSV",
    "get_plot": "Хочу график! 📈",
    "set_recommended_sleep": "Установить рекомендуемое время сна. 🛌",
    "toggle_weekly_report_on": "Включить еженедельный отчёт",
    "toggle_weekly_report_off": "Выключить еженедельный отчёт",
    "set_assistant_role": "Роль ассистента",
    "keep_current_role": "Оставить текущую роль",
    "enter_custom_role": "Введите свою роль",
    },
    
    Language.ENG.value: {
    "go_back": "Go back! 🔙",
    "settings": "⚙️",
    "track_mood": "Track mood",
    "help": "Help",
    "change_language": "🌐, Eng/Ru",
    "toggle_reminder": "Toggle bot reminders",
    "mood_data": "Mood analytics",
    "pick_emoji": "Pick an emoji",
    "accept": "Accept",
    "track_periods_on": "Track periods on",
    "track_periods_off": "Track periods off",
    "cancel": "Cancel",
    "do_not_save": "Do not save record",
    "get_csv": "Download my data as CSV",
    "get_plot": "I want a plot! 📈",
    "set_recommended_sleep": "Set recommended sleep time. 🛌",
    "toggle_weekly_report_on": "Enable weekly report",
    "toggle_weekly_report_off": "Disable weekly report",
    "set_assistant_role": "Your assistant role",
    "keep_current_role": "Keep current role",
    "enter_custom_role": "Enter custom role",
    }
}


def get_button_text(button_text: str, user: User) -> str:
    """Like for the get_msg_from_dict function, but for buttons."""
    return get_msg_from_dict(BUTTONS_TEXT_LANG, user, button_text)

def get_all_buttons_text(button_text: str) -> list[str]:
    langs = [lang.value for lang in Language]
    return [BUTTONS_TEXT_LANG[lang][button_text] for lang in langs]
    

def get_inline_keyboard_buttons_from_list(options: list[str], callback_group: str, picked_options: list[str] = list()) -> list[InlineKeyboardButton]:
    """Create a list of InlineKeyboardButtons from a list of options.
    Used for creating a checklist of options for the user to choose from."""
    keyboard_buttons = list()
    
    for option in options:
        if option in picked_options:
            keyboard_buttons.append([InlineKeyboardButton(text=f"{option} ✅",
                             callback_data=f"{callback_group}_{option}"
            )])
        else:
            keyboard_buttons.append([InlineKeyboardButton(text=option,
                             callback_data=f"{callback_group}_{option}"
            )])
            
    # TODO: Accept button language should be based on the user language
    accept_button = InlineKeyboardButton(text=BUTTONS_TEXT_LANG[Language.ENG.value]["accept"],
                                         callback_data=f"{callback_group}_accept"
    )
    keyboard_buttons.append([accept_button])
    return keyboard_buttons


def get_lang(user: User | None = None) -> str:
    if user is None:
        return Language.ENG.value
    return user.settings.language
    

def get_start_keyboard(user: User | None = None):
    
    language = get_lang(user)
    
    keyboard_buttons = [
        [
            KeyboardButton(text=BUTTONS_TEXT_LANG[language]["track_mood"]),
            KeyboardButton(text=BUTTONS_TEXT_LANG[language]["mood_data"]),

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
            KeyboardButton(text=BUTTONS_TEXT_LANG[language]["toggle_reminder"]),
            KeyboardButton(text=BUTTONS_TEXT_LANG[language]["set_recommended_sleep"]),
            KeyboardButton(text=BUTTONS_TEXT_LANG[language]["go_back"]),
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=keyboard_buttons,
        resize_keyboard=True,
        input_field_placeholder="ТЫК"
    )
    return keyboard

def get_inline_settings_keyboard(user: User | None = None) -> InlineKeyboardBuilder:
        
    if user is None:
        language = Language.ENG.value
    else:
        language = get_lang(user)
        
    inline_keyboard=[
        [
            InlineKeyboardButton(text=BUTTONS_TEXT_LANG[language]["change_language"],
                                callback_data="change_language")
        ],
        [
            InlineKeyboardButton(text=BUTTONS_TEXT_LANG[language]["set_recommended_sleep"],
                                callback_data="set_recommended_sleep"),
        ],
        [
            InlineKeyboardButton(text=BUTTONS_TEXT_LANG[language]["toggle_reminder"],
                                callback_data="toggle_reminder"),
        ],
        [
            InlineKeyboardButton(text=BUTTONS_TEXT_LANG[language]["set_assistant_role"],
                                 callback_data="set_assistant_role"),
        ]
    ]
    if user is not None:
        if user.settings.weekly_report_enabled:
            inline_keyboard.append([
                InlineKeyboardButton(text=BUTTONS_TEXT_LANG[language]["toggle_weekly_report_off"],
                                    callback_data="toggle_weekly_report_off"),
            ])
        else:
            inline_keyboard.append([
                InlineKeyboardButton(text=BUTTONS_TEXT_LANG[language]["toggle_weekly_report_on"],
                                    callback_data="toggle_weekly_report_on"),
            ])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return keyboard
        

class EmojiSet():
    """EmojiSet class is used to store a set of emojis for a specific mood or emotion.
    It is used to create a keyboard with emojis for the user to choose from.
    """
    def __init__(self,
                 emoji_set: list,
                 data_type_names: list[str] | None = None,
                 comment: dict | None=None) -> None:  # Dict with language keys and comments as values
                
        self.emoji_set = emoji_set
        self.comment = comment
        self.data_type_names = data_type_names
        
    def get_number_from_emoji(self, emoji: str):
        return self.emoji_set.index(emoji)
    
    def get_inline_keyboard_buttons(self, callback_group: str | None = None) -> list[InlineKeyboardButton]:
        
        if not callback_group:
            if self.data_type_names is None:
                raise ValueError("No data type names provided for the emoji set.")
            callback_group = self.data_type_names[0]
        
        keyboard_buttons = [
            InlineKeyboardButton(text=emoji,
                                 callback_data=f"{callback_group}_{self.get_number_from_emoji(emoji)}"
            )
            for emoji in self.emoji_set
        ]
        return keyboard_buttons
    
    def get_keyboard_buttons(self):
        
        keyboard_buttons = [
            [
                KeyboardButton(text=emoji)
                for emoji in self.emoji_set
            ]
        ]
        return keyboard_buttons
    
    def get_comment(self, language: str = Language.ENG.value):
        if self.comment is None:
            return ""
        elif language not in self.comment:
            return ""
        return self.comment[language]
    
    def get_keyboard_builder(self) -> InlineKeyboardBuilder:
        
        keyboard_buttons = self.get_inline_keyboard_buttons()
        builder = InlineKeyboardBuilder()
        for button in keyboard_buttons:
            builder.add(button)
        return builder

def find_emojis_in_string(string: str) -> list:
    """Find all emojis in a string."""
    return [char for char in string if char in emoji.EMOJI_DATA]


emotional_emoji_sets = {
    
    # For mood
    "mood" : EmojiSet(
        emoji_set = ['😭', '😢', '😟', '😐', '🙂', '😃', '😄'],
        data_type_names = ["mood"]
    ),
    
    # For horny level:
    "horny" : EmojiSet(
        emoji_set = ['😐', '🙂', '😏', '😍', '😈', '🔥'],
        data_type_names = ["horny"],
        comment={
            Language.ENG.value : """Explanation:
    😐 (Neutral): Level 1, least horny, neutral expression.
    🙂 (Slightly Interested): Level 2, slight interest.
    😏 (Suggestive): Level 3, suggestive, showing some intent.
    😍 (Very Interested): Level 4, eyes in love, clearly interested.
    😈 (Playful and Intense): Level 5, playful, with a mischievous intent.
    🔥 (On Fire): Level 6, most intense, full-on passion.""",
            Language.RU.value : """Объяснение:
    😐 (Нейтральное): Уровень 1, минимальный интерес, нейтральное выражение.
    🙂 (Слегка заинтересованное): Уровень 2, небольшой интерес.
    😏 (Намекающее): Уровень 3, намекающее, показывает некоторую заинтересованность.
    😍 (Очень заинтересованное): Уровень 4, влюблённые глаза, явный интерес.
    😈 (Игривое и интенсивное): Уровень 5, игривое, с озорным намерением.
    🔥 (В огне): Уровень 6, максимальная интенсивность, полная страсть.
    """
        }
    ),

    # For energy level:
    "energy" : EmojiSet(
        emoji_set = ['😴', '😪', '😌', '😊', '😀', '💥'],
        data_type_names = ["energy"],
        comment={
            Language.ENG.value : """Explanation:
    😴 (Exhausted): Level 1, lowest energy, ready to sleep.
    😪 (Sleepy): Level 2, very low energy, drowsy.
    😌 (Relaxed): Level 3, moderate energy, calm and at ease.
    😊 (Content): Level 4, good energy, feeling well.
    😀 (Happy): Level 5, high energy, cheerful and active.
    💥 (Explosive): Level 6, highest energy, bursting with enthusiasm.
    """,
            Language.RU.value : """Объяснение:
    😴 (Измученный): Уровень 1, самый низкий уровень энергии, готов ко сну.
    😪 (Сонный): Уровень 2, очень низкий уровень энергии, дремота.
    😌 (Расслабленный): Уровень 3, умеренный уровень энергии, спокойствие.
    😊 (Довольный): Уровень 4, хороший уровень энергии, ощущение благополучия.
    😀 (Счастливый): Уровень 5, высокий уровень энергии, бодрый и активный.
    💥 (Взрывной): Уровень 6, максимальный уровень энергии, переполнен энтузиазмом.
    """
        }
    ),
    # For anxiety level:
    "anxiety" : EmojiSet(
        emoji_set = ['😌', '😕', '😟', '😧', '😨', '😱'],
        data_type_names = ["anxiety"],
        comment={
            Language.ENG.value : """Explanation:
    😌 (Calm): Level 1, least anxious, relaxed and calm.
    😕 (Uneasy): Level 2, slight anxiety, unsure or uneasy.
    😟 (Worried): Level 3, moderate anxiety, concerned or worried.
    😧 (Distressed): Level 4, high anxiety, distressed or troubled.
    😨 (Afraid): Level 5, very high anxiety, feeling fear or panic.
    😱 (Terrified): Level 6, extreme anxiety, overwhelming fear or terror.
    """,
            Language.RU.value : """Объяснение:
    😌 (Спокойный): Уровень 1, минимальная тревожность, расслабленное и спокойное состояние.
    😕 (Неуверенный): Уровень 2, небольшая тревожность, неуверенность или беспокойство.
    😟 (Взволнованный): Уровень 3, умеренная тревожность, беспокойство или волнение.
    😧 (Огорчённый): Уровень 4, высокая тревожность, огорчение или волнение.
    😨 (Испуганный): Уровень 5, очень высокая тревожность, чувство страха или паники.
    😱 (Ужас): Уровень 6, крайне встревоженный.
    """
        }
    ),
}


