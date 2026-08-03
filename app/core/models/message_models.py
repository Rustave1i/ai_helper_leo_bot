from dataclasses import dataclass

from .enums import Role


@dataclass(slots=True)
class Message:
    role: Role
    content: str