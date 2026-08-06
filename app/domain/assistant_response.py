from app.domain.base import DomainModel


class AssistantResponse(DomainModel):
    text: str | None = None