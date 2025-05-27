from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    id: int
    telegram_id: int
    username: str
    created_at: datetime

    @staticmethod
    def from_row(row) -> "User":
        return User(
            id=row["id"],
            telegram_id=row["telegram_id"],
            username=row["username"],
            created_at=(
                datetime.fromisoformat(row["created_at"]) if row["created_at"] else None
            ),
        )
