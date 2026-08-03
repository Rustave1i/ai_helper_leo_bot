from enum import Enum


class AIProvider(str, Enum):
    GEMINI = "gemini"
    MISTRAL = "mistral"
    OPENROUTER = "openrouter"