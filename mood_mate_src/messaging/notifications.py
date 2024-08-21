# In this file I want to notify users periodically.
import asyncio
from datetime import datetime, timedelta
import random

from mood_mate_src.database_tools.users import User, UserSettings, get_all_users_from_db, default_reminder_time
from mood_mate_src.messaging.send import send_message_to_user
from mood_mate_src.mate_logger import logger
from mood_mate_src.messaging.states_text import reminder_notification_text
from mood_mate_src.bot import bot


async def notification_routine():
    """
    Periodically notify users about the mood record
    """
    await schedule_daily_task(notify_users, hour=default_reminder_time.hour, minute=default_reminder_time.minute, name="notification_routine")


async def notify_user(user: User):
    """
    Notify the user about the mood record
    """
    
    language = user.settings.language
    # Pick random message from the reminder_notification_text
    reminder_text = random.choice(reminder_notification_text[language])
    print(f"Sending reminder to user {user.chat_id}: {reminder_text}")
    await send_message_to_user(user.chat_id, reminder_text) 

async def notify_users():
    """
    Notify all users in the database.
    # TODO refactor for custom notification time in future
    """
    users = get_all_users_from_db()
    print(f"Users to notify: {users}")
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
        now = datetime.now()
        target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # If the target time is in the past, move it to the next day
        if now > target_time:
            target_time += timedelta(days=1)
        time_to_wait = (target_time - now).total_seconds()
        logger.info(f"Next {name} run scheduled at: {target_time} (in {time_to_wait} seconds)")

        # Wait until the scheduled time
        await asyncio.sleep(time_to_wait)
        # Run the task
        await task()
        # Wait one day before scheduling again
        await asyncio.sleep(24 * 60 * 60)
