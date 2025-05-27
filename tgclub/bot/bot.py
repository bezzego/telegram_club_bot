from telegram.ext import (
    Updater,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    Filters,
)
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from .. import config

subscription_service = None
POST_CONTENT = 1


def is_admin(uid):
    return uid in config.ADMIN_IDS


def start(update, context):
    uid = update.effective_user.id
    uname = update.effective_user.username or update.effective_user.first_name
    pay_link, active_until = subscription_service.start_subscription(uid, uname)
    if active_until:
        update.message.reply_text(f"✔ Подписка активна до {active_until}")
    else:
        update.message.reply_text(f"Оформите подписку: {pay_link}")


def subscribe(update, context):
    start(update, context)


def admin_menu(update, context):
    uid = update.effective_user.id
    if not is_admin(uid):
        update.message.reply_text("❌ Доступ запрещён.")
        return
    kb = [["/list_users", "/send_post"]]
    update.message.reply_text(
        "Админ-панель:\n/list_users — список пользователей\n/send_post — отправить пост в канал",
        reply_markup=ReplyKeyboardMarkup(kb, one_time_keyboard=True),
    )


def list_users(update, context):
    uid = update.effective_user.id
    if not is_admin(uid):
        update.message.reply_text("❌ Доступ запрещён.")
        return
    users = subscription_service.user_repo.list_users_with_subscription()
    if not users:
        update.message.reply_text("Нет пользователей.")
        return
    lines = []
    for u in users:
        status = "-"
        if u["plan"]:
            status = (
                f"активна до {u['end_date']}"
                if u["active"]
                else f"истекла {u['end_date']}"
            )
        lines.append(
            f"ID {u['id']}: @{u['username'] or u['telegram_id']} — {u['plan'] or 'нет'} ({status})"
        )
    text = "\n".join(lines)
    update.message.reply_text(text)


def send_post_start(update, context):
    uid = update.effective_user.id
    if not is_admin(uid):
        update.message.reply_text("❌ Доступ запрещён.")
        return ConversationHandler.END
    update.message.reply_text(
        "Введите текст поста:", reply_markup=ReplyKeyboardRemove()
    )
    return POST_CONTENT


def send_post_receive(update, context):
    text = update.message.text
    try:
        subscription_service.telegram_service.bot.send_message(
            chat_id=config.TELEGRAM_CHANNEL_ID, text=text
        )
        update.message.reply_text("✅ Пост отправлен.")
    except Exception as e:
        update.message.reply_text(f"Ошибка: {e}")
    return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text("Отменено.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def start_bot(sub_service):
    global subscription_service
    subscription_service = sub_service
    updater = Updater(token=config.TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("subscribe", subscribe))
    dp.add_handler(CommandHandler("admin", admin_menu))
    dp.add_handler(CommandHandler("list_users", list_users))

    conv = ConversationHandler(
        entry_points=[CommandHandler("send_post", send_post_start)],
        states={
            POST_CONTENT: [
                MessageHandler(Filters.text & ~Filters.command, send_post_receive)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    dp.add_handler(conv)

    updater.start_polling()
    updater.idle()
