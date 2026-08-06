from typing import Literal

from pydantic import BaseModel


class AIMessage(BaseModel):
    """Сообщение для AI."""

    role: Literal[
        "system",
        "user",
        "assistant",
    ]

    content: str


class AIRequest(BaseModel):
    """Запрос к AI."""

    messages: list[AIMessage]


class AIResponse(BaseModel):
    """Ответ AI."""

    text: str