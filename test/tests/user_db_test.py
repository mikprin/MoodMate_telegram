import asyncio
import os
# Setenv for the database path
os.environ["SQLITE_DB_PATH"] = "./test_db.db"

import unittest
from unittest.mock import patch, AsyncMock
from mood_mate_src.database_tools.users import get_user_from_db, User, UserSettings, add_user_to_db, Language, update_user_in_db
from mood_mate_src.database_tools.db_init import init_db
from mood_mate_src.database_tools.query import DB_PATH
from datetime import datetime


class TestGetUserFromDb(unittest.TestCase):


    def setUp(self):
        print(f"DB_PATH: {DB_PATH}")
        # Set up an in-memory SQLite database
        init_db()
        
    def tearDown(self):
        # Drop the table
        # Close the database connection if needed
        # self.conn.close()
        # Remove the database file after the test
        os.remove(os.getenv("SQLITE_DB_PATH"))
        # pass

    def test_add_user_to_db(self):
        # Define the test data
        user = User(
            user_id = 1,
            chat_id = 1,
            settings = UserSettings(**{
                             "name": "Test User",
                            "created_at" : int(datetime.now().timestamp()),
                            "username": "test_user",
                            "language": "en",
                             }),
        )
        # Add the user to the database
        asyncio.run(add_user_to_db(user))
        # Get the user from the database
        user_from_db = get_user_from_db(1)
        # Check if the user was added to the database
        self.assertEqual(user, user_from_db)
        assert user.settings.language == user_from_db.settings.language
        assert user.settings.language == Language.ENG.value


    def test_update_user_in_db(self):
        # Define the test data
        user = User(
            user_id = 1,
            chat_id = 1,
            settings = UserSettings(**{
                             "name": "Test User",
                            "created_at" : int(datetime.now().timestamp()),
                            "username": "test_user",
                            "language": "en",
                             }),
        )
        # Add the user to the database
        asyncio.run(add_user_to_db(user))
        # Update the user in the database
        user.settings.language = "ru"
        asyncio.run(update_user_in_db(user))
        # Get the user from the database
        user_from_db = get_user_from_db(1)
        # Check if the user was updated in the database
        assert user.settings.language == user_from_db.settings.language
        assert user.settings.language == Language.RU.value

if __name__ == '__main__':
    unittest.main()