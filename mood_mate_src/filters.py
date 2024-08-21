from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from mood_mate_src.keyboard import emotional_emoji_sets
from mood_mate_src.admins import admins
class ButtonTextFilter(BaseFilter):
    """
    Filter for checking if the message text is in the list of button texts
    """
    def __init__(self, button_texts: list[str]):
        self.button_texts = button_texts

    async def __call__(self, message: Message) -> bool:
        return message.text in self.button_texts


class CallbackDataFilter(BaseFilter):
    """
    Filter for checking if the callback data is in the list of callback data
    """
    def __init__(self, prefix: str):
        self.prefix = prefix

    async def __call__(self, call: CallbackQuery) -> bool:
        return call.data.startswith(self.prefix)   

class MoodCallbackFilter(BaseFilter):
    async def __call__(self, call: CallbackQuery):
        # Check if the callback data starts with "mood"
        return call.data.startswith(emotional_emoji_sets["mood"].data_type_names[0])


class AdminFilter(BaseFilter):
    async def __call__(self, message: Message):
        # Check that the user is in the list of admins
        # Or the chat is in the list of admin chats
        return message.from_user.username in admins["users"] or message.chat.id in admins["chats"]