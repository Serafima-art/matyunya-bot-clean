"""
System prompts for Task 6 (Fractions and Powers) GPT dialog.
Combines strict safety rules with rich pedagogical instructions.
"""

from __future__ import annotations

from textwrap import dedent
from typing import Any, Dict, List, Optional, Union, Sequence

# 1. Броня (Безопасность)
from matunya_bot_final.gpt.prompts.behavior_protocols import (
    BASE_CHATTER_PERSONA,
    TASK_FOCUS_PROTOCOL,
    DIALOG_HISTORY_PROTOCOL,
)

# 2. Правила математики
from matunya_bot_final.gpt.prompts.rules_format import RULES_FORMAT

# 3. Утилиты
from matunya_bot_final.gpt.prompts.prompt_utils import gender_words, safe_text, format_history


def get_task_6_dialog_prompt(
    task_data: Dict[str, Any],
    solution_core: Dict[str, Any],
    dialog_history: List[Dict[str, Any]],
    student_name: Optional[str] = None,
    gender: Optional[str] = None,
    golden_set: Union[Dict[str, str], Sequence[str], None] = None,
) -> str:
    """
    Генерирует системный промпт для диалога по Заданию 6.
    """
    name = student_name or "друг"

    # Определяем формы слов
    gw = gender_words(gender) # ready, sure... (пока не используем напрямую в f-строке, но полезно)

    if gender in ['female', 'жен', 'ж', 'woman', 'girl']:
        pronoun = "ученице"
        suffix_l = ""     # поняла
    else:
        pronoun = "ученику"
        suffix_l = "а"    # понял

    # 1. ДАННЫЕ ЗАДАЧИ
    # В Task 6 условие обычно лежит в source_expression или question_text
    source_expression = task_data.get("source_expression") or task_data.get("question_text") or "N/A"

    # 2. ЭТАЛОННОЕ РЕШЕНИЕ
    # Идея
    idea_key = solution_core.get("explanation_idea_key", "")
    idea_text = _get_idea_text(idea_key)

    # Шаги
    steps_text = _format_steps_for_ai(solution_core.get("calculation_steps", []))

    # Ответ
    final_answer = solution_core.get("final_answer", {}).get("value_display", "N/A")

    # Подсказки из солвера
    hints_list = solution_core.get("hints", [])
    # hints могут быть списком строк или списком словарей {'text': '...'}
    hints_clean = []
    for h in hints_list:
        if isinstance(h, dict): hints_clean.append(h.get('text', ''))
        else: hints_clean.append(str(h))
    hints_str = "\n".join([f"• {h}" for h in hints_clean if h])

    # 3. БАЗА ЗНАНИЙ (Golden Set)
    golden_block = ""
    if golden_set:
        entries: list[str] = []
        if isinstance(golden_set, dict):
            for k, v in golden_set.items(): entries.append(f'- {v}')
        elif isinstance(golden_set, (list, tuple)):
            for phrase in golden_set: entries.append(f'- {phrase}')

        if entries:
            golden_block = "\n### ДОПОЛНИТЕЛЬНАЯ ТЕОРИЯ (GOLDEN SET)\n" + "\n".join(entries)

    # 4. ФИНАЛЬНЫЙ ПРОМПТ
    return dedent(f"""
    {BASE_CHATTER_PERSONA}

    # ТВОЯ ТЕКУЩАЯ МИССИЯ (РЕЖИМ "РЕПЕТИТОР ПО ЗАДАНИЮ 6")
    Ты помогаешь {pronoun} {name} разобраться с **Заданием 6** ОГЭ (Действия с дробями и степенями).
    Твоя цель — не дать ответ, а привести ученика к пониманию через наводящие вопросы.

    # КОНТЕКСТ ЗАДАЧИ
    Вычислить выражение: <code>{source_expression}</code>

    # ЭТАЛОННОЕ РЕШЕНИЕ (ТВОЯ ШПАРГАЛКА)
    **Основная идея:** {idea_text}

    {steps_text}

    **Итоговый ответ:** {final_answer}

    # ПОЛЕЗНЫЕ ПОДСКАЗКИ ИЗ РЕШЕНИЯ
    {hints_str}
    {golden_block}

    # ПРАВИЛА ОБЩЕНИЯ

    1. **Стиль:** Будь максимально дружелюбным и терпеливым. Используй эмодзи (💡, 🤔, ✅, 👍). Обращайся к ученику по имени: <b>{name}</b>.

    2. **Верификация (ГЛАВНОЕ ПРАВИЛО):**
       Когда ученик пишет свой ответ или промежуточное действие, **СНАЧАЛА** переспроси.
       Пример: "Дай-ка я проверю. Ты говоришь, что 1/10 + 1/5 равно 2/15? Я правильно тебя понял{suffix_l}?"
       Только после подтверждения объясняй ошибку (или хвали за правильность).

    3. **Специфика Задания 6:**
       - **Дроби:** Напоминай про общий знаменатель (НОК) при сложении/вычитании. При делении — про "переворот" второй дроби.
       - **Степени:** Следи, чтобы не путали свойства ($a^n \cdot a^m$ vs $(a^n)^m$).
       - **Десятичные:** Напоминай, что запятую при сложении нужно ставить под запятой.
       - **Ответ:** В ОГЭ ответ всегда должен быть десятичной дробью (0,5), а не обыкновенной (1/2). Напоминай переводить в конце.

    4. **Социальный протокол:**
       - На вопросы "Ты робот?", "Как дела?" отвечай кратко и возвращай к задаче.
       - Не здоровайся каждым сообщением.

    {RULES_FORMAT}
    """).strip()


# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def _get_idea_text(idea_key: str) -> str:
    """Возвращает читаемое описание идеи (если в солвере пришел ключ)."""
    # Здесь можно расширить словарь, если в Task 6 используются ключи
    ideas = {
        "POWERS_FRACTIONS_FACTOR_OUT_IDEA": "Заметить общий множитель и вынести его за скобки.",
        "POWERS_FRACTIONS_STANDARD_IDEA": "Действовать по порядку: степени -> умножение -> сложение.",
        "POWERS_OF_TEN_IDEA": "Сгруппировать числа с числами, а степени десятки со степенями десятки.",
        "ADD_SUB_FRACTIONS_IDEA": "Привести дроби к общему знаменателю и выполнить действие."
    }
    return ideas.get(idea_key, "Решаем последовательно, соблюдая порядок действий.")


def _format_steps_for_ai(steps: list) -> str:
    """Превращает список шагов из solution_core в текст для GPT."""
    if not steps:
        return "Шаги решения отсутствуют."

    lines = ["**Пошаговое решение:**"]
    for step in steps:
        num = step.get("step_number", "?")
        desc = str(step.get("description_text") or step.get("description") or "")

        # Очистка от HTML для промпта (GPT лучше читает Markdown)
        desc_clean = desc.replace("<b>", "").replace("</b>", "")

        formula = str(step.get("formula_calculation") or "")
        formula_clean = formula.replace("<b>", "`").replace("</b>", "`").replace("\n", " ")

        step_block = f"Шаг {num}. {desc_clean}"
        if formula_clean.strip():
            step_block += f"\n   Формула: {formula_clean.strip()}"

        lines.append(step_block)

    return "\n\n".join(lines)
