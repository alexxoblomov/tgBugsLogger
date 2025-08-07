from datetime import datetime, timedelta, timezone
from environs import Env
from aiogram import Router, F
from aiogram.types import Message
from utils.message_links import MessageLinkGenerator
from utils.link_logger import LinkLogger
from utils.slack_logger import SlackLogger

env = Env()
env.read_env()

router = Router()
link_logger = LinkLogger()

slack_webhook_url = env('SLACK_WEBHOOK_URL', default=None)
slack_logger = SlackLogger(slack_webhook_url)

allowed_topics = [2462438, 1410514]
chat_id = -1001529097328
topic_names = {2462438: "Баги с беты", 1410514: "Репорт багов"}

last_slack_sent_time = None

@router.message(
    (F.text | F.photo | F.video | F.document),
    F.chat.id == chat_id,
    F.message_thread_id.func(lambda x: x in allowed_topics)
)
async def handle_text_message(message: Message):
    """Текстовый хэндлер"""
    global last_slack_sent_time

    content = message.text or message.caption or ""
    message_link = MessageLinkGenerator.get_message_link(message)
    topic_id = message.message_thread_id
    topic_name = topic_names.get(topic_id, str(topic_id))

    now = datetime.now(timezone.utc)

    # Проверяем, прошло ли 15 минут с последней отправки
    if last_slack_sent_time is None or (now - last_slack_sent_time > timedelta(minutes=15)):
        if slack_logger:
            slack_logger.log_message(
                message_link,
                message.chat.title or message.chat.username or 'Приватный',
                message.from_user.full_name,
                topic_name,
                content
            )
            last_slack_sent_time = now  # обновляем время последней отправки

    link_logger.log_message_link(message)