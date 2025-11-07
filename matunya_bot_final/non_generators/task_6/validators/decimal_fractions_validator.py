# matunya_bot_final/non_generators/task_6/validators/decimal_fractions_validator.py

import re
from matunya_bot_final.help_core.solvers.task_6.task6_text_formatter import normalize_for_display
from decimal import Decimal, getcontext
from sympy.parsing.sympy_parser import parse_expr
from sympy import sympify, SympifyError, Rational, Add, Mul, Pow, Integer, Float


# ─────────────────────────────────────────────────────────────────────────────
# Вспомогательные форматтеры
# ─────────────────────────────────────────────────────────────────────────────

def _format_text_ru(x: Decimal | float | int | str) -> str:
    """
    Красивое текстовое представление числа для expression_tree:
    - без хвостовых нулей,
    - с запятой как десятичным разделителем,
    - без скобок.
    """
    s = str(x)
    # через Decimal для аккуратной обрезки хвостов
    try:
        d = Decimal(s)
    except Exception:
        return s.replace(".", ",")
    s = format(d.normalize(), "f")  # убираем экспоненту и хвосты
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s.replace(".", ",")


def _decimal_node(value: Decimal | float | int) -> dict:
    """
    Единый узел-лист для темы decimal_fractions:
    ВСЕГДА type == "decimal", даже если число целое.
    """
    d = Decimal(str(value))
    # значение для машины храним как float
    val = float(d)
    return {
        "type": "decimal",
        "value": val,
        "text": _format_text_ru(d),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Построение дерева без упрощения
# ─────────────────────────────────────────────────────────────────────────────

def _sympy_to_json_tree_decimal(expr):
    """
    Рекурсивно строит expression_tree для десятичных дробей.
    НИКОГДА не вычисляет скобки / частично не упрощает выражение.
    Все листы — type == "decimal".
    """
    # Числа
    if isinstance(expr, (Integer, Float, Rational)):
        # Rational здесь используется крайне редко (evaluate=False), но подстрахуемся
        if isinstance(expr, Rational):
            # Превращаем в Decimal через строку для стабильности
            d = Decimal(str(expr.evalf()))  # .evalf() только для числового формата строки
        else:
            d = Decimal(str(expr))
        return _decimal_node(d)

    # Вычитание как Add(a, -b)
    if expr.is_Add and len(expr.args) == 2:
        a, b = expr.args
        # ищем форму a + (-1)*c
        if (b.is_Mul and len(b.args) == 2 and b.args[0] == -1):
            return {
                "operation": "subtract",
                "operands": [
                    _sympy_to_json_tree_decimal(a),
                    _sympy_to_json_tree_decimal(b.args[1]),
                ]
            }
        if (a.is_Mul and len(a.args) == 2 and a.args[0] == -1):
            # (-c) + d -> d - c
            return {
                "operation": "subtract",
                "operands": [
                    _sympy_to_json_tree_decimal(b),
                    _sympy_to_json_tree_decimal(a.args[1]),
                ]
            }
        # обычное сложение
        return {
            "operation": "add",
            "operands": [_sympy_to_json_tree_decimal(arg) for arg in expr.args]
        }

    # SymPy представляет деление A/B как A * B**-1
    if expr.is_Mul and any(isinstance(arg, Pow) and arg.exp == -1 for arg in expr.args):
        # Собираем все, что не является степенью -1, в числитель
        numer_args = [arg for arg in expr.args if not (isinstance(arg, Pow) and arg.exp == -1)]
        # Собираем основания степеней -1 в знаменатель
        denom_args = [arg.base for arg in expr.args if isinstance(arg, Pow) and arg.exp == -1]

        # Собираем их обратно в выражения SymPy
        num = Mul(*numer_args) if len(numer_args) > 1 else (numer_args[0] if numer_args else Integer(1))
        den = Mul(*denom_args) if len(denom_args) > 1 else (denom_args[0] if denom_args else Integer(1))

        return {
            "operation": "divide",
            "operands": [_sympy_to_json_tree_decimal(num), _sympy_to_json_tree_decimal(den)]
        }

    # Умножение
    if expr.is_Mul:
        return {
            "operation": "multiply",
            "operands": [_sympy_to_json_tree_decimal(arg) for arg in expr.args]
        }

    # Возведение в степень — на всякий случай
    if expr.is_Pow and len(expr.args) == 2:
        base, power = expr.args
        # В задании 6 по десятичным обычно не нужно, но пусть будет «multiply» развёрнуто.
        #  base ** power -> (повторное умножение) — оставим как есть «unknown», если потребуется.
        return {
            "operation": "unknown_pow",
            "operands": [
                _sympy_to_json_tree_decimal(base),
                _sympy_to_json_tree_decimal(power),
            ]
        }

    # Фолбэк
    return {"type": "unknown", "text": str(expr)}


def _preprocess_expression(expression_str: str) -> str:
    """
    Подготавливает строку к парсингу SymPy без вычисления:
    - заменяет «·» → '*', «:» → '/'
    - заменяет запятые на точки
    - добавляет пробелы вокруг операторов, чтобы SymPy не сливал числа
    - оборачивает всё выражение в скобки для сохранения порядка.
    """
    s = expression_str.strip()

    # 1. Замена операторов
    s = s.replace("·", "*").replace(":", "/")

    # 2. Запятая → точка только внутри чисел
    s = re.sub(r"(?<=\d),(?=\d)", ".", s)

    # 3. Добавляем пробелы вокруг операторов, чтобы не сливались числа и знаки
    s = re.sub(r"([*/+\-()])", r" \1 ", s)
    s = re.sub(r"\s+", " ", s).strip()

    # 4. Если отсутствуют внешние скобки — добавляем (чтобы не потерялся приоритет)
    if not (s.startswith("(") and s.endswith(")")):
        s = f"({s})"

    return s


# ─────────────────────────────────────────────────────────────────────────────
# Публичная функция-валидатор
# ─────────────────────────────────────────────────────────────────────────────

def validate_decimal_fraction(line: str):
    """
    Главная функция-валидатор для подтипа 'decimal_fractions'.

    На входе строка формата:
      "<pattern>|<выражение>"
    Пример:
      "fraction_structure|6.3 / (4.2 - 5.1)"
    """
    try:
        pattern, expression_str = [part.strip() for part in line.split('|', 1)]
        print(f"[DEBUG] Проверяем: {expression_str}")
        processed = _preprocess_expression(expression_str)

        # 1) Строим дерево БЕЗ вычисления
        # 👇 Теперь парсим в режиме строгого приоритета и без вычисления
        sympy_expr_unevaluated = parse_expr(
            processed,
            evaluate=False,
            transformations=(),
        )
        expression_tree = _sympy_to_json_tree_decimal(sympy_expr_unevaluated)

        # 2) Считаем финальный ответ отдельно (это не влияет на дерево)
        getcontext().prec = 10
        raw_result = sympify(processed)  # тут можно посчитать уже с вычислением
        final_dec = Decimal(str(raw_result))

        # 3) Контроль ОГЭ: не более 2 знаков после запятой
        #    Проверяем через умножение на 100 (и целочисленность)
        if (final_dec * 100) != (final_dec * 100).to_integral_value():
            return None  # «брак» — слишком длинная дробь

        if final_dec == final_dec.to_integral_value():
            final_answer = int(final_dec)
            answer_type = "integer"
        else:
            final_answer = float(final_dec.normalize())
            answer_type = "decimal"

        # Централизованное форматирование выражения
        expr_display = normalize_for_display(expression_str, subtype="decimal_fractions")
        question_text = f"Выполни вычисления и запиши ответ:\n{expr_display}\n\nОтвет: ____________"

        return {
            "pattern": pattern,
            "question_text": question_text,
            "answer": str(final_answer),
            "answer_type": answer_type,
            "expression_tree": expression_tree,   # генератор потом положит внутрь variables
            "source_expression": expression_str,
        }

    except Exception as e:
        print(f"[ERROR] {expression_str} -> {type(e).__name__}: {e}")  # type: ignore
        return None
