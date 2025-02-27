import importlib.resources as pkg_resources
import json
import random
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from mood_mate_src.ai_agent.ai_requests import (METRICS_EXPLANATION,
                                                AIResponse, ClaudeRequest,
                                                Message, OpenAIRequest,
                                                get_messages_from_prompt,
                                                get_provider_for_model,
                                                make_ai_request,
                                                make_ai_request_async)
from mood_mate_src.analytics.assistants import DEFAULT_ASSISTANT_ROLE
from mood_mate_src.database_tools.mood_data import (
    MoodRecord, get_all_records_for_past_time, get_user_records_for_past_time)
from mood_mate_src.database_tools.schema import User
from mood_mate_src.mate_logger import logger


class ActionSuggestion(BaseModel):
    """
    Suggestion for an action
    Consists of dict with suggestion with different languages descriptions
    and categories. Categories are used to filter suggestions
    """
    suggestion: dict[str, str]
    categories: Optional[List[str]] = None


def convert_timestamp_to_time(timestamp: int) -> str:
    """
    Convert timestamp to time using pendulum and timezone
    """
    # Implementation pending
    return datetime.fromtimestamp(timestamp).strftime("%H:%M")


def get_default_suggestions() -> list[ActionSuggestion]:
    """
    Read mood_mate_src/ai_agent/default_suggestions.json using pkg_resources
    """
    default_suggestions = list()

    package_name = 'mood_mate_src.ai_agent'
    file_name = 'default_suggestions.json'

    try:
        with pkg_resources.open_text(package_name, file_name) as file:
            default_suggestions_json = json.load(file)

        for element in default_suggestions_json:
            default_suggestions.append(ActionSuggestion(**element))
    except Exception as e:
        logger.error(f"Error loading default suggestions: {e}")
        # Fallback to empty list
        default_suggestions = []

    return default_suggestions


def get_user_suggestions_prompt_from_records(
    user: User,
    records: list[MoodRecord],
    parsing: str | None = "html"
) -> str:
    """
    Get suggestions prompt based on user records

    Args:
        user: The user to generate suggestions for
        records: List of user's mood records
        parsing: Output format (html or plain)

    Returns:
        Prompt string for AI model
    """
    if not records:
        return None

    suggestions = get_default_suggestions()
    # Pick random 5 suggestions
    suggestions = random.sample(suggestions, min(5, len(suggestions)))
    # Get only suggestions text in user's language
    suggestion_texts = [suggestion.suggestion.get(user.settings.language,
                       suggestion.suggestion.get('en', 'No suggestion available'))
                       for suggestion in suggestions]

    # Check if user has a custom role
    role = user.get_assistant_role()
    last_record = records[-1]

    record_time = datetime.now().strftime("%H:%M")

    prompt = f"""We just got a record from {user.settings.name}.

record is {last_record.data}. Time the record was created is {record_time}.
{METRICS_EXPLANATION}
You are addressing the user. Tell him or her that the record was saved! Then can you give a short funny reaction (maybe use emoji) on this and thoughts (Don't just tell the numbers). Maybe comment user's data note.
Mention for user one of the following actions:
{suggestion_texts}
You can suggest them for today or tomorrow. Depending on the time record was created and suggested action.
But if you feel like you have your own idea. Improvise if user note is present."""

    if parsing == "html":
        prompt += f"\nUse HTML formatting if needed."
    if user.settings.language == "ru":
        prompt += f"\nAnswer in Russian language!"
    # Add role specific prompt
    prompt += f"\nUse a tone of following role: {role.role_name}!"
    if role.role_description is not None:
        prompt += f" (role description: {role.role_description})"
    return prompt


