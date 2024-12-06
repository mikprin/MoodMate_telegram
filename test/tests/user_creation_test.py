import os
import unittest
from datetime import datetime
from unittest.mock import MagicMock

from mood_mate_src.database_tools.schema import (DEFAULT_ASSISTANT_ROLE,
                                                 AssistantRole)
from mood_mate_src.database_tools.users import (
    Message, User, UserSettings, create_user_from_telegram_message)

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


def test_user_get_assistant_role():
    # Create a User object
    user = User(
        user_id=1,
        chat_id=123,
        settings=UserSettings(
            name="John Doe",
            username="joh",
            created_at=int(datetime.now().timestamp())
        )
    )

    # Test when user has no custom role
    role = user.get_assistant_role()
    assert isinstance(role, AssistantRole)
    assert role == DEFAULT_ASSISTANT_ROLE


if __name__ == '__main__':
    unittest.main()
