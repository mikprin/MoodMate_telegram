import asyncio
from dotenv import load_dotenv
from mood_mate_src.database_tools.redis_tools import redis_watchdog_task
from mood_mate_src.bot import run_bot
from mood_mate_src.messaging.notifications import notification_routine

async def run_tasks():
    redis_task = asyncio.create_task(redis_watchdog_task())
    bot_task = asyncio.create_task(run_bot())
    notification_task = asyncio.create_task(notification_routine())
    await asyncio.gather(redis_task, bot_task, notification_task)

def run():
    asyncio.run(run_tasks())


if __name__ == "__main__":
    load_dotenv()
    run()