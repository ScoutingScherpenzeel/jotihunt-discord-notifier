import asyncio
import logging

from .bot import JotihuntBot
from .config import (
    DISCORD_TOKEN,
    SENT_ARTICLES_FILE,
)
from .storage import SentArticleRepository


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
    )


async def main() -> None:
    configure_logging()

    sent_articles = (
        SentArticleRepository(
            SENT_ARTICLES_FILE
        )
    )

    sent_articles.load()

    bot = JotihuntBot(
        sent_articles=sent_articles
    )

    async with bot:
        await bot.start(
            DISCORD_TOKEN
        )


if __name__ == "__main__":
    asyncio.run(main())