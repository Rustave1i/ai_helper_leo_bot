"""Immutable input and stored records for the standalone group journal."""
from dataclasses import dataclass
from enum import Enum


def integer(value: int, name: str, minimum: int = -(2**63)) -> None:
    if type(value) is not int or not minimum <= value < 2**63:
        raise ValueError(f"{name} must be a valid SQLite integer")


class IngestResult(str, Enum):
    INSERTED = "inserted"
    UPDATED = "updated"
    DUPLICATE = "duplicate"
    STALE = "stale"
    CONFLICT = "conflict"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class GroupChat:
    chat_id: int
    timezone: str
    retention_days: int
    observation_started_at: int
    collect_after: int
    enabled: bool = False


@dataclass(frozen=True, slots=True)
class GroupMessageEvent:
    chat_id: int
    message_id: int
    thread_id: int
    sender_kind: str
    text: str
    sent_at_utc_ms: int
    source_update_id: int
    sender_user_id: int | None = None
    sender_chat_id: int | None = None
    display_name: str | None = None
    author_signature: str | None = None
    sender_is_bot: bool | None = None
    edited_at_utc_ms: int | None = None
    reply_to_message_id: int | None = None

    def __post_init__(self) -> None:
        integer(self.chat_id, "chat_id")
        integer(self.message_id, "message_id", 1)
        integer(self.thread_id, "thread_id", 0)
        integer(self.sent_at_utc_ms, "sent_at_utc_ms", 0)
        integer(self.source_update_id, "source_update_id", 0)
        if self.edited_at_utc_ms is not None:
            integer(self.edited_at_utc_ms, "edited_at_utc_ms", self.sent_at_utc_ms)
        if self.reply_to_message_id is not None:
            integer(self.reply_to_message_id, "reply_to_message_id", 1)
        if self.sender_kind == "user":
            if self.sender_chat_id is not None:
                raise ValueError("User authors cannot have sender_chat_id")
            integer(self.sender_user_id, "sender_user_id", 1)
        elif self.sender_kind == "chat":
            if self.sender_user_id is not None:
                raise ValueError("Chat authors cannot have sender_user_id")
            integer(self.sender_chat_id, "sender_chat_id")
        elif self.sender_kind == "unknown":
            if self.sender_user_id is not None or self.sender_chat_id is not None:
                raise ValueError("Unknown authors cannot have an invented ID")
        else:
            raise ValueError("Unknown sender_kind")
        if self.sender_is_bot is not None and type(self.sender_is_bot) is not bool:
            raise ValueError("sender_is_bot must be bool or None")
        for name in ("display_name", "author_signature"):
            value = getattr(self, name)
            if value is not None and not isinstance(value, str):
                raise ValueError(f"{name} must be str or None")
        if not isinstance(self.text, str):
            raise ValueError("text must be str")


@dataclass(frozen=True, slots=True)
class JournalMessage:
    event: GroupMessageEvent
    first_received_at_utc_ms: int
    revision_received_at_utc_ms: int
    first_seen_as: str
