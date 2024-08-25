import pandas as pd
from mood_mate_src.database_tools.mood_data import MoodRecord, MoodData
from mood_mate_src.analytics.convert import flatten_record, convert_records_to_pandas


def test_flatten_record():
    data = MoodData(mood=1, sleep=2.0, horny=3, exercise=4.0, dopings=["doping1", "doping2"], energy=5, anxiety=6, period=True, note="note", extra={"key": "value"}, future_in_years=7.0)
    record = MoodRecord(user_id=1, date="2022-01-01", created_at=1640995200, data=data)
    
    result = flatten_record(record)
    
    assert result == {
        'user_id': 1,
        'date': '2022-01-01',
        'created_at': 1640995200,
        'mood': 1,
        'sleep': 2.0,
        'horny': 3,
        'exercise': 4.0,
        'dopings': ["doping1", "doping2"],
        'energy': 5,
        'anxiety': 6,
        'period': True,
        'note': "note",
        'extra': {"key": "value"},
        'future_in_years': 7.0
    }
    
def test_convert_records_to_pandas():
    data1 = MoodData(mood=1, sleep=2.0, horny=3, exercise=4.0, dopings=["doping1", "doping2"], energy=5, anxiety=6, period=True, note="note", extra={"key": "value"}, future_in_years=7.0)
    data2 = MoodData(mood=2, sleep=3.0, horny=4, exercise=5.0, dopings=["doping3", "doping4"], energy=6, anxiety=7, period=False, note="note2", extra={"key2": "value2"}, future_in_years=8.0)
    record1 = MoodRecord(user_id=1, date="2022-01-01", created_at=1640995200, data=data1)
    record2 = MoodRecord(user_id=2, date="2022-01-02", created_at=1641081600, data=data2)
    
    result = convert_records_to_pandas([record1, record2])
    
    expected = pd.DataFrame([
        {
            'user_id': 1,
            'date': '2022-01-01',
            'created_at': 1640995200,
            'mood': 1,
            'sleep': 2.0,
            'horny': 3,
            'exercise': 4.0,
            'dopings': ["doping1", "doping2"],
            'energy': 5,
            'anxiety': 6,
            'period': True,
            'note': "note",
            'extra': {"key": "value"},
            'future_in_years': 7.0
        },
        {
            'user_id': 2,
            'date': '2022-01-02',
            'created_at': 1641081600,
            'mood': 2,
            'sleep': 3.0,
            'horny': 4,
            'exercise': 5.0,
            'dopings': ["doping3", "doping4"],
            'energy': 6,
            'anxiety': 7,
            'period': False,
            'note': "note2",
            'extra': {"key2": "value2"},
            'future_in_years': 8.0
        }
    ])