from mood_mate_src.database_tools.schema import User


def get_msg_from_dict(msg_dict: dict, user: User, msg_name: str) -> str:
    """Get the message from the dictionary by its name and language"""

    try:
        msg = msg_dict[user.settings.language][msg_name]
        return msg
    except KeyError:
        return f"Message {msg_name} not found in the language {user.settings.language}"
