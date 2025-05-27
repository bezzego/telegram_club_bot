from datetime import datetime, timedelta
from typing import Optional, List
from ..database import get_connection
from ..models.subscription import Subscription


class SubscriptionRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_by_user(self, user_id: int) -> Optional[Subscription]:
        conn = get_connection(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM subscriptions WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        conn.close()
        return Subscription.from_row(row) if row else None

    def upsert_subscription(
        self, user_id: int, plan: str, duration_days: int
    ) -> Subscription:
        conn = get_connection(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM subscriptions WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        from datetime import datetime

        now = datetime.now()
        if row:
            sub = Subscription.from_row(row)
            from datetime import datetime

            base_date = (
                datetime.fromisoformat(sub.end_date)
                if (sub.end_date and datetime.fromisoformat(sub.end_date) > now)
                else now
            )
            new_end = base_date + timedelta(days=duration_days)
            cur.execute(
                """UPDATE subscriptions SET plan = ?, start_date = ?, end_date = ?, active = 1
                   WHERE user_id = ?""",
                (
                    plan,
                    now.isoformat(sep=" ", timespec="seconds"),
                    new_end.isoformat(sep=" ", timespec="seconds"),
                    user_id,
                ),
            )
        else:
            from datetime import datetime

            start_date = now
            end_date = start_date + timedelta(days=duration_days)
            cur.execute(
                """INSERT INTO subscriptions (user_id, plan, start_date, end_date, active)
                   VALUES (?, ?, ?, ?, 1)""",
                (
                    user_id,
                    plan,
                    start_date.isoformat(sep=" ", timespec="seconds"),
                    end_date.isoformat(sep=" ", timespec="seconds"),
                ),
            )
        conn.commit()
        cur.execute("SELECT * FROM subscriptions WHERE user_id = ?", (user_id,))
        new_row = cur.fetchone()
        conn.close()
        return Subscription.from_row(new_row)

    def set_inactive(self, user_id: int):
        conn = get_connection(self.db_path)
        cur = conn.cursor()
        cur.execute("UPDATE subscriptions SET active = 0 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()

    def get_active_subscriptions(self) -> List[Subscription]:
        conn = get_connection(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM subscriptions WHERE active = 1")
        rows = cur.fetchall()
        conn.close()
        return [Subscription.from_row(row) for row in rows]
