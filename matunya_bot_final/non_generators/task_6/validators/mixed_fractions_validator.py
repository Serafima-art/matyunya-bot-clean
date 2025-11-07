# matunya_bot_final/non_generators/task_6/validators/mixed_fractions_validator.py
"""Validator for task 6 subtype mixed_fractions."""

from __future__ import annotations

import re
from decimal import Decimal, getcontext
from typing import Any, Dict, List, Optional, Tuple

from sympy import Add, Float, Integer, Mul, Rational, Symbol, sympify
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    convert_xor,
)

from matunya_bot_final.help_core.solvers.task_6.task6_text_formatter import (
    normalize_for_display,
    fix_negative_after_operators,
)

MIX_TOKEN_TEMPLATE = "__MIX_{sign}{whole}_{num}_{den}__"
MIX_TOKEN_RE = re.compile(r"__MIX_(NEG_)?(\d+)_([0-9]+)_([0-9]+)__")

getcontext().prec = 28


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _format_decimal_ru(value: Any) -> str:
    """
    Returns a string with comma as decimal separator (no trailing zeros).
    """
    s = str(value)
    if "e" in s.lower():
        s = format(Decimal(s), "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s.replace(".", ",")


def _make_decimal_node(value: str) -> Dict[str, Any]:
    formatted = _format_decimal_ru(value)
    return {"type": "decimal", "value": formatted, "text": formatted}


def _make_integer_node(value: int) -> Dict[str, Any]:
    ivalue = int(value)
    return {"type": "integer", "value": ivalue, "text": str(ivalue)}


def _make_common_node(num: int, den: int) -> Dict[str, Any]:
    return {
        "type": "common",
        "value": [int(num), int(den)],
        "text": f"{int(num)}/{int(den)}",
    }


def _make_operation_node(operation: str, operands: List[Dict[str, Any]]) -> Dict[str, Any]:
    node = {"operation": operation, "operands": operands}
    node["text"] = _format_operation_text(operation, operands)
    return node


def _format_operation_text(operation: str, operands: List[Dict[str, Any]]) -> str:
    texts = [op.get("text", "") for op in operands]
    if operation == "add":
        return " + ".join(texts)
    if operation == "subtract" and len(texts) == 2:
        return f"{texts[0]} - {texts[1]}"
    if operation == "multiply":
        return " ⋅ ".join(texts)
    if operation == "divide" and len(texts) == 2:
        right = texts[1]
        right_op = operands[1].get("operation")
        if right_op in {"add", "subtract"}:
            right = f"({right})"
        return f"{texts[0]} : {right}"
    if operation == "pow" and len(texts) == 2:
        return f"{texts[0]}^{texts[1]}"
    return ""


# ---------------------------------------------------------------------------
# Sympy expression helpers
# ---------------------------------------------------------------------------

def _strip_negative(expr):
    if expr.is_Number and expr.is_negative:
        return -expr, True
    if expr.is_Mul and expr.args and expr.args[0] == -1:
        rest = expr.args[1:]
        if len(rest) == 1:
            return rest[0], True
        return Mul(*rest, evaluate=False), True
    return expr, False


def _detect_subtract(args):
    if len(args) != 2:
        return None
    left, right = args
    right_inner, is_neg = _strip_negative(right)
    if is_neg:
        return left, right_inner
    left_inner, left_neg = _strip_negative(left)
    if left_neg:
        return right, left_inner
    return None


def _detect_divide(args):
    if len(args) != 2:
        return None
    left, right = args
    if right.is_Pow and len(right.args) == 2 and right.args[1] == -1:
        return left, right.args[0]
    if left.is_Pow and len(left.args) == 2 and left.args[1] == -1:
        return right, left.args[0]
    if right == Integer(1) and left.is_Pow and len(left.args) == 2 and left.args[1] == -1:
        return Integer(1), left.args[0]
    return None


def _sympy_to_json_tree(expr):
    if isinstance(expr, Rational) and not isinstance(expr, Integer):
        return _make_common_node(expr.p, expr.q)
    if isinstance(expr, Integer):
        return _make_integer_node(expr)
    if isinstance(expr, Float):
        return _make_decimal_node(str(expr))
    if isinstance(expr, Symbol):
        return {"type": "symbol", "text": str(expr)}

    if expr.is_Add:
        subtract = _detect_subtract(list(expr.args))
        if subtract:
            left_expr, right_expr = subtract
            return _make_operation_node(
                "subtract",
                [_sympy_to_json_tree(left_expr), _sympy_to_json_tree(right_expr)],
            )
        operands = [_sympy_to_json_tree(arg) for arg in expr.args]
        return _make_operation_node("add", operands)

    if expr.is_Mul:
        division = _detect_divide(list(expr.args))
        if division:
            left_expr, right_expr = division
            return _make_operation_node(
                "divide",
                [_sympy_to_json_tree(left_expr), _sympy_to_json_tree(right_expr)],
            )
        operands = [_sympy_to_json_tree(arg) for arg in expr.args]
        return _make_operation_node("multiply", operands)

    if expr.is_Pow:
        operands = [_sympy_to_json_tree(expr.base), _sympy_to_json_tree(expr.exp)]
        return _make_operation_node("pow", operands)

    return {"type": "unknown", "text": str(expr)}


# ---------------------------------------------------------------------------
# Mixed number helpers
# ---------------------------------------------------------------------------

def _build_mixed_node(whole: int, num: int, den: int) -> Dict[str, Any]:
    return {
        "type": "mixed",
        "whole": whole,
        "num": num,
        "den": den,
        "text": f"{whole} {num}/{den}",
    }


def _mixed_from_text(text: Optional[str]) -> Optional[Dict[str, Any]]:
    if not isinstance(text, str):
        return None
    match = MIX_TOKEN_RE.fullmatch(text.strip())
    if not match:
        return None
    has_neg, whole_str, num_str, den_str = match.groups()
    whole = int(whole_str)
    if has_neg:
        whole = -whole
    num = int(num_str)
    den = int(den_str)
    return _build_mixed_node(whole, num, den)


def _replace_mix_symbols(node: Any) -> Any:
    if isinstance(node, dict):
        if node.get("type") in {"symbol", "unknown"}:
            mixed = _mixed_from_text(node.get("text"))
            if mixed:
                return mixed
        if "operation" in node:
            operands = [_replace_mix_symbols(child) for child in node.get("operands", [])]
            node["operands"] = operands
            node["text"] = _format_operation_text(node["operation"], operands)
            return node
        if "text" in node:
            mixed = _mixed_from_text(node["text"])
            if mixed:
                return mixed
        return node
    if isinstance(node, list):
        return [_replace_mix_symbols(child) for child in node]
    return node


def _preprocess_expression(expression_str: str) -> str:
    processed = expression_str.replace("\u00A0", " ").replace("\u202F", " ")
    for symbol in ("×", "⋅", "∙", "•", "·"):
        processed = processed.replace(symbol, "*")
    processed = processed.replace(":", "/")

    mixed_pattern = re.compile(r"(-?\d+)\s+(\d+)/(\d+)")

    def make_token(match: re.Match) -> str:
        whole_raw, num, den = match.groups()
        sign = "NEG_" if whole_raw.startswith("-") else ""
        whole = whole_raw.lstrip("-")
        return MIX_TOKEN_TEMPLATE.format(sign=sign, whole=whole, num=num, den=den)

    return mixed_pattern.sub(make_token, processed)


def _restore_mixed_for_eval(expression: str) -> str:
    def repl(match: re.Match) -> str:
        has_neg, whole_str, num_str, den_str = match.groups()
        whole = int(whole_str)
        if has_neg:
            whole = -whole
        num = int(num_str)
        den = int(den_str)
        if whole >= 0:
            return f"({whole} + {num}/{den})"
        return f"({whole} - {num}/{den})"

    return MIX_TOKEN_RE.sub(repl, expression)


# ---------------------------------------------------------------------------
# Answer helpers
# ---------------------------------------------------------------------------

def _is_finite_decimal(den: int) -> bool:
    den = abs(int(den))
    if den == 0:
        return False
    while den % 2 == 0:
        den //= 2
    while den % 5 == 0:
        den //= 5
    return den == 1


def _rational_to_decimal(value: Rational) -> Optional[str]:
    if not _is_finite_decimal(value.q):
        return None
    decimal_value = Decimal(value.p) / Decimal(value.q)
    return _format_decimal_ru(decimal_value)


def _build_answer(result: Rational) -> Optional[Tuple[str, str]]:
    if result.is_Integer:
        return "integer", str(int(result))
    if result.is_Rational:
        decimal_str = _rational_to_decimal(result)
        if decimal_str is None:
            return None
        return "decimal", decimal_str
    return None


# ---------------------------------------------------------------------------
# Public validator
# ---------------------------------------------------------------------------

def validate_mixed_fraction(line: str):
    try:
        pattern, expression_str = [part.strip() for part in line.split("|", 1)]
    except ValueError:
        return None

    try:
        processed = _preprocess_expression(expression_str)
        transformations = standard_transformations + (convert_xor,)
        expr_sympy = parse_expr(processed, evaluate=False, transformations=transformations)

        expression_tree = _sympy_to_json_tree(expr_sympy)
        expression_tree = _replace_mix_symbols(expression_tree)

        eval_ready = _restore_mixed_for_eval(processed)
        result = sympify(eval_ready, rational=True)
        answer_data = _build_answer(result)
        if answer_data is None:
            return None
        answer_type, answer_value = answer_data

        expr_display = normalize_for_display(expression_str, subtype="mixed_fractions")
        expr_display = fix_negative_after_operators(expr_display)
        question_text = (
            "Выполни вычисления и запиши ответ:\n"
            f"{expr_display}\n\nОтвет: ____________"
        )

        return {
            "pattern": pattern,
            "question_text": question_text,
            "answer": answer_value,
            "answer_type": answer_type,
            "expression_tree": expression_tree,
            "source_expression": expression_str,
        }
    except Exception as exc:  # pylint: disable=broad-except
        print(f"[ERROR:mixed_validator] {type(exc).__name__}: {exc}")
        return None
