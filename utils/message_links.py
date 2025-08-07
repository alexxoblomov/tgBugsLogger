from aiogram.types import Message
from typing import Optional


class MessageLinkGenerator:
    """Класс для генерации ссылок на сообщения"""

    @staticmethod
    def create_public_link(message: Message) -> str:
        """Создает ссылку для публичных каналов/групп"""
        if message.chat.username:
            return f"https://t.me/{message.chat.username}/{message.message_id}"
        return None


    @staticmethod
    def get_message_link(message: Message) -> Optional[str]:
        """Получает ссылку на сообщение в зависимости от типа чата"""
        public_link = MessageLinkGenerator.create_public_link(message)
        return public_link


    @staticmethod
    def get_chat_info(message: Message) -> dict:
        """Получает информацию о чате"""
        return {
            'id': message.chat.id,
            'type': message.chat.type,
            'title': message.chat.title,
            'username': message.chat.username,
            'is_public': bool(message.chat.username)
        }