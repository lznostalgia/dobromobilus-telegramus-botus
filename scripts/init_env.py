import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"


def create_environment():
    if ENV_FILE.exists():
        print(".env already exists. Keeping existing credentials.")
        return

    db_user = "bot_" + secrets.token_hex(8)
    db_password = secrets.token_urlsafe(32)

    env_content = f"""\
BOT_TOKEN=PASTE_YOUR_TELEGRAM_BOT_TOKEN_HERE

POSTGRES_USER={db_user}
POSTGRES_PASSWORD={db_password}
POSTGRES_DB=shelter_db

DATABASE_URL=postgresql+asyncpg://{db_user}:{db_password}@db:5432/shelter_db

ADMIN_IDS=
"""

    ENV_FILE.write_text(env_content, encoding="utf-8")

    # На Unix-подобных системах ограничиваем доступ к файлу.
    try:
        ENV_FILE.chmod(0o600)
    except OSError:
        pass

    print("Environment created.")
    print("Generated PostgreSQL credentials and saved them in .env")
    print("Add your Telegram bot token to .env before starting the bot.")


if __name__ == "__main__":
    create_environment()