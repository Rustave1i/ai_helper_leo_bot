# AI Helper Bot — Architecture

## Цель проекта

AI Helper Bot — модульный Telegram-бот с поддержкой нескольких AI-провайдеров, инструментов (Tools) и возможностью дальнейшего масштабирования.

Основные цели архитектуры:

- простое добавление новых AI-моделей;
- разделение ответственности между слоями;
- минимальная связанность компонентов;
- возможность замены любой реализации без изменения остального кода.

---

# Архитектура

```
Telegram
    │
    ▼
Handlers
    │
    ▼
Chat Engine
    │
 ┌──┴─────────────┐
 │                │
 ▼                ▼
AI Engine     Tool Manager
 │                │
 ▼                ▼
Clients      Services
 │
 ▼
External APIs

Conversation Memory
```

---

# Структура проекта

```
app/
│
├── core/
│   ├── ai/
│   ├── chat/
│   ├── memory/
│   ├── models/
│   ├── services/
│   └── tools/
│
├── handlers/
├── data/
├── utils/
├── bot.py
└── config.py
```

---

# Ответственность модулей

## AI

Отвечает только за работу с языковыми моделями.

Не знает ничего про Telegram, память или инструменты.

Примеры:

- Gemini
- Mistral
- DeepSeek
- Claude

---

## Chat

Главный оркестратор проекта.

Отвечает за:

- получение сообщения;
- работу с памятью;
- вызов AI;
- вызов ToolManager;
- формирование ответа.

---

## Memory

Отвечает только за хранение истории сообщений.

В будущем возможны реализации:

- InMemory
- SQLite
- Redis

---

## Services

Работают с внешними API.

Например:

- OpenWeather
- News API
- Search API

Service ничего не знает о Telegram и AI.

---

## Tools

Инструменты, которые определяют:

"Нужно ли использовать сервис?"

Например:

WeatherTool

↓

WeatherService

↓

OpenWeather API

---

## Models

Типизированные объекты проекта.

Например:

- Message
- Weather
- News

---

# Правила зависимостей

Разрешенные зависимости:

Chat
↓
AI

Chat
↓
Memory

Chat
↓
Tools

Tools
↓
Services

Services
↓
External APIs

Запрещено:

AI → Telegram

AI → Services

Services → Telegram

Tools → AI

Memory → Telegram

---

# Правила именования

## AI

```
*_client.py
```

Пример:

```
gemini_client.py
mistral_client.py
```

---

## Services

```
*_service.py
```

Пример:

```
weather_service.py
search_service.py
```

---

## Tools

```
*_tool.py
```

Пример:

```
weather_tool.py
news_tool.py
```

---

## Memory

```
*_memory.py
*_store.py
```

---

## Models

```
*_models.py
```

---

# Принципы разработки

1. Один класс — одна ответственность.

2. Engine координирует работу, но не содержит бизнес-логику сервисов.

3. Services работают только с внешними API.

4. Tools принимают решение о вызове сервисов.

5. AI не знает о Telegram.

6. Telegram не знает о внутренней реализации AI.

7. Любой компонент можно заменить без изменения остальных.

---

# Roadmap

- [x] AI Engine
- [ ] Conversation Engine
- [ ] Memory
- [ ] Tool Manager
- [ ] Telegram Adapter
- [ ] SQLite
- [ ] RAG
- [ ] Plugins