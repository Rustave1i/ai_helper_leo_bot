from dataclasses import dataclass


@dataclass(slots=True)
class NewsArticle:
    title: str
    description: str
    url: str