import logging

import aiohttp
import discord
from discord.ext import tasks

from .api import JotihuntApi
from .articles import build_article_message
from .config import (
    API_URL,
    DISCORD_CHANNEL_ID,
    HTTP_TIMEOUT_SECONDS,
    POLL_INTERVAL_SECONDS,
)
from .storage import SentArticleRepository


logger = logging.getLogger(__name__)


class JotihuntBot(
    discord.Client
):
    def __init__(
        self,
        sent_articles: SentArticleRepository,
    ):
        intents = discord.Intents.default()

        super().__init__(
            intents=intents,
        )

        self.sent_articles = sent_articles

        self.http_session: (
            aiohttp.ClientSession | None
        ) = None

        self.api: (
            JotihuntApi | None
        ) = None

    async def setup_hook(
        self,
    ) -> None:
        timeout = aiohttp.ClientTimeout(
            total=HTTP_TIMEOUT_SECONDS
        )

        self.http_session = (
            aiohttp.ClientSession(
                timeout=timeout,
            )
        )

        self.api = JotihuntApi(
            session=self.http_session,
            api_url=API_URL,
        )

        self.poll_articles.start()

    async def close(
        self,
    ) -> None:
        self.poll_articles.cancel()

        if self.http_session:
            await self.http_session.close()

        await super().close()

    async def on_ready(
        self,
    ) -> None:
        logger.info(
            "Logged in as %s (%s)",
            self.user,
            (
                self.user.id
                if self.user
                else "unknown"
            ),
        )

    @tasks.loop(
        seconds=POLL_INTERVAL_SECONDS
    )
    async def poll_articles(
        self,
    ) -> None:
        try:
            await self.send_new_articles()

        except Exception:
            logger.exception(
                "Unexpected error while polling articles"
            )

    @poll_articles.before_loop
    async def before_poll_articles(
        self,
    ) -> None:
        await self.wait_until_ready()

    @poll_articles.error
    async def poll_articles_error(
        self,
        error: BaseException,
    ) -> None:
        logger.error(
            "Article polling task failed",
            exc_info=(
                type(error),
                error,
                error.__traceback__,
            ),
        )

    async def send_new_articles(
        self,
    ) -> None:
        if self.api is None:
            logger.error(
                "Jotihunt API has not been initialized"
            )
            return

        channel = self.get_channel(
            DISCORD_CHANNEL_ID
        )

        if channel is None:
            logger.error(
                "Could not find Discord channel %s",
                DISCORD_CHANNEL_ID,
            )
            return

        if not isinstance(
            channel,
            discord.abc.Messageable,
        ):
            logger.error(
                "Discord channel %s is not messageable",
                DISCORD_CHANNEL_ID,
            )
            return

        articles = (
            await self.api.get_articles()
        )

        if not articles:
            return

        for article in reversed(
            articles
        ):
            await self.process_article(
                channel=channel,
                article=article,
            )

    async def process_article(
        self,
        channel: discord.abc.Messageable,
        article: dict,
    ) -> None:
        article_id_raw = (
            article.get("id")
        )

        if article_id_raw is None:
            logger.warning(
                "Ignoring article without ID"
            )
            return

        article_id = str(
            article_id_raw
        )

        if self.sent_articles.contains(
            article_id
        ):
            return

        try:
            embed, view = (
                build_article_message(
                    article_id=article_id,
                    article=article,
                )
            )

            await channel.send(
                embed=embed,
                view=view,
            )

        except discord.HTTPException:
            logger.exception(
                "Discord rejected article %s",
                article_id,
            )
            return

        except Exception:
            logger.exception(
                "Failed to process article %s",
                article_id,
            )
            return

        self.sent_articles.add(
            article_id
        )

        logger.info(
            "Sent article %s: %s",
            article_id,
            article.get("title"),
        )