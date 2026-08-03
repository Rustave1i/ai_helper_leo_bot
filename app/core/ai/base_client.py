from abc import ABC, abstractmethod

from app.core.models import Message


class BaseAIClient(ABC):

    @abstractmethod
    def ask(
        self,
        messages: list[Message],
    ) -> str:
        pass