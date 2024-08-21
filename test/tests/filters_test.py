import pytest
from aiogram.types import Message
from mood_mate_src.filters import ButtonTextFilter
from unittest.mock import MagicMock



# Use magic methods to create Message object

def test_button_filter():
    """#TODO broken test, fix it"""
    button_texts = ["Button 1", "Button 2", "Button 3"]
    filt = ButtonTextFilter(button_texts)
    
    assert filt.button_texts == button_texts
    
    message = MagicMock()
    message.text = "Button 1"
    # assert filt(message) == True
    
    wrong_message = MagicMock()
    wrong_message.text = "Button 4"

# @pytest.fixture
# def button_text_filter():
#     button_texts = ["Button 1", "Button 2", "Button 3"]
#     return ButtonTextFilter(button_texts)

# @pytest.mark.asyncio
# async def test_button_text_filter(button_text_filter):
#     message_with_button_1 = Message(text="Button 1")
#     message_with_button_2 = Message(text="Button 2")
#     message_with_button_3 = Message(text="Button 3")
#     message_with_other_text = Message(text="Other Text")

#     assert await button_text_filter(message_with_button_1) == True
#     assert await button_text_filter(message_with_button_2) == True
#     assert await button_text_filter(message_with_button_3) == True
#     assert await button_text_filter(message_with_other_text) == False