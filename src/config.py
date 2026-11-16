import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

def required_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        raise ValueError(f"{name} is missing from the environment")
    return value.strip()

BOT_TOKEN = required_env("BOT_TOKEN")
DATABASE_URL = required_env("DATABASE_URL")

raw_admin_ids = required_env("ADMIN_IDS").split(",")
admin_ids = set()

for raw_id in raw_admin_ids:
    user_id = raw_id.strip()
    if not user_id.isascii() or not user_id.isdecimal():
        raise ValueError("ADMIN_IDS must be comma-separated positive integer IDs")

    parsed_id = int(user_id)
    if parsed_id <= 0:
        raise ValueError("ADMIN_IDS must contain positive integer IDs")

    admin_ids.add(parsed_id)

if not admin_ids:
    raise ValueError("ADMIN_IDS must contain at least one ID")

ADMIN_IDS = frozenset(admin_ids)
