import logging
import threading
from tgclub import config, database
from tgclub.repositories.user_repository import UserRepository
from tgclub.repositories.subscription_repository import SubscriptionRepository
from tgclub.services.payment_service import PaymentService
from tgclub.services.telegram_service import TelegramService
from tgclub.services.subscription_service import SubscriptionService
from tgclub.bot.bot import start_bot
from apscheduler.schedulers.background import BackgroundScheduler

# Настройка логирования
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def main():
    # Инициализация БД
    database.init_db(config.DB_PATH)

    # Репозитории
    user_repo = UserRepository(config.DB_PATH)
    sub_repo = SubscriptionRepository(config.DB_PATH)

    # Сервисы
    payment_service = PaymentService(
        config.PRODAMUS_FORM_URL, config.PRODAMUS_SECRET_KEY
    )
    telegram_service = TelegramService(
        config.TELEGRAM_TOKEN, config.TELEGRAM_CHANNEL_ID
    )
    subscription_service = SubscriptionService(
        user_repo, sub_repo, payment_service, telegram_service
    )

    # Запуск Telegram-бота
    bot_thread = threading.Thread(target=start_bot, args=(subscription_service,))
    bot_thread.daemon = True
    bot_thread.start()

    # Планировщик задач
    scheduler = BackgroundScheduler()
    scheduler.add_job(subscription_service.check_payments, "interval", minutes=1)
    scheduler.add_job(subscription_service.remind_subscriptions, "interval", days=1)
    scheduler.add_job(
        subscription_service.remove_expired_subscriptions, "interval", days=1
    )
    scheduler.start()

    # Удерживаем основной поток
    bot_thread.join()


if __name__ == "__main__":
    main()
