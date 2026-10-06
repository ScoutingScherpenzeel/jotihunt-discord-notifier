import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise RuntimeError(f"Environment variable {name} is required")

    return value


DISCORD_TOKEN = get_required_env("DISCORD_BOT_TOKEN")

DISCORD_CHANNEL_ID = int(
    get_required_env("DISCORD_JOTIHUNT_CHANNEL_ID")
)

API_URL = os.getenv(
    "API_URL",
    "https://jotihunt.nl/api/2.0/articles",
)

ARTICLE_BASE_URL = os.getenv(
    "ARTICLE_BASE_URL",
    "https://jotihunt.nl/article/",
)

POLL_INTERVAL_SECONDS = int(
    os.getenv("POLL_INTERVAL_SECONDS", "5")
)

HTTP_TIMEOUT_SECONDS = int(
    os.getenv("HTTP_TIMEOUT_SECONDS", "15")
)

SENT_ARTICLES_FILE = Path(
    os.getenv(
        "SENT_ARTICLES_FILE",
        "./sent_articles.json",
    )
)

DISCORD_EMBED_TITLE_LIMIT = 256
DISCORD_EMBED_DESCRIPTION_LIMIT = 4096