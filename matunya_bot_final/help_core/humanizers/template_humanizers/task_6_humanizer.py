# matunya_bot_final/help_core/humanizers/template_humanizers/task_6_humanizer.py

from typing import Dict, Any, List

# Важно: Нам не нужны никакие сторонние форматеры вроде escape_for_telegram.
# Наш message_manager справится с этим сам при отправке.
# "Декоратор" отдает чистый HTML, как мы и договаривались.

def humanize(solution_core: Dict[str, Any]) -> str:
    """
    Формирует HTML-ответ для "Помощи" Задания 6,
    строго следуя утвержденному шаблону "Финальный Штрих".
    """

    parts: List[str] = []

    # --- Блок 1: Идея решения ---
    idea = solution_core.get("explanation_idea", "Выполним вычисления по порядку.")
    parts.append(f"💡 <b>Идея решения:</b>\n<i>{idea}</i>")

    # --- Блок 2: Пошаговое решение ---
    steps = solution_core.get("calculation_steps", [])

    steps_parts = []
    for step in steps:
        step_number = step.get("step_number")
        description = step.get("description", "")
        calculation = step.get("formula_calculation", "")

        # Формируем один шаг по нашему "Золотому Стандарту"
        step_text = (
            f"<b>Шаг {step_number}:</b> {description}\n"
            f"<code>{calculation}</code>"
        )
        steps_parts.append(step_text)

    # Собираем все шаги в один большой блок
    if steps_parts:
        all_steps_text = "\n\n".join(steps_parts)
        parts.append(f"📝 <b>Пошаговое решение:</b>\n\n{all_steps_text}")

    # --- Блок 3: Ответ ---
    final_answer_display = solution_core.get("final_answer", {}).get("value_display", "Не удалось вычислить")
    parts.append(f"✅ <b>Ответ:</b> <code>{final_answer_display}</code>")

    # --- Блок 4: Полезно помнить (под спойлером) ---
    hints = solution_core.get("hints", [])
    if hints:
        hints_text = "\n".join([f"• {hint}" for hint in hints])
        spoiler_block = (
            f"<tg-spoiler>⚠️ <b>Полезно помнить:</b>\n"
            f"{hints_text}</tg-spoiler>"
        )
        parts.append(spoiler_block)

    # --- Финальная сборка ---
    # Соединяем все главные блоки двумя переносами строки
    return "\n\n".join(parts)
