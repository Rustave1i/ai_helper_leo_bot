from enum import Enum


class ChatAction(Enum):
    CHAT = "chat"
    RESET = "reset"
    WEATHER = "weather"
    SEARCH = "search"
    NEWS = "news"
    IMAGE = "image"
    FILE = "file"