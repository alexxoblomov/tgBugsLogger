import requests
import json
from datetime import datetime


class SlackLogger:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def log_message(self, message_link: str, chat_name: str, user_name: str, topic_name: str, message_text: str):
        """Отправляет сообщение в Slack"""

        message = {
            "text": "*New message in followed topics*",
            "attachments": [
                {
                    "color": "#ff0000",  # Красный цвет для багов
                    "fields": [
                        {
                            "title": "Topic name",
                            "value": f"{topic_name}",
                            "short": True
                        },
                        {
                            "title": "Text",
                            "value": message_text,
                            "short": False
                        },
                        {
                            "title": "Link",
                            "value": message_link,
                            "short": False
                        },
                        {
                            "title": "User",
                            "value": user_name,
                            "short": True
                        }
                    ],
                    "footer": f"tgBugs Bot • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            ]
        }

        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(message),
                headers={'Content-Type': 'application/json'}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Ошибка отправки в Slack: {e}")
            return False