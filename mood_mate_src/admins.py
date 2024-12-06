import os

from mood_mate_src.mate_logger import logger

# Read admin chats from the .env file

ADMIN_CHATS_KEY = "ADMIN_CHATS"

chats_users = os.getenv(ADMIN_CHATS_KEY, "")

elements = chats_users.split(",")

admins = {
    "users": list(),
    "chats": list(),
}

for element in elements:
    if element.strip().startswith("@"):
        # Remove the "@" symbol
        admin = element.strip()[1:]
        admins["users"].append(admin)
    # If this is an integer, then it is a chat id
    elif element.isdigit():
        admins["chats"].append(int(element))
    else:
        logger.error(f"Unknown element in the admin chats: {element}")

logger.info(f"Admins: {admins}")
