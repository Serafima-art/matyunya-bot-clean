"""Validator for task 20 polynomial_factorization subtype."""

from __future__ import annotations

import ast
import re
from fractions import Fraction
from typing import Any, Dict, Iterable, List, Sequence, Tuple


SUPERSCRIPT_TO_DIGIT = {
    "\u2070": "0",
    "\u00b9": "1",
    "\u00b2": "2",
    "\u00b3": "3",
    "\u2074": "4",
    "\u2075": "5",
    "\u2076": "6",
    "\u2077": "7",
    "\u2078": "8",
    "\u2079": "9",
}

MINUS_SIGNS = ("\u2212", "\u2014", "\u2013")
ALLOWED_SOLUTION_PATTERNS = {"common_poly", "diff_squares", "grouping"}


class _ExpressionEvaluator:
    """Safe evaluator for single-variable polynomial-like expressions."""

    allowed_nodes = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Name,
        ast.Constant,
    )
    allowed_ops = (ast.Add, ast.Sub, ast.Mult, ast.Pow)
    allowed_unary_ops = (ast.UAdd, ast.USub)

    def __init__(self, expression: str) -> None:
        normalized = _normalize_expression_string(expression)
        sanitized = normalized.replace("^", "**")
        try:
            self._tree = ast.parse(sanitized, mode="eval")
        except SyntaxError as exc:  # pragma: no cover - defensive
            raise ValueError(f"Invalid expression: {expression}") from exc
        self._validate_node(self._tree)

    def _validate_node(self, node: ast.AST) -> None:
        if isinstance(node, ast.Expression):
            self._validate_node(node.body)
        elif isinstance(node, ast.BinOp):
            if not isinstance(node.op, self.allowed_ops):
                raise ValueError("Unsupported binary operator in expression.")
            self._validate_node(node.left)
            self._validate_node(node.right)
        elif isinstance(node, ast.UnaryOp):
            if not isinstance(node.op, self.allowed_unary_ops):
                raise ValueError("Unsupported unary operator in expression.")
            self._validate_node(node.operand)
        elif isinstance(node, ast.Name):
            if node.id != "x":
                raise ValueError("Only variable x is allowed in expressions.")
        elif isinstance(node, ast.Constant):
            if not isinstance(node.value, (int, float)):
                raise ValueError("Constants must be numeric.")
        else:  # pragma: no cover - defensive
            raise ValueError("Unsupported syntax in expression.")

    def evaluate(self, x_value: Fraction) -> Fraction:
        """Evaluate expression for the provided x."""
        return self._eval_node(self._tree, x_value)

    def _eval_node(self, node: ast.AST, x_value: Fraction) -> Fraction:
        if isinstance(node, ast.Expression):
            return self._eval_node(node.body, x_value)
        if isinstance(node, ast.Constant):
            return Fraction(node.value)
        if isinstance(node, ast.Name):
            return x_value
        if isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand, x_value)
            if isinstance(node.op, ast.UAdd):
                return operand
            return -operand
        if isinstance(node, ast.BinOp):
            left = self._eval_node(node.left, x_value)
            right = self._eval_node(node.right, x_value)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Pow):
                if right.denominator != 1:
                    raise ValueError("Exponent must be an integer.")
                exponent = right.numerator
                if exponent < 0:
                    raise ValueError("Negative exponents are not supported.")
                return left ** exponent
        raise ValueError("Unsupported structure in expression.")


def _replace_superscripts(expression: str) -> str:
    """Convert superscript powers back to ASCII representation."""

    def _replace(match: re.Match[str]) -> str:
        superscripts = match.group(1)
        digits = "".join(SUPERSCRIPT_TO_DIGIT.get(ch, "") for ch in superscripts)
        if not digits:
            raise ValueError("Unsupported superscript notation in expression.")
        return f"x^{digits}"

    superscripts_pattern = "".join(re.escape(ch) for ch in SUPERSCRIPT_TO_DIGIT)
    expression = re.sub(r"x([{}]+)".format(superscripts_pattern), _replace, expression)
    for superscript, digit in SUPERSCRIPT_TO_DIGIT.items():
        expression = expression.replace(superscript, f"^{digit}")
    return expression


