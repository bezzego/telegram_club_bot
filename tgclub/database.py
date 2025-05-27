import sqlite3
from sqlite3 import Connection


def get_connection(db_path: str) -> Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str):
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS users (
             id          INTEGER PRIMARY KEY AUTOINCREMENT,
             telegram_id INTEGER UNIQUE,
             username    TEXT,
             created_at  TEXT
           );"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS subscriptions (
             id          INTEGER PRIMARY KEY AUTOINCREMENT,
             user_id     INTEGER UNIQUE,
             plan        TEXT,
             start_date  TEXT,
             end_date    TEXT,
             active      INTEGER,
             FOREIGN KEY(user_id) REFERENCES users(id)
           );"""
    )
    conn.commit()
    conn.close()
