from telegram import Bot


class TelegramService:
    def __init__(self, bot_token: str, channel_id):
        self.bot = Bot(token=bot_token)
        self.channel_id = channel_id

    def send_message_to_user(self, telegram_id: int, text: str):
        self.bot.send_message(chat_id=telegram_id, text=text)

    def create_invite_link(self) -> str:
        invite = self.bot.create_chat_invite_link(
            chat_id=self.channel_id, member_limit=1
        )
        return invite.invite_link

    def remove_user_from_channel(self, user_telegram_id: int):
        self.bot.ban_chat_member(chat_id=self.channel_id, user_id=user_telegram_id)
        self.bot.unban_chat_member(chat_id=self.channel_id, user_id=user_telegram_id)
