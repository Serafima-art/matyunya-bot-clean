"""
ФИНАЛЬНАЯ ВЕРСИЯ: Простой, надежный валидатор для 'powers'.
Строит "педагогический" JSON по образцу Задания 20.
"""
from __future__ import annotations
import re
from decimal import Decimal
from typing import Any, Dict, Optional

# Используем SymPy ТОЛЬКО для вычислений и парсинга, но не для анализа структуры
from sympy import sympify
from sympy.parsing.sympy_parser import parse_expr, rationalize, convert_xor

# ---------------------------------------------------------------------------
# Главная функция-диспетчер
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

    return None

# ---------------------------------------------------------------------------
# Парсеры и Валидаторы для каждого паттерна
# ---------------------------------------------------------------------------

def _validate_powers_with_fractions(expr_str: str) -> Optional[Dict[str, Any]]:
    """Анализирует строку и строит 'педагогический' JSON для powers_with_fractions."""
    try:
        from sympy.parsing.sympy_parser import parse_expr, rationalize, convert_xor
        from sympy import Add

        processed = _preprocess_expression(expr_str)
        sympy_tree = parse_expr(processed, evaluate=False, transformations=(rationalize, convert_xor))
        expression_tree = _sympy_to_clean_json(sympy_tree)

        fractions = _collect_fractions_from_tree(expression_tree)
        common_fraction_node = next((frac for frac in set(fractions) if fractions.count(frac) >= 2), None)

        operation = "add" if isinstance(sympy_tree, Add) else "subtract"

        result_raw = sympify(processed)
        # Сразу округляем до ~10 знаков, чтобы убить "грязь" float еще на входе
        result = Decimal(str(result_raw.evalf(10)))

        # Проверка на "красивость" по стандарту ОГЭ
        if (result * 100).quantize(Decimal('1e-9')) != (result * 100).to_integral_value().quantize(Decimal('1e-9')):
            return None

        answer_str = f"{result.normalize():g}".replace(".", ",")
        answer_type = "integer" if result == result.to_integral_value() else "decimal"

        variables = {
            "has_common_factor": bool(common_fraction_node),
            "solution_paths": ["standard", "rational"] if common_fraction_node else ["standard"],
            "operation": operation,
        }

        return {
            "pattern": "powers_with_fractions",
            "question_text": f"Вычисли выражение:\n{expr_str}\n\nОтвет: ____________",
            "answer": answer_str,
            "answer_type": answer_type,
            "expression_tree": expression_tree,
            "source_expression": expr_str,
            "variables": variables,
        }
    except Exception:
        return None

def _validate_powers_of_ten(expr_str: str) -> Optional[Dict[str, Any]]:
    """Анализирует строку и строит 'педагогический' JSON для powers_of_ten."""
    try:
        from sympy.parsing.sympy_parser import parse_expr, rationalize, convert_xor

        processed = _preprocess_expression(expr_str)
        sympy_tree = parse_expr(processed, evaluate=False, transformations=(rationalize, convert_xor))
        expression_tree = _sympy_to_clean_json(sympy_tree)

        # --- НОВЫЙ, НАДЕЖНЫЙ БЛОК ВЫЧИСЛЕНИЯ ОТВЕТА ---
        result_raw = sympify(processed)
        # Сразу округляем до ~10 знаков, чтобы убить "грязь" float еще на входе
        result = Decimal(str(result_raw.evalf(10)))

        # Проверка на "красивость" по стандарту ОГЭ
        if (result * 100).quantize(Decimal('1e-9')) != (result * 100).to_integral_value().quantize(Decimal('1e-9')):
            return None

        # Форматируем ответ без научной нотации
        answer_str = format(result.normalize(), 'f').replace(".", ",")
        if "," in answer_str:
            answer_str = answer_str.rstrip('0').rstrip(',')

        answer_type = "integer" if result == result.to_integral_value() else "decimal"
        # --- КОНЕЦ НОВОГО БЛОКА ---

        return {
            "pattern": "powers_of_ten",
            "question_text": f"Вычисли выражение:\n{expr_str}\n\nОтвет: ____________",
            "answer": answer_str,
            "answer_type": answer_type,
            "expression_tree": expression_tree,
            "source_expression": expr_str,
            "variables": {},
        }
    except Exception:
        return None

# ---------------------------------------------------------------------------
# Утилиты: Предобработка и Построение Чистого Дерева
# ---------------------------------------------------------------------------

def _preprocess_expression(expr: str) -> str:
    # Эта функция из старого валидатора идеальна, оставляем ее
    expr = expr.strip().replace(":", "/").replace("−", "-")
    for dot in ("·", "⋅", "∙", "×"): expr = expr.replace(dot, "*")
    expr = re.sub(r"(?<=\d),(?=\d)", ".", expr)
    expr = expr.replace("²", "**2").replace("³", "**3")
    # Добавляем обработку отрицательных степеней
    sup_map = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")
    expr = re.sub(r"10([⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+)", lambda m: f"10**({m.group(1).translate(sup_map)})", expr)
    return expr

def _sympy_to_clean_json(expr) -> Dict[str, Any]:
    """Строит чистое дерево, используя надежную логику."""
    from sympy import Integer, Float, Rational, Add, Mul, Pow

    # 1. Базовый случай: Числа
    if isinstance(expr, (Integer, Float, Rational)):
        clean_decimal = Decimal(str(expr.evalf(15)))
        if clean_decimal == clean_decimal.to_integral_value():
            return {"type": "integer", "value": int(clean_decimal), "text": str(int(clean_decimal))}
        else:
            clean_decimal = clean_decimal.normalize()
            return {"type": "decimal", "value": float(clean_decimal), "text": f"{clean_decimal:g}".replace(".", ",")}

    # 2. Операции
    op_map = {Add: "add", Mul: "multiply", Pow: "power"}

    # Вычитание
    if expr.is_Add and len(expr.args) == 2 and expr.args[1].could_extract_minus_sign():
        return {"operation": "subtract", "operands": [_sympy_to_clean_json(expr.args[0]), _sympy_to_clean_json(-expr.args[1])]}

    # Деление
    if expr.is_Mul and any(isinstance(arg, Pow) and arg.exp == -1 for arg in expr.args):
        num = Mul(*[arg for arg in expr.args if not (isinstance(arg, Pow) and arg.exp == -1)])
        den = Mul(*[arg.base for arg in expr.args if isinstance(arg, Pow) and arg.exp == -1])
        return {"operation": "divide", "operands": [_sympy_to_clean_json(num), _sympy_to_clean_json(den)]}

    # Другие операции
    if expr.func in op_map:
        return {"operation": op_map[expr.func], "operands": [_sympy_to_clean_json(arg) for arg in expr.args]}

    return {"type": "unknown", "text": str(expr)}

def _collect_fractions_from_tree(node: Dict[str, Any]) -> list:
    """Рекурсивно собирает все узлы дробей из дерева."""
    fractions = []
    if node.get("type") == "common":
        fractions.append(tuple(node["value"]))
    if "operands" in node:
        for operand in node["operands"]:
            fractions.extend(_collect_fractions_from_tree(operand))
    return fractions
