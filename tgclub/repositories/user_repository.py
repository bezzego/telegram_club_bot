from typing import Optional, List
from ..database import get_connection
from ..models.user import User


class UserRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def create_user(self, telegram_id: int, username: Optional[str] = None) -> User:
        conn = get_connection(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """INSERT OR IGNORE INTO users (telegram_id, username, created_at)
                VALUES (?, ?, datetime('now'))""",
            (telegram_id, username),
        )
        conn.commit()
        cur.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        row = cur.fetchone()
        conn.close()
        return User.from_row(row)

    def get_by_id(self, user_id: int) -> Optional[User]:
        conn = get_connection(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        conn.close()
        return User.from_row(row) if row else None

    def list_users_with_subscription(self) -> List[dict]:
        conn = get_connection(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """SELECT u.id as user_id, u.telegram_id, u.username,
                          s.plan, s.end_date, s.active
               FROM users u
               LEFT JOIN subscriptions s ON u.id = s.user_id"""
        )
        rows = cur.fetchall()
        conn.close()
        users = []
        for row in rows:
            users.append(
                {
                    "id": row["user_id"],
                    "telegram_id": row["telegram_id"],
                    "username": row["username"],
                    "plan": row["plan"],
                    "end_date": row["end_date"],
                    "active": (
                        bool(row["active"]) if row["active"] is not None else False
                    ),
                }
            )
        return users
