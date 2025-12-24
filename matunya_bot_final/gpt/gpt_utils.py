# matunya_bot_final/gpt/gpt_utils.py

import os
import logging
from typing import List, Dict, Optional, Tuple

from openai import OpenAI

logger = logging.getLogger(__name__)

# --- системный промпт ---
DEFAULT_SYSTEM_PROMPT_FOR_GENERATION = (
    "Ты — добрый и очень внимательный AI-репетитор 'Матюня'. "
    "Объясняй понятно, по шагам, без формального языка."
)

def _get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY не найден в окружении")
    return OpenAI(api_key=api_key)


async def ask_gpt_with_history(
    user_prompt: str,
    dialog_history: List[Dict[str, str]],
    system_prompt: Optional[str] = None,
) -> Tuple[str, List[Dict[str, str]]]:

    final_system_content = (
        system_prompt
        if system_prompt is not None
        else DEFAULT_SYSTEM_PROMPT_FOR_GENERATION
    )

    logger.info("GPT вызван. Используем Responses API.")

    messages = []
    messages.append({"role": "system", "content": final_system_content})
    messages.extend(dialog_history)
    messages.append({"role": "user", "content": user_prompt})

    try:
        client = _get_openai_client()

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=messages,
        )

        reply_text = response.output_text.strip()

        updated_history = list(dialog_history)
        updated_history.append({"role": "user", "content": user_prompt})
        updated_history.append({"role": "assistant", "content": reply_text})

        return reply_text, updated_history

    except Exception as e:
        logger.exception("Ошибка GPT")
        return f"Ошибка GPT: {e}", dialog_history
