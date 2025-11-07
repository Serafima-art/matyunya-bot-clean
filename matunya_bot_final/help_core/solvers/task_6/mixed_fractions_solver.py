# matunya_bot_final/help_core/solvers/task_6/mixed_fractions_solver.py

"""
Решатель для подтипа 'mixed_fractions' (Задание 6, тема 3 ФИПИ).
Формат решения строго соответствует методическим рекомендациям ФИПИ/Ященко:
— Сначала идея решения;
— Затем перевод всех чисел в обыкновенные дроби;
— Далее выполнение действий в порядке;
— Финальное преобразование в десятичную дробь.
"""

from fractions import Fraction
from typing import Dict, List, Any
from decimal import Decimal, getcontext
import math
import re


# ================================================================
# 🔹 Вспомогательные функции форматирования
# ================================================================

def _beautify_ops(s: str) -> str:
    """Заменяет служебные символы на «красивые»: *→⋅, -→−."""
    return s.replace('*', '⋅').replace('-', '−')


def _decimal_from_fraction(frac: Fraction) -> Decimal:
    """Точный перевод Fraction в Decimal без артефактов float."""
    getcontext().prec = 28
    return Decimal(frac.numerator) / Decimal(frac.denominator)


def _decimal_display(frac: Fraction) -> str:
    """Красивое отображение десятичного результата."""
    d = _decimal_from_fraction(frac).normalize()
    s = format(d, 'f').rstrip('0').rstrip('.')
    if s == '-0':
        s = '0'
    return s.replace('.', ',')


def _format_fraction(frac: Fraction) -> str:
    """Форматирует дробь в виде a/b или целое число."""
    if frac.denominator == 1:
        return str(frac.numerator)
    return f"{frac.numerator}/{frac.denominator}"


# ================================================================
# 🔹 Основная функция solve()
# ================================================================

