from app.models.chat_action import ChatAction


class IntentRouter:
    """Определяет намерение пользователя."""

    RESET_PATTERNS = (
        "очисти память",
        "сбрось память",
        "очисти историю",
        "сбрось историю",
        "сбрось диалог",
        "очисти диалог",
        "начнем сначала",
        "начать сначала",
        "забудь всё",
        "забудь все",
    )

    WEATHER_PATTERNS = (
        "погода",
        "температура",
        "дождь",
        "снег",
        "ветер",
        "прогноз",
    )

    def detect(self, message: str) -> ChatAction:
        """
        Определяет действие пользователя.
        """

        text = message.lower().strip()

        for pattern in self.RESET_PATTERNS:
            if pattern in text:
                return ChatAction.RESET

        return ChatAction.CHAT