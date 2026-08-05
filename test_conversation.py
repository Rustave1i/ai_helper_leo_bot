import asyncio

from app.core.chat import chat


async def main() -> None:

    while True:

        text = input("Вы: ")

        if text.lower() in (
            "exit",
            "quit",
        ):
            break

        answer = await chat.process(
            user_id=1,
            text=text,
        )

        print("AI:", answer)


if __name__ == "__main__":

    asyncio.run(
        main()
    )