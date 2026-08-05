PRAGMA foreign_keys = ON;

-- =====================================================
-- Chats
-- =====================================================

CREATE TABLE IF NOT EXISTS Chats (
    telegram_chat_id INTEGER PRIMARY KEY,
    type TEXT NOT NULL,
    title TEXT,
    username TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- =====================================================
-- Users
-- =====================================================

CREATE TABLE IF NOT EXISTS Users (
    telegram_user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT NOT NULL,
    last_name TEXT,
    language_code TEXT,
    is_bot INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- =====================================================
-- Messages
-- =====================================================

CREATE TABLE IF NOT EXISTS Messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    telegram_message_id INTEGER NOT NULL,

    chat_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,

    reply_to_message_id INTEGER,

    text TEXT,

    created_at TEXT NOT NULL,
    edited_at TEXT,

    is_deleted INTEGER NOT NULL DEFAULT 0,

    FOREIGN KEY (chat_id)
        REFERENCES Chats(telegram_chat_id),

    FOREIGN KEY (user_id)
        REFERENCES Users(telegram_user_id),

    UNIQUE(chat_id, telegram_message_id)
);

-- =====================================================
-- MessageHistory
-- =====================================================

CREATE TABLE IF NOT EXISTS MessageHistory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    message_id INTEGER NOT NULL,

    text TEXT NOT NULL,

    edited_at TEXT NOT NULL,

    FOREIGN KEY (message_id)
        REFERENCES Messages(id)
);

-- =====================================================
-- Indexes
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_messages_chat
ON Messages(chat_id);

CREATE INDEX IF NOT EXISTS idx_messages_user
ON Messages(user_id);

CREATE INDEX IF NOT EXISTS idx_messages_created
ON Messages(created_at);

CREATE INDEX IF NOT EXISTS idx_history_message
ON MessageHistory(message_id);