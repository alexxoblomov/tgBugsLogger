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

        if additional_info:
            reason = additional_info.get("reason", "—")
            if additional_info.get("is_valid"):
                validation_status = f"[APPROVED: {reason}]"
            else:
                validation_status = f"[REJECTED: {reason}]"

        log_message = (
            f"{validation_status} "
            f"Ссылка: {message_link} | "
            f"Чат: {chat_info.get('title') or chat_info.get('username') or 'Приватный'} | "
            f"Пользователь: {message.from_user.full_name}"
        )

        self.logger.info(log_message)