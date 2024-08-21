import os, asyncio
# Import magic MagicMock
from unittest.mock import MagicMock


os.environ["ADMIN_CHATS"] = "1234567890, @test_user"

from mood_mate_src.admins import admins

def test_admin_chats():
    assert admins == {
        "users": ["test_user"],
        "chats": [1234567890],
    }
    
    
from mood_mate_src.filters import AdminFilter


def test_admin_filter():
    
    message = MagicMock()
    message.from_user.username = "test_user"
    message.chat.id = 1234567890
    
    admin_filter = AdminFilter()
    
    assert asyncio.run(admin_filter(message)) == True
    
    # Assert false if the user is not in the list of admins
    message.from_user.username = "another_user"
    
    # TODO fix this test
    # assert asyncio.run(admin_filter(message)) == False
    