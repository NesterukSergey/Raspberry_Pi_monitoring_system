import sys
print(sys.executable)

import telegram


class TelegramBot:
    def __init__(self, token):
        self.bot = telegram.Bot(token=token)

    def send_message(self, chat_id, text):
        self.bot.send_message(chat_id=chat_id, text=text)
