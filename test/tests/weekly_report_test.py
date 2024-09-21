from mood_mate_src.analytics.user_analytics import get_user_report_prompt_from_records
from mood_mate_src.database_tools.users import User, UserSettings
from mood_mate_src.database_tools.mood_data import MoodRecord, MoodData
from datetime import datetime

def test_get_user_report_prompt_from_records():
    user = User(
        user_id=372682204,
        chat_id=1,
        settings=UserSettings(**{
            "name": "Test User",
            "created_at": int(datetime.now().timestamp()),
            "username": "test_user",
            "language": "en",
        }),
    )
    records = [
        MoodRecord(user_id=372682204, date='2024.08.21', created_at=1724265777, data=MoodData(mood=None, sleep=5.0, horny=2, exercise=5.0, dopings=[], energy=2, anxiety=2, period=None, note=None, extra=None, future_in_years=0.1)),
        MoodRecord(user_id=372682204, date='2024.08.21', created_at=1724266364, data=MoodData(mood=None, sleep=0.0, horny=2, exercise=0.0, dopings=[], energy=2, anxiety=2, period=None, note='FROM', extra=None, future_in_years=1.0)),
        MoodRecord(user_id=372682204, date='2024.08.21', created_at=1724266797, data=MoodData(mood=3, sleep=6.0, horny=2, exercise=5.0, dopings=['Pills?: 💊', 'Mushrooms: 🍄', 'Weed: 🌿'], energy=2, anxiety=2, period=None, note=None, extra=None, future_in_years=1.0)),
        MoodRecord(user_id=372682204, date='2024.08.23', created_at=1724440130, data=MoodData(mood=3, sleep=2.0, horny=1, exercise=19.0, dopings=[], energy=2, anxiety=3, period=None, note=None, extra=None, future_in_years=1.0)),
        MoodRecord(user_id=372682204, date='2024.08.25', created_at=1724587113, data=MoodData(mood=3, sleep=8.0, horny=1, exercise=1.0, dopings=[], energy=2, anxiety=2, period=None, note=None, extra=None, future_in_years=1.0))
    ]
    
    prompt = get_user_report_prompt_from_records(records, user)
    # assert prompt == expected_prompt
    
    assert "MoodRecord(user_id=372682204, date='2024.08.21', created_at=1724266364, data=MoodData(mood=None, sleep=0.0, horny=2, exercise=0.0, dopings=[], energy=2, anxiety=2, period=None, note='FROM', extra=None, future_in_years=1.0))," in prompt
    assert "Here is the description of the metrics used and how they are presented to the user:" in prompt
    
    user = User(
        user_id=372682204,
        chat_id=1,
        settings=UserSettings(**{
            "name": "Test User",
            "created_at": int(datetime.now().timestamp()),
            "username": "test_user",
            "language": "ru",
        }),
    )
    
    prompt = get_user_report_prompt_from_records(records, user)
    assert "Answer in Russian language!" in prompt