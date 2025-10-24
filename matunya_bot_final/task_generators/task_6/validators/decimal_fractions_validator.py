# matunya_bot_final/task_generators/task_6/validators/decimal_fractions_validator.py

from __future__ import annotations

from typing import Any, Dict, List, Tuple

_ALLOWED_PREFIXES = [
    "Посчитай значение",
    "Вычисли выражение",
    "Посчитай значение дроби",
]


def _trim_leading_noise(value: str) -> str:
    for idx, char in enumerate(value):
        if char.isalpha():
            return value[idx:]
    return value


def _normalise_variants(text: str) -> list[str]:
    normalised = text.replace("\u00a0", " ").replace("\u202f", " ").strip()
    variants = {normalised, _trim_leading_noise(normalised)}
    try:
        converted = normalised.encode("cp1251", errors="ignore").decode(
            "utf-8", errors="ignore"
        )
        variants.add(converted)
        variants.add(_trim_leading_noise(converted))
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    return list(variants)


def validate_decimal_fractions_task(task: Dict[str, Any]) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    if task.get("task_number") != 6:
        errors.append("Некорректный номер задания (ожидается 6).")

    if task.get("subtype") != "decimal_fractions":
        errors.append("Некорректный subtype (ожидалось 'decimal_fractions').")

    if "pattern" not in task:
        errors.append("Отсутствует обязательное поле 'pattern'.")

    if task.get("answer_type") != "decimal":
        errors.append("answer_type должен быть 'decimal'.")

    answer = task.get("answer")
    try:
        # поддерживаем и '0,25', и '0.25'
        float(str(answer).replace(",", "."))
    except Exception:
        errors.append("Ответ не преобразуется в число при answer_type='decimal'.")

    q_text = task.get("question_text", "")
    variants = _normalise_variants(q_text)
    if not any(
        variant.startswith(prefix)
        for variant in variants
        for prefix in _ALLOWED_PREFIXES
    ):
        errors.append(f"Unexpected question_text: {q_text}")

    expression_tree = task.get("variables", {}).get("expression_tree")
    if expression_tree:
        _validate_expression_tree(expression_tree, errors)
    else:
        errors.append("Отсутствует variables.expression_tree")

    # ★★★ ВОТ ПРАВИЛЬНОЕ МЕСТО ДЛЯ RETURN ★★★
    is_valid = len(errors) == 0
    return is_valid, errors


def _validate_expression_tree(node: Any, errors: List[str]) -> None:
    if not isinstance(node, dict):
        errors.append("expression_tree: узел не является словарём")
        return # Просто выходим, не возвращая ничего

    if "operation" in node:
        if node["operation"] not in ["add", "subtract", "multiply", "divide"]:
            errors.append(f"expression_tree: недопустимая операция '{node['operation']}'")

        operands = node.get("operands")
        if isinstance(operands, list):
            for child in operands:
                _validate_expression_tree(child, errors)
        else:
            errors.append("expression_tree: 'operands' должен быть списком")

    elif "type" in node:
        if node["type"] != "decimal":
            errors.append(f"expression_tree: недопустимый тип '{node['type']}' (ожидался 'decimal')")
    else:
        errors.append("expression_tree: узел не содержит ни 'operation', ни 'type'")

    # ★★★ А ОТСЮДА RETURN УБРАН ★★★