def _normalize_expression_string(expression: str) -> str:
    """Insert implicit multiplication symbols and normalise minus signs."""
    for sign in MINUS_SIGNS:
        expression = expression.replace(sign, "-")
    expression = _replace_superscripts(expression)
    compact = expression.replace(" ", "")
    if not compact:
        return compact
    result: List[str] = []
    previous = ""
    for char in compact:
        if char == "x" and previous and (previous.isdigit() or previous == ")" or previous == "x"):
            result.append("*")
        if char == "(" and previous and (previous.isdigit() or previous == "x" or previous == ")"):
            result.append("*")
        result.append(char)
        previous = char
    return "".join(result)


def _extract_equation_line(text: str) -> str:
    for line in text.splitlines():
        if "=" in line:
            return line.strip()
    raise ValueError("Equation line not found in question text.")


def _split_equation(equation_line: str) -> Tuple[str, str]:
    parts = equation_line.split("=")
    if len(parts) != 2:
        raise ValueError("Equation must contain exactly one '=' sign.")
    left, right = parts
    left = left.strip()
    right = right.strip()
    if not left or not right:
        raise ValueError("Equation sides must be non-empty.")
    return left, right


def _trim_trailing_zeros(coeffs: Sequence[int]) -> List[int]:
    result = list(coeffs)
    while result and result[-1] == 0:
        result.pop()
    return result or [0]


def _parse_answer(answer: Any) -> List[Fraction]:
    if not isinstance(answer, list) or not answer:
        raise ValueError("Field 'answer' must be a non-empty list.")
    parsed: List[Fraction] = []
    for item in answer:
        if not isinstance(item, str):
            raise ValueError("Answer items must be strings.")
        try:
            value = Fraction(item)
        except ValueError as exc:  # pragma: no cover - defensive
            raise ValueError(f"Answer item '{item}' is not a valid rational number.") from exc
        if value.denominator != 1:
            raise ValueError("All answers must be integers.")
        parsed.append(value)
    if len(parsed) != len(set(parsed)):
        raise ValueError("Answer list contains duplicate values.")
    return sorted(parsed)


def _evaluate_polynomial(coeffs: Sequence[int], x_value: Fraction) -> Fraction:
    result = Fraction(0)
    power = Fraction(1)
    for coefficient in coeffs:
        result += Fraction(coefficient) * power
        power *= x_value
    return result


def _ensure_int_list(name: str, values: Iterable[Any]) -> List[int]:
    result: List[int] = []
    for element in values:
        if not isinstance(element, int):
            raise ValueError(f"{name} must contain integers.")
        result.append(element)
    if not result:
        raise ValueError(f"{name} must not be empty.")
    return result


def _poly_add(poly_a: Sequence[int], poly_b: Sequence[int]) -> List[int]:
    max_len = max(len(poly_a), len(poly_b))
    result = [0 for _ in range(max_len)]
    for index in range(max_len):
        coeff = 0
        if index < len(poly_a):
            coeff += poly_a[index]
        if index < len(poly_b):
            coeff += poly_b[index]
        result[index] = coeff
    return result


def _poly_sub(poly_a: Sequence[int], poly_b: Sequence[int]) -> List[int]:
    max_len = max(len(poly_a), len(poly_b))
    result = [0 for _ in range(max_len)]
    for index in range(max_len):
        coeff = 0
        if index < len(poly_a):
            coeff += poly_a[index]
        if index < len(poly_b):
            coeff -= poly_b[index]
        result[index] = coeff
    return result


