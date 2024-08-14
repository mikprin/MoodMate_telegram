import os
import json
from pydantic import BaseModel
from mood_mate_src.database_tools.query import execute_query_with_lock, DB_PATH
from mood_mate_src.database_tools.locks import data_db_lock

DATA_TABLE = "users_data"

class MoodData(BaseModel):
    """Data json structure for mood records:
    - `mood` (int): mood of the user
    - `sleep` (int): hours of sleep
    - `horny` (int): horny level
    - `exercise` (int): hours of exercise
    - `doping` (str): list of doping
    - `energy` (int): energy level
    - `anxiety` (int): anxiety level
    - `period` (str): period  (optional)
    - `note` (str): note from the user
    - `extra` (json): extra data
    """
    mood: int | None = None
    sleep: int | None = None
    horny: int | None = None
    exercise: int | None = None
    doping: list = list()
    energy: int | None = None
    anxiety: int | None = None
    period: bool | None = None
    note: str | None = None
    extra: dict | None = None
    
    class ConfigDict:
        orm_mode = True
    
class MoodRecord(BaseModel):
    """Root record object for mood records. Prototype for the database:
    (
    user_id INTEGER,
    date DATE NOT NULL,
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