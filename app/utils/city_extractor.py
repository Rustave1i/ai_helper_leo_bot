import re


class CityExtractor:
    """Извлекает название города из текста."""

    PATTERNS = (
        r"\bв\s+([А-ЯA-ZЁ][А-ЯA-Zа-яa-zё\-\s]+)",
        r"\bдля\s+([А-ЯA-ZЁ][А-ЯA-Zа-яa-zё\-\s]+)",
    )

    def extract(self, message: str) -> str | None:

        text = message.strip()

        for pattern in self.PATTERNS:

            match = re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            )

            if match:
                city = match.group(1).strip()

                city = city.rstrip("?.!,:")

                return city

        return None