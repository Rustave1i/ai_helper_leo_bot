from app.core.chat import chat


while True:

    text = input("Вы: ")

    if text.lower() in ("exit", "quit"):
        break

    answer = chat.process(
        user_id=1,
        text=text,
    )

    print("AI:", answer)