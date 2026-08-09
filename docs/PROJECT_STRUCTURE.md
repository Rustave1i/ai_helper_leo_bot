# PROJECT_STRUCTURE

Статус: Active
Версия: 1.0
Последнее обновление: 05.08.2026

---

# Назначение

Данный документ описывает архитектуру проекта Leo.

Каждый компонент имеет одну ответственность и взаимодействует только через разрешенные зависимости.

---

# Общая схема

                Telegram
                    │
                    ▼
          Telegram Adapter
                    │
                    ▼
         Conversation Store
               (SQLite)
                    │
                    ▼
               Platform API
                    │
                    ▼
                 Leo AI
                    │
                    ▼
              Telegram Adapter
                    │
                    ▼
                Пользователь

---

# Структура проекта

app/

├── adapters/
├── leo/
├── platform/
├── models/
├── config.py
└── main.py

---

# adapters/

Внешние интеграции.

На данном этапе содержит только Telegram Adapter.

Ответственность:

- получение Update;
- отправка сообщений;
- никаких интеллектуальных решений.

---

# platform/

Инфраструктура платформы.

Содержит:

- Conversation Store;
- Repository;
- Platform API.

Platform не знает ничего об AI.

---

# leo/

Интеллект платформы.

Содержит:

- AI Engine;
- Prompt Builder;
- Model Provider.

Только здесь принимаются решения.

---

# models/

Общие модели приложения.

Например:

- User
- Chat
- Message
- SearchResult

Модели не содержат бизнес-логики.

---

# Разрешенные зависимости

Telegram Adapter

↓

Platform

↓

Leo AI

---

Leo AI

↓

Platform API

---

Platform API

↓

Conversation Store

---

Repository

↓

SQLite

---

# Запрещенные зависимости

AI

✗ SQLite

---

SQLite

✗ AI

---

Telegram Adapter

✗ Repository

---

Repository

✗ Telegram

---

Platform API

✗ Telegram

---

# Главный принцип

Каждый компонент знает только то, что необходимо ему для выполнения своей задачи.

Ни один компонент не должен знать внутреннее устройство другого компонента.