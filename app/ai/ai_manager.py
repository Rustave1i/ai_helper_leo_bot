from app.ai.providers import AIProvider
from app.ai.gemini_client import GeminiClient
from app.ai.mistral_client import MistralClient
from app.config import AI_PROVIDER


class AIManager:
    """
    Управляет всеми AI-провайдерами.
    """

    def __init__(self):

        self.providers = {
            AIProvider.GEMINI: GeminiClient(),
            AIProvider.MISTRAL: MistralClient(),
        }

        try:
            self.current = AIProvider(
                AI_PROVIDER.lower()
            )

        except ValueError:

            self.current = AIProvider.MISTRAL

    def ask(
        self,
        messages: list[dict],
    ) -> str:

        provider = self.providers[self.current]

        return provider.ask(messages)

    def get_provider(self):

        return self.current

    def set_provider(
        self,
        provider: AIProvider,
    ):

        if provider not in self.providers:
            raise ValueError(
                f"Провайдер {provider} не зарегистрирован."
            )

        self.current = provider

    def available(self):

        return list(self.providers.keys())