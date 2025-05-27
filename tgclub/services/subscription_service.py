from datetime import datetime, timedelta
import logging


class SubscriptionService:
    def __init__(self, user_repo, sub_repo, payment_service, telegram_service):
        self.user_repo = user_repo
        self.sub_repo = sub_repo
        self.payment_service = payment_service
        self.telegram_service = telegram_service
        self._last_check = datetime.utcnow() - timedelta(minutes=2)

    def start_subscription(self, telegram_id, username):
        user = self.user_repo.create_user(telegram_id, username)
        sub = self.sub_repo.get_by_user(user.id)
        if sub and sub.active and datetime.fromisoformat(sub.end_date) > datetime.now():
            return None, sub.end_date
        payment_link = self.payment_service.create_payment_link(user.id)
        logging.info(f"User {user.id} initiated subscription.")
        return payment_link, None

    def activate_subscription(self, user_id, plan="monthly"):
        days = 30 if plan == "monthly" else 90
        sub = self.sub_repo.upsert_subscription(user_id, plan, days)
        try:
            link = self.telegram_service.create_invite_link()
            self.telegram_service.send_message_to_user(
                user_id, f"Вступите в канал: {link}"
            )
            logging.info(f"Activated subscription for {user_id} until {sub.end_date}")
        except Exception as e:
            logging.error(f"Invite send failed for {user_id}: {e}")
        return sub

    def check_payments(self):
        now = datetime.utcnow()
        try:
            payments = self.payment_service.fetch_new_payments(self._last_check)
            for tx in payments:
                oid = tx.get("order_id", "")
                try:
                    uid = int(oid.split("-", 1)[0])
                except:
                    continue
                self.activate_subscription(uid)
            self._last_check = now
        except Exception as e:
            logging.error(f"Error during polling payments: {e}")

    def remind_subscriptions(self):
        now = datetime.now()
        for sub in self.sub_repo.get_active_subscriptions():
            end = datetime.fromisoformat(sub.end_date)
            if (end.date() - now.date()).days == 2:
                user = self.user_repo.get_by_id(sub.user_id)
                if user:
                    self.telegram_service.send_message_to_user(
                        user.telegram_id, "Напоминание: до окончания подписки 2 дня."
                    )
                    logging.info(f"Reminder sent to {user.id}")

    def remove_expired_subscriptions(self):
        now = datetime.now()
        for sub in self.sub_repo.get_active_subscriptions():
            end = datetime.fromisoformat(sub.end_date)
            if end <= now:
                user = self.user_repo.get_by_id(sub.user_id)
                if user:
                    try:
                        self.telegram_service.remove_user_from_channel(user.telegram_id)
                        logging.info(f"Removed {user.id} (expired)")
                    except Exception as e:
                        logging.error(f"Removal failed for {user.id}: {e}")
                self.sub_repo.set_inactive(sub.user_id)
