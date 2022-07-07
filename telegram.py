import requests


class TelegramNotifications:
    bot_token = ''
    bot_chatID = ''
    api_url = 'https://api.telegram.org/bot'

    @classmethod
    def send_notification(cls, msg):
        if len(msg) > 4096:
            msg = msg[0:4096]
        headers = {
            "Accept": "application/json",
            "User-Agent": "Telegram Bot SDK - (https://github.com/irazasyed/telegram-bot-sdk)",
            "Content-Type": "application/json"
        }
        response = requests.post(
            f"{cls.api_url}{cls.bot_token}/sendMessage",
            headers=headers,
            json={
                'chat_id': cls.bot_chatID,
                'parse_mode': "Markdown",
                'text': msg
            }
        )
        response.raise_for_status()
        return response.json()
