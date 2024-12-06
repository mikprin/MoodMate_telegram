# In this file I want to notify users periodically.
import asyncio
import random
from datetime import datetime, timedelta

import pendulum

from mood_mate_src.ai_agent.ai_requests import \
    get_user_report_for_past_time_with_open_ai
from mood_mate_src.database_tools.mood_data import MoodData, MoodRecord
from mood_mate_src.database_tools.schema import (Language, User,
                                                 default_reminder_time)
from mood_mate_src.database_tools.users import get_all_users_from_db
from mood_mate_src.mate_logger import logger
from mood_mate_src.messaging.send import send_message_to_chat_id
from mood_mate_src.messaging.states_text import (get_state_msg,
                                                 reminder_notification_text)


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
    await send_message_to_chat_id(user.chat_id, reminder_text)

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
        await send_message_to_chat_id(user.chat_id, text)

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


async def weekly_report():
    """
    Send weekly report to all users
    """
    users = get_all_users_from_db()
    for user in users:
        if user.settings.weekly_report_enabled:
            response = get_user_report_for_past_time_with_open_ai(delta=60*60*24*10, user=user)
            if response is not None:
                if 'error' in response:
                    logger.error(f"Error in weekly report for user {user.settings.username}: {response['error']}")
                    # await send_message_to_chat_id(user.chat_id, response['error'])
                else:
                    await send_message_to_chat_id(user.chat_id, response['response'])
            else:
                logger.info(f"No records for user {user.settings.username} in the last 10 days")
                await send_message_to_chat_id(user.chat_id, get_state_msg("lack_of_records_for_report", user))
        else:
            logger.info(f"User {user.settings.username} has disabled weekly report")

async def weekly_report_routine():
    """Runs the task every Sunday at 13:00."""
    while True:
        now = pendulum.now(tz="Asia/Yerevan")

        # Calculate the next Sunday 13:00
        next_run = now + timedelta(days=(6 - now.weekday()))  # Days until Sunday
        next_run = next_run.replace(hour=14, minute=0, second=0, microsecond=0)

        # If it's past 13:00 today, set the next run to next Sunday
        if now > next_run:
            next_run += timedelta(weeks=1)

        # Calculate the delay in seconds
        delay = (next_run - now).total_seconds()

        logger.info(f"Next run of weekly report scheduled at {next_run} (in {delay} seconds)")

        # Sleep until the next scheduled time
        await asyncio.sleep(delay)

        # Run the task
        await weekly_report()
