from typing import Any, Dict, Iterable, List

from matunya_bot_final.utils.text_formatters import escape_for_telegram

def humanize_solution_11(solution_core: Dict[str, Any]) -> str:
    parts: List[str] = []

    explanation = solution_core.get("explanation_idea")
    if explanation:
        parts.append("🧠 <b>Идея решения</b>")
        parts.append(escape_for_telegram(explanation))
        parts.append("")

    steps: Iterable[Dict[str, Any]] = solution_core.get("calculation_steps") or []
    steps = list(steps)
    if steps:
        parts.append("🔍 <b>Разбор шагов</b>")
        for step in steps:
            step_number = step.get("step_number")
            description = escape_for_telegram(step.get("description", ""))
            formula = step.get("formula_representation")
            result = escape_for_telegram(step.get("calculation_result", ""))

            header = f"• <b>Шаг {step_number}</b>: {description}" if step_number is not None else f"• {description}"
            parts.append(header)
            if formula and str(formula).upper() != "N/A":
                parts.append(f"  <code>{escape_for_telegram(str(formula))}</code>")
            if result:
                parts.append(f"  ⇒ {result}")
        parts.append("")

    final_answer = solution_core.get("final_answer") or {}
    final_display = final_answer.get("value_display")
    if final_display:
        parts.append("✅ <b>Ответ</b>")
        parts.append(escape_for_telegram(final_display))
        parts.append("")

    hints: Iterable[str] = solution_core.get("hints") or []
    hints = [hint for hint in hints if hint]
    if hints:
        parts.append("💡 <b>Полезно помнить</b>")
        for hint in hints:
            parts.append(f"• {escape_for_telegram(hint)}")

    text = "\n".join(part for part in parts if part is not None)
    return text.strip() or "ℹ️ Подсказка отсутствует."

__all__ = ['humanize_solution_11']
