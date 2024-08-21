from mood_mate_src.database_tools.mood_data import MoodRecord, MoodData


def test_create_record():
    
    data = MoodData()
    record = MoodRecord(user_id=1, date="2022-01-01", created_at=1640995200, data=data)
    
    assert record.user_id == 1
    assert record.date == "2022-01-01"
    assert record.created_at == 1640995200
    assert record.data == data