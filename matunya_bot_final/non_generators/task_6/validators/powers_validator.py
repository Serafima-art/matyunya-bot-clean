"""
ФИНАЛЬНАЯ ВЕРСИЯ: Простой, надежный валидатор для 'powers'.
Строит "педагогический" JSON по образцу Задания 20.

- Для 'powers_of_ten' используется SymPy для вычислений и базового дерева.
- Для 'powers_with_fractions' используется полностью ручной парсер для сохранения структуры.
- Все ответы проходят через "Фильтр ОГЭ" на предмет "красивости".
"""
from __future__ import annotations
import re
from decimal import Decimal
from typing import Any, Dict, Optional

from sympy import sympify

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
# Валидатор для powers_of_ten (с Фильтром ОГЭ)
# ---------------------------------------------------------------------------

def _validate_powers_of_ten(expr_str: str) -> Optional[Dict[str, Any]]:
    """Анализирует строку и строит 'педагогический' JSON для powers_of_ten."""
    try:
        from sympy.parsing.sympy_parser import parse_expr, rationalize, convert_xor

        processed_for_sympy = _preprocess_expression(expr_str)

        result_raw = sympify(processed_for_sympy)
        expression_tree = _sympy_to_clean_json(parse_expr(processed_for_sympy, evaluate=False, transformations=(rationalize, convert_xor)))
        result = Decimal(str(result_raw.evalf(10)))

        if (result * 100).quantize(Decimal('1e-9')) != (result * 100).to_integral_value().quantize(Decimal('1e-9')):
            return None

        answer_str = format(result.normalize(), 'f').replace(".", ",")
        if "," in answer_str:
            answer_str = answer_str.rstrip('0').rstrip(',')

        # === ФИЛЬТР ОГЭ ===
        MAX_ANSWER_LENGTH = 5
        if len(answer_str) > MAX_ANSWER_LENGTH:
            print(f"[VALIDATOR_REJECT] Ответ '{answer_str}' для выражения '{expr_str}' слишком длинный. Пример отбракован.")
            return None
        # === КОНЕЦ ФИЛЬТРА ===

        answer_type = "integer" if result == result.to_integral_value() else "decimal"

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
# Валидатор и Ручной Парсер для powers_with_fractions
# ---------------------------------------------------------------------------

def _parse_term_manual(term_str: str) -> Dict[str, Any]:
    """Ручной парсер для одного слагаемого/вычитаемого. (ИСПРАВЛЕННАЯ ВЕРСЯ)"""
    term_str = term_str.strip()

    # Сначала проверяем самый сложный паттерн: "коэффициент · (дробь) в степени"
    # ИСПРАВЛЕНО: Регулярное выражение теперь ищет символы ² и ³
    m_full = re.match(r"(\d+)\s*·\s*\(([\d\.]+)/([\d\.]+)\)([²³])", term_str)
    if m_full:
        coef, num, den, exp_char = m_full.groups()
        exp_map = {'²': 2, '³': 3}
        return {
            "operation": "multiply",
            "operands": [
                {"type": "integer", "value": int(coef)},
                {
                    "operation": "power",
                    "operands": [
                        {"operation": "divide", "operands": [{"type": "integer", "value": int(num)}, {"type": "integer", "value": int(den)}]},
                        {"type": "integer", "value": exp_map[exp_char]}
                    ]
                }
            ]
        }

    # Паттерн для "коэффициент · (числитель/знаменатель)"
    m_simple_mul = re.match(r"(\d+)\s*·\s*\(([\d\.]+)/([\d\.]+)\)", term_str)
    if m_simple_mul:
        coef, num, den = m_simple_mul.groups()
        return {
            "operation": "multiply",
            "operands": [
                {"type": "integer", "value": int(coef)},
                {"operation": "divide", "operands": [{"type": "integer", "value": int(num)}, {"type": "integer", "value": int(den)}]}
            ]
        }

    # Паттерн для простого числа
    if term_str.isdigit():
        return {"type": "integer", "value": int(term_str)}

    raise ValueError(f"Не удалось распознать структуру слагаемого: {term_str}")

def _validate_powers_with_fractions(expr_str: str) -> Optional[Dict[str, Any]]:
    """Анализирует строку и строит 'педагогический' JSON, используя ручной парсер."""
    try:
        # 1. Вычисляем ответ с помощью SymPy (здесь он незаменим)
        processed_for_sympy = _preprocess_expression(expr_str)
        result_raw = sympify(processed_for_sympy)
        result = Decimal(str(result_raw.evalf(10)))

        # 2. Фильтр ОГЭ на "красивость"
        if (result * 100).quantize(Decimal('1e-9')) != (result * 100).to_integral_value().quantize(Decimal('1e-9')):
            return None

        answer_str = format(result.normalize(), 'f').replace(".", ",")
        if "," in answer_str:
            answer_str = answer_str.rstrip('0').rstrip(',')

        # 3. Ручной парсинг для построения дерева
        # Находим главный оператор (первый + или - с пробелами)
        parts = re.split(r"(\s*[-+]\s*)", expr_str, 1)
        if len(parts) != 3:
            raise ValueError("Не найдена структура 'A [+-] B'")

        left_str, op_str, right_str = parts
        operation = "add" if "+" in op_str else "subtract"

        left_node = _parse_term_manual(left_str)
        right_node = _parse_term_manual(right_str)

        expression_tree = {
            "operation": operation,
            "operands": [left_node, right_node]
        }

        # 4. Формируем финальный JSON
        answer_type = "integer" if result == result.to_integral_value() else "decimal"

        return {
            "pattern": "powers_with_fractions",
            "question_text": f"Вычисли выражение:\n{expr_str}\n\nОтвет: ____________",
            "answer": answer_str,
            "answer_type": answer_type,
            "expression_tree": expression_tree,
            "source_expression": expr_str,
            "variables": {}, # variables больше не нужны, т.к. дерево уже идеальное
        }
    except Exception:
        return None

# ---------------------------------------------------------------------------
# Утилиты: Предобработка и Построение Чистого Дерева из SymPy (только для powers_of_ten)
# ---------------------------------------------------------------------------

def _preprocess_expression(expr: str) -> str:
    expr = expr.strip().replace(":", "/").replace("−", "-")
    for dot in ("·", "⋅", "∙", "×"): expr = expr.replace(dot, "*")
    expr = re.sub(r"(?<=\d),(?=\d)", ".", expr)
    expr = expr.replace("²", "**2").replace("³", "**3")
    sup_map = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")
    expr = re.sub(r"10([⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+)", lambda m: f"10**({m.group(1).translate(sup_map)})", expr)
    return expr

def _sympy_to_clean_json(expr) -> Dict[str, Any]:
    """Строит чистое дерево из SymPy-объекта. Используется ТОЛЬКО для powers_of_ten."""
    from sympy import Integer, Float, Rational, Add, Mul, Pow

    # 1. Базовый случай: Числа
    if isinstance(expr, (Integer, Float, Rational)):
        clean_decimal = Decimal(str(expr.evalf(15)))
        if clean_decimal == clean_decimal.to_integral_value():
            return {"type": "integer", "value": int(clean_decimal)}
        else:
            clean_decimal = clean_decimal.normalize()
            return {"type": "decimal", "value": float(clean_decimal)}
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
