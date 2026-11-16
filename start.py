import subprocess
import sys

from pathlib import Path

ROOT = Path(__file__).resolve().parent

subprocess.run(
    [sys.executable, "scripts/init_env.py"],
    cwd=ROOT,
    check=True,
)

env_file = ROOT / ".env"
content = env_file.read_text(encoding="utf-8")

if "PASTE_YOUR_TELEGRAM_BOT_TOKEN_HERE" in content:
    print("Please add your Telegram bot token to .env")
    sys.exit(1)

subprocess.run(
    ["docker", "compose", "up", "--build", "-d"],
    cwd=ROOT,
    check=True,
)