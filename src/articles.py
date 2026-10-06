import logging
import re
from datetime import datetime
from typing import Any

import discord
from bs4 import BeautifulSoup
from markdownify import markdownify as md

from .config import (
    ARTICLE_BASE_URL,
    DISCORD_EMBED_DESCRIPTION_LIMIT,
    DISCORD_EMBED_TITLE_LIMIT,
)


logger = logging.getLogger(__name__)


def clean_html_to_discord(
    raw_html: str,
) -> tuple[str, str | None]:
    soup = BeautifulSoup(
        raw_html or "",
        "html.parser",
    )

    first_image_url: str | None = None

    image = soup.find("img")

    if image and image.get("src"):
        first_image_url = str(
            image["src"]
        )

    # Images are displayed separately in the Discord embed.
    for figure in soup.find_all("figure"):
        figure.decompose()

    markdown = md(
        str(soup),
        heading_style="ATX",
        bullets="•",
    )

    # Trix/Jotihunt HTML contains a lot of <br> elements,
    # which can result in excessive blank lines.
    markdown = re.sub(
        r"\n{3,}",
        "\n\n",
        markdown,
    )

    return (
        markdown.strip(),
        first_image_url,
    )


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

    return (
        value[: limit - 3].rstrip()
        + "..."
    )


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

    message = article.get(
        "message"
    )

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
        clean_html_to_discord(
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
        formatted_date = (
            format_dutch_date(
                publish_at
            )
        )
    else:
        formatted_date = (
            "Onbekende datum"
        )

    article_url = (
        f"{ARTICLE_BASE_URL}"
        f"{article_id}"
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