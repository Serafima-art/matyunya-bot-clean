# matunya_bot_final/help_core/humanizers/template_humanizers/task_20_humanizer.py

from typing import Any, Dict
from matunya_bot_final.utils.text_formatters import escape_for_telegram, normalize_formula


def humanize_solution_20(solution_core: Dict[str, Any]) -> str:
    """
    Формирует HTML-ответ для 'Помощи' Задания 20 (ФИПИ-стиль):
    💡 Идея решения
    🪜 Пошаговое решение
    ✅ Ответ
    💭 Полезно помнить (остается под спойлером)
    """

    parts = []

    # 💡 ИДЕЯ РЕШЕНИЯ
    explanation = (solution_core.get("explanation_idea") or "").strip()
    if explanation:
        parts.append(f"💡 <b>Идея решения</b>\n{escape_for_telegram(explanation)}")

    # --- разделитель ---
    parts.append("\n\n---\n\n")

    # 🪜 ПОШАГОВОЕ РЕШЕНИЕ
    steps = solution_core.get("calculation_steps", [])
    if steps:
        parts.append("🪜 <b>Пошаговое решение</b>")

        for step in steps:
            step_num = step.get("step_number", "?")
            description = step.get("description", "")

            formula_general = normalize_formula(step.get("formula_general", "")) if step.get("formula_general") else ""
            formula_calc = normalize_formula(step.get("formula_calculation", "")) if step.get("formula_calculation") else ""
            formula_repr = normalize_formula(step.get("formula_representation", "")) if step.get("formula_representation") else ""
            calc_result = step.get("calculation_result", "")

            # 🔹 Блок шага
            block_lines = []
            if description:
                block_lines.append(f"<b>Шаг {escape_for_telegram(str(step_num))}.</b> {escape_for_telegram(description)}")

            # 🔹 Формулы — построчно
            if formula_general:
                block_lines.append(escape_for_telegram(formula_general))

            # --- оформление систем уравнений ---
            # если внутри формулы есть '{' и ';', пробуем отформатировать как систему
            if '{' in formula_calc and ';' in formula_calc:
                system_body = formula_calc.replace('{', '⎧').replace(';', '\n⎩').replace('}', '')
                block_lines.append(f"<code>{escape_for_telegram(system_body)}</code>")
            elif formula_calc:
                block_lines.append(f"<code>{escape_for_telegram(formula_calc)}</code>")
            elif formula_repr:
                block_lines.append(f"<code>{escape_for_telegram(formula_repr)}</code>")

            if calc_result:
                block_lines.append(f"➡️ {escape_for_telegram(calc_result)}")

            step_block = "\n".join(block_lines)
            parts.append(step_block)

    # --- ОТВЕТ ---
    final = solution_core.get("final_answer", {}) or {}
    value_display = normalize_formula(final.get("value_display", ""))
    if value_display:
        parts.append("\n\n---\n\n")
        parts.append("✅ <b>Ответ</b>")
        parts.append(f"Ответ: {escape_for_telegram(str(value_display))}")

    # --- ПОЛЕЗНО ПОМНИТЬ ---
    hints = solution_core.get("hints", []) or []
    common_mistakes_raw = (
        solution_core.get("common_mistakes")
        or solution_core.get("mistakes")
    )

    # Нормализуем список ошибок (если он есть)
    mistakes_lines = []
    if isinstance(common_mistakes_raw, str):
        mistakes_lines = [line.strip() for line in common_mistakes_raw.splitlines() if line.strip()]
    elif isinstance(common_mistakes_raw, (list, tuple)):
        mistakes_lines = [str(item).strip() for item in common_mistakes_raw if str(item).strip()]

    # СКЛЕЙКА: всё показываем в одном спойлере «Полезно помнить»
    combined_tips = []
    if hints:
        combined_tips.extend(hints)
    if mistakes_lines:
        combined_tips.extend([f"⚠️ {line}" for line in mistakes_lines])

    if combined_tips:
        parts.append("\n\n---\n\n")
        parts.append("💭 <b>Полезно помнить</b>")
        formatted = "\n".join(f"• {escape_for_telegram(t)}" for t in combined_tips)
        parts.append(f"<tg-spoiler>{formatted}</tg-spoiler>")

    # Собираем результат
    return "\n\n".join(parts)


__all__ = ["humanize_solution_20"]
