-- BookNest database (SQLite). Run automatically by backend/db.py on first start.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    user_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name              TEXT NOT NULL,
    email             TEXT NOT NULL UNIQUE,
    password          TEXT NOT NULL,                 -- hashed, never plain text
    registration_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS books (                   -- the "Products" table
    book_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    title       TEXT NOT NULL,
    author      TEXT NOT NULL,
    category    TEXT NOT NULL,
    price       REAL NOT NULL CHECK (price >= 0),
    description TEXT,
    image       TEXT,                                -- uploaded file name (optional)
    created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (                -- contact / feedback
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name  TEXT NOT NULL,
    email      TEXT NOT NULL,
    message    TEXT NOT NULL,
    date       TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS favorites (               -- wishlist (users <-> books)
    user_id    INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    book_id    INTEGER NOT NULL REFERENCES books(book_id) ON DELETE CASCADE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, book_id)
);
