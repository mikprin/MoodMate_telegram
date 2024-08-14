import unittest
import os
from unittest.mock import MagicMock
from datetime import datetime
from mood_mate_src.database_tools.users import create_user_from_telegram_message, User, UserSettings, Message

os.environ["SQLITE_DB_PATH"] = "./test_db.db"

class TestCreateUserFromTelegramMessage(unittest.TestCase):
    def test_create_user_from_telegram_message(self):
        # Mock the Message class
        mock_message = MagicMock()
        mock_message.from_user.id = 123
        mock_message.chat.id = 456
        mock_message.from_user.full_name = "John Doe"
        mock_message.from_user.username = "joh"
        
        # Call the function
        user = create_user_from_telegram_message(mock_message)
        
        # Assert the User object
        self.assertEqual(user.user_id, 123)
        self.assertEqual(user.chat_id, 456)
        self.assertEqual(user.settings.name, "John Doe")
        self.assertEqual(user.settings.username, "joh")
        self.assertIsInstance(user.settings.created_at, int)

if __name__ == '__main__':
    unittest.main()