from app.core.ai import ai
from app.core.ai.prompts import SYSTEM_PROMPT


messages = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT,
    },
    {
        "role": "user",
        "content": "Привет! Представься одним предложением.",
    },
]

answer = ai.ask(messages)

print(answer)