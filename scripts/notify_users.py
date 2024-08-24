# Add parent directory to sys.path
import sys,os

script_path = os.path.abspath(__file__)
sys.path.append(os.path.join(os.path.dirname(script_path), '..'))

from mood_mate_src.messaging.notifications import notify_users
import asyncio

# Run notification routine in asyncio
asyncio.run(notify_users())