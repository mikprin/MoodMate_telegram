from mood_mate_src.database_tools.users import Language
from mood_mate_src.keyboard import BUTTONS_TEXT_LANG

mood_record_states_messages = {
    Language.RU.value: {
        "greetings": "Привет! Я MoodMate, бот для отслеживания настроения."
        f"Давай начнем! Нажми на кнопку {BUTTONS_TEXT_LANG[Language.RU.value]['track_mood']} чтобы сделать первую запись."
        "Когда у тебя будет несколько записей, ты сможешь посмотреть свою историю настроения и статистику! 📊 Жду тебя завтра!",
        "mood": "Какое у тебя сейчас настроение?",
        "sleep": "Сколько часов ты спал(а) сегодня?",
        "horny": "Какой у тебя субьективный уровень возбуждения?",
        "exercise": "Примерно сколько часов ты занимался(ась) спортом? Введите число разделенное точкой если хочется не целое",
        "doping": "Какие допинги ты употребил(а) сегодня? Отметь по кнопкам! Если нужных нет в списке, введи их текстом через запятую, в конце нажми кнопку продолжить",
        "lang_changed": "Язык изменен на русский",
    },
    
    Language.ENG.value: {
        "greetings": "Hello! I am MoodMate, your personal mood tracker."
        f"Let's start! Press the {BUTTONS_TEXT_LANG[Language.ENG.value]['track_mood']} button to make your first record."
        "When you have several records, you can view your mood history and statistics! 📊 See you tomorrow!",
        "mood": "How are you feeling right now?",
        "sleep": "How many hours did you sleep today?",
        "horny": "What is your subjective level of sexual arousal?",
        "exercise": "Approximately how many hours did you exercise? Enter a number separated by a dot if you want a non-integer",
        "doping": "What doping did you take today? Check the buttons! If the necessary ones are not in the list, enter them in text separated by commas, at the end press the continue button",
        "lang_changed": "Language changed to English",
    },
    
}