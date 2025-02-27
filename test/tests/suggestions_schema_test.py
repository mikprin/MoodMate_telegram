import json
import random

from mood_mate_src.ai_agent.suggestions import (
    ActionSuggestion, get_default_suggestions,
    get_user_suggestions_prompt_from_records)
from mood_mate_src.database_tools.mood_data import MoodData, MoodRecord
from mood_mate_src.database_tools.schema import (DEFAULT_ASSISTANT_ROLE,
                                                 AssistantRole, User,
                                                 UserSettings)


def test_get_default_suggestions():
    """Test that all default suggestions are loaded correctly"""
    default_suggestons = get_default_suggestions()

    assert len(default_suggestons) > 0
    for element in default_suggestons:
        assert isinstance(element, ActionSuggestion)

def test_pick_random_suggestions():
    """Test that random suggestions are picked correctly"""
    suggestions = get_default_suggestions()

    picked_suggestions = random.sample(suggestions, 4)

    assert len(picked_suggestions) == 4
    for element in picked_suggestions:
        assert isinstance(element, ActionSuggestion)


def test_prompt_generation():

    user_settings = UserSettings(
        name="John Doe",
        created_at=1633036800,
        language="en",
        dopings_list=[],
        periods_are_tracked=False,
        reminder_time="08:00",
        reminder_enabled=True,
        gender=None,
        recommended_sleep=8.0,
        username="johndoe",
        weekly_report_enabled=True,
        assistant_custom_role=DEFAULT_ASSISTANT_ROLE,
    )

    user = User(
        user_id=12345,
        chat_id=67890,
        settings=user_settings
    )


    records = [
        MoodRecord(
        user_id=12345,
        date="2023-10-01",
        created_at=1696156800,
        data=MoodData(
            mood=7,
            sleep=7.5,
            energy=4,
            anxiety=3,
            exercise=1.0,
            dopings=["coffee"],
            horny=4,
            period=False,
            note="Feeling good today",
        )
        ),
        MoodRecord(
        user_id=12345,
        date="2023-10-02",
        created_at=1696243200,
        data=MoodData(
            mood=5,
            sleep=6.0,
            energy=5,
            anxiety=4,
            exercise=0.5,
            dopings=["tea"],
            horny=3,
            period=False,
            note="A bit tired",
        )
        ),
        MoodRecord(
        user_id=12345,
        date="2023-10-03",
        created_at=1696329600,
        data=MoodData(
            mood=6,
            sleep=8.0,
            energy=5,
            anxiety=2,
            exercise=1.5,
            dopings=[],
            horny=5,
            period=False,
            note="Feeling great",
        )
        )
    ]


    prompt = get_user_suggestions_prompt_from_records(user = user, records = records)
    assert isinstance(prompt, str)
    assert len(prompt) > 0

    prompt = get_user_suggestions_prompt_from_records(user = user, records = records, parsing="plain")
    assert isinstance(prompt, str)
    assert len(prompt) > 0
    assert "html" not in prompt
    assert "HTML" not in prompt
