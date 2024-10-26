from aiogram.fsm.state import StatesGroup, State
from mood_mate_src.database_tools.mood_data import MoodData

class AddRecord(StatesGroup):
    """States implementing each field in MoodData model"""
    mood = State()
    sleep = State()
    energy = State()
    anxiety = State()
    exercise = State()
    dopings = State()
    horny = State()
    future_in_years = State()
    period = State()
    note = State()
    extra = State()


class SettingsStates(StatesGroup):
    """States implementing each field in UserSettings model"""
    recommended_sleep = State()
    assistant_role = State()
    enter_custom_role = State()