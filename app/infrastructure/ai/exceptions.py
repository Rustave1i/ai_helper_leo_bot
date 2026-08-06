class AIError(Exception):
    """Базовая ошибка AI."""


class AIConnectionError(AIError):
    """Ошибка подключения к AI."""


class AIResponseError(AIError):
    """Ошибка ответа AI."""