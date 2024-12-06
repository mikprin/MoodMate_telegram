import json
import os
from datetime import datetime, timedelta

from pydantic import BaseModel

from mood_mate_src.database_tools.locks import data_db_lock
from mood_mate_src.database_tools.query import (DB_PATH, execute_query,
                                                execute_query_with_lock)

DATA_TABLE = "users_data"

class MoodData(BaseModel):
    """Data json structure for mood records:
    - `mood` (int): mood of the user
    - `sleep` (float): hours of sleep
    - `energy` (int): energy level
    - `anxiety` (int): anxiety level
    - `exercise` (float): hours of exercise
    - `dopings` (str): list of doping
    - `horny` (int): horny level
    - `period` (str): period  (optional)
    - `note` (str): note from the user
    - `extra` (json): extra data
    """
    mood: int | None = None
    sleep: float | None = None
    horny: int | None = None
    exercise: float | None = None
    dopings: list = list()
    energy: int | None = None
    anxiety: int | None = None
    period: bool | None = None
    note: str | None = None
    extra: dict | None = None
    future_in_years: float | None = None

    class ConfigDict:
        orm_mode = True

class MoodRecord(BaseModel):
    """Root record object for mood records. Prototype for the database:
    (
    user_id INTEGER,
    date DATE NOT NULL,data
    created_at INTEGER NOT NULL,
    data JSON NOT NULL)
    """
    user_id: int
    date: str
    created_at: int
    data: MoodData

    class ConfigDict:
        orm_mode = True

async def add_mood_record_to_db(record: MoodRecord):
    """Add a mood record to the database.
    This function is async and will be executed with a lock.

    Args:
        record (MoodRecord): _description_
    """
    record_data_json = json.dumps(record.data.model_dump())

    await execute_query_with_lock(
        db_path=DB_PATH,
        db_lock=data_db_lock,
        query=f'''
        INSERT INTO {DATA_TABLE} (user_id, date, created_at, data)
        VALUES (?, ?, ?, ?)
        ''',
        params=(record.user_id, record.date, record.created_at, record_data_json))


def get_mood_records_from_db(user_id: int) -> list[MoodRecord]:
    """Get all mood records for a user from the database.

    Args:
        user_id (int): user id
    Returns:
        list[MoodRecord]: list of mood records
    """
    records = []
    query = f'''
    SELECT * FROM {DATA_TABLE}
    WHERE user_id = ?
    '''
    rows = execute_query(
        db_path=DB_PATH,
        query=query,
        params=(user_id,),
        return_result=True,
        dict_result=False)

    if rows is None:
        return records
    for row in rows:
        record = MoodRecord(
            user_id=row[0],
            date=row[1],
            created_at=row[2],
            data=MoodData(**json.loads(row[3]))
        )
        records.append(record)
    return records


def get_user_records_for_past_time(user_id: int, time_period: int) -> list[MoodRecord]:
    """Get all mood records for a user from the database for the past time period.

    Args:
        time_period (timedelta): Time period to filter records (e.g., last week, last month).
        user_id (int): User ID

    Returns:
        list[MoodRecord]: List of mood records for the user within the specified time period.
    """
    records = []

    # Calculate the starting date (current time - time_period)
    start_date = int(datetime.now().timestamp()) - time_period

    # Cast start_date to int


    query = f'''
    SELECT * FROM {DATA_TABLE}
    WHERE user_id = ? AND created_at >= ?
    '''
    rows = execute_query(
        db_path=DB_PATH,
        query=query,
        params=(user_id, start_date),  # Passing the start date as a parameter
        return_result=True,
        dict_result=False,
    )

    if rows is None:
        return records

    for row in rows:
        record = MoodRecord(
            user_id=row[0],
            date=row[1],
            created_at=row[2],
            data=MoodData(**json.loads(row[3]))
        )
        records.append(record)

    return records


def get_all_records_for_past_time(time_period: int) -> list[MoodRecord]:
    """Get all mood records from the database for the past time period.

    Args:
        time_period (timedelta): Time period to filter records (e.g., last week, last month).

    Returns:
        list[MoodRecord]: List of mood records within the specified time period.
    """
    records = []

    # Calculate the starting date (current time - time_period)
    start_date = int(datetime.now().timestamp()) - time_period

    query = f'''
    SELECT * FROM {DATA_TABLE}
    WHERE created_at >= ?
    '''
    rows = execute_query(
        db_path=DB_PATH,
        query=query,
        params=(start_date,),  # Passing the start date as a parameter
        return_result=True,
        dict_result=False,
    )

    if rows is None:
        return records

    for row in rows:
        record = MoodRecord(
            user_id=row[0],
            date=row[1],
            created_at=row[2],
            data=MoodData(**json.loads(row[3]))
        )
        records.append(record)

    return records
