import asyncio
import logging
from typing import Any

import aiohttp


logger = logging.getLogger(__name__)


class JotihuntApi:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        api_url: str,
    ):
        self.session = session
        self.api_url = api_url

    async def get_articles(
        self,
    ) -> list[dict[str, Any]]:
        try:
            async with self.session.get(
                self.api_url
            ) as response:
                response.raise_for_status()
                payload = await response.json()

        except asyncio.TimeoutError:
            logger.error(
                "Jotihunt API request timed out"
            )
            return []

        except aiohttp.ContentTypeError:
            logger.exception(
                "Jotihunt API returned an invalid content type"
            )
            return []

        except aiohttp.ClientError:
            logger.exception(
                "Failed to fetch articles from Jotihunt API"
            )
            return []

        if not isinstance(payload, dict):
            logger.error(
                "Unexpected Jotihunt API response: root value is not an object"
            )
            return []

        data = payload.get("data", [])

        if not isinstance(data, list):
            logger.error(
                "Unexpected Jotihunt API response: 'data' is not a list"
            )
            return []

        return [
            article
            for article in data
            if isinstance(article, dict)
        ]