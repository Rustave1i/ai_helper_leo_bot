import asyncio

from app.infrastructure.ai.models import (
    AIMessage,
    AIRequest,
)
from app.infrastructure.ai.openrouter import OpenRouterClient


async def main() -> None:
    client = OpenRouterClient()

    try:
        response = await client.generate(
            AIRequest(
                messages=[
                    AIMessage(
                        role="system",
                        content="Ты помощник Leo.",
                    ),
                    AIMessage(
                        role="user",
                        content="Ответь одним словом: привет",
                    ),
                ],
            ),
        )

        print("\n========== AI RESPONSE ==========")
        print(response.text)
        print("=================================\n")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())