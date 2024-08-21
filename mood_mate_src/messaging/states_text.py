from mood_mate_src.database_tools.users import Language, User
from mood_mate_src.keyboard import BUTTONS_TEXT_LANG



def get_state_msg(state_name: str, user: User) -> str:
    """
    Get the message for the state by its name and language
    """
    
    try:
        msg = mood_record_states_messages[user.settings.language][state_name]
    except KeyError:
        return f"Message for state {state_name} not found in the language {user.settings.language}"
    return msg

mood_record_states_messages = {
    Language.RU.value: {
        "greetings": "Привет! Я MoodMate, бот для отслеживания настроения.\nВажно следить за своим настроением и эмоциями, чтобы понимать, как мы себя чувствуем и выявлять паттерны, которые могут влиять на наше психическое здоровье. Этот проект призван помочь людям отслеживать свое настроение и эмоции, предоставляя им простой и удобный инструмент, с помощью которого они могут записывать свое настроение и эмоции ежедневно. Инструмент предоставит пользователям сводку их настроения со временем и предложит способы улучшить настроение на основе их ответов."
        f"Давай начнем! Нажми на кнопку {BUTTONS_TEXT_LANG[Language.RU.value]['track_mood']} чтобы сделать первую запись."
        "Когда у тебя будет несколько записей, ты сможешь посмотреть свою историю настроения и статистику! 📊 Жду тебя завтра!",
        "mood": "Какое у тебя сейчас настроение?",
        "sleep": "Сколько часов ты спал(а) сегодня? Введите число сообщением. Разделенное точкой если хочется не целое.",
        "horny": "Какой у тебя субьективный уровень возбуждения?",
        "exercise": "Примерно сколько часов ты занимался(ась) спортом? Введите число разделенное точкой если хочется не целое",
        "dopings": "Какие допинги ты употребил(а) сегодня? Отметь по кнопкам! Если нужных нет в списке, введи их текстом через запятую, в конце нажми кнопку продолжить",
        "lang_changed": "Язык изменен на русский",
        "toggle_reminder_off": "Напоминания теперь отключены.\nНапоминания можно включить обратно в настройках. Помни что напоминания помогают не забывать делать записи о настроении!",
        "toggle_reminder_on": "Напоминания теперь включены.\nЭто грамотное решение! Помни что напоминания помогают не забывать делать записи о настроении!",
        "emoji_explained": "Выберите подходящую пиктограмму, которая наилучшим образом отражает ваше настроение. Если вдруг ошибся, нажми кнопку начать заново",
        "anxiety": "Какой у тебя уровень тревоги?",
        "energy": "Какой у тебя уровень энергии?",
        "future_in_years": "Насколько определенно ты видишь свое будущее? Укажи примерно в годах.",
        "note": f"Есть что добавить? Напиши заметку, если хочешь. Если нет, просто нажми кнопку продолжить и я сохраню запись. Если не хочешь сохранять ее, то нажми  {BUTTONS_TEXT_LANG[Language.RU.value]['do_not_save']}",
        "invalid_number_input": "Некорректный ввод. Введите число, разделенное точкой, если хотите ввести не целое число",
        "record_saved": "Я сохранил твою запись 🎉! Спасибо за то, что делишься своим настроением! 📝",
        "record_not_saved": "Я не сохранил твою запись 🚫!",
    },
    
    Language.ENG.value: {
        "greetings": "Hello! I am MoodMate, your personal mood tracker.\nIt is important to keep track of our mood and emotions to understand how we are feeling and to identify patterns that may be affecting our mental health. This project aims to help people track their mood and emotions by providing them with a simple and easy-to-use tool that they can use to record their mood and emotions on a daily basis. The tool will provide users with a summary of their mood over time and suggest ways to improve their mood based on their responses."
        f"Let's start! Press the {BUTTONS_TEXT_LANG[Language.ENG.value]['track_mood']} button to make your first record."
        "When you have several records, you can view your mood history and statistics! 📊 See you tomorrow!",
        "mood": "How are you feeling right now?",
        "sleep": "How many hours did you sleep today? Enter a number separated by a dot if you want a non-integer",
        "horny": "What is your subjective level of sexual arousal?",
        "exercise": "Approximately how many hours did you exercise? Enter a number separated by a dot if you want a non-integer",
        "dopings": "What doping did you take today? Check the buttons! If the necessary ones are not in the list, enter them in text separated by commas, at the end press the continue button",
        "lang_changed": "Language changed to English",
        "record_reminder": "Hello! I want to remind you to make a record of your mood! Press the button to start",
        "toggle_reminder_off": "Reminders are now disabled.\nYou can enable reminders back in the settings. Remember that reminders help you not to forget to make mood records!",
        "toggle_reminder_on": "Reminders are now enabled.\nThis is a smart decision! Remember that reminders help you not to forget to make mood records!",
        "emoji_explained": "Select the appropriate emoji that best reflects your mood. If you made a mistake, press the start over button",
        "anxiety": "What is your level of anxiety?",
        "energy": "What is your level of energy?",
        "future_in_years": "Насколько определенно ты видишь свое будущее? Укажи примерно в годах.",
        "note": f"Anything to add? Write a note if you want. If not, just press the {BUTTONS_TEXT_LANG[Language.ENG.value]['do_not_save']} button",
        "invalid_number_input": "Invalid input. Enter a number separated by a dot if you want a non-integer",
        "record_saved": "I saved your record 🎉! Thank you for sharing your mood! 📝",
        "record_not_saved": "I didn't save your record 🚫!",
    },
    
}

reminder_notification_text = {
    Language.RU.value: [
        "Привет! Я хочу напомнить тебе сделать запись о своем настроении! Нажми на кнопку, чтобы начать.",
        "Не забудь поделиться своим настроением сегодня! Жми на кнопку и записывай!",
        "Время записать своё настроение! Нажми на кнопку и расскажи, как прошел твой день.",
        "Запиши своё настроение прямо сейчас! Нажми на кнопку, чтобы начать.",
        "Как ты сегодня? Не забудь сделать запись о настроении! Жми на кнопку."
    ],
    Language.ENG.value: [
        "Hello! I want to remind you to make a record of your mood! Press the button to start.",
        "Don't forget to share your mood today! Hit the button and record it!",
        "It's time to log your mood! Tap the button and tell us how your day went.",
        "Record your mood right now! Press the button to begin.",
        "How are you feeling today? Don’t forget to log your mood! Press the button."
    ],
}
