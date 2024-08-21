import os
os.environ["SQLITE_DB_PATH"] = "./test_db.db"


from mood_mate_src.keyboard import get_all_buttons_text, BUTTONS_TEXT_LANG

def test_get_all_buttons_text():
    button = "track_mood"
    labels = get_all_buttons_text(button)
    assert set(labels) == {"Записать настроение", "Track mood"}
    
