from google import genai

from app.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
)

from .base_client import BaseAIClient


class GeminiClient(BaseAIClient):

    def __init__(self):

        self.client = genai.Client(
            api_key=GEMINI_API_KEY,
        )

    def ask(
        self,
        messages: list[dict],
    ) -> str:

        prompt = []

        for message in messages:

            role = message["role"]

            if role == "assistant":
                role = "model"

            prompt.append(
                {
                    "role": role,
                    "parts": [
                        {
                            "text": message["content"]
                        }
                    ],
                }
            )

        response = self.client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )

        return response.text