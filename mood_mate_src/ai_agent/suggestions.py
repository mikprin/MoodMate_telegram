import importlib.resources as pkg_resources
import json
import random
from datetime import datetime

from pydantic import BaseModel

from mood_mate_src.ai_agent.ai_requests import (METRICS_EXPLANATION,
                                                get_simple_messages_from_role,
                                                make_open_ai_request_routed)
from mood_mate_src.analytics.assistants import DEFAULT_ASSISTANT_ROLE
from mood_mate_src.database_tools.mood_data import (
    MoodRecord, get_all_records_for_past_time, get_user_records_for_past_time)
from mood_mate_src.database_tools.users import User


class ActionSuggestion(BaseModel):
    """
    Suggestion for an action
    Consits for dict with suggestion with different languages descriptions
    and categories. Categories are used to filter suggestions
    """
    suggestion: dict[str, str]
    categories: list[str] | None = None


def convert_timestamp_to_time(timestamp: int) -> str:
    """
    Convert timestamp to time using pendulum and timezone
    """



def get_default_suggestions() -> list[ActionSuggestion]:
    """
    Read mood_mate_src/ai_agent/default_suggestions.json using pkg_resources
    """
    default_suggestions = list()

    package_name = 'mood_mate_src.ai_agent'
    file_name = 'default_suggestions.json'

    with pkg_resources.open_text(package_name, file_name) as file:
        default_suggestions_json = json.load(file)

    for element in default_suggestions_json:
        default_suggestions.append(ActionSuggestion(**element))
    return default_suggestions

def get_user_suggestions_prompt_from_records(user: User, records : list[MoodRecord], parsing = "html") -> list:
    """
    Get suggestions for a specific day
    # TODO set default period to a 10 days
    """
    suggestions = get_default_suggestions()
    # Pick random 4 suggestions
    suggestions = random.sample(suggestions, 5)
    # Get only suggestions text:
    suggestions: list[str] = [suggestion.suggestion[user.settings.language] for suggestion in suggestions]
    # Check if user has a custom role
    role = user.get_assistant_role()
    last_record = records[-1]

    prompt = f"""We just got a record from {user.settings.name}.
record is {last_record.data}. Time the record was created is 18:00.
{METRICS_EXPLANATION}
You are addressing the user. Tell him or her that the record was saved! Then can you give a short funny reaction (maybe use emoji) on this and thougts (Don't just tell the numbers). Maybe comment user's data note.
Mention for user one of the following actions:
{suggestions}
You can suggest them for today or tommorow. Depending on the time record was created and suggested action.
But if you feel like you have your own idea. Improvise if user note is present."""

    if parsing == "html":
        prompt += f"\nUse HTML formating if needed."
    if user.settings.language == "ru":
        prompt += f"\nAnswer in Russian language!"
    return prompt


def get_ai_reaction_to_record(user: User, record: MoodRecord) -> str:
    """
    Get AI reaction to a record
    """
    prompt = get_user_suggestions_prompt_from_records(user, [record])
    messages = get_simple_messages_from_role(role=user.get_assistant_role(), prompt=prompt)
    response = make_open_ai_request_routed(messages, model_name=user.settings.ai_model.value)
    if "response" in response.keys():
        return response["response"]
    else:
        return None
