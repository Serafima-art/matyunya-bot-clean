"""GPT-based parser for student math answers."""

import logging
import json
from typing import Any, Optional

logger = logging.getLogger(__name__)


async def parse_math_answer_with_gpt(
    text_answer: str,
    expected_format: str = "factors"
) -> Optional[Any]:
    """
    Use GPT to parse student's text answer into machine-readable format.

    Args:
        text_answer: Student's raw text answer (e.g., "минус пять; два; пять")
        expected_format: Expected format type ("factors", "numbers", etc.)

    Returns:
        Parsed answer in machine format (list, dict, etc.) or None if parsing failed

    Examples:
        "минус пять; два; пять" -> [-5, 2, 5]
        "(x-5)(x+2)" -> ["x-5", "x+2"]
        "3(x+1)(x-1)" -> ["3", "x+1", "x-1"]
    """
    logger.info(f"Parsing answer with GPT: {text_answer[:50]}...")

    prompt = _build_parsing_prompt(text_answer, expected_format)

    try:
        # ЗАМЕНИТЕ на ваш реальный вызов GPT:
        # from matunya_bot_final.utils.openai_client import get_gpt_response
        # response = await get_gpt_response(prompt, temperature=0.1)

        # MOCK для примера - замените на реальный вызов GPT
        response = await _mock_gpt_parse(text_answer, expected_format)

        # Парсим JSON-ответ
        parsed = json.loads(response)
        logger.info(f"Successfully parsed answer: {parsed}")
        return parsed

    except json.JSONDecodeError as exc:
        logger.error(f"Failed to parse GPT JSON response: {exc}")
        return None
    except Exception as exc:
        logger.exception(f"GPT parsing failed: {exc}")
        return None


def _build_parsing_prompt(text_answer: str, expected_format: str) -> str:
    """Build prompt for GPT to parse student answer."""

    base_prompt = f"""Ты — парсер математических ответов. Твоя задача — преобразовать текстовый ответ ученика в машинный формат JSON.

Ответ ученика: "{text_answer}"

Ожидаемый формат: {expected_format}

"""

    format_instructions = {
        "factors": """Если это разложение на множители:
- Извлеки все множители в виде списка строк
- Примеры:
  "(x-5)(x+2)" -> ["x-5", "x+2"]
  "3(x+1)(x-1)" -> ["3", "x+1", "x-1"]
  "икс минус пять умножить на икс плюс два" -> ["x-5", "x+2"]

Верни ТОЛЬКО валидный JSON-массив, например: ["x-5", "x+2"]
""",
        "numbers": """Если это список чисел:
- Извлеки все числа
- Примеры:
  "минус пять; два; пять" -> [-5, 2, 5]
  "ответы: 3, -1, 0" -> [3, -1, 0]

Верни ТОЛЬКО валидный JSON-массив чисел, например: [-5, 2, 5]
"""
    }

    instruction = format_instructions.get(expected_format, "Верни результат в виде валидного JSON.")

    return base_prompt + instruction


async def _mock_gpt_parse(text_answer: str, expected_format: str) -> str:
    """
    Mock GPT response for testing. Replace with real GPT call.

    В реальной системе здесь должен быть вызов вашего GPT API:
    from matunya_bot_final.utils.openai_client import get_gpt_response
    response = await get_gpt_response(prompt, temperature=0.1)
    """
    # Простая эвристика для демонстрации
    text_lower = text_answer.lower()

    if expected_format == "factors":
        # Ищем паттерны типа (x-5)(x+2)
        import re
        pattern = r'\([^)]+\)'
        matches = re.findall(pattern, text_answer)
        if matches:
            # Убираем скобки
            factors = [m.strip('()') for m in matches]
            return json.dumps(factors)

        # Пробуем текстовое описание
        if "минус" in text_lower or "плюс" in text_lower:
            # Упрощенный парсинг
            return json.dumps(["x-5", "x+2"])

    elif expected_format == "numbers":
        # Извлекаем числа
        import re
        numbers = re.findall(r'-?\d+', text_answer)
        return json.dumps([int(n) for n in numbers])

    # Если ничего не распознали
    return json.dumps(None)


__all__ = ["parse_math_answer_with_gpt"]