async def get_ai_reaction_to_record_async(user: User, record: MoodRecord) -> Optional[str]:
    """
    Asynchronous version of get_ai_reaction_to_record

    Args:
        user: The user who created the record
        record: The mood record to react to

    Returns:
        AI-generated reaction text or None if request failed
    """
    # Get user's preferred model
    model_name = user.settings.ai_model.value if user.settings.ai_model else "gpt-4o-mini"

    # Determine the model provider based on the model name
    provider = get_provider_for_model(model_name)

    # Generate the prompt and convert to messages format
    prompt = get_user_suggestions_prompt_from_records(user, [record], parsing=None)
    if not prompt:
        logger.error("Failed to generate suggestion prompt")
        return None

    messages = get_messages_from_prompt(prompt, role=user.get_assistant_role(), provider=provider)

    # Create the appropriate request object based on the provider
    if provider.name == "openai":
        request = OpenAIRequest(model_name=model_name, messages=messages)
    else:  # anthropic
        request = ClaudeRequest(model_name=model_name, messages=messages)

    # Make the request asynchronously
    response = await make_ai_request_async(request, provider)

    if response.response is not None:
        return response.response
    else:
        logger.error(f"AI request failed: {response.error}")
        return None


def get_contextual_suggestions(
    user: User,
    record: MoodRecord,
    time_of_day: str = None,
    weather: str = None
) -> Optional[str]:
    """
    Get contextual suggestions based on user's mood record, time of day, and weather

    Args:
        user: The user to suggest actions for
        record: The latest mood record
        time_of_day: Current time of day (morning, afternoon, evening, night)
        weather: Current weather conditions

    Returns:
        AI-generated suggestions or None if request failed
    """
    # Get user's preferred model
    model_name = user.settings.ai_model.value if user.settings.ai_model else "gpt-4o-mini"

    # Determine the model provider
    provider = get_provider_for_model(model_name)

    # Get default suggestions filtered by time of day and mood
    all_suggestions = get_default_suggestions()

    # Filter suggestions based on time of day if provided
    if time_of_day:
        all_suggestions = [s for s in all_suggestions if not s.categories or time_of_day in s.categories]

    # Filter suggestions based on mood (for example, energizing activities for low energy)
    mood_level = record.data.get("mood", 3)
    energy_level = record.data.get("energy", 3)

    if mood_level < 3 and energy_level < 3:
        # For low mood and energy, prioritize uplifting activities
        energizing_suggestions = [s for s in all_suggestions if s.categories and "energizing" in s.categories]
        if energizing_suggestions:
            all_suggestions = energizing_suggestions

    # Select random suggestions from filtered list
    num_suggestions = min(3, len(all_suggestions))
    if num_suggestions == 0:
        # Fallback to default suggestions if filters are too restrictive
        all_suggestions = get_default_suggestions()
        num_suggestions = min(3, len(all_suggestions))

    selected_suggestions = random.sample(all_suggestions, num_suggestions)

    # Get suggestion texts in user's language
    suggestion_texts = [s.suggestion.get(user.settings.language,
                        s.suggestion.get('en', 'No suggestion available'))
                        for s in selected_suggestions]

    # Create contextual prompt
    context_info = ""
    if time_of_day:
        context_info += f"It's currently {time_of_day}. "
    if weather:
        context_info += f"The weather is {weather}. "

    prompt = f"""Based on {user.settings.name}'s latest mood record:
{record.data}

{context_info}

Please suggest {num_suggestions} personalized activities from the following options:
{suggestion_texts}

Explain why each activity might help with their current mood and energy levels.
Keep the tone conversational and supportive, using the voice of {user.get_assistant_role().role_name}.
"""

    if user.settings.language == "ru":
        prompt += "\nAnswer in Russian language!"

    # Convert to messages format
    messages = get_messages_from_prompt(
        prompt,
        role=user.get_assistant_role(),
        provider=provider
    )

    # Create the appropriate request object
    if provider.name == "openai":
        request = OpenAIRequest(model_name=model_name, messages=messages)
    else:  # anthropic
        request = ClaudeRequest(model_name=model_name, messages=messages)

    # Make the request
    response = make_ai_request(request, provider)

    if response.response:
        return response.response
    else:
        logger.error(f"Contextual suggestion request failed: {response.error}")
        return None
