"""Helpers for formatting text output for Telegram."""

from __future__ import annotations

import html
import re
from typing import Dict, List, Tuple


ALLOWED_TAGS: Tuple[str, ...] = (
    "b",
    "i",
    "u",
    "code",
    "br",
    "pre",
    "tg-spoiler",
)


def escape_for_telegram(text: str) -> str:
    """Escape everything except a whitelist of HTML tags supported by Telegram."""
    placeholders: List[str] = []

    def _protect(match: re.Match[str]) -> str:
        placeholders.append(match.group(0))
        return f"__TG_TAG_{len(placeholders) - 1}__"

    allowed_pattern = re.compile(r"</?(?:" + "|".join(ALLOWED_TAGS) + r")>")
    protected = allowed_pattern.sub(_protect, text)
    protected = html.escape(protected, quote=False)

    def _restore(match: re.Match[str]) -> str:
        idx = int(match.group(1))
        return placeholders[idx]

    return re.sub(r"__TG_TAG_(\d+)__", _restore, protected)


def bold_numbers_safe(text: str) -> str:
    pattern = r"(?<!<b>)(?<!\w)(\d+(?:[.,]\d+)?)(?!</b>)(?![\w)])"
    return re.sub(pattern, r"<b>\1</b>", text)


def bold_numbers_task11(text: str) -> str:
    text = re.sub(r"(?m)^\s*(\d+)\)", r"<b>\1</b>)", text)
    pattern = r"(?<!<b>)(?<!\w)(\d+(?:[.,]\d+)?)(?!</b>)(?![\w)])"
    return re.sub(pattern, r"<b>\1</b>", text)


def format_task(task_type: str, task_text: str) -> str:
    if task_type == "11":
        parts = task_text.split("\n\n", 1)
        if len(parts) == 2:
            condition, rest = parts
            condition = escape_for_telegram(condition)
            rest = bold_numbers_task11(escape_for_telegram(rest))
            body = f"{condition}\n\n{rest}"
        else:
            body = bold_numbers_task11(escape_for_telegram(task_text))
    else:
        body = bold_numbers_safe(escape_for_telegram(task_text))

    return (
        f"ℹ️ <b>Задание {escape_for_telegram(task_type)}:</b>\n\n"
        f"{body}\n\n"
        "Если нужна подсказка — жми <b>🆘 Помощь</b>"
    )


def format_theory(title: str, body: str, example: str | None = None) -> str:
    text = f"📘 <b>{escape_for_telegram(title)}</b>\n\n{escape_for_telegram(body)}"
    if example:
        text += f"\n\nПример: <code>{escape_for_telegram(example)}</code>"
    return text


def format_info(title: str, body: str) -> str:
    return f"ℹ️ <b>{escape_for_telegram(title)}</b>\n\n{escape_for_telegram(body)}"


def format_success(title: str, body: str) -> str:
    return f"✅ <b>{escape_for_telegram(title)}</b>\n\n{escape_for_telegram(body)}"


def format_warning(title: str, body: str) -> str:
    return f"⚠️ <b>{escape_for_telegram(title)}</b>\n\n{escape_for_telegram(body)}"


bold_numbers = bold_numbers_safe


def sanitize_gpt_response(text: str) -> str:
    processed_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    processed_text = processed_text.replace("*", "").replace("_", "").replace("#", "")
    processed_text = processed_text.replace("\\", "")

    def _normalize_tag(match: re.Match[str]) -> str:
        slash = "/" if match.group(1) else ""
        tag = match.group(2).lower()
        if tag in ALLOWED_TAGS:
            return f"<{slash}{tag}>"
        return ""

    processed_text = re.sub(r"<\s*(/)?\s*([a-zA-Z0-9\-]+)\s*>", _normalize_tag, processed_text)
    processed_text = processed_text.replace("cdot", "·").replace("div", "÷")
    processed_text = re.sub(r"text\{([^}]+)\}", r"\1", processed_text)
    processed_text = escape_for_telegram(processed_text)

    # --- 🔸 Заменяем десятичные точки на запятые ---
    # 12.5 → 12,5 но 12/5 остаётся
    processed_text = re.sub(r"(?<=\d)\.(?=\d)", ",", processed_text)

    return processed_text.replace("&nbsp;", " ")


