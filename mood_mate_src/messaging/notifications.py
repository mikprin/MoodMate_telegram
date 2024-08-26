# In this file I want to notify users periodically.
import asyncio
from datetime import datetime, timedelta
import random
import pendulum

from mood_mate_src.database_tools.schema import User, Language, default_reminder_time
from mood_mate_src.database_tools.users import get_all_users_from_db
from mood_mate_src.messaging.send import send_message_to_user
from mood_mate_src.mate_logger import logger
from mood_mate_src.messaging.states_text import reminder_notification_text
from mood_mate_src.bot import bot


async def notification_routine():
    """
    Periodically notify users about the mood record
    """
    
    default_reminder_time_pendulum = pendulum.parse(default_reminder_time)
    await schedule_daily_task(notify_users, hour=default_reminder_time_pendulum.hour,
                              minute=default_reminder_time_pendulum.minute,
                              name="notification_routine")


async def notify_user(user: User):
    """
    Notify the user about the mood record
    """
    
    language = user.settings.language
    # Pick random message from the reminder_notification_text
    reminder_text = random.choice(reminder_notification_text[language])
    logger.info(f"Sending reminder to user {user.settings.username}: {reminder_text}")
    await send_message_to_user(user.chat_id, reminder_text) 

async def notify_users():
    """
    Notify all users in the database.
    # TODO refactor for custom notification time in future
    """
    users = get_all_users_from_db()
    logger.info(f"Users to notify: {[user.settings.username for user in users]}")
    for user in users:
        if user.settings.reminder_enabled:
            await notify_user(user)

async def send_text_message_to_all_users(text):
    users = get_all_users_from_db()
    logger.info(f"Sending message to all users: {text}")
    for user in users:
        await send_message_to_user(user.chat_id, text)

async def schedule_daily_task(task, hour=19, minute=0, name="notification_routine"):
    while True:
        now = pendulum.now(tz="Asia/Yerevan")
        target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # If the target time is in the past, move it to the next day
        if now > target_time:
            target_time = target_time.add(days=1)
        
        time_to_wait = (target_time - now).total_seconds()
        logger.info(f"Running {name}. Next {name} run scheduled at: {target_time.to_datetime_string()} (in {time_to_wait} seconds) (in {time_to_wait/60/60} hours)")

        # Wait until the scheduled time
        await asyncio.sleep(time_to_wait)
        # Run the task
        await task()
        # Wait one day before scheduling again
        await asyncio.sleep(24 * 60 * 60)

