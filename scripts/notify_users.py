# Add parent directory to sys.path
import os
import sys

script_path = os.path.abspath(__file__)
sys.path.append(os.path.join(os.path.dirname(script_path), '..'))

import asyncio

from mood_mate_src.messaging.notifications import notify_users

# Run notification routine in asyncio
asyncio.run(notify_users())