def _evaluate_equation(
    evaluator_left: _ExpressionEvaluator,
    evaluator_right: _ExpressionEvaluator,
    x_values: Iterable[Fraction],
) -> List[Tuple[Fraction, Fraction]]:
    results: List[Tuple[Fraction, Fraction]] = []
    for value in x_values:
        left = evaluator_left.evaluate(value)
        right = evaluator_right.evaluate(value)
        results.append((left, right))
    return results


def _validate_common_poly(
    variables: Dict[str, Any],
    answers: List[Fraction],
    evaluator_left: _ExpressionEvaluator,
    evaluator_right: _ExpressionEvaluator,
) -> None:
    linear = variables.get("linear_factor")
    common_factor = variables.get("common_factor")
    rhs = variables.get("rhs")
    if not isinstance(linear, dict) or not isinstance(common_factor, dict) or not isinstance(rhs, dict):
        raise ValueError("Pattern 'common_poly' requires 'linear_factor', 'common_factor' and 'rhs' dictionaries.")

    a = linear.get("a")
    b = linear.get("b")
    root = linear.get("root")
    multiplier = rhs.get("multiplier")
    if not all(isinstance(value, int) for value in (a, b, root, multiplier)):
        raise ValueError("Linear factor parameters must be integers.")
    if multiplier in (0, 1, -1):
        raise ValueError("Right-hand multiplier must not be 0, 1 or -1.")

    common_coeffs = _ensure_int_list("Common factor coefficients", common_factor.get("coeffs", []))
    rhs_coeffs = _ensure_int_list("Right-hand coefficients", rhs.get("coeffs", []))
    expected_rhs = [coeff * multiplier for coeff in common_coeffs]
    if rhs_coeffs != expected_rhs:
        raise ValueError("Right-hand side coefficients do not match multiplier * common factor.")

    common_roots = _ensure_int_list("Common factor roots", common_factor.get("roots", []))
    for value in common_roots:
        if _evaluate_polynomial(common_coeffs, Fraction(value)) != 0:
            raise ValueError(f"Declared common factor root {value} does not annul the polynomial.")

    expected_root = Fraction(multiplier - b, a)
    if expected_root.denominator != 1 or expected_root != Fraction(root):
        raise ValueError("Stored linear factor root is inconsistent with coefficients and multiplier.")

    expected_answers = sorted({Fraction(value) for value in common_roots} | {Fraction(root)})
    if expected_answers != answers:
        raise ValueError("Answer list does not match roots encoded in variables.")

    sample_points = [Fraction(val) for val in (-3, -2, -1, 0, 1, 2, 3)]
    poly_values = {point: _evaluate_polynomial(common_coeffs, point) for point in sample_points}
    for point in sample_points:
        left, right = evaluator_left.evaluate(point), evaluator_right.evaluate(point)
        expected_left = (Fraction(a) * point + Fraction(b)) * poly_values[point]
        expected_right = Fraction(multiplier) * poly_values[point]
        if left != expected_left:
            raise ValueError("Left-hand side of equation is inconsistent with stored coefficients.")
        if right != expected_right:
            raise ValueError("Right-hand side of equation is inconsistent with stored coefficients.")

    for answer in answers:
        if evaluator_left.evaluate(answer) != evaluator_right.evaluate(answer):
            raise ValueError(f"Root {answer} does not satisfy the equation.")


