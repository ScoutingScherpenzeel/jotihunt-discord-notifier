import logging
from datetime import datetime
from typing import Any

import discord
import html2text
from bs4 import BeautifulSoup

from .config import (
    ARTICLE_BASE_URL,
    DISCORD_EMBED_DESCRIPTION_LIMIT,
    DISCORD_EMBED_TITLE_LIMIT,
)


logger = logging.getLogger(__name__)


def clean_html_to_markdown(
    raw_html: str,
) -> tuple[str, str | None]:
    soup = BeautifulSoup(
        raw_html or "",
        "html.parser",
    )

    first_image_url: str | None = None

    for figure in soup.find_all("figure"):
        if first_image_url is None:
            image = figure.find("img")

            if image:
                source = image.get("src")

                if source:
                    first_image_url = str(source)

        figure.decompose()

    converter = html2text.HTML2Text()

    converter.ignore_links = False
    converter.ignore_images = True
    converter.body_width = 0
    converter.single_line_break = True
    converter.skip_internal_links = True

    markdown = converter.handle(
        str(soup)
    ).strip()

    return markdown, first_image_url


def format_dutch_date(
    iso_date: str,
) -> str:
    try:
        parsed = datetime.fromisoformat(
            iso_date.replace(
                "Z",
                "+00:00",
            )
        )

        return parsed.strftime(
            "%d/%m/%Y %H:%M"
        )

    except (ValueError, AttributeError):
        logger.warning(
            "Could not parse article date: %r",
            iso_date,
        )

        return "Onbekende datum"


def truncate(
    value: str,
    limit: int,
) -> str:
    if len(value) <= limit:
        return value

    if limit <= 3:
        return value[:limit]

    return value[: limit - 3].rstrip() + "..."


def build_article_message(
    article_id: str,
    article: dict[str, Any],
) -> tuple[
    discord.Embed,
    discord.ui.View,
]:
    title = str(
        article.get("title")
        or "Geen titel"
    )

    title = truncate(
        title,
        DISCORD_EMBED_TITLE_LIMIT,
    )

    message = article.get("message")

    if not isinstance(
        message,
        dict,
    ):
        message = {}

    raw_content = message.get(
        "content",
        "",
    )

    if not isinstance(
        raw_content,
        str,
    ):
        raw_content = str(
            raw_content
        )

    cleaned_message, image_url = (
        clean_html_to_markdown(
            raw_content
        )
    )

    if not cleaned_message:
        cleaned_message = (
            "*Dit bericht bevat geen tekst.*"
        )

    cleaned_message = truncate(
        cleaned_message,
        DISCORD_EMBED_DESCRIPTION_LIMIT,
    )

    publish_at = article.get(
        "publish_at"
    )

    if isinstance(
        publish_at,
        str,
    ):
        formatted_date = format_dutch_date(
            publish_at
        )
    else:
        formatted_date = "Onbekende datum"

    article_url = (
        f"{ARTICLE_BASE_URL}{article_id}"
    )

    embed = discord.Embed(
        title=title,
        description=cleaned_message,
        color=0x00FF00,
        url=article_url,
    )

    embed.set_footer(
        text=(
            "Gepubliceerd op: "
            f"{formatted_date}"
        )
    )

    if image_url:
        embed.set_image(
            url=image_url
        )

    view = discord.ui.View(
        timeout=None
    )

    view.add_item(
        discord.ui.Button(
            label="Origineel bericht",
            url=article_url,
        )
    )

    return embed, view