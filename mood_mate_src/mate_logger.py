import logging
import os

# Create logger from name
logger = logging.getLogger(__name__)


# Set logging level

logging_level_var = os.getenv("MOOD_BOT_LOGGING_LEVEL", "DEBUG")
if logging_level_var == "ERROR":
    logger.setLevel(logging.ERROR)
elif logging_level_var == "INFO":
    logger.setLevel(logging.INFO)
elif logging_level_var == "DEBUG":
    logger.setLevel(logging.DEBUG)


# Add a handler if no handlers are present
if not logger.hasHandlers():
    handler = logging.StreamHandler()  # This logs to stdout
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)