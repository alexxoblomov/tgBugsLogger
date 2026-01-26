from environs import Env
from aiogram import Router, F
from aiogram.types import Message
from utils.message_links import MessageLinkGenerator
from utils.link_logger import LinkLogger
from utils.slack_logger import SlackLogger
from utils.ai_moderator import validate_bug_report

env = Env()
env.read_env()

router = Router()
link_logger = LinkLogger()

slack_webhook_url = env('SLACK_WEBHOOK_URL', default=None)
slack_logger = SlackLogger(slack_webhook_url)

allowed_topics = [2918475, 1410514]
chat_id = -1001529097328
topic_names = {2918475: "Баги с беты", 1410514: "Репорт багов"}


@router.message(
    (F.text | F.photo | F.video | F.document),
    F.chat.id == chat_id,
    F.message_thread_id.func(lambda x: x in allowed_topics)
)
async def handle_text_message(message: Message):
    """Текстовый хэндлер"""

    content = message.text or message.caption or ""
    message_link = MessageLinkGenerator.get_message_link(message)
    topic_id = message.message_thread_id
    topic_name = topic_names.get(topic_id, str(topic_id))

    # Проверяем, это reply на реального пользователя?
    reply = message.reply_to_message
    is_reply_to_user = reply and reply.from_user and not reply.forum_topic_created

    # AI-модерация для всех топиков
    validation = await validate_bug_report(content)
    should_send_to_slack = validation.get("is_valid", False)

    # Отправка в Slack: AI одобрил И это не reply на пользователя
    if should_send_to_slack and not is_reply_to_user and slack_logger:
        slack_logger.log_message(
            message_link,
            message.chat.title or message.chat.username or 'Приватный',
            message.from_user.full_name,
            topic_name,
            content
        )

    link_logger.log_message_link(message, additional_info={
    "is_valid": validation.get("is_valid"),
    "reason": validation.get("reason")})