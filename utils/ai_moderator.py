import json
from groq import AsyncGroq
from environs import Env

env = Env()
env.read_env()

# Настройка Groq
groq_api_key = env('GROQ_API_KEY', default=None)
client = AsyncGroq(api_key=groq_api_key) if groq_api_key else None

SYSTEM_PROMPT = """Ты строгий модератор баг-репортов мобильной игры.

Твоя задача — определить, является ли сообщение ПОЛНОЦЕННЫМ баг-репортом.

ОТКЛОНЯЙ (is_valid: false), если:
- Флуд, приветствия, оффтоп, эмоции без сути ("опять баги!", "разрабы, фиксите!")
- Вопросы ("почему не работает?", "когда пофиксят?", "у кого такое?")
- Обсуждения и ответы другим пользователям
- Сообщения с цитированием (содержат ">" в начале строк или упоминания других игроков)
- Жалобы на геймплей/баланс/контент (это не технические баги)
- Неполные репорты без устройства ИЛИ без ID игрока

ПРОПУСКАЙ сообщение (is_valid: true), ЕСЛИ СОБЛЮДЕНЫ ВСЕ ТРИ УСЛОВИЯ:
1. Описана КОНКРЕТНАЯ техническая проблема (вылет, краш, зависание, графический глюк, ошибка загрузки)
2. Указано устройство (явно или неявно: "самсунг", "айфон", "на андроиде", "ios")
3. Есть ID игрока или игровой ник

ПРИЗНАКИ ЦИТИРОВАНИЯ (отклоняй такие сообщения):
- Текст начинается с ">" 
- Есть фразы типа "@username", "как сказал выше", "отвечу на это", "согласен с"
- Обращение к конкретному человеку по имени

Примеры ОТКЛОНИТЬ:
- "опять баги после обнова" — нет конкретики, устройства, ID
- "у меня тоже такое" — ответ другому, нет деталей  
- "> вылетает игра\nда, подтверждаю" — цитирование
- "почему не заходит в игру?" — вопрос без информации

Примеры ПРОПУСТИТЬ:
- "На Samsung A52 вылетает при входе в магазин, ID 123456" — есть всё
- "Айфон 13, ник Player_99, не грузятся текстуры в городе" — есть всё

Верни ТОЛЬКО JSON без markdown-форматирования:
{
  "is_valid": true/false,
  "reason": "краткое пояснение решения (почему одобрено или отклонено)"
}"""


async def validate_bug_report(text: str) -> dict:
    """
    Проверяет сообщение через AI и возвращает результат валидации.
    
    Returns:
        dict: {
            "is_valid": bool,
            "reason": str | None
        }
    """
    if not text or not text.strip():
        return {
            "is_valid": False,
            "reason": "Пустое сообщение"
        }
    
    # Если AI не настроен — пропускаем все сообщения
    if not client:
        return {
            "is_valid": False,
            "reason": "AI не настроен (GROQ_API_KEY отсутствует)"
        }
    
    try:
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Очищаем ответ от возможных markdown-блоков
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        response_text = response_text.strip()
        
        return json.loads(response_text)
        
    except Exception as e:
        # В случае ошибки AI — пропускаем сообщение
        print(f"AI validation error: {e}")
        return {
            "is_valid": False,
            "reason": "AI недоступен, требуется ручная проверка"
        }
