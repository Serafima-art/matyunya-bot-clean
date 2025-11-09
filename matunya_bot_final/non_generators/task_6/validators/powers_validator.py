# matunya_bot_final/non_generators/task_6/validators/powers_validator.py
"""Validator for non-generator Task 6 subtype 'powers'."""

from __future__ import annotations

import re
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction
from typing import Any, Dict, Optional

from sympy import sympify, Rational
from sympy.parsing.sympy_parser import parse_expr, convert_xor, rationalize

from matunya_bot_final.utils.task6.powers_helpers import is_ten_power_node


# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------


SUPERSCRIPT_TRANSLATION = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")


def _preprocess_expression(expr: str) -> str:
    if not expr:
        return ""

    expr = expr.strip()

    for space in ("\u00A0", "\u202F", "\u2009", "\u200B", "\u2060"):
        expr = expr.replace(space, "")

    expr = expr.replace(":", "/")

    for dot in ("·", "⋅", "∙", "×"):
        expr = expr.replace(dot, "*")

    expr = expr.replace("−", "-")

    expr = re.sub(r"(?<=\d),(?=\d)", ".", expr)

    def _replace_superscripts(match: re.Match) -> str:
        base = match.group("base")
        exponent = match.group("sup").translate(SUPERSCRIPT_TRANSLATION)
        return f"{base}^{exponent}"

    expr = re.sub(
        r"(?P<base>(?:\d+(?:\.\d+)?|\)))(?P<sup>[⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+)",
        _replace_superscripts,
        expr,
    )

    expr = expr.replace("²", "^2").replace("³", "^3")

    expr = expr.translate(SUPERSCRIPT_TRANSLATION)

    return expr


def _normalize_decimal(value: float | Decimal | str, places: int = 3) -> str:
    """Round value to <places> decimals, trim zero tail, use comma separator."""
    decimal_value = Decimal(str(value))
    quant = Decimal("1." + "0" * places)
    rounded = decimal_value.quantize(quant, rounding=ROUND_HALF_UP)
    text = format(rounded, "f").rstrip("0").rstrip(".")
    if text in {"", "-"}:
        text = "0"
    elif text == "-0":
        text = "0"
    return text.replace(".", ",")




# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------

def _make_integer_node(value: int) -> Dict[str, Any]:
    return {"type": "integer", "value": int(value), "text": str(value)}


def _make_common_node(num: int, den: int) -> Dict[str, Any]:
    return {"type": "common", "value": [int(num), int(den)], "text": f"{num}/{den}"}


def _make_operation_node(op: str, operands: list[Dict[str, Any]]) -> Dict[str, Any]:
    texts = [opd.get("text", "") for opd in operands]
    if op == "add":
        text = " + ".join(texts)
    elif op == "subtract":
        text = f"{texts[0]} - {texts[1]}"
    elif op == "divide":
        text = f"{texts[0]} / {texts[1]}"
    elif op == "multiply":
        text = " * ".join(texts)
    elif op == "power":
        text = f"{texts[0]}^{texts[1]}"
    else:
        text = " ".join(texts)
    return {"operation": op, "operands": operands, "text": text}


def _sympy_to_json(expr) -> Dict[str, Any]:
    from sympy import Integer, Rational as SymRational, Float

    if isinstance(expr, Integer):
        return _make_integer_node(int(expr))

    if isinstance(expr, SymRational):
        if expr.q == 1:
            return _make_integer_node(int(expr.p))
        return _make_common_node(expr.p, expr.q)

    if isinstance(expr, Float):
        normalized = _normalize_decimal(str(expr))
        return {"type": "decimal", "value": normalized, "text": normalized}

    if expr.is_Add:
        terms = list(expr.args)
        if len(terms) == 2 and terms[1].is_negative:
            left = _sympy_to_json(terms[0])
            right = _sympy_to_json(-terms[1])
            return _make_operation_node("subtract", [left, right])
        return _make_operation_node("add", [_sympy_to_json(arg) for arg in terms])

    if expr.is_Mul:
        numerators: list[Dict[str, Any]] = []
        denominators: list[Dict[str, Any]] = []
        for arg in expr.args:
            if arg.is_Pow and arg.exp.is_Integer and arg.exp < 0:
                from sympy import Pow

                positive_exp = -int(arg.exp)
                if positive_exp == 1:
                    denominators.append(_sympy_to_json(arg.base))
                else:
                    positive_pow = Pow(arg.base, positive_exp, evaluate=False)
                    denominators.append(_sympy_to_json(positive_pow))
            else:
                numerators.append(_sympy_to_json(arg))
        if denominators:
            numerator_node = _collapse_multiply(numerators)
            denominator_node = _collapse_multiply(denominators)
            return _make_operation_node("divide", [numerator_node, denominator_node])
        return _make_operation_node("multiply", numerators)

    if expr.is_Pow:
        base = _sympy_to_json(expr.base)
        exp = _sympy_to_json(expr.exp)
        return _make_operation_node("power", [base, exp])

    return {"type": "unknown", "text": str(expr)}


