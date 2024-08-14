from aiogram.fsm.state import StatesGroup, State
from mood_mate_src.database_tools.mood_data import MoodData

class AddRecord(StatesGroup):
    """States implementing each field in MoodData model"""
    mood = State()
    sleep = State()
    horny = State()
    exercise = State()
    doping = State()
    energy = State()
    anxiety = State()
    period = State()
    note = State()
