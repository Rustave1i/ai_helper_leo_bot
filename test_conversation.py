from app.core.chat import conversation

while True:

    text = input("Вы: ")

    if text == "/exit":
        break

    answer = conversation.ask(
        user_id=1,
        text=text,
    )

    print("AI:", answer)