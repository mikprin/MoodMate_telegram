import pandas as pd
import requests
import os
# from openai import OpenAI
from mood_mate_src.database_tools.users import get_all_users_from_db, get_user_from_db
from mood_mate_src.database_tools.schema import User, AssistantRole
from mood_mate_src.database_tools.mood_data import get_all_records_for_past_time, get_user_records_for_past_time
from mood_mate_src.analytics.assistants import DEFAULT_ASSISTANT_ROLE
from mood_mate_src.analytics.convert import convert_records_to_pandas
from mood_mate_src.mate_logger import logger


METRICS_EXPLANATION = f"""Here is the description of the metrics used and how they are presented to the user:
    mood": "How are you feeling right now? (scale of 7)
    sleep": "How many hours did you sleep today? Enter a number separated by a dot if you want a non-integer
    exercise": "Approximately how many hours did you exercise? Enter a number separated by a dot if you want a non-integer. If you haven't exercised yet but plan to, put 0 and make another mood record after the workout! I will take this into account in the statistics. Your efforts will be recorded!",
    dopings": "What doping did you take today? Check the buttons! If the necessary ones are not in the list, enter them in text separated by commas, at the end press the continue button",
    anxiety": "What is your level of anxiety? (scale of 6)
    energy": "What is your level of energy? (scale of 6)
    future_in_years": "How certain do you see your future? Specify approximately in years.
    note": f"Anything to add? Write a note if you want.
"""


def get_user_statistics_text() -> str:
    
    users = get_all_users_from_db()
    
    # Header
    stats = "User statistics\n"
    
    stats = f"Total users: {len(users)}\n"
    
    # Activity for the last 7 days
    delta = 60*60*24*7
    records = get_all_records_for_past_time(delta)
    
    df : pd.DataFrame = convert_records_to_pandas(records)
    
    unique_weekly_users = df['user_id'].unique()
    
    stats += f"Total records for the last 7 days: {len(records)}\n"
    stats += f"Unique users for the last 7 days: {len(unique_weekly_users)}\n"
    
    return stats

def get_user_report_prompt_from_records(records: list, user: User, role: AssistantRole = DEFAULT_ASSISTANT_ROLE) -> str:
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
    prompt += "Be not very critical of habits and behavior, but rather supportive and helpful.
    Use a tone of {role.role_name}!"""
    # Pick a language
    if user.settings.language == "ru":
        prompt += f"Answer in Russian language!"
    return prompt

def get_user_report_for_past_time(delta: int,
                                  user: User,
                                  role: AssistantRole = DEFAULT_ASSISTANT_ROLE) -> str:
    """
    Get prompt for creating a report for the last delta seconds
    """
    records = get_user_records_for_past_time(user.user_id, delta)
    prompt = get_user_report_prompt_from_records(records, user, role)
    return prompt


def make_open_ai_request_routed(messages: list[dict], model_name="gpt-4o-mini") -> dict:
    """
    Sends a request to the FastAPI OpenAI service. Via Router.

    :param api_url: The URL of the FastAPI service (e.g., http://localhost:8000/api/open_ai_request).
    :param model_name: The name of the OpenAI model (e.g., "gpt-4").
    :param messages: A list of message dictionaries with "role" and "content" (e.g., [{"role": "user", "content": "Hello"}]).
    :param auth_token: The authorization token required for the API.

    :return: The response from the OpenAI service.
    """
    
    auth_token = os.getenv("OPENAI_RELAY_KEY", "")
    api_url = os.getenv("RELAY_API_URL", "localhost:8000/api/open_ai_request")
    
    headers = {
        "Authorization": auth_token,
        "Content-Type": "application/json"
    }

    payload = {
        "model_name": model_name,
        "messages": messages
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for 4xx/5xx errors
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


# def make_open_ai_request(messages: list[dict], system_role = "You are a helpful assistant.") -> str:
#     """
#     Make a request to OpenAI API
#     """
#     client = OpenAI()

#     if messages is None or len(messages) == 0:
#         logger.error("make_open_ai_request: prompt is empty")
#         return None
    
#     try:
#         completion = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=messages
#         )
#         return completion.choices[0].message.content
#     except Exception as e:
#         logger.error(f"OpenAI request failed: {e}")
#         return None


def get_simple_messages_from_role(prompt: str, role: AssistantRole) -> list[dict]:
    """Create a list of messages from the role and the prompt"""    
    if role.role_description is not None:
        role_description = f"Your role is {role.role_name}. Description of your role: {role.role_description}"
    else:
        role_description = f"Your role is {role.role_name}."

    messages = [
        {"role": "system", "content": role_description},
        {"role": "user", "content": prompt}
    ]
    return messages

def get_user_report_for_past_time_with_open_ai(delta: int,
                                               user: User) -> dict[str,str] | None:
    """
    Get prompt for creating a report for the last delta seconds
    """
    
    # Check if user has a custom role
    if user.settings.assistant_custom_role is not None:
        role = user.settings.assistant_custom_role
    else:
        role = DEFAULT_ASSISTANT_ROLE
    
    prompt = get_user_report_for_past_time(delta, user, role=role)
    messages = get_simple_messages_from_role(prompt, role=role)
    response = make_open_ai_request_routed(messages=messages)
    
    # Add response disclamer:
    if ("error" in response.keys()):
        logger.error(f"OpenAI request failed: {response['error']}")
        return response
    if 'response' in response.keys():
        # resp_text = response['response']
        pass
    else:
        logger.error(f"OpenAI response does not contain 'response' key")
        return None
    if user.settings.language == "ru":
        response['response'] += f"\n\nВаш скромный еженедельный отчет от {role.role_name} 📊. Не бери близко к сердцу, ведь я не настоящий, а вот ты да!"
    else:
        response['response'] += f"\n\nYour humble weekly report from {role.role_name} 📊. Don't take it to heart, because I'm not real, but you are!"
    return response