def _validate_diff_squares(
    variables: Dict[str, Any],
    answers: List[Fraction],
    evaluator_left: _ExpressionEvaluator,
    evaluator_right: _ExpressionEvaluator,
) -> None:
    factored = variables.get("factored_form")
    diff = variables.get("difference_of_squares")
    if not isinstance(factored, dict) or not isinstance(diff, dict):
        raise ValueError("Pattern 'diff_squares' requires 'factored_form' and 'difference_of_squares' dictionaries.")

    minus_data = factored.get("poly_minus", {})
    plus_data = factored.get("poly_plus", {})
    a_data = diff.get("A", {})
    b_data = diff.get("B", {})
    if not all(isinstance(item, dict) for item in (minus_data, plus_data, a_data, b_data)):
        raise ValueError("Invalid structure for difference of squares pattern.")

    poly_minus_coeffs = _ensure_int_list("poly_minus coefficients", minus_data.get("coeffs", []))
    poly_plus_coeffs = _ensure_int_list("poly_plus coefficients", plus_data.get("coeffs", []))
    a_coeffs = _ensure_int_list("A coefficients", a_data.get("coeffs", []))
    b_coeffs = _ensure_int_list("B coefficients", b_data.get("coeffs", []))

    a_minus_b = _trim_trailing_zeros(_poly_sub(a_coeffs, b_coeffs))
    a_plus_b = _trim_trailing_zeros(_poly_add(a_coeffs, b_coeffs))
    if a_minus_b != poly_minus_coeffs or a_plus_b != poly_plus_coeffs:
        raise ValueError("Stored factors are inconsistent with A and B polynomials.")

    minus_roots = _ensure_int_list("poly_minus roots", minus_data.get("roots", []))
    plus_roots = _ensure_int_list("poly_plus roots", plus_data.get("roots", []))
    for value in minus_roots:
        if _evaluate_polynomial(poly_minus_coeffs, Fraction(value)) != 0:
            raise ValueError(f"Root {value} does not annul poly_minus.")
    for value in plus_roots:
        if _evaluate_polynomial(poly_plus_coeffs, Fraction(value)) != 0:
            raise ValueError(f"Root {value} does not annul poly_plus.")

    expected_answers = sorted({Fraction(value) for value in minus_roots + plus_roots})
    if expected_answers != answers:
        raise ValueError("Answer list does not match factor roots.")

    sample_points = [Fraction(val) for val in (-3, -2, -1, 0, 1, 2, 3)]
    for point in sample_points:
        left_value = evaluator_left.evaluate(point)
        right_value = evaluator_right.evaluate(point)
        a_value = _evaluate_polynomial(a_coeffs, point)
        b_value = _evaluate_polynomial(b_coeffs, point)
        if left_value != a_value ** 2:
            raise ValueError("Left-hand side is inconsistent with A(x)^2.")
        if right_value != b_value ** 2:
            raise ValueError("Right-hand side is inconsistent with B(x)^2.")
        factor_product = _evaluate_polynomial(poly_minus_coeffs, point) * _evaluate_polynomial(
            poly_plus_coeffs, point
        )
        if (a_value - b_value) * (a_value + b_value) != factor_product:
            raise ValueError("Factorisation (A - B)(A + B) is inconsistent with stored coefficients.")

    for answer in answers:
        if evaluator_left.evaluate(answer) != evaluator_right.evaluate(answer):
            raise ValueError(f"Root {answer} does not satisfy the equation.")


def _validate_grouping(
    variables: Dict[str, Any],
    answers: List[Fraction],
    evaluator_left: _ExpressionEvaluator,
    evaluator_right: _ExpressionEvaluator,
) -> None:
    coefficients = variables.get("coefficients")
    grouping = variables.get("grouping")
    roots = _ensure_int_list("Grouping roots", variables.get("roots", []))

    if not isinstance(coefficients, dict) or not isinstance(grouping, dict):
        raise ValueError("Pattern 'grouping' requires 'coefficients' and 'grouping' dictionaries.")

    a = coefficients.get("a")
    b = coefficients.get("b")
    c = coefficients.get("c")
    d = coefficients.get("d")
    coeffs_list = coefficients.get("as_list")
    if not all(isinstance(value, int) for value in (a, b, c, d)):
        raise ValueError("Coefficients a, b, c, d must be integers.")
    coeffs_list_checked = _ensure_int_list("Coefficient list", coeffs_list or [])
    if coeffs_list_checked != [d, c, b, a]:
        raise ValueError("Coefficient list order is incorrect.")
    if a == 0:
        raise ValueError("Leading coefficient 'a' must be non-zero.")
    if a * d != b * c:
        raise ValueError("Coefficients do not satisfy grouping condition a/b = c/d.")

    common_factor = grouping.get("common_factor", {})
    group1 = grouping.get("group1_multiplier")
    group2 = grouping.get("group2_multiplier")
    factor_coeffs = _ensure_int_list("Common factor coefficients", common_factor.get("coeffs", []))
    if factor_coeffs != [b, a]:
        raise ValueError("Common factor coefficients must match ax + b.")
    if group1 != "x^2":
        raise ValueError("First grouping multiplier must be 'x^2'.")
    if not isinstance(group2, int):
        raise ValueError("Second grouping multiplier must be an integer.")
    if c % a != 0 or group2 != c // a:
        raise ValueError("Second grouping multiplier is inconsistent with coefficients.")

    expected_answers = sorted({Fraction(value) for value in roots})
    if expected_answers != answers:
        raise ValueError("Answer list must coincide with declared roots.")

    sample_points = [Fraction(val) for val in (-3, -2, -1, 0, 1, 2, 3)]
    for point in sample_points:
        left_value = evaluator_left.evaluate(point)
        right_value = evaluator_right.evaluate(point)
        expected_left = _evaluate_polynomial(coeffs_list_checked, point)
        if left_value != expected_left or right_value != 0:
            raise ValueError("Equation text is inconsistent with stored coefficients.")
        grouped_value = (point ** 2) * _evaluate_polynomial([b, a], point) + Fraction(group2) * _evaluate_polynomial(
            [b, a], point
        )
        if grouped_value != expected_left:
            raise ValueError("Grouping multipliers do not reproduce the polynomial.")

    for answer in answers:
        if evaluator_left.evaluate(answer) != evaluator_right.evaluate(answer):
            raise ValueError(f"Root {answer} does not satisfy the equation.")


def validate_task_20_polynomial_factorization(task: Dict[str, Any]) -> bool:
    """
    Validate task payload for polynomial_factorization subtype.

    Raises:
        ValueError: If any structural or logical check fails.
    """
    if not isinstance(task, dict):
        raise ValueError("Task payload must be a dictionary.")

    required_fields = {
        "id",
        "task_number",
        "topic",
        "subtype",
        "question_text",
        "answer",
        "variables",
    }
    missing = required_fields - set(task.keys())
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(sorted(missing))}.")

    if task.get("task_number") != 20:
        raise ValueError("Field 'task_number' must be equal to 20.")
    if task.get("topic") != "algebraic_expressions":
        raise ValueError("Field 'topic' must be 'algebraic_expressions'.")
    if task.get("subtype") != "polynomial_factorization":
        raise ValueError("Field 'subtype' must be 'polynomial_factorization'.")

    question_text = task.get("question_text")
    if not isinstance(question_text, str) or "Реши уравнение" not in question_text:
        raise ValueError("Field 'question_text' must contain instruction and equation.")

    answers = _parse_answer(task.get("answer"))
    variables = task.get("variables")
    if not isinstance(variables, dict):
        raise ValueError("Field 'variables' must be a dictionary.")

    pattern = variables.get("solution_pattern")
    if pattern not in ALLOWED_SOLUTION_PATTERNS:
        raise ValueError("Field 'solution_pattern' must be one of 'common_poly', 'diff_squares', 'grouping'.")

    equation_line = _replace_superscripts(_extract_equation_line(question_text))
    left_text, right_text = _split_equation(equation_line)
    evaluator_left = _ExpressionEvaluator(left_text)
    evaluator_right = _ExpressionEvaluator(right_text)

    if pattern == "common_poly":
        _validate_common_poly(variables, answers, evaluator_left, evaluator_right)
    elif pattern == "diff_squares":
        _validate_diff_squares(variables, answers, evaluator_left, evaluator_right)
    elif pattern == "grouping":
        _validate_grouping(variables, answers, evaluator_left, evaluator_right)
    else:  # pragma: no cover - defensive
        raise ValueError(f"Unsupported solution pattern: {pattern}")

    return True


__all__ = ["validate_task_20_polynomial_factorization"]
