from mood_mate_src.database_tools.users import Language, User
from mood_mate_src.keyboard import BUTTONS_TEXT_LANG, get_button_text
from mood_mate_src.messaging.lang_support import get_msg_from_dict


def get_state_msg(state_name: str, user: User) -> str:
    """
    Get the message for the state by its name and language
    """
    return get_msg_from_dict(mood_record_states_messages, user, state_name)

mood_record_states_messages = {
    Language.RU.value: {
        "greetings": "Привет! Я MoodMate, бот для отслеживания настроения.\nВажно следить за своим настроением и эмоциями, чтобы понимать, как мы себя чувствуем и выявлять паттерны, которые могут влиять на наше психологическое здоровье. Этот проект призван помочь людям отслеживать свое настроение и эмоции, предоставляя им простой и удобный инструмент, с помощью которого они могут записывать свое настроение и эмоции ежедневно. С появлением данных вам будут предложены умные предложения по тому какие действия можно и нужно предпринять.\n"
        f"Давай начнем! Нажми на кнопку {BUTTONS_TEXT_LANG[Language.RU.value]['track_mood']} чтобы сделать первую запись.\n"
        "Когда у тебя будет несколько записей, ты сможешь посмотреть свою историю настроения и статистику! 📊 Жду тебя завтра!"
        "Есть вопросы? Нажми на кнопку помощь! Там можно оставить обратную связь и я свяжусь с вами!",
        "settings": f"Добро пожаловать в настройки! Здесь ты можешь изменить язык бота и включить/отключить напоминания о записи настроения. Нажми на кнопку {BUTTONS_TEXT_LANG[Language.RU.value]['change_language']}, чтобы изменить язык бота.",
        "mood": "Какое у тебя сейчас настроение?",
        "sleep": "Сколько часов ты спал(а) сегодня? Введите число сообщением. Разделенное точкой если хочется не целое.",
        "horny": "Какой у тебя субъективный уровень возбуждения?",
        "exercise": "Примерно сколько часов ты занимался(ась) спортом? Введите число разделенное точкой если хочется не целое.\nЕсли еще не тренировался но планируешь, ставь 0 и сделай еще одну запись о настроении после тренировки! Я учту это в статистике. Твои усилия будут записаны!",
        "dopings": "Какие допинги ты употребил(а) сегодня? Отметь по кнопкам! Если нужных нет в списке, введи их текстом через запятую, в конце нажми кнопку продолжить",
        "lang_changed": "Язык изменен на русский",
        "toggle_reminder_off": "Напоминания теперь отключены.\nНапоминания можно включить обратно в настройках. Помни что напоминания помогают не забывать делать записи о настроении!",
        "toggle_reminder_on": "Напоминания теперь включены.\nЭто грамотное решение! Помни что напоминания помогают не забывать делать записи о настроении!",
        "emoji_explained": "Выберите подходящую пиктограмму, которая наилучшим образом отражает ваше настроение. Если вдруг ошибся, нажми правильную пиктограмму снова",
        "anxiety": "Какой у тебя уровень тревоги?",
        "energy": "Какой у тебя уровень энергии?",
        "future_in_years": "Насколько определенно ты видишь свое будущее? Укажи примерно в годах.",
        "note": f"Есть что добавить? Напиши заметку, если хочешь 📝. Если нет, просто нажми кнопку продолжить и я сохраню запись. Если не хочешь сохранять ее, то нажми  {BUTTONS_TEXT_LANG[Language.RU.value]['do_not_save']}",
        "invalid_number_input": "Некорректный ввод. Введите число, разделенное точкой, если хотите ввести не целое число",
        "record_saved": "Я сохранил твою запись 🎉! Спасибо за то, что делишься своим настроением! 📝",
        "record_not_saved": "Я не сохранил твою запись 🚫!",
        "mood_analytics": "Здесь вы можете посмотреть свою статистику настроения и эмоций.",
        "not_enough_records": "У вас недостаточно записей для аналитики. Сделайте еще записей и попробуйте снова!",
        "recommended_sleep": "Сколько часов тебе рекомендуется спать в среднем? Введите число сообщением. Разделенное точкой если хочется не целое. Используй 0 чтобы установить None",
        "recommended_sleep_set": "Рекомендуемое время сна установлено",
        "weekly_report_enabled_on": "Еженедельный отчет включен. Теперь каждую неделю вам будет приходить отчет о вашем настроении и эмоциях.",
        "weekly_report_enabled_off": "Еженедельный отчет отключен. Теперь вам не будет приходить отчет о вашем настроении и эмоциях.",
        "lack_of_records_for_report": "Вам бы сейчас пришел еженедельный отчет, но у вас недостаточно записей для аналитики. Сделайте еще записей и будет веселый отчет в следующий раз!",
        "toggle_weekly_report_enabled_on": "Еженедельный отчет включен. Теперь каждую неделю вам будет приходить отчет о вашем настроении и эмоциях.",
        "toggle_weekly_report_enabled_off": "Еженедельный отчет отключен. Теперь вам не будет приходить отчет о вашем настроении и эмоциях.",
        "choose_assistant_role": "Текущая роль ассистента: {}. Если хотите его сменить, пожалуйста, выбери роль ассистента из предложенных или нажми 'Ввести свою роль'.",
        "enter_custom_role_prompt": "Пожалуйста, введи свою роль для ассистента.",
        "invalid_custom_role": "Введено некорректное название роли. Попробуйте снова.",
        "role_set": "Роль {} установлена как ваша роль ассистента.",
        "role_unchanged": "Роль ассистента не изменена. Текущая роль: {}",
        "choose_ai_model": "Пожалуйста, выберите предпочитаемую вами модель ИИ:",
        "ai_model_set": "Модель ИИ установлена на {}. ",
    },

    Language.ENG.value: {
        "greetings": "Hello! I am MoodMate, your personal mood tracker.\nIt is important to keep track of our mood and emotions to understand how we are feeling and to identify patterns that may be affecting our mental health. This project aims to help people track their mood and emotions by providing them with a simple and easy-to-use tool that they can use to record their mood and emotions on a daily basis. With the appearance of data, you will be offered smart suggestions on what actions can and should be taken.\n"
        f"Let's start! Press the {BUTTONS_TEXT_LANG[Language.ENG.value]['track_mood']} button to make your first record."
        "When you have several records, you can view your mood history and statistics! 📊 See you tomorrow!"
        "Have questions? Press the help button! You can leave feedback there and I will contact you!",
        "settings": f"Welcome to the settings! Here you can change the bot's language and enable/disable mood record reminders. Press the {BUTTONS_TEXT_LANG[Language.ENG.value]['change_language']} button to change the bot's language.",
        "mood": "How are you feeling right now?",
        "sleep": "How many hours did you sleep today? Enter a number separated by a dot if you want a non-integer",
        "horny": "What is your subjective level of sexual arousal?",
        "exercise": "Approximately how many hours did you exercise? Enter a number separated by a dot if you want a non-integer.\nIf you haven't exercised yet but plan to, put 0 and make another mood record after the workout! I will take this into account in the statistics. Your efforts will be recorded!",
        "dopings": "What doping did you take today? Check the buttons! If the necessary ones are not in the list, enter them in text separated by commas, at the end press the continue button",
        "lang_changed": "Language changed to English",
        "record_reminder": "Hello! I want to remind you to make a record of your mood! Press the button to start",
        "toggle_reminder_off": "Reminders are now disabled.\nYou can enable reminders back in the settings. Remember that reminders help you not to forget to make mood records!",
        "toggle_reminder_on": "Reminders are now enabled.\nThis is a smart decision! Remember that reminders help you not to forget to make mood records!",
        "emoji_explained": "Select the appropriate emoji that best reflects your mood. If you made a mistake, press the correct again.",
        "anxiety": "What is your level of anxiety?",
        "energy": "What is your level of energy?",
        "future_in_years": "How certain do you see your future? Specify approximately in years.",
        "note": f"Anything to add? Write a note if you want 📝. If not, just press the {BUTTONS_TEXT_LANG[Language.ENG.value]['do_not_save']} button",
        "invalid_number_input": "Invalid input. Enter a number separated by a dot if you want a non-integer",
        "record_saved": "I saved your record 🎉! Thank you for sharing your mood! 📝",
        "record_not_saved": "I didn't save your record 🚫!",
        "mood_analytics": "Here you can view your mood and emotions statistics.",
        "not_enough_records": "You don't have enough records for analytics. Make more records and try again!",
        "recommended_sleep": "How many hours are you recommended to sleep on average? Enter a number separated by a dot if you want a non-integer. Use 0 to set it to None",
        "recommended_sleep_set": "The recommended sleep time is set",
        "weekly_report_enabled_on": "Weekly report enabled. Now you will receive a report on your mood and emotions every week.",
        "weekly_report_enabled_off": "Weekly report disabled. Now you will not receive a report on your mood and emotions.",
        "lack_of_records_for_report": "You would have received a weekly report now, but you don't have enough records for analytics. Make more records and you will have a fun report next week!",
        "toggle_weekly_report_enabled_on": "Weekly report enabled. Now you will receive a report on your mood and emotions every week.",
        "toggle_weekly_report_enabled_off": "Weekly report disabled. Now you will not receive a report on your mood and emotions.",
        "choose_assistant_role": "Current assistant role: {}. If you want to change it, please select an assistant role from the list or press 'Enter your role'.",
        "enter_custom_role_prompt": "Please enter your role for the assistant.",
        "invalid_custom_role": "Invalid role name entered. Try again.",
        "role_set": "The role {} is set as your assistant role.",
        "role_unchanged": "The assistant role has not been changed. Current role: {}",
        "choose_ai_model": "Please select the AI model you prefer:",
        "ai_model_set": "AI model set to {}.",
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
