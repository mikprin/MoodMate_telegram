import asyncio
import json
import os
import time

import redis
from pydantic import BaseModel

from mood_mate_src.database_tools.mood_data import MoodData, MoodRecord
from mood_mate_src.database_tools.users import User, UserSettings
from mood_mate_src.mate_logger import logger

REDIS_PORT = 16379

# I use MOOD_MATE_REDIS_HOST env variable to set the host
REDIS_HOST = os.getenv("MOOD_MATE_REDIS_HOST", "localhost")

USER_SESSION_DB = 0

USER_SESSION_PREFIX = "user_session_"

logger.info(f"Connecting to Redis database at {REDIS_HOST}:{REDIS_PORT} at db {USER_SESSION_DB}")

class UserSession(BaseModel):
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


class RedisDB:
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, db=0):
        self.client = redis.Redis(host=host, port=port, db=db)

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
        mood_record=MoodRecord(
                user_id = user.user_id,
                date = time.strftime("%Y.%m.%d"),
                created_at = int(time.time()),
                data = MoodData(),
        ),
        last_update=int(time.time()),
        started_at=int(time.time()),
    )
    _redis = RedisDB()
    _redis.set_json(USER_SESSION_PREFIX + str(user.user_id), session)
    return session


def save_user_session(session: UserSession):
    """Save the user session object to the Redis database.
    Args:
        session (UserSession): User session object
    """
    _redis = RedisDB()
    session.last_update = int(time.time())
    _redis.set_json(USER_SESSION_PREFIX + str(session.user.user_id), session)


def get_user_session(user_id: int) -> UserSession:
    """Get the user session object from the Redis database.
    Args:
        user_id (int): User ID
    Returns:
        UserSession: User session object
    """
    _redis = RedisDB()
    session = _redis.get_json(USER_SESSION_PREFIX + str(user_id), UserSession)
    if not session:
        return create_user_session(User(user_id=user_id))
    return session

def get_today_session(user_id: int) -> UserSession:
    """Get the user session object from the Redis database that was created not more than 24 hours ago.
    """
    session = get_user_session(user_id)
    if time.time() - session.started_at > 86400:
        return create_user_session(User(user_id=user_id))
    return session

async def redis_watchdog_task():
    while True:
        await asyncio.sleep(100)


def remove_user_session(user_id: int):
    """Remove the user session object from the Redis database.
    Args:
        user_id (int): User ID
    """
    _redis = RedisDB()
    _redis.delete(USER_SESSION_PREFIX + str(user_id))