def _collapse_multiply(nodes: list[Dict[str, Any]]) -> Dict[str, Any]:
    if not nodes:
        return _make_integer_node(1)
    if len(nodes) == 1:
        return nodes[0]
    return _make_operation_node("multiply", nodes)


def _rational_to_decimal_str(value: Fraction) -> str:
    from decimal import Decimal

    tmp = abs(value.denominator)
    for prime in (2, 5):
        while tmp % prime == 0:
            tmp //= prime
    if tmp != 1:
        return f"{value.numerator}/{value.denominator}"

    result = str(Decimal(value.numerator) / Decimal(value.denominator))
    if "." in result:
        result = result.rstrip("0").rstrip(".")
    return result.replace(".", ",")


# ---------------------------------------------------------------------------
# Pattern-specific validators
# ---------------------------------------------------------------------------

def _validate_powers_with_fractions(expr_str: str) -> Optional[Dict[str, Any]]:
    try:
        processed = _preprocess_expression(expr_str)
        parsed = parse_expr(
            processed,
            evaluate=False,
            transformations=(rationalize, convert_xor),
        )
        tree = _sympy_to_json(parsed)

        result = sympify(processed)
        if not result.is_Rational:
            return None

        answer_fraction = Fraction(result.p, result.q)
        answer_str = _rational_to_decimal_str(answer_fraction)

        question_text = (
            "Вычисли выражение:\n"
            f"{expr_str}\n\nОтвет: ____________"
        )

        return {
            "pattern": "powers_with_fractions",
            "question_text": question_text,
            "answer": answer_str,
            "answer_type": "decimal" if "," in answer_str else "common",
            "expression_tree": tree,
            "source_expression": expr_str,
        }
    except Exception as exc:
        print(f"[ERROR:powers_with_fractions] {exc}")
        return None


def _validate_powers_of_ten(expr_str: str) -> Optional[Dict[str, Any]]:
    try:
        processed = _preprocess_expression(expr_str)
        parsed = parse_expr(
            processed,
            evaluate=False,
            transformations=(rationalize, convert_xor),
        )
        tree = _sympy_to_json(parsed)

        ten_found = False

        def _walk(node: Dict[str, Any]):
            nonlocal ten_found
            if not isinstance(node, dict):
                return
            ok, _ = is_ten_power_node(node)
            if ok:
                ten_found = True
            for child in node.get("operands", []):
                _walk(child)

        _walk(tree)
        if not ten_found:
            raise ValueError("В выражении отсутствует множитель 10^n.")

        result = sympify(processed)
        answer_value = _normalize_decimal(result.evalf())

        question_text = (
            "Вычисли выражение:\n"
            f"{expr_str}\n\nОтвет: ____________"
        )

        return {
            "pattern": "powers_of_ten",
            "question_text": question_text,
            "answer": answer_value,
            "answer_type": "decimal",
            "expression_tree": tree,
            "source_expression": expr_str,
        }
    except Exception as exc:
        print(f"[ERROR:powers_of_ten] {exc}")
        return None


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def validate_powers(line: str) -> Optional[Dict[str, Any]]:
    try:
        pattern, expr_str = [part.strip() for part in line.split("|", 1)]
    except ValueError:
        return None

    if pattern == "powers_with_fractions":
        return _validate_powers_with_fractions(expr_str)
    if pattern == "powers_of_ten":
        return _validate_powers_of_ten(expr_str)

    print(f"[WARN:powers_validator] Unknown pattern: {pattern}")
    return None
