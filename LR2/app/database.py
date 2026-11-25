import sqlite3
from pathlib import Path


def connect(db_path: str):
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db(db_path: str):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    with connect(db_path) as connection:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'OPEN',
                priority TEXT NOT NULL DEFAULT 'medium',
                assignee_id INTEGER,
                created_at TEXT NOT NULL,
                FOREIGN KEY (assignee_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                issue_id INTEGER NOT NULL,
                author_id INTEGER NOT NULL,
                body TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (issue_id) REFERENCES issues(id),
                FOREIGN KEY (author_id) REFERENCES users(id)
            );
        """)

        connection.execute(
            "INSERT OR IGNORE INTO users (id, name) VALUES (1, 'Agent A')"
        )
        connection.execute(
            "INSERT OR IGNORE INTO users (id, name) VALUES (2, 'Agent B')"
        )
