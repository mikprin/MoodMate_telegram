import asyncio
from dotenv import load_dotenv
from mood_mate_src.database_tools.redis_tools import redis_watchdog_task
from mood_mate_src.bot import run_bot

async def run_tasks():
    redis_loop = asyncio.create_task(redis_watchdog_task())
    bot_loop = asyncio.create_task(run_bot())
    await asyncio.gather(redis_loop, bot_loop)

def run():
    asyncio.run(run_tasks())


if __name__ == "__main__":
    load_dotenv()
    run()