import asyncio
import os
from typing import Literal, Optional, Union

import aiohttp
import requests
from pydantic import BaseModel, Field

from mood_mate_src.analytics.assistants import DEFAULT_ASSISTANT_ROLE
from mood_mate_src.database_tools.mood_data import (
    get_all_records_for_past_time, get_user_records_for_past_time)
from mood_mate_src.database_tools.schema import AssistantRole, User
from mood_mate_src.mate_logger import logger

METRICS_EXPLANATION = f"""Here is the description of the metrics used and how they are presented to the user:
mood": "How are you feeling right now? (scale of 0 to 6)
sleep": "How many hours did you sleep today? Enter a number separated by a dot if you want a non-integer
exercise": "Approximately how many hours did you exercise? Enter a number separated by a dot if you want a non-integer. If you haven't exercised yet but plan to, put 0 and make another mood record after the workout! I will take this into account in the statistics. Your efforts will be recorded!",
dopings": "What doping did you take today? Check the buttons! If the necessary ones are not in the list, enter them in text separated by commas, at the end press the continue button",
anxiety": "What is your level of anxiety? (scale 0 to 5)
energy": "What is your level of energy? (scale 0 to 5)
future_in_years": "How certain do you see your future? Specify approximately in years.
note": f"Anything to add? Write a note if you want.
"""


class Message(BaseModel):
    """Single message in a conversation"""
    role: str
    content: str


class ClaudeRequest(BaseModel):
    """Claude API request model"""
    model_name: str
    messages: list[Message]
    role_description: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 0.2


class OpenAIRequest(BaseModel):
    """OpenAI API request model"""
    model_name: str
    messages: list[Message]
    max_tokens: int = 1000
    temperature: float = 0.7


class AIResponse(BaseModel):
    """Response from AI models"""
    response: str | None = None
    error: str | None = None


class ModelProvider(BaseModel):
    """Model provider configuration"""
    name: Literal["openai", "anthropic"]
    model_prefix: str
    api_endpoint: str


MODEL_PROVIDERS = {
    "openai": ModelProvider(
        name="openai",
        model_prefix="gpt",
        api_endpoint="api/open_ai_request"
    ),
    "anthropic": ModelProvider(
        name="anthropic",
        model_prefix="claude",
        api_endpoint="api/claude_request"
    )
}


def get_provider_for_model(model_name: str) -> ModelProvider:
    """Determine the provider based on model name prefix"""
    for provider in MODEL_PROVIDERS.values():
        if model_name.startswith(provider.model_prefix):
            return provider
    # Default to OpenAI if unknown
    logger.warning(f"Unknown model prefix for {model_name}, defaulting to OpenAI")
    return MODEL_PROVIDERS["openai"]


def get_user_report_prompt_from_records(
    records: list, user: User, role: AssistantRole = DEFAULT_ASSISTANT_ROLE
) -> Optional[str]:
    """
    Get prompt for creating a report from records
    """
    if len(records) == 0:
        return None

    prompt = f"""User {user.settings.name} (username {user.settings.username}) has following mood data statistics for the last period of {len(records)} records:
    Total records: {len(records)}
    Records: {records}

    {METRICS_EXPLANATION}

    Tell user some supportive comment on how do you see the situation and what you can advise for this person?
    Try to add more energy if the user energy is low.
    """
    prompt += "Be not very critical of habits and behavior, but rather supportive and helpful. "
    prompt += f"Use a tone of {role.role_name}!"

    # Pick a language
    if user.settings.language == "ru":
        prompt += " Answer in Russian language!"

    return prompt


def get_prompt_for_user_report(
    delta: int, user: User, role: AssistantRole = DEFAULT_ASSISTANT_ROLE
) -> Optional[str]:
    """
    Get prompt for creating a report for the last delta seconds
    """
    records = get_user_records_for_past_time(user.user_id, delta)
    prompt = get_user_report_prompt_from_records(records, user, role)
    return prompt


def make_ai_request(request: Union[OpenAIRequest, ClaudeRequest], provider: ModelProvider) -> AIResponse:
    """
    Send a request to the appropriate AI model API endpoint

    Args:
        request: The model-specific request object
        provider: The model provider configuration

    Returns:
        AIResponse object with either response or error
    """
    api_url = os.getenv("RELAY_API_URL", "http://localhost:8000") + provider.api_endpoint
    auth_token = os.getenv("OPENAI_RELAY_KEY", "")

    headers = {"Authorization": auth_token, "Content-Type": "application/json"}

    try:
        response = requests.post(api_url, json=request.model_dump(), headers=headers)
        response.raise_for_status()
        return AIResponse(**response.json())
    except requests.exceptions.RequestException as e:
        logger.error(f"Request to {api_url} failed: {e}")
        return AIResponse(error=str(e))


async def make_ai_request_async(request: Union[OpenAIRequest, ClaudeRequest], provider: ModelProvider) -> AIResponse:
    """
    Asynchronous version of make_ai_request
    """
    api_url = os.getenv("RELAY_API_URL", "http://localhost:8000") + provider.api_endpoint
    auth_token = os.getenv("OPENAI_RELAY_KEY", "")

    headers = {"Authorization": auth_token, "Content-Type": "application/json"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=request.model_dump(), headers=headers) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    return AIResponse(error=f"HTTP Error {response.status}: {error_text}")

                response_json = await response.json()
                return AIResponse(**response_json)
    except aiohttp.ClientError as e:
        logger.error(f"Async request to {api_url} failed: {e}")
        return AIResponse(error=str(e))


def get_messages_from_prompt(
    prompt: str, role: AssistantRole, provider: ModelProvider
) -> list[Message]:
    """Create a list of messages from the role and the prompt"""
    role_description = f"Your role is {role.role_name}."
    if role.role_description:
        role_description += f" Description of your role: {role.role_description}"

    if provider.name == "openai":
        return [
            Message(role="system", content=role_description),
            Message(role="user", content=prompt),
        ]
    elif provider.name == "anthropic":
        # Claude doesn't have a standard system role, so we include the role description in the user message
        prompt = f"{role_description}\n{prompt}"
        return [
            Message(role="user", content=prompt),
        ]

    # Default case
    return [Message(role="user", content=prompt)]


# def get_user_report_for_past_time_with_ai(
#     delta: int, user: User
# ) -> Optional[AIResponse]:
#     """
#     Get a report for the user's mood data over the past time period
#     """
#     # Get the user's preferred assistant role and AI model
#     role = user.get_assistant_role()
#     model_name = user.settings.ai_model.value if user.settings.ai_model else "gpt-4o-mini"

#     logger.info(f"Using model {model_name} for user {user.settings.username}")

#     # Determine the model provider based on the model name
#     provider = get_provider_for_model(model_name)

#     # Get the prompt and messages
#     prompt = get_prompt_for_user_report(delta, user, role=role)
#     if not prompt:
#         return AIResponse(error="No records found for the specified time period")

#     messages = get_messages_from_prompt(prompt, role=role, provider=provider)

#     # Create the appropriate request object based on the provider
#     if provider.name == "openai":
#         request = OpenAIRequest(model_name=model_name, messages=messages)
#     else:  # anthropic
#         request = ClaudeRequest(model_name=model_name, messages=messages)

#     # Make the request
#     response = make_ai_request(request, provider)

#     # Add disclaimer to the response
#     if response.response:
#         disclaimer = get_disclaimer_for_user(user, role)
#         response.response += f"\n\n{disclaimer}"

#     return response


async def get_user_report_for_past_time_with_ai_async(
    delta: int, user: User
) -> Optional[AIResponse]:
    """
    Asynchronous version of get_user_report_for_past_time_with_ai
    """
    # Get the user's preferred assistant role and AI model
    role = user.get_assistant_role()
    model_name = user.settings.ai_model.value if user.settings.ai_model else "gpt-4o-mini"

    logger.info(f"Using model {model_name} for user {user.settings.username}")

    # Determine the model provider based on the model name
    provider = get_provider_for_model(model_name)

    # Get the prompt and messages
    prompt = get_prompt_for_user_report(delta, user, role=role)
    if not prompt:
        return AIResponse(error="No records found for the specified time period")

    messages = get_messages_from_prompt(prompt, role=role, provider=provider)

    # Create the appropriate request object based on the provider
    if provider.name == "openai":
        request = OpenAIRequest(model_name=model_name, messages=messages)
    else:  # anthropic
        request = ClaudeRequest(model_name=model_name, messages=messages)

    # Make the request asynchronously
    response = await make_ai_request_async(request, provider)

    # Add disclaimer to the response
    if response.response:
        disclaimer = get_disclaimer_for_user(user, role)
        response.response += f"\n\n{disclaimer}"

    return response


def get_disclaimer_for_user(user: User, role: AssistantRole) -> str:
    """Get localized disclaimer based on user language"""
    if user.settings.language == "ru":
        return f"Ваш скромный еженедельный отчет от {role.role_name} 📊. Не бери близко к сердцу, ведь я не настоящий, а вот ты да!"
    else:
        return f"Your humble weekly report from {role.role_name} 📊. Don't take it to heart, because I'm not real, but you are!"