def normalize_formula(formula_str: str) -> str:
    """Convert raw formula text to a nicer, human-friendly representation."""
    replacements = {
        "^3": "³",
        "^2": "²",
        "*": "·",
    }
    normalised = formula_str
    for raw, pretty in replacements.items():
        normalised = normalised.replace(raw, pretty)
    return normalised


def format_solution(steps: List[Dict[str, str]]) -> List[str]:
    """Return a list of formatted messages for a step-by-step solution."""
    messages: List[str] = [
        "💡 <b>Пошаговое решение</b>\n\n<i>Открывай шаги по очереди, чтобы свериться со своей работой.</i>"
    ]

    if not steps:
        messages.append("🔎 <b>Шаг 1</b>\n<tg-spoiler>Пока нет шагов.</tg-spoiler>")
        return messages

    total_steps = len(steps)
    for index, step in enumerate(steps, start=1):
        step_text_raw = (step.get("step_text") or "").strip()
        step_formula_raw = step.get("step_formula")
        step_name = (step.get("step_name") or "").lower()

        is_final = "final" in step_name or index == total_steps
        step_header = "✅ <b>Ответ</b>" if is_final else f"🔎 <b>Шаг {index}</b>"

        spoiler_lines: List[str] = []
        if step_text_raw:
            spoiler_lines.append(escape_for_telegram(step_text_raw))
        if step_formula_raw:
            normalized_formula = normalize_formula(str(step_formula_raw))
            spoiler_lines.append(f"<code>{escape_for_telegram(normalized_formula)}</code>")

        if not spoiler_lines:
            spoiler_lines.append("Нет данных.")

        spoiler_content = "\n".join(spoiler_lines)
        messages.append(f"{step_header}\n<tg-spoiler>{spoiler_content}</tg-spoiler>")

    return messages


_DECIMAL_POINT_RE = re.compile(r'(?<=\d)\.(?=\d)')                   # 2.5 -> 2,5
_TRAILING_ZERO_RE = re.compile(r'(?<=\d),(?:0{1,2})(?!\d)')          # 4,0 / 12,00 -> 4 / 12
_PLUS_MINUS_RE = re.compile(r'\+\s*-\s*')                            # + -x -> − x
_MINUS_MINUS_RE = re.compile(r'(?:−|-)\s*-\s*')                      # − -x / - -x -> + x
_PAREN_SINGLE_NUMBER_RE = re.compile(r'\(\s*(-?\d+(?:,\d+)?)\s*\)')  # (1,2) -> 1,2; (-3) -> -3
_MUL_TIGHT_RE = re.compile(r'\s*·\s*')                               # пробелы вокруг ·

def cleanup_math_for_display(text: str) -> str:
    """
    Деликатная нормализация математических выражений для показа:
    - десятичная точка -> запятая;
    - убираем хвост ',0' / ',00' у целых;
    - '+ -x' -> '− x', '− -x'/'- -x' -> '+ x';
    - снимаем лишние скобки вокруг одиночных чисел: (1,2) -> 1,2; (-3) -> -3;
    - приводим умножение к «·» без пробелов.
    """
    s = _DECIMAL_POINT_RE.sub(',', text)
    s = _PLUS_MINUS_RE.sub('− ', s)
    s = _MINUS_MINUS_RE.sub('+ ', s)
    s = _PAREN_SINGLE_NUMBER_RE.sub(r'\1', s)
    s = _TRAILING_ZERO_RE.sub('', s)
    s = _MUL_TIGHT_RE.sub('·', s)
    return s


__all__ = [
    "escape_for_telegram",
    "bold_numbers_safe",
    "bold_numbers_task11",
    "format_task",
    "format_theory",
    "format_info",
    "format_success",
    "format_warning",
    "bold_numbers",
    "sanitize_gpt_response",
    "normalize_formula",
    "format_solution",
    "cleanup_math_for_display",
]
