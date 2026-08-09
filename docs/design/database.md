Chats
| Поле             | Тип            | Описание                               |
| ---------------- | -------------- | -------------------------------------- |
| id               | INTEGER PK     | Внутренний идентификатор               |
| telegram_chat_id | INTEGER UNIQUE | ID чата Telegram                       |
| type             | TEXT           | private / group / supergroup / channel |
| title            | TEXT           | Название чата                          |
| username         | TEXT           | Username (если есть)                   |
| created_at       | DATETIME       | Когда запись появилась                 |
| updated_at       | DATETIME       | Последнее обновление                   |


Users
| Поле             | Тип            | Описание          |
| ---------------- | -------------- | ----------------- |
| id               | INTEGER PK     | Внутренний ID     |
| telegram_user_id | INTEGER UNIQUE | Telegram ID       |
| username         | TEXT           | username          |
| first_name       | TEXT           | Имя               |
| last_name        | TEXT           | Фамилия           |
| language_code    | TEXT           | Язык              |
| is_bot           | BOOLEAN        | Является ли ботом |
| created_at       | DATETIME       | Создан            |
| updated_at       | DATETIME       | Обновлен          |


Messages
| Поле                | Тип           | Описание                 |
| ------------------- | ------------- | ------------------------ |
| id                  | INTEGER PK    | Внутренний ID            |
| telegram_message_id | INTEGER       | ID сообщения Telegram    |
| chat_id             | INTEGER FK    | Ссылка на Chats          |
| user_id             | INTEGER FK    | Автор                    |
| reply_to_message_id | INTEGER NULL  | Ответ на сообщение       |
| text                | TEXT          | Текст                    |
| created_at          | DATETIME      | Время сообщения          |
| edited_at           | DATETIME NULL | Последнее редактирование |
| is_deleted          | BOOLEAN       | Удалено ли сообщение     |


MessageHistory
| Поле       | Тип        | Описание            |
| ---------- | ---------- | ------------------- |
| id         | INTEGER PK | Внутренний ID       |
| message_id | INTEGER FK | Ссылка на Messages  |
| text       | TEXT       | Предыдущая версия   |
| edited_at  | DATETIME   | Когда была заменена |

