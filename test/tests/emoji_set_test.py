from mood_mate_src.keyboard import EmojiSet, emotional_emoji_sets
from mood_mate_src.database_tools.users import Language, User
from aiogram.types.keyboard_button import KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def test_emoji_set():
    assert type(emotional_emoji_sets["mood"]) == EmojiSet
    assert type(emotional_emoji_sets["mood"].emoji_set) == list
    
    availible_langs = [lang.value for lang in Language]
    
    set_comments = emotional_emoji_sets["horny"].comment
    assert type(set_comments) == dict
    for lang in availible_langs:
        assert lang in set_comments.keys()
        assert type(set_comments[lang]) == str
        
def test_get_number_from_emoji():
    assert emotional_emoji_sets["mood"].get_number_from_emoji('😢') == 1
    assert emotional_emoji_sets["mood"].get_number_from_emoji('😄') == 6
    assert emotional_emoji_sets["horny"].get_number_from_emoji('😐') == 0
    assert emotional_emoji_sets["horny"].get_number_from_emoji('🔥') == 5
    
def test_get_keyboard_buttons():
    mood_keyboard = emotional_emoji_sets["mood"].get_keyboard_buttons()
    horny_keyboard = emotional_emoji_sets["horny"].get_keyboard_buttons()
    
    assert len(mood_keyboard) == 1
    assert len(mood_keyboard[0]) == 7
    assert len(horny_keyboard) == 1
    assert len(horny_keyboard[0]) == 6
    for emoji in emotional_emoji_sets["mood"].emoji_set:
        assert KeyboardButton(text=emoji) in mood_keyboard[0]
    for emoji in emotional_emoji_sets["horny"].emoji_set:
        assert KeyboardButton(text=emoji) in horny_keyboard[0]
        
    mood_keyboard_builder = emotional_emoji_sets["mood"].get_keyboard_builder()
    horny_keyboard_builder = emotional_emoji_sets["horny"].get_keyboard_builder()
    
    assert isinstance(mood_keyboard_builder, InlineKeyboardBuilder)
    assert isinstance(horny_keyboard_builder, InlineKeyboardBuilder)
        
def test_inline_keyboard():
    mood_inline_keyboard = emotional_emoji_sets["mood"].get_inline_keyboard_buttons()
    horny_inline_keyboard = emotional_emoji_sets["horny"].get_inline_keyboard_buttons()
    
    assert len(mood_inline_keyboard) == 7
    assert len(horny_inline_keyboard) == 6
    for emoji in emotional_emoji_sets["mood"].emoji_set:
        assert emoji in [button.text for button in mood_inline_keyboard]
    for emoji in emotional_emoji_sets["horny"].emoji_set:
        assert emoji in [button.text for button in horny_inline_keyboard]
        
    assert mood_inline_keyboard[0].callback_data == "mood_0"
    assert mood_inline_keyboard[5].callback_data == "mood_5"
    assert horny_inline_keyboard[0].callback_data == "horny_0"
    assert horny_inline_keyboard[5].callback_data == "horny_5"
