# MoodMate_telegram

## Short description
Telegram bot with AI integration to track mood and emotions.

## Motivation

Our mental health is as important as our physical health. It is important to keep track of our mood and emotions to understand how we are feeling and to identify patterns that may be affecting our mental health. This project aims to help people track their mood and emotions by providing them with a simple and easy-to-use tool that they can use to record their mood and emotions on a daily basis. The tool will provide users with a summary of their mood over time and suggest ways to improve their mood based on their responses.

## Idea behind the project

The idea behind the project is to create a telegram bot that can help people to track their mood and emotions. The bot will ask the user how they are feeling and the user can respond with an emoji that represents their mood. The bot will then store this information and provide the user with a summary of their mood over time. The bot will also provide the user with suggestions on how to improve their mood based on their responses.
Things to track:
- Mood (emoji)
- Sleep (hrs)
- Horny level (emoji)
- Exercise (hrs)
- Use of any doping (list)
- Energy level (emoji)
- Anxiety (emoji)
- List could be extended


User can ask for summary in the following ways:
- Summary as plot for the last N days. Some items can be ticked off.
- Weekly AI powered reports! Inspiaring you to start a new week!
- AI suggestions to improve mood and life quality.

Reminders are implemented to remind the user to track their mood and emotions on a daily basis.

### Ideas for the future
It would be nice to have an advice or cheers up message based on the mood of the user and probably using some ML model.

If you feel like it you can send a message to the bot and it will send it to random user if they are feeling down.

Track anger?

## Stack

- Python as main language
- aiogram for telegram bot
- SQLite3 for database
- Redis as cache and for storing chats
- Docker for deployment


### Database structure

I use SQLite3 for the database. The database has two tables right now:

- Table `users`:
    - `user_id` (int): unique user id
    - `chat_id` (int): chat id of the user
    - `settings` (json): user settings
- Table `user_data`:
    - `user_id` (int): unique user id
    - `date` (date): date of the entry
    - `mood` (int): mood of the user
    - `sleep` (int): hours of sleep
    - `horny` (int): horny level
    - `exercise` (int): hours of exercise
    - `dopings` (str): list of doping
    - `energy` (int): energy level
    - `anxiety` (int): anxiety level
    - `period` (str): period  (optional)
    - `note` (str): note from the user
    - `created_at` (timestamp): timestamp of the entry
    - `extra` (json): extra data

## Testing

I use pytest for testing. You can run the tests with the following command:

```bash
source venv/bin/activate
python -m pytest test/tests
```
