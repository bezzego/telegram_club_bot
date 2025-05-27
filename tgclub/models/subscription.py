from dataclasses import dataclass
from datetime import datetime


@dataclass
class Subscription:
    id: int
    user_id: int
    plan: str
    start_date: datetime
    end_date: datetime
    active: bool

    @staticmethod
    def from_row(row) -> "Subscription":
        return Subscription(
            id=row["id"],
            user_id=row["user_id"],
            plan=row["plan"],
            start_date=(
                datetime.fromisoformat(row["start_date"]) if row["start_date"] else None
            ),
            end_date=(
                datetime.fromisoformat(row["end_date"]) if row["end_date"] else None
            ),
            active=bool(row["active"]),
        )
