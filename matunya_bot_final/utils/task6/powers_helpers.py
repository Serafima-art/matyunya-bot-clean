"""Shared helpers for task 6 powers subtype."""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Dict, Tuple, Union


NumberLike = Union[Fraction, int, float]


def _to_fraction(value: NumberLike) -> Fraction:
    """Convert supported numeric types to Fraction."""
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value, 1)
    return Fraction(str(value))


def format_fraction(value: NumberLike) -> str:
    """
    Render a number as a simple fraction string.

    Examples:
        Fraction(3, 4) -> "3/4"
        5 -> "5"
        2.5 -> "5/2"
    """
    frac = _to_fraction(value)
    if frac.denominator == 1:
        return str(frac.numerator)
    return f"{frac.numerator}/{frac.denominator}"


def format_power(base: str, exponent: int) -> str:
    """Return textual representation of base raised to exponent."""
    return f"{base}^{exponent}"


def format_power_of_ten(coefficient: NumberLike, exponent: int) -> str:
    """
    Produce string in scientific form a · 10^n, using fraction-friendly coefficient.
    """
    coef_text = format_fraction(_to_fraction(coefficient))
    return f"{coef_text} · 10^{exponent}"


def _extract_int_from_node(node: Dict[str, Any]) -> Tuple[bool, int]:
    """Attempt to read integer value from a tree node."""
    node_type = node.get("type")
    if node_type == "integer":
        return True, int(node.get("value"))
    if node_type == "decimal":
        value = node.get("value")
        if float(value).is_integer():
            return True, int(float(value))
    if node_type == "common":
        num, den = node.get("value", [0, 1])
        if den == 1:
            return True, int(num)
    return False, 0


def is_ten_power_node(node: Any) -> Tuple[bool, int]:
    """
    Check whether the provided node represents 10 raised to an integer exponent.

    Supported shapes:
        {"type": "ten_power", "exp": n}
        {"operation": "power", "operands": [base_node, exponent_node]}
            where base_node is decimal/integer/common equal to 10,
            exponent_node reduces to integer.
    Returns tuple (is_match, exponent_value_if_match_else_0).
    """
    if not isinstance(node, dict):
        return False, 0

    if node.get("type") == "ten_power":
        exp = int(node.get("exp", 0))
        return True, exp

    if node.get("operation") != "power":
        return False, 0

    operands = node.get("operands")
    if not (isinstance(operands, list) and len(operands) == 2):
        return False, 0

    base_node, exponent_node = operands

    base_is_ten = False
    if isinstance(base_node, dict):
        base_type = base_node.get("type")
        if base_type in {"decimal", "integer", "common"}:
            try:
                base_value = float(base_node.get("value"))
            except (TypeError, ValueError):
                base_value = None
            text_value = base_node.get("text", "").replace(",", ".").strip()
            if base_value == 10 or text_value == "10":
                base_is_ten = True

    if not base_is_ten:
        return False, 0

    ok, exponent_value = _extract_int_from_node(exponent_node)
    if not ok:
        return False, 0

    return True, exponent_value
