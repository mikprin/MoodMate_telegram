import redis
import os
import asyncio
import json
import time
from pydantic import BaseModel
from mood_mate_src.mate_logger import logger
from mood_mate_src.database_tools.mood_data import MoodRecord
from mood_mate_src.database_tools.users import User, UserSettings

REDIS_PORT = 16379

# I use MOOD_MATE_REDIS_HOST env variable to set the host
REDIS_HOST = os.getenv("MOOD_MATE_REDIS_HOST", "localhost")

USER_SESSION_DB = 0

USER_SESSION_PREFIX = "user_session_"

class UserSession:
    """In this class I will store the user session data in the Redis database.
    User session includes:
    - User object
    - User settings
    - Mood record while it is being created
    
    """
    user: User  # Contains the user object and user settings
    mood_record: MoodRecord | None  # Contains the mood record object
    last_update: int  # Contains the last update timestamp
    started_at: int  # Contains the session start timestamp
    last_command: str | None  # Contains the last command

class RedisDB:
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, db=0):
        self.client = redis.Redis(host=host, port=port, db=0)

    def set(self, key: str, value: str):
        self.client.set(key, value)

    def get(self, key: str) -> str:
        return self.client.get(key)

    def delete(self, key: str):
        self.client.delete(key)

    def set_json(self, key: str, value: BaseModel):
        self.client.set(key, value.json())

    def get_json(self, key: str, model: BaseModel) -> BaseModel:
        data = self.client.get(key)
        if data is None:
            return None
        return model.parse_raw(data)

    def delete_json(self, key: str):
        self.client.delete(key)


def create_user_session(user: User) -> UserSession:
    """Create a user session object from a user object.
    Args:
        user (User): User object
    Returns:
        UserSession: User session object
    """
    session = UserSession(
        user=user,
        mood_record=None,
        last_update=int(time.time()),
        started_at=int(time.time()),
        last_command=None
    )
    _redis = RedisDB()
    _redis.set_json(USER_SESSION_PREFIX + str(user.user_id), session)


def get_user_session(user_id: int) -> UserSession:
    """Get the user session object from the Redis database.
    Args:
        user_id (int): User ID
    Returns:
        UserSession: User session object
    """
    _redis = RedisDB()
    return _redis.get_json(USER_SESSION_PREFIX + str(user_id), UserSession)

async def redis_watchdog_task():
    while True:
        await asyncio.sleep(100)

