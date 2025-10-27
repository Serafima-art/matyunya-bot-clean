import re
import random
from sympy.parsing.sympy_parser import parse_expr
from sympy import sympify, SympifyError, Rational, Add, Mul, Pow, Integer


def _preprocess_expression(expression_str: str) -> str:
    processed_str = expression_str
    for symbol in ('�', '·', '×', '∙', '•'):
        processed_str = processed_str.replace(symbol, '*')
    processed_str = processed_str.replace(':', '/')
    mixed_number_pattern = r'(\d+)\s+(\d+/\d+)'
    processed_str = re.sub(mixed_number_pattern, r'(\1 + \2)', processed_str)
    return processed_str


def _make_integer_node(value: int) -> dict:
    integer_value = int(value)
    return {"type": "integer", "value": integer_value, "text": str(integer_value)}


def _make_common_node(numerator: int, denominator: int, text: str = None) -> dict:
    num = int(numerator)
    den = int(denominator)
    if den < 0:
        num, den = -num, -den
    node_text = text if text is not None else f"{num}/{den}"
    return {"type": "common", "value": [num, den], "text": node_text}


def _reduce_operation(operation: str, nodes: list) -> dict:
    if not nodes:
        identity = 0 if operation == "add" else 1
        return _make_integer_node(identity)
    result = nodes[0]
    for node in nodes[1:]:
        result = {"operation": operation, "operands": [result, node]}
    return result


def _extract_simple_fraction(expr):
    if isinstance(expr, Rational):
        if expr.q == 1:
            return None
        return int(expr.p), int(expr.q)

    if isinstance(expr, Pow) and expr.exp == -1 and isinstance(expr.base, Integer):
        return 1, int(expr.base)

    if expr.is_Mul:
        factors = list(expr.args)
        if len(factors) != 2:
            return None
        numerator = None
        denominator = None
        for factor in factors:
            if isinstance(factor, Pow) and factor.exp == -1 and isinstance(factor.base, Integer):
                denominator = int(factor.base)
            elif isinstance(factor, Integer):
                numerator = int(factor)
            elif isinstance(factor, Rational) and factor.q == 1:
                numerator = int(factor.p)
            else:
                return None
        if numerator is not None and denominator is not None:
            return numerator, denominator
    return None


def _sympy_to_json_tree(expr):
    if isinstance(expr, Add) and len(expr.args) == 2:
        first, second = expr.args
        if isinstance(first, Integer):
            second_fraction = _extract_simple_fraction(second)
            if second_fraction:
                num, den = second_fraction
                improper = int(first) * den + num
                text = f"{int(first)} {abs(num)}/{den}"
                return _make_common_node(improper, den, text=text)

    simple_fraction = _extract_simple_fraction(expr)
    if simple_fraction:
        num, den = simple_fraction
        return _make_common_node(num, den)

    if isinstance(expr, Integer):
        return _make_integer_node(expr)

    if isinstance(expr, Rational):
        return _make_common_node(expr.p, expr.q)

    if isinstance(expr, Add):
        positive_terms = []
        negative_terms = []
        for arg in expr.args:
            coeff, _ = arg.as_coeff_mul()
            if coeff < 0:
                negative_terms.append(_sympy_to_json_tree(-arg))
            else:
                positive_terms.append(_sympy_to_json_tree(arg))

        if not positive_terms:
            positive_terms.append(_make_integer_node(0))

        left = _reduce_operation("add", positive_terms)
        if not negative_terms:
            return left

        right = _reduce_operation("add", negative_terms)
        return {"operation": "subtract", "operands": [left, right]}

    if isinstance(expr, Mul):
        numerator_parts = []
        denominator_parts = []
        for arg in expr.args:
            if isinstance(arg, Pow) and arg.exp == -1:
                denominator_parts.append(arg.base)
            else:
                numerator_parts.append(arg)

        if denominator_parts:
            numerator_nodes = [_sympy_to_json_tree(part) for part in numerator_parts]
            if not numerator_nodes:
                numerator_nodes = [_make_integer_node(1)]
            denominator_nodes = [_sympy_to_json_tree(part) for part in denominator_parts]
            numerator_node = _reduce_operation("multiply", numerator_nodes)
            denominator_node = _reduce_operation("multiply", denominator_nodes)
            return {"operation": "divide", "operands": [numerator_node, denominator_node]}

        return _reduce_operation("multiply", [_sympy_to_json_tree(part) for part in numerator_parts])

    if isinstance(expr, Pow) and expr.exp == -1:
        numerator_node = _make_integer_node(1)
        denominator_node = _sympy_to_json_tree(expr.base)
        return {"operation": "divide", "operands": [numerator_node, denominator_node]}

    return {"type": "unknown", "value": str(expr)}


def validate_common_fraction(line: str):
    try:
        pattern, expression_str = [part.strip() for part in line.split('|')]
        processed_expression = _preprocess_expression(expression_str)

        sympy_expr_unevaluated = parse_expr(processed_expression, evaluate=False)
        expression_tree = _sympy_to_json_tree(sympy_expr_unevaluated)

        final_sympy_result = sympify(processed_expression, rational=True)

        # --- НОВЫЙ МОДУЛЬНЫЙ ПАРСЕР (Версия 3.0 от "Кодекса") ---
        if pattern == 'cf_addition_subtraction':
            result_fraction = Rational(final_sympy_result)
            choice = random.choice(["numerator", "denominator"])
            if choice == "numerator":
                question_text = f"Выполни вычисления:\n{expression_str}\n\nПолучи несократимую дробь и в ответ запиши только числитель этой дроби."
                final_answer = result_fraction.p
            else:
                question_text = f"Выполни вычисления:\n{expression_str}\n\nПолучи несократимую дробь и в ответ запиши только знаменатель этой дроби."
                final_answer = result_fraction.q
            answer_type = "integer"
        else:
            if pattern == 'complex_fraction':
                question_text = f"Вычисли значение дроби:\n{expression_str}\n\nОтвет: ____________"
            else:
                question_text = f"Выполни вычисления и запиши ответ:\n{expression_str}\n\nОтвет: ____________"

            if final_sympy_result.is_Integer:
                final_answer = int(final_sympy_result)
                answer_type = "integer"
            elif final_sympy_result.is_Rational:
                q = final_sympy_result.q
                while q % 2 == 0:
                    q //= 2
                while q % 5 == 0:
                    q //= 5
                if q == 1:
                    final_answer = float(final_sympy_result)
                    answer_type = "decimal"
                else:
                    return None
            else:
                return None

        return {
            "pattern": pattern,
            "question_text": question_text,
            "answer": str(final_answer),
            "answer_type": answer_type,
            "expression_tree": expression_tree,
            "source_expression": expression_str,
        }
    except Exception:
        return None