def solve(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Главный решатель для 'mixed_fractions'.
    Пошагово объясняет перевод смешанных и десятичных дробей и порядок действий.
    """
    expression_tree = task_data.get("variables", {}).get("expression_tree")
    if not expression_tree:
        raise ValueError("Отсутствует 'expression_tree' в task_data")

    steps: List[Dict[str, Any]] = []
    step_counter = [1]

    # === Шаг 0. Идея решения ===
    idea_solution = (
        "Чтобы избежать ошибок, приведём все числа к одному виду — обыкновенным дробям. "
        "Порядок действий: сначала умножение и деление, затем сложение и вычитание."
    )

    # === Шаг 1. Перевод всех чисел ===
    conversion_lines = _collect_conversions(expression_tree)
    steps.append({
        "step_number": step_counter[0],
        "description": "Преобразуем все числа в обыкновенные дроби.",
        "formula_representation": "\n".join(conversion_lines),
        "formula_calculation": "",
        "calculation_result": ""
    })
    step_counter[0] += 1

    # === Шаг 2. Рекурсивный расчёт выражения ===
    final_fraction = _evaluate_tree(expression_tree, steps, step_counter)

    # === Шаг 3. Преобразуем результат в десятичную дробь ===
    _add_decimal_conversion_step(final_fraction, steps, step_counter)

    # === Финальные значения ===
    value_machine = float(_decimal_from_fraction(final_fraction))
    value_display = _decimal_display(final_fraction)

    return {
        "question_id": task_data.get("id", "placeholder_id"),
        "question_group": "TASK6_MIXED",
        "idea_solution": idea_solution,
        "explanation_idea": "Переводим числа в обыкновенные дроби и выполняем действия по порядку.",
        "calculation_steps": steps,
        "final_answer": {
            "value_machine": value_machine,
            "value_display": value_display
        },
        "hints": _generate_hints()
    }


# ================================================================
# 🔹 Универсальный рекурсивный движок вычислений
# ================================================================

def _evaluate_tree(node: Dict[str, Any], steps: List[Dict], step_counter: List[int]) -> Fraction:
    """Рекурсивно вычисляет выражение, преобразуя все числа в Fraction."""
    if node.get("type") == "common":
        return Fraction(node["value"][0], node["value"][1])

    if node.get("type") == "decimal":
        decimal_value = node["value"]
        fraction = Fraction(str(decimal_value))
        return fraction

    operation = node.get("operation")
    operands = node.get("operands")

    left = _evaluate_tree(operands[0], steps, step_counter)
    right = _evaluate_tree(operands[1], steps, step_counter)

    return _perform_operation(operation, left, right, steps, step_counter)


# ================================================================
# 🔹 Преобразования и операции
# ================================================================

def _as_fraction_from_decimal(val: float) -> Fraction:
    # точное преобразование без двоичных артефактов
    return Fraction(str(val))

def _decimal_chain(val: float) -> str:
    """
    Строит цепочку вроде:
    8,4 = 8 4/10 = 84/10 = 42/5
    0,2 = 2/10 = 1/5
    """
    dec_str = str(val).replace('.', ',')
    frac = _as_fraction_from_decimal(val)  # уже несократимая дробь
    num, den = frac.numerator, frac.denominator

    # базовая 10-я форма до сокращения
    # для 8,4 → 84/10, для 0,2 → 2/10
    s = str(val)
    if '.' in s:
        digits = len(s.split('.')[1])
        base_den = 10 ** digits
        base_num = int(round(float(s) * base_den))
    else:
        base_den = 1
        base_num = int(val)

    # если число >= 1, показываем смешанную форму a b/den
    chain = []
    if den != 1:
        if base_den != den:
            # возможна цепочка: 8,4 = 8 4/10 = 84/10 = 42/5
            if base_den != 1:
                if base_num >= base_den:
                    a, b = divmod(base_num, base_den)
                    if a > 0 and b > 0:
                        chain = [f"{dec_str} = {a} {b}/{base_den}", f"{base_num}/{base_den}", f"{num}/{den}"]
                    else:
                        chain = [f"{dec_str} = {base_num}/{base_den}", f"{num}/{den}"]
                else:
                    # например 0,2
                    chain = [f"{dec_str} = {base_num}/{base_den}", f"{num}/{den}"]
            else:
                # на всякий случай
                chain = [f"{dec_str} = {num}/{den}"]
        else:
            # уже в несократимом виде
            chain = [f"{dec_str} = {num}/{den}"]
    else:
        # целое 8,0 → просто 8
        chain = [f"{dec_str} = {num}/1 = {num}"]

    # склейка с " = "
    return " = ".join(chain)

def _match_mixed_number(node) -> tuple | None:
    """
    Узнаём структуру смешанного:  a + (1) * (1/b)  → вернём (a, 1, b)
    В твоих деревьях '1' часто как decimal с value == 1.0.
    """
    if not isinstance(node, dict):
        return None
    if node.get("operation") != "add":
        return None

    left, right = node.get("operands", [None, None])
    # левый — целое a
    if not (isinstance(left, dict) and left.get("type") == "decimal"):
        return None
    a_val = left.get("value")
    if float(a_val) != 1.0 and float(a_val) != int(a_val):
        # допускаем только целые (обычно как decimal с .0)
        pass
    a = int(round(float(a_val)))

    # правый — multiply( decimal(1), divide( decimal(1) , decimal(b) ) )
    if not (isinstance(right, dict) and right.get("operation") == "multiply"):
        return None
    r_ops = right.get("operands", [])
    if len(r_ops) != 2:
        return None

    one_node, div_node = r_ops
    if not (isinstance(one_node, dict) and one_node.get("type") == "decimal" and float(one_node.get("value")) == 1.0):
        return None
    if not (isinstance(div_node, dict) and div_node.get("operation") == "divide"):
        return None
    d_ops = div_node.get("operands", [])
    if len(d_ops) != 2:
        return None
    num_node, den_node = d_ops
    if not (isinstance(num_node, dict) and num_node.get("type") == "decimal" and float(num_node.get("value")) == 1.0):
        return None
    if not (isinstance(den_node, dict) and den_node.get("type") == "decimal"):
        return None

    b = int(round(float(den_node.get("value"))))
    return (a, 1, b)

def _collect_conversions(node: Dict[str, Any]) -> List[str]:
    """
    Собираем только осмысленные конверсии «из исходных чисел»:
    - десятичные числа → цепочка десятичная→десятая дробь→несократимая;
    - смешанное число по паттерну → (a·b+c)/b → неправильная дробь;
    - готовые common (если есть) → как есть.
    Не тащим из внутренних узлов случайные 5 и 7.
    """
    seen: List[str] = []
    lines: List[str] = []

    def add_once(s: str):
        if s not in seen:
            seen.append(s)
            lines.append(s)

    def walk(n):
        if not isinstance(n, dict):
            return
        t = n.get("type")
        if t == "decimal":
            val = float(n["value"])
            add_once(_decimal_chain(val))
            return
        if t == "common":
            num, den = n["value"]
            add_once(f"{num}/{den}")
            return

        # пробуем распознать смешанное
        mixed = _match_mixed_number(n)
        if mixed is not None:
            a, c, b = mixed  # (a,1,b)
            improper = a * b + c
            add_once(f"{a} {c}/{b} = ({a}·{b}+{c})/{b} = {improper}/{b}")
            # дочерние не разворачиваем, чтобы не плодить «5/1», «7/1»
            return

        # рекурсивно дальше
        for child in n.get("operands", []):
            walk(child)

    walk(node)
    return lines if lines else ["(нет чисел)"]


def _perform_operation(operation: str, left: Fraction, right: Fraction,
                       steps: List[Dict], step_counter: List[int]) -> Fraction:
    """Выполняет математическую операцию с пояснениями."""
    if operation == "add":
        return _perform_addition(left, right, steps, step_counter)
    elif operation == "subtract":
        return _perform_subtraction(left, right, steps, step_counter)
    elif operation == "multiply":
        return _perform_multiplication(left, right, steps, step_counter)
    elif operation == "divide":
        return _perform_division(left, right, steps, step_counter)
    else:
        raise ValueError(f"Неизвестная операция: {operation}")


def _perform_addition(left: Fraction, right: Fraction,
                     steps: List[Dict], step_counter: List[int]) -> Fraction:
    """Сложение дробей по ФИПИ."""
    lcm = _lcm(left.denominator, right.denominator)
    left_new = left.numerator * (lcm // left.denominator)
    right_new = right.numerator * (lcm // right.denominator)
    result_num = left_new + right_new
    result = Fraction(result_num, lcm)

    description = "Выполним сложение. Приведём к общему знаменателю."
    formula_calc = f"{left_new}/{lcm} + {right_new}/{lcm} = {result_num}/{lcm}"
    if result != Fraction(result_num, lcm):
        gcd = math.gcd(result_num, lcm)
        formula_calc += f" = {_format_fraction(result)} (сокращаем на {gcd})"

    _append_step(steps, step_counter, description, f"{_format_fraction(left)} + {_format_fraction(right)}",
                 formula_calc, _format_fraction(result))
    return result


def _perform_subtraction(left: Fraction, right: Fraction,
                        steps: List[Dict], step_counter: List[int]) -> Fraction:
    """Вычитание дробей по ФИПИ."""
    lcm = _lcm(left.denominator, right.denominator)
    left_new = left.numerator * (lcm // left.denominator)
    right_new = right.numerator * (lcm // right.denominator)
    result_num = left_new - right_new
    result = Fraction(result_num, lcm)

    description = "Выполним вычитание. Приведём к общему знаменателю."
    formula_calc = f"{left_new}/{lcm} − {right_new}/{lcm} = {result_num}/{lcm}"
    if result != Fraction(result_num, lcm):
        gcd = math.gcd(abs(result_num), lcm)
        formula_calc += f" = {_format_fraction(result)} (сокращаем на {gcd})"

    _append_step(steps, step_counter, description, f"{_format_fraction(left)} − {_format_fraction(right)}",
                 formula_calc, _format_fraction(result))
    return result


def _perform_multiplication(left: Fraction, right: Fraction,
                           steps: List[Dict], step_counter: List[int]) -> Fraction:
    """Умножение дробей по ФИПИ."""
    result = left * right
    description = "Выполним умножение дробей. Перемножаем числители и знаменатели."
    formula_calc = f"{_format_fraction(left)} ⋅ {_format_fraction(right)} = {_format_fraction(result)}"
    _append_step(steps, step_counter, description, f"{_format_fraction(left)} ⋅ {_format_fraction(right)}",
                 formula_calc, _format_fraction(result))
    return result


def _perform_division(left: Fraction, right: Fraction,
                     steps: List[Dict], step_counter: List[int]) -> Fraction:
    """Деление дробей по ФИПИ."""
    result = left / right
    description = f"Выполним деление. Деление дробей заменяем умножением на перевёрнутую дробь {right.denominator}/{right.numerator}."
    formula_calc = f"{_format_fraction(left)} : {_format_fraction(right)} = {_format_fraction(left)} ⋅ {right.denominator}/{right.numerator} = {_format_fraction(result)}"
    _append_step(steps, step_counter, description, f"{_format_fraction(left)} : {_format_fraction(right)}",
                 formula_calc, _format_fraction(result))
    return result


def _add_decimal_conversion_step(fraction: Fraction, steps: List[Dict], step_counter: List[int]) -> None:
    """Финальный шаг: преобразование результата в десятичное число."""
    display = _decimal_display(fraction)
    description = "Преобразуем результат в десятичное число."
    formula_calc = f"{_format_fraction(fraction)} = {display}"
    _append_step(steps, step_counter, description, _format_fraction(fraction), formula_calc, display)


# ================================================================
# 🔹 Утилиты
# ================================================================

def _append_step(steps, step_counter, desc, repr_str, calc, result):
    steps.append({
        "step_number": step_counter[0],
        "description": desc,
        "formula_representation": _beautify_ops(repr_str),
        "formula_calculation": _beautify_ops(calc),
        "calculation_result": result
    })
    step_counter[0] += 1


def _lcm(a: int, b: int) -> int:
    """Наименьшее общее кратное."""
    return abs(a * b) // math.gcd(a, b)


def _generate_hints() -> List[str]:
    """Подсказки в стиле ФИПИ."""
    return [
        "Сначала переведи все числа в обыкновенные дроби.",
        "При делении дробей — умножай на перевёрнутую.",
        "Сначала умножение и деление, затем сложение и вычитание.",
        "Проверяй, можно ли сократить дробь после каждого действия."
    ]
