import json
import logging
from pathlib import Path


logger = logging.getLogger(__name__)


class SentArticleRepository:
    def __init__(
        self,
        path: Path,
    ):
        self.path = path
        self.article_ids: set[str] = set()

    def load(self) -> None:
        if not self.path.exists():
            logger.info(
                "Sent articles file does not exist yet: %s",
                self.path,
            )
            return

        try:
            with self.path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

            if not isinstance(
                data,
                list,
            ):
                raise ValueError(
                    "Sent articles file must contain a JSON array"
                )

            self.article_ids = {
                str(article_id)
                for article_id in data
            }

            logger.info(
                "Loaded %d previously sent articles",
                len(self.article_ids),
            )

        except (
            OSError,
            json.JSONDecodeError,
            ValueError,
        ):
            logger.exception(
                "Failed to read sent articles file"
            )

            self.article_ids = set()

    def contains(
        self,
        article_id: str,
    ) -> bool:
        return (
            article_id
            in self.article_ids
        )

    def add(
        self,
        article_id: str,
    ) -> None:
        self.article_ids.add(
            article_id
        )

        self.save()

    def save(self) -> None:
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary_path = (
            self.path.with_suffix(
                f"{self.path.suffix}.tmp"
            )
        )

        try:
            with temporary_path.open(
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    sorted(
                        self.article_ids
                    ),
                    file,
                    indent=2,
                )

            temporary_path.replace(
                self.path
            )

        except OSError:
            logger.exception(
                "Failed to save sent articles"
            )
