import logging
from datetime import datetime
from aiogram.types import Message
from utils.message_links import MessageLinkGenerator


class LinkLogger:
    """Класс для логирования ссылок на сообщения"""

    def __init__(self, log_file: str = 'message_links.log'):
        self.logger = logging.getLogger('link_logger')
        self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def log_message_link(self, message: Message, additional_info: dict = None):
        """Логирует ссылку на сообщение с дополнительной информацией"""

        message_link = MessageLinkGenerator.get_message_link(message)
        chat_info = MessageLinkGenerator.get_chat_info(message)
        text = message.text or message.caption or "",

        log_data = {
            'timestamp': datetime.now().isoformat(),
            'message_id': message.message_id,
            'chat_id': message.chat.id,
            'chat_type': message.chat.type,
            'chat_title': message.chat.title,
            'chat_username': message.chat.username,
            'user_id': message.from_user.id,
            'user_name': message.from_user.full_name,
            'user_username': message.from_user.username,
            'message_link': message_link,
            'message_text': text[:200] + '...' if len(text) > 200 else text,
            'additional_info': additional_info or {}
        }

        log_message = (
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"Ссылка: {log_data['message_link']} | "
            f"Чат: {log_data['chat_title'] or chat_info['username'] or 'Приватный'} | "
            f"Пользователь: {log_data['user_name']}"
        )

        self.logger.info(log_message)
        return log_data