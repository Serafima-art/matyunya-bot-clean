# gpt/gpt_utils.py

import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from openai import OpenAI
from dotenv import load_dotenv
import logging

# --- НАСТРОЙКА ---
load_dotenv(Path(__file__).resolve().parent.parent / ".env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
logger = logging.getLogger(__name__)

# --- СИСТЕМНЫЙ ПРОМПТ ДЛЯ ОБРАТНОЙ СОВМЕСТИМОСТИ (УСИЛЕННЫЙ) ---
DEFAULT_SYSTEM_PROMPT_FOR_GENERATION = (
    "Ты — добрый и очень внимательный AI-репетитор 'Матюня'. Твоя задача — сгенерировать математическую задачу для 9 класса в стиле ОГЭ (сборник Ященко 2025). "
    "Будь креативным, но реалистичным. Текст задачи должен быть понятным и интересным для подростка."
    "\n\n"
    "**СТРОГИЕ ПРАВИЛА ОФОРМЛЕНИЯ:**"
    "\n1. **Никакого Markdown или LaTeX.** Используй только обычный текст и HTML-теги `<b>` и `<i>` для выделения."
    "\n2. **Математические выражения:**"
    "\n   - Степени: только надстрочные символы (², ³, ⁻¹)."
    "\n   - Корни: только символы √ или ³√."
    "\n   - Дроби: обычные через слэш (`3/4`), десятичные с запятой (`0,25`)."
    "\n   - Умножение: символ `·`."
    "\n   - Не используй `*`, `^`, `**`, `sqrt`."
    "\n3. **Стиль:** Говори просто, по-человечески. Не пиши 'Дано:', 'Найти:'. Просто сформулируй условие задачи."
)

# --- УНИВЕРСАЛЬНАЯ И ПРОСТАЯ ФУНКЦИЯ ДЛЯ РАБОТЫ С GPT ---
async def ask_gpt_with_history(
    user_prompt: str,
    dialog_history: List[Dict[str, str]],
    system_prompt: Optional[str] = None
) -> Tuple[str, List[Dict[str, str]]]:
    """
    Универсальная и чистая функция для общения с GPT.
    Принимает историю, пользовательский промпт и необязательный системный промпт.
    Возвращает ответ и обновленную историю.
    """
    # 1. Выбираем системный промпт
    final_system_content = system_prompt if system_prompt is not None else DEFAULT_SYSTEM_PROMPT_FOR_GENERATION
    if system_prompt:
        logger.info("GPT вызван с кастомным системным промптом.")
    else:
        logger.info("GPT вызван с промптом по умолчанию для генерации заданий.")

    # 2. Собираем сообщения для API
    messages = [{"role": "system", "content": final_system_content}]
    messages.extend(dialog_history)
    messages.append({"role": "user", "content": user_prompt})

    logger.info(f"Отправляем в OpenAI API {len(messages)} сообщений.")

    try:
        # 3. Вызываем API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7
        )
        reply_text = (response.choices[0].message.content or "").strip()
        logger.info(f"Получен ответ от OpenAI API длиной {len(reply_text)} символов.")

        # 4. Формируем обновленную историю
        updated_history = list(dialog_history)
        updated_history.append({"role": "user", "content": user_prompt})
        updated_history.append({"role": "assistant", "content": reply_text})
        
        return reply_text, updated_history

    except Exception as e:
        logger.error(f"Ошибка при обращении к OpenAI API: {e}")
        return f"Ошибка GPT: {e}", dialog_history