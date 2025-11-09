# matunya_bot_final/task_generators/task_6/validators/powers_validator.py

from __future__ import annotations

from fractions import Fraction
from typing import Any, Dict, List, Tuple

from matunya_bot_final.utils.task6.powers_helpers import is_ten_power_node

_ALLOWED_PREFIXES = [
    "Вычисли выражение",
    "Вычислите выражение",
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


def validate_powers_task(task: Dict[str, Any]) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    if task.get("task_number") != 6:
        errors.append("Неверный номер задания (ожидается 6).")

    if task.get("subtype") != "powers":
        errors.append("subtype должен быть 'powers'.")

    pattern = task.get("pattern") or ""
    if not pattern:
        errors.append("Не указан pattern задачи.")

    if task.get("answer_type") != "decimal":
        errors.append("answer_type должен быть 'decimal'.")

    try:
        float(str(task.get("answer")).replace(",", "."))
    except Exception:
        errors.append("Ответ невозможно привести к числу.")

    question_text = task.get("question_text", "")
    variants = _normalise_variants(question_text)
    if not any(
        variant.startswith(prefix)
        for variant in variants
        for prefix in _ALLOWED_PREFIXES
    ):
        errors.append("question_text не содержит ожидаемого префикса.")

    expression_tree = task.get("variables", {}).get("expression_tree")
    if not expression_tree:
        errors.append("Отсутствует variables.expression_tree")
    else:
        if _pattern_is_fraction(pattern):
            _validate_fraction_pattern(expression_tree, errors)
        elif _pattern_is_ten(pattern):
            _validate_ten_pattern(expression_tree, errors)
        else:
            errors.append(f"Неизвестный pattern: {pattern}")

    return len(errors) == 0, errors


def _pattern_is_fraction(pattern: str) -> bool:
    return "powers_with_fractions" in pattern


def _pattern_is_ten(pattern: str) -> bool:
    return "powers_of_ten" in pattern


# --- powers_with_fractions -------------------------------------------------------------


def _validate_fraction_pattern(node: Dict[str, Any], errors: List[str]) -> None:
    if node.get("operation") not in {"add", "subtract"}:
        errors.append("Выражение должно быть суммой или разностью двух блоков.")
        return

    operands = node.get("operands") or []
    if len(operands) != 2:
        errors.append("Корневой узел обязан иметь два слагаемых.")
        return

    power_term = None
    linear_term = None

    for child in operands:
        if _contains_power(child):
            if power_term is not None:
                errors.append("Найдено несколько множителей со степенью.")
                return
            power_term = child
        else:
            if linear_term is not None:
                errors.append("Найдено более одного линейного множителя.")
                return
            linear_term = child

    if power_term is None or linear_term is None:
        errors.append("Не удалось выделить блок со степенью и линейный блок.")
        return

    base_fraction, exponent = _extract_power_components(power_term, errors)
    if base_fraction is None:
        return

    linear_base = _extract_linear_base(linear_term, errors)
    if linear_base is None:
        return

    if base_fraction != linear_base:
        errors.append("Базовые дроби в обоих множителях должны совпадать.")


def _contains_power(node: Dict[str, Any]) -> bool:
    if node.get("operation") != "multiply":
        return False
    return any(child.get("operation") == "power" for child in node.get("operands", []))


def _extract_power_components(node: Dict[str, Any], errors: List[str]) -> Tuple[Fraction | None, int]:
    if node.get("operation") != "multiply":
        errors.append("Множитель со степенью должен быть операцией multiply.")
        return None, 0

    power_nodes = [child for child in node.get("operands", []) if child.get("operation") == "power"]
    if len(power_nodes) != 1:
        errors.append("В каждом блоке со степенью должна быть ровно одна операция power.")
        return None, 0

    power_node = power_nodes[0]
    operands = power_node.get("operands") or []
    if len(operands) != 2:
        errors.append("У узла power должно быть два аргумента.")
        return None, 0

    base_node, exponent_node = operands
    try:
        base_fraction = _node_to_fraction(base_node)
    except ValueError as exc:
        errors.append(f"Основание степени должно быть дробью: {exc}")
        return None, 0

    exponent_ok, exponent_value = _extract_integer_value(exponent_node)
    if not exponent_ok or exponent_value <= 0:
        errors.append("Показатель степени должен быть натуральным числом.")
        return None, 0

    return base_fraction, exponent_value


def _extract_linear_base(node: Dict[str, Any], errors: List[str]) -> Fraction | None:
    if node.get("operation") != "multiply":
        errors.append("Линейный блок должен быть операцией multiply.")
        return None

    base_candidates = [child for child in node.get("operands", []) if child.get("type") in {"common", "decimal"}]
    if not base_candidates:
        errors.append("Линейный блок обязан содержать дробь.")
        return None

    try:
        return _node_to_fraction(base_candidates[-1])
    except ValueError as exc:
        errors.append(f"Не удалось прочитать дробь в линейном блоке: {exc}")
        return None


# --- powers_of_ten ---------------------------------------------------------------------


def _validate_ten_pattern(node: Dict[str, Any], errors: List[str]) -> None:
    if node.get("operation") != "multiply":
        errors.append("Показатели степеней десяти должны перемножаться (корневой multiply).")
        return

    factors = _flatten_multiply(node)
    if len(factors) < 2:
        errors.append("Выражение должно содержать как минимум два множителя.")
        return

    for factor in factors:
        _validate_ten_factor(factor, errors)


def _flatten_multiply(node: Dict[str, Any]) -> List[Dict[str, Any]]:
    if node.get("operation") != "multiply":
        return [node]
    result: List[Dict[str, Any]] = []
    for child in node.get("operands", []):
        result.extend(_flatten_multiply(child))
    return result


def _validate_ten_factor(node: Dict[str, Any], errors: List[str]) -> None:
    if node.get("operation") == "power":
        operands = node.get("operands") or []
        if len(operands) != 2:
            errors.append("power должен иметь основание и показатель.")
            return
        base_node, exponent_node = operands
        ok, _ = _extract_integer_value(exponent_node)
        if not ok:
            errors.append("Показатель внешней степени должен быть целым.")
            return
        _validate_ten_multiplier(base_node, errors)
    else:
        _validate_ten_multiplier(node, errors)


def _validate_ten_multiplier(node: Dict[str, Any], errors: List[str]) -> None:
    """
    Проверяет блок вида (коэффициент · 10^n).
    """
    if node.get("operation") == "multiply":
        ten_found = False
        for child in node.get("operands", []):
            is_ten, _ = is_ten_power_node(child)
            if is_ten:
                ten_found = True
            elif child.get("operation") == "power":
                _validate_ten_factor(child, errors)
            elif child.get("type") in {"common", "decimal"}:
                continue
            else:
                errors.append("Коэффициенты должны быть числами без дополнительных операций.")
        if not ten_found:
            errors.append("Каждый множитель должен содержать степень десяти.")
    else:
        is_ten, _ = is_ten_power_node(node)
        if not is_ten:
            errors.append("Ожидалась степень десяти в одном из множителей.")


# --- utility helpers -------------------------------------------------------------------


def _node_to_fraction(node: Dict[str, Any]) -> Fraction:
    node_type = node.get("type")
    if node_type == "common":
        num, den = node.get("value", [0, 1])
        return Fraction(int(num), int(den))
    if node_type == "decimal":
        return Fraction(str(node.get("value")))
    raise ValueError("узел не является числовой дробью")


def _extract_integer_value(node: Dict[str, Any]) -> Tuple[bool, int]:
    node_type = node.get("type")
    if node_type == "common":
        num, den = node.get("value", [0, 1])
        if den == 1:
            return True, int(num)
    if node_type == "decimal":
        value = node.get("value")
        if float(value).is_integer():
            return True, int(float(value))
    return False, 0
