import pandas as pd
import pytest

from mood_mate_src.analytics.convert import (convert_records_to_pandas,
                                             flatten_record)
from mood_mate_src.database_tools.mood_data import MoodData, MoodRecord


@pytest.fixture
def get_records():
    data1 = MoodData(
        mood=1,
        sleep=2.0,
        horny=3,
        exercise=4.0,
        dopings=["doping1", "doping2"],
        energy=5,
        anxiety=6,
        period=True,
        note="note",
        extra={"key": "value"},
        future_in_years=7.0,
    )
    data2 = MoodData(
        mood=2,
        sleep=3.0,
        horny=4,
        exercise=5.0,
        dopings=["doping3", "doping4"],
        energy=6,
        anxiety=7,
        period=False,
        note="note2",
        extra={"key2": "value2"},
        future_in_years=8.0,
    )
    data3 = MoodData(
        mood=3,
        sleep=4.0,
        horny=5,
        exercise=6.0,
        dopings=[],
        energy=7,
        anxiety=8,
        period=True,
        note="note3",
        future_in_years=9.0,
    )
    record1 = MoodRecord(
        user_id=1, date="2022-01-01", created_at=1640995200, data=data1
    )
    record2 = MoodRecord(
        user_id=2, date="2022-01-02", created_at=1641081600, data=data2
    )
    record3 = MoodRecord(
        user_id=3, date="2022-01-03", created_at=1641168000, data=data3
    )
    return [record1, record2, record3]


def test_flatten_record():
    data = MoodData(
        mood=1,
        sleep=2.0,
        horny=3,
        exercise=4.0,
        dopings=["doping1", "doping2"],
        energy=5,
        anxiety=6,
        period=True,
        note="note",
        extra={"key": "value"},
        future_in_years=7.0,
    )
    record = MoodRecord(user_id=1, date="2022-01-01", created_at=1640995200, data=data)

    result = flatten_record(record)

    assert result == {
        "user_id": 1,
        "date": "2022-01-01",
        "created_at": 1640995200,
        "mood": 1,
        "sleep": 2.0,
        "horny": 3,
        "exercise": 4.0,
        "dopings": ["doping1", "doping2"],
        "energy": 5,
        "anxiety": 6,
        "period": True,
        "note": "note",
        "extra": {"key": "value"},
        "future_in_years": 7.0,
    }


def test_convert_records_to_pandas(get_records):

    records = get_records

    result = convert_records_to_pandas(records[:2])

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    expected = pd.DataFrame(
        [
            {
                "user_id": 1,
                "date": "2022-01-01",
                "created_at": 1640995200,
                "mood": 1,
                "sleep": 2.0,
                "horny": 3,
                "exercise": 4.0,
                "dopings": ["doping1", "doping2"],
                "energy": 5,
                "anxiety": 6,
                "period": True,
                "note": "note",
                "extra": {"key": "value"},
                "future_in_years": 7.0,
            },
            {
                "user_id": 2,
                "date": "2022-01-02",
                "created_at": 1641081600,
                "mood": 2,
                "sleep": 3.0,
                "horny": 4,
                "exercise": 5.0,
                "dopings": ["doping3", "doping4"],
                "energy": 6,
                "anxiety": 7,
                "period": False,
                "note": "note2",
                "extra": {"key2": "value2"},
                "future_in_years": 8.0,
            },
        ]
    )

    result = convert_records_to_pandas(get_records, drop_na_for=["dopings"])
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
