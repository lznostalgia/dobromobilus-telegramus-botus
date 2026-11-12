import os



def get_bot_token() -> str:
    "Get bot token from environment, raise exception if it doesn't exist."
    token = os.getenv("BOT_TOKEN")

    if not token:
        raise ValueError("No BOT_TOKEN found in environment variables")
    return token