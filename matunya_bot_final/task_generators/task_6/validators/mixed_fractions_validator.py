# matunya_bot_final/task_generators/task_6/validators/mixed_fractions_validator.py

from __future__ import annotations

from typing import Any, Dict, List, Tuple

_ALLOWED_PREFIXES = [
    "Вычисли выражение",
    "Выполни вычисления",
    "Найди результат вычислений",
    "Посчитай значение выражения",
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


def validate_mixed_fractions_task(task: Dict[str, Any]) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    if task.get("task_number") != 6:
        errors.append("Некорректный номер задания (ожидается 6).")

    # ★★★ ИСПРАВЛЕНО ЗДЕСЬ ★★★
    if task.get("subtype") != "mixed_fractions":
        errors.append("Некорректный subtype (ожидалось 'mixed_fractions').")

    if "pattern" not in task:
        errors.append("Отсутствует обязательное поле 'pattern'.")

    answer = task.get("answer")
    try:
        float(str(answer).replace(",", "."))
    except Exception:
        errors.append("Ответ не преобразуется в число.")

    q_text = task.get("question_text", "")
    variants = _normalise_variants(q_text)
    if not any(
        variant.startswith(prefix)
        for variant in variants
        for prefix in _ALLOWED_PREFIXES
    ):
        errors.append(f"Unexpected question_text: {q_text}")

    # ★★★ ИСПРАВЛЕНО ЗДЕСЬ ★★★
    expression_tree = task.get("variables", {}).get("expression_tree")
    if expression_tree:
        _validate_expression_tree(expression_tree, errors)
    else:
        errors.append("Отсутствует variables.expression_tree")

    return len(errors) == 0, errors


def _validate_expression_tree(node: Any, errors: List[str]) -> None:
    """
    Рекурсивно проверяет expression_tree для смешанных задач.
    """
    if not isinstance(node, dict):
        errors.append("expression_tree: узел не является словарём")
        return

    if "operation" in node:
        # Проверяем операции
        if node["operation"] not in ["add", "subtract", "multiply", "divide"]:
            errors.append(f"expression_tree: недопустимая операция '{node['operation']}'")

        # Рекурсивно проверяем операнды
        operands = node.get("operands")
        if isinstance(operands, list):
            for child in operands:
                _validate_expression_tree(child, errors)
        else:
            errors.append("expression_tree: 'operands' должен быть списком")

    elif "type" in node:
        # Проверяем типы: теперь могут быть 'common' или 'decimal'
        if node["type"] not in ["common", "decimal"]:
            errors.append(f"expression_tree: недопустимый тип '{node['type']}' (ожидался 'common' или 'decimal')")
    else:
        errors.append("expression_tree: узел не содержит ни 'operation', ни 'type'")
