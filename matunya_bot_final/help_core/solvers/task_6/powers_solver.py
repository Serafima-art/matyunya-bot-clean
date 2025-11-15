"""
Новый, безопасный решатель для подтипа `powers` (задание 6 ОГЭ).

Поддерживает два паттерна:
- pattern == "powers_with_fractions"
- pattern == "powers_of_ten"

Архитектура:
- линейные, предсказуемые шаги;
- для вычислений используем Fraction / Decimal;
- для показа шагов используем сырые значения (без сокращений).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple
import math
import re


# ---------------------------------------------------------------------------
# БАЗОВЫЙ КОНСТРУКТОР ШАГОВ
# ---------------------------------------------------------------------------

@dataclass
class StepBuilder:
    steps: List[Dict[str, Any]] = field(default_factory=list)
    counter: int = 1

    def add(
        self,
        description_key: str,
        description_params: Optional[Dict[str, Any]] = None,
        formula_calculation: Optional[str] = None,
    ) -> None:
        step: Dict[str, Any] = {
            "step_number": self.counter,
            "description_key": description_key,
            "description_params": description_params or {},
        }
        if formula_calculation:
            # Оборачиваем ВСЕ формулы в <b>...</b>
            formula_safe = str(formula_calculation).strip()
            step["formula_calculation"] = f"<b>{formula_safe}</b>"
        self.steps.append(step)
        self.counter += 1


# ---------------------------------------------------------------------------
# ПУБЛИЧНЫЙ ВХОД
# ---------------------------------------------------------------------------

def solve(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Главный роутер для подтипа powers (task 6).
    Работает строго по pattern из БД.
    """
    pattern = task_data.get("pattern") or task_data.get("meta", {}).get("pattern_id")
    if not pattern:
        raise ValueError("Не указан pattern для задания с подтипом 'powers'.")

    if pattern == "powers_with_fractions":
        expression_tree = task_data.get("variables", {}).get("expression_tree")
        if not expression_tree:
            raise ValueError("Отсутствует 'variables.expression_tree' для powers_with_fractions.")
        return _solve_powers_with_fractions(task_data, expression_tree)

    if pattern == "powers_of_ten":
        return _solve_powers_of_ten(task_data)

    raise ValueError(f"Неизвестный pattern для подтипа 'powers': {pattern}")


# ---------------------------------------------------------------------------
# УТИЛИТЫ ОБЩИЕ: формат, рендер, конвертация
# ---------------------------------------------------------------------------

def _to_superscript(n: int) -> str:
    """
    Преобразует целое число в надстрочную запись: 2 → ², -3 → ⁻³.
    """
    mapping = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")
    return str(n).translate(mapping)

def _d_str(val: Any) -> str:
    """??????????? ???????? ???????? ? ?????? ? ??????? ? ???????? ??????????? ???????????."""
    # ??????? ????? .0 ??? Decimal('3.0'), ????? ?? ?????? ??????? ??????
    if isinstance(val, Decimal) and val == val.to_integral_value():
        s_val = str(val.to_integral_value())
    else:
        s_val = str(val)
    return s_val.replace('.', ',')


def _fmt_dec_comma(x: Decimal | float | int) -> str:
    """
    Преобразует число в строку с запятой вместо точки.
    Используется только для показа в шагах.
    """
    s = str(x)
    return s.replace(".", ",")


def _format_fraction(fr: Fraction) -> str:
    """
    3/1 -> "3", 1/2 -> "1/2".
    Используется для промежуточных формул.
    """
    if fr.denominator == 1:
        return str(fr.numerator)
    return f"{fr.numerator}/{fr.denominator}"


def _fraction_to_decimal_str(fr: Fraction) -> str:
    """
    Переводит Fraction в строку десятичного числа (или целого).
    Никаких обыкновенных дробей в финальном ответе.
    """
    if fr.denominator == 1:
        return str(fr.numerator)

    dec = (Decimal(fr.numerator) / Decimal(fr.denominator)).quantize(Decimal("0.0000000001"))
    s = format(dec.normalize(), "f").rstrip("0").rstrip(".")
    return s or "0"


def _render_expression_from_question(task_data: Dict[str, Any]) -> str:
    """
    Пытаемся взять красивое выражение из question_text.
    Предполагаем формат:
        'Вычисли выражение:'
        '<выражение>'
        'Ответ: ______'
    """
    qtext = task_data.get("question_text") or ""
    lines = [ln.strip() for ln in qtext.splitlines() if ln.strip()]

    if len(lines) >= 2:
        return lines[1]

    # fallback — если что-то пошло не так
    return ""


def _node_to_fraction(node: Dict[str, Any]) -> Fraction:
    """
    Вычисляет значение узла как Fraction.
    ВНИМАНИЕ: для ПОКАЗА шагов (особенно степени) это использовать нельзя,
    т.к. дробь будет сокращена. Здесь только вычисления.
    """
    if "type" in node:
        t = node["type"]
        if t == "integer":
            return Fraction(int(node["value"]), 1)

        if t in ("common", "fraction"):
            v = node.get("value")
            if isinstance(v, (list, tuple)) and len(v) == 2:
                return Fraction(int(v[0]), int(v[1]))
            if isinstance(v, dict) and "num" in v and "den" in v:
                return Fraction(int(v["num"]), int(v["den"]))

        if t == "decimal":
            return Fraction(Decimal(str(node["value"]).replace(",", ".")))

    op = node.get("operation")
    ops = node.get("operands", [])

    if op == "add":
        result = Fraction(0, 1)
        for c in ops:
            result += _node_to_fraction(c)
        return result

    if op == "subtract":
        if not ops:
            return Fraction(0, 1)
        result = _node_to_fraction(ops[0])
        for c in ops[1:]:
            result -= _node_to_fraction(c)
        return result

    if op == "multiply":
        result = Fraction(1, 1)
        for c in ops:
            result *= _node_to_fraction(c)
        return result

    if op == "divide":
        if len(ops) != 2:
            raise ValueError("Ожидалось два операнда для 'divide'.")
        num = _node_to_fraction(ops[0])
        den = _node_to_fraction(ops[1])
        if den == 0:
            raise ZeroDivisionError("Обнаружено деление на ноль в дереве выражения.")
        return num / den

    if op == "power":
        if len(ops) != 2:
            raise ValueError("Ожидались два операнда для 'power'.")
        base = _node_to_fraction(ops[0])
        exp_val = ops[1].get("value")
        if not isinstance(exp_val, int):
            raise ValueError("Показатель степени должен быть целым числом.")
        return base ** exp_val

    # Фоллбек по text
    if "text" in node:
        try:
            return Fraction(Decimal(str(node["text"]).replace(",", ".")))
        except Exception:
            pass

    return Fraction(0, 1)


def _extract_raw_fraction(node: Dict[str, Any]) -> Tuple[int, int]:
    """
    Возвращает дробь в исходном (сыром) виде — БЕЗ сокращений.
    Это строго для отображения шага ФИПИ (возведение в степень).
    """

    # 1) Чистая дробь {"type": "common"/"fraction", "value": [num, den]} или dict
    if node.get("type") in ("common", "fraction"):
        v = node.get("value")
        if isinstance(v, (list, tuple)) and len(v) == 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict) and "num" in v and "den" in v:
            return int(v["num"]), int(v["den"])

    # 2) Операция деления: num / den
    if node.get("operation") == "divide":
        ops = node.get("operands", [])
        if len(ops) == 2:
            num_raw, num_den = _extract_raw_fraction(ops[0])
            den_raw, den_den = _extract_raw_fraction(ops[1])
            # (num_raw/num_den) / (den_raw/den_den) =
            # (num_raw * den_den) / (num_den * den_raw)
            return num_raw * den_den, num_den * den_raw

    # 3) Целое число
    if node.get("type") == "integer":
        return int(node["value"]), 1

    # 4) Десятичное число → дробь
    if node.get("type") == "decimal":
        val = Decimal(str(node["value"]).replace(",", "."))
        num, den = val.as_integer_ratio()
        return int(num), int(den)

    # 5) Фоллбек по text
    if "text" in node:
        try:
            val = Decimal(str(node["text"]).replace(",", "."))
            num, den = val.as_integer_ratio()
            return int(num), int(den)
        except Exception:
            pass

    # дефолт
    return 0, 1


# ---------------------------------------------------------------------------
# powers_with_fractions
# ---------------------------------------------------------------------------

def _find_power_node(node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Ищет первый узел с operation == 'power' в поддереве.
    """
    if node.get("operation") == "power":
        return node

    for child in node.get("operands", []):
        if isinstance(child, dict):
            found = _find_power_node(child)
            if found is not None:
                return found
    return None


def _extract_left_right_nodes(root: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any], str]:
    """
    Ожидаем, что корень — это add или subtract с двумя операндами:
    left оперирует с степенью, right — вторая часть.
    """
    op = root.get("operation")
    operands = root.get("operands", [])
    if op not in {"add", "subtract"} or len(operands) != 2:
        raise ValueError("Ожидалась операция сложения/вычитания с двумя операндами.")
    return operands[0], operands[1], op


def _extract_left_structure(left_node: Dict[str, Any]) -> Dict[str, Any]:
    """
    Из левой части (где есть степень) достаём:
    - coef_node — коэффициент перед степенью
    - power_node — сам узел степени
    """
    if left_node.get("operation") == "multiply":
        ops = left_node.get("operands", [])
        if len(ops) == 2:
            if ops[0].get("operation") == "power":
                return {"coef_node": ops[1], "power_node": ops[0]}
            if ops[1].get("operation") == "power":
                return {"coef_node": ops[0], "power_node": ops[1]}

    # fallback: ищем power где-то внутри
    power_node = _find_power_node(left_node)
    if power_node is None:
        raise ValueError("В левой части выражения не найден узел со степенью.")
    return {"coef_node": left_node, "power_node": power_node}


def _extract_right_structure(right_node: Dict[str, Any]) -> Dict[str, Any]:
    """
    Усиленный распознаватель.
    Корректно находит коэффициент и дробь даже при записи дроби через divide.
    """

    def _is_fraction_like(node: Dict[str, Any]) -> bool:
        """Проверяет, можно ли трактовать узел как дробь без преобразований."""
        if not isinstance(node, dict):
            return False
        op = node.get("operation")
        if op in {"fraction", "divide"}:
            return True
        return node.get("type") in {"common", "fraction"}

    # Сценарий 1: правый узел — умножение коэффициента на дробь
    if right_node.get("operation") == "multiply":
        ops = right_node.get("operands", [])
        if len(ops) == 2:
            op1, op2 = ops[0], ops[1]
            if _is_fraction_like(op1):
                return {"mode": "mul_frac", "coef_node": op2, "frac_node": op1}
            if _is_fraction_like(op2):
                return {"mode": "mul_frac", "coef_node": op1, "frac_node": op2}

    # Сценарий 2: сама правая часть — дробь, коэффициент равен 1
    if _is_fraction_like(right_node):
        return {"mode": "mul_frac", "coef_node": {"type": "integer", "value": 1}, "frac_node": right_node}

    # Сценарий 3: обычное число/выражение без дроби
    return {"mode": "plain", "value_node": right_node}

def _build_power_formula_raw(num: int, den: int, exponent: int) -> str:
    """
    Строит строку вида:
    (1/5)² = 1²/5² = 1/25
    Без LaTeX и без '^'.
    """
    sup = _to_superscript(exponent)
    left = f"({num}/{den}){sup}"
    mid = f"{num}{sup}/{den}{sup}"
    res = f"{num ** exponent}/{den ** exponent}"
    return f"{left} = {mid} = {res}"


def _solve_powers_with_fractions(task_data: Dict[str, Any], expression_tree: Dict[str, Any]) -> Dict[str, Any]:
    """
    ФИНАЛЬНАЯ, ПОЛНОСТЬЮ ИСПРАВЛЕННАЯ ВЕРСИЯ.
    Реализует два разных педагогических сценария и корректно их выбирает.
    """
    builder = StepBuilder()

    # --- Общая часть: подготовка и парсинг ---
    expression_preview = _render_expression_from_question(task_data)
    builder.add(
        description_key="INITIAL_EXPRESSION",
        description_params={"expression": expression_preview},
    )
    left_node, right_node, root_op = _extract_left_right_nodes(expression_tree)
    left_struct = _extract_left_structure(left_node)
    # Используется исправленная версия с универсальным распознаванием дробей
    right_struct = _extract_right_structure(right_node)

    coef_left_node = left_struct["coef_node"]
    power_node = left_struct["power_node"]
    base_node, exp_node = power_node.get("operands", [None, None])
    if base_node is None or exp_node is None:
        raise ValueError("Некорректный узел степени.")

    raw_num, raw_den = _extract_raw_fraction(base_node)
    exponent = exp_node.get("value")
    base_frac_calc = Fraction(raw_num, raw_den)
    coef_left = _node_to_fraction(coef_left_node)

    # --- Диспетчер сценариев (ФИНАЛЬНАЯ ВЕРСИЯ) ---
    is_factorable = False
    if right_struct["mode"] == "mul_frac":
        # Сравниваем СЫРЫЕ значения, чтобы избежать проблем с авто-упрощением
        raw_base_num, raw_base_den = _extract_raw_fraction(base_node)
        raw_right_num, raw_right_den = _extract_raw_fraction(right_struct["frac_node"])
        if (raw_base_num, raw_base_den) == (raw_right_num, raw_right_den):
            is_factorable = True

    # --- Выбор и исполнение сценария ---
    final_result = None
    final_operation_name = "сложение" if root_op == "add" else "вычитание"
    idea_key = ""

    if is_factorable:
        # СЦЕНАРИЙ №1: Вынесение за скобку (теперь выбирается правильно)
        idea_key = "POWERS_FRACTIONS_FACTOR_OUT_IDEA"
        coef_right = _node_to_fraction(right_struct["coef_node"])
        op_symbol = "+" if root_op == "add" else "−"
        inside_expr = f"{_format_fraction(coef_left)} · {_format_fraction(base_frac_calc)} {op_symbol} {_format_fraction(coef_right)}"
        builder.add(
            description_key="POWERS_FACTOR_OUT",
            description_params={"num": raw_num, "den": raw_den},
            formula_calculation=f"{_format_fraction(base_frac_calc)} · ({inside_expr})"
        )
        inside_mult_result = coef_left * base_frac_calc
        builder.add(
            description_key="POWERS_MULTIPLY_IN_BRACKETS",
            description_params={},
            formula_calculation=f"{_format_fraction(coef_left)} · {_format_fraction(base_frac_calc)} = {_format_fraction(inside_mult_result)}"
        )
        bracket_result = inside_mult_result + coef_right if root_op == "add" else inside_mult_result - coef_right
        bracket_key = "POWERS_ADD_IN_BRACKETS" if root_op == "add" else "POWERS_SUBTRACT_IN_BRACKETS"
        builder.add(
            description_key=bracket_key,
            description_params={},
            formula_calculation=f"{_format_fraction(inside_mult_result)} {op_symbol} {_format_fraction(coef_right)} = {_format_fraction(bracket_result)}"
        )
        # Шаг 5. Финальное умножение
        final_result = base_frac_calc * bracket_result

        # Новый блок: форматируем второй множитель, добавляя скобки для отрицательных чисел
        formatted_bracket_value = f"({_format_fraction(bracket_result)})" if bracket_result < 0 else _format_fraction(bracket_result)

        builder.add(
            description_key="POWERS_FINAL_MULTIPLY",
            description_params={"num": raw_num, "den": raw_den, "value": _format_fraction(bracket_result)},
            formula_calculation=f"{_format_fraction(base_frac_calc)} · {formatted_bracket_value} = {_format_fraction(final_result)}"
        )

    else:
        # СЦЕНАРИЙ №2: Прямой счёт (теперь с исправленным БАГОМ Б)
        idea_key = "POWERS_FRACTIONS_STANDARD_IDEA"

        # Шаг 2. Возводим дробь в степень
        power_result = base_frac_calc ** exponent
        builder.add(
            description_key="POWERS_FRACTION_POWER",
            description_params={"num": raw_num, "den": raw_den, "exponent": exponent},
            formula_calculation=f"<b>{_build_power_formula_raw(raw_num, raw_den, exponent)}</b>",
        )

        # Шаг 3. Умножаем коэффициент на результат степени
        left_result = coef_left * power_result

        # ВАЖНО: Используем сырые значения для отображения, чтобы избежать скрытого упрощения
        raw_power_num = raw_num ** exponent
        raw_power_den = raw_den ** exponent
        cancel_gcd = math.gcd(coef_left.numerator, raw_power_den)

        builder.add(
            description_key="POWERS_MULTIPLY_WITH_CANCEL",
            description_params={
                "left_num": coef_left.numerator,
                "right_num": raw_power_num,
                "right_den": raw_power_den,
                "cancel_num": coef_left.numerator,
                "cancel_den": raw_power_den,
                "cancel_gcd": cancel_gcd,
            },
            formula_calculation=f"{_format_fraction(coef_left)} · {raw_power_num}/{raw_power_den} = {_format_fraction(left_result)}"
        )

        # Шаг 4. Вторая часть выражения
        right_result = None
        if right_struct["mode"] == "mul_frac":
            coef_right = _node_to_fraction(right_struct["coef_node"])
            frac_right = _node_to_fraction(right_struct["frac_node"])
            right_result = coef_right * frac_right
            cancel_gcd_r = math.gcd(coef_right.numerator, frac_right.denominator)
            builder.add(
                description_key="POWERS_MULTIPLY_WITH_CANCEL",
                description_params={
                    "left_num": coef_right.numerator, "right_num": frac_right.numerator, "right_den": frac_right.denominator,
                    "cancel_num": coef_right.numerator, "cancel_den": frac_right.denominator, "cancel_gcd": cancel_gcd_r,
                },
                formula_calculation=f"{_format_fraction(coef_right)} · {_format_fraction(frac_right)} = {_format_fraction(right_result)}"
            )
        else:
            right_result = _node_to_fraction(right_node)
            builder.add(
                description_key="POWERS_LEAVE_SECOND_NUMBER",
                description_params={},
                formula_calculation=_format_fraction(right_result),
            )

        # Шаг 5. Финальная операция
        final_result = left_result + right_result if root_op == "add" else left_result - right_result
        final_key = "POWERS_FINAL_ADD_INTEGERS" if root_op == "add" else "POWERS_FINAL_SUBTRACT_INTEGERS"
        op_symbol = "+" if root_op == "add" else "−"
        builder.add(
            description_key=final_key,
            description_params={},
            formula_calculation=f"{_format_fraction(left_result)} {op_symbol} {_format_fraction(right_result)} = {_format_fraction(final_result)}"
        )

    # --- Общая часть: формирование ответа ---
    value_display = _fraction_to_decimal_str(final_result)
    value_machine = float(Decimal(value_display.replace(',', '.')))

    # === ФИНАЛЬНЫЙ ШТРИХ: Контекстные подсказки ===
    hints = []
    if is_factorable:
        # Подсказки для сценария "Вынесение за скобку"
        hints = ["HINT_COMMON_FACTOR", "HINT_ORDER_OF_OPERATIONS"]
    else:
        # Стандартные подсказки для сценария "Прямой счет"
        hints = ["HINT_ORDER_OF_OPERATIONS", "HINT_POWER_OF_FRACTION"]

    return {
        "question_id": task_data.get("id"),
        "question_group": "TASK6_POWERS",
        "explanation_idea_key": idea_key,
        "explanation_idea_params": {"final_operation": final_operation_name},
        "calculation_steps": builder.steps,
        "final_answer": {
            "value_machine": value_machine,
            "value_display": value_display,
        },
        "hints_keys": hints,
    }

# ---------------------------------------------------------------------------
# powers_of_ten
# ---------------------------------------------------------------------------

def _parse_power_of_ten_expression(expr: str) -> Dict[str, Any]:
    """
    Парсинг строки вида:
        (2 · 10³) · (1.5 · 10⁻¹)
        (4 · 10²)² · (5 · 10⁻⁵)
        (8 · 10³) : (2 · 10)
        (3 · 10⁻¹)³ · (2 · 10⁴)

    Возвращает структуру:
    {
        "left": {"mant": Decimal, "exp": int, "outer_pow": int},
        "op": "multiply" | "divide",
        "right": {"mant": Decimal, "exp": int, "outer_pow": int}
    }
    """

    # Убираем пробелы вокруг операторов
    expr_clean = expr.replace(" ", "")

    # Паттерн блока (a·10ⁿ)ᵏ
    block_pattern = r"\(([^·]+)·10([⁰¹²³⁴⁵⁶⁷⁸⁹⁻]*)\)([⁰¹²³⁴⁵⁶⁷⁸⁹⁻]*)"
    blocks = re.findall(block_pattern, expr_clean)
    if len(blocks) != 2:
        raise ValueError(f"Не удалось распарсить два множителя вида (a·10ⁿ): '{expr}'")

    def superscript_to_int(s: str) -> int:
        mapping = {
            "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4",
            "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9", "⁻": "-"
        }
        if not s:
            return 1  # если нет внешней степени
        normal = "".join(mapping[ch] for ch in s)
        return int(normal)

    def parse_block(raw_mant: str, raw_exp: str, raw_outer: str) -> Dict[str, Any]:
        mant = Decimal(raw_mant.replace(",", "."))

        # Пустая степень → n = 0
        if raw_exp.strip() == "":
            exp = 0
        else:
            exp = superscript_to_int(raw_exp)

        outer_pow = superscript_to_int(raw_outer)
        return {"mant": mant, "exp": exp, "outer_pow": outer_pow}

    left_raw = blocks[0]
    right_raw = blocks[1]

    left = parse_block(*left_raw)
    right = parse_block(*right_raw)

    # Определяем операцию между блоками: '·' или ':'
    # Ищем символ между закрывающей и открывающей скобками
    op_match = re.search(r"\)[⁰¹²³⁴⁵⁶⁷⁸⁹⁻]*([·:])\(", expr_clean)
    if not op_match:
        raise ValueError(f"Не удалось определить операцию между блоками в выражении: '{expr}'")
    op_symbol = op_match.group(1)
    op = "multiply" if op_symbol == "·" else "divide"

    return {"left": left, "right": right, "op": op}


def _solve_powers_of_ten(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Реализует pipeline ФИПИ для pattern == powers_of_ten.
    Опирается ТОЛЬКО на question_text.
    """

    builder = StepBuilder()

    # 1) Получаем строку выражения из текста задания
    expr = _render_expression_from_question(task_data)

    # Шаг 1. Исходное выражение
    builder.add(
        description_key="INITIAL_EXPRESSION",
        description_params={"expression": expr},
    )

    # 2) Парсим выражение
    parsed = _parse_power_of_ten_expression(expr)
    left = parsed["left"]   # {"mant": Decimal, "exp": int, "outer_pow": int}
    right = parsed["right"] # {"mant": Decimal, "exp": int, "outer_pow": int}
    op = parsed["op"]       # "multiply" | "divide"

    # 3) Вычисляем "обработанный" левый множитель:
    # (a·10^n)^k = a^k · 10^(n·k), но ТОЛЬКО если k != 1.
    a1 = left["mant"]
    n1 = left["exp"]
    k1 = left["outer_pow"]

    if k1 == 1:
        # Внешней степени нет — не показываем лишний шаг,
        # работаем сразу с a1 и 10^n1
        a1_power = a1
        n1_power = n1
    else:
        # Есть настоящая степень — показываем раскрытие
        a1_power = a1 ** k1
        n1_power = n1 * k1

        builder.add(
            description_key="POWERS_TEN_EXPAND_POWER",
            description_params={},
            formula_calculation=(
                f"({_d_str(a1)} · 10{_to_superscript(n1)}){_to_superscript(k1)}"
                f" = {_d_str(a1)}^{k1} · 10{_to_superscript(n1_power)}"
                f" = {_d_str(a1_power)} · 10{_to_superscript(n1_power)}"
            ),
        )

    # 4) Подставляем результат в исходное выражение
    # 🔧 Если k1 == 1, левая часть не меняется — шаг можно пропустить,
    # чтобы не было странного «подставим полученный результат».
    if k1 != 1:
        op_symbol = "·" if op == "multiply" else ":"
        rewritten = (
            f"{_d_str(a1_power)} · 10{_to_superscript(n1_power)} "
            f"{op_symbol} "
            f"({_d_str(right['mant'])} · 10{_to_superscript(right['exp'])})"
        )

        builder.add(
            description_key="POWERS_TEN_REWRITE",
            description_params={},
            formula_calculation=rewritten,
        )
    else:
        # Всё равно нужен op_symbol дальше
        op_symbol = "·" if op == "multiply" else ":"

    # 5) Группируем множители
    mantissa_op_symbol = "·" if op == "multiply" else ":"

    builder.add(
        description_key="POWERS_TEN_GROUP",
        description_params={},
        formula_calculation=(
            f"({_d_str(a1_power)} {mantissa_op_symbol} {_d_str(right['mant'])}) · "
            f"(10{_to_superscript(n1_power)} {op_symbol} 10{_to_superscript(right['exp'])})"
        ),
    )

    # 6) Считаем отдельно числовую и степенную части
    if op == "multiply":
        mantissa = a1_power * right["mant"]
        exponent = n1_power + right["exp"]
    else:
        mantissa = a1_power / right["mant"]
        exponent = n1_power - right["exp"]

    # Определяем символы для красивой записи
    if op == "multiply":
        num_sym = "·"
        exp_sym = "·"
        exp_op_sup = "⁺"   # aⁿ · aᵐ = aⁿ⁺ᵐ
    else:
        num_sym = ":"
        exp_sym = ":"
        exp_op_sup = "⁻"   # aⁿ : aᵐ = aⁿ⁻ᵐ

    # === ИСПРАВЛЕНИЕ №1 НАЧАЛО ===
    # Раньше был один шаг с \n, теперь два отдельных.

    # Шаг 6.1. Вычисление мантиссы
    builder.add(
        # Новый ключ для ГОСТ-2025
        description_key="POWERS_TEN_CALCULATE_MANTISSA",
        description_params={},
        formula_calculation=f"{_d_str(a1_power)} {num_sym} {_d_str(right['mant'])} = {_d_str(mantissa)}"
    )

    # Шаг 6.2. Вычисление степени
    builder.add(
        # Новый ключ для ГОСТ-2025
        description_key="POWERS_TEN_CALCULATE_EXPONENT",
        description_params={},
        formula_calculation=(
            f"10{_to_superscript(n1_power)} {exp_sym} 10{_to_superscript(right['exp'])}"
            f" = 10{_to_superscript(n1_power)}{exp_op_sup}{_to_superscript(right['exp'])}"
            f" = 10{_to_superscript(exponent)}"
        )
    )
    # === ИСПРАВЛЕНИЕ №1 КОНЕЦ ===

    # 7) Финальный шаг: переводим mantissa · 10^exponent в обычное число
    final_decimal = mantissa * (Decimal(10) ** exponent)

    # === ИСПРАВЛЕНИЕ №2 НАЧАЛО ===
    # Замена ненадежного .rstrip() на проверку целочисленности.
    if final_decimal == final_decimal.to_integral_value():
        final_str = str(final_decimal.to_integral_value())
    else:
        # Убираем лишние нули на конце для дробных чисел, как normalize()
        final_str = format(final_decimal.normalize(), 'f')

    # Защита от пустого ответа, если результат был 0.00
    if final_str == "":
        final_str = "0"
    # === ИСПРАВЛЕНИЕ №2 КОНЕЦ ===

    builder.add(
        description_key="POWERS_TEN_FINAL",
        description_params={},
        formula_calculation=f"{_d_str(mantissa)} · 10{_to_superscript(exponent)} = {final_str.replace('.', ',')}",
    )

    return {
        "question_id": task_data.get("id"),
        "question_group": "TASK6_POWERS",
        "explanation_idea_key": "POWERS_OF_TEN_IDEA",
        "explanation_idea_params": {},
        "calculation_steps": builder.steps,
        "final_answer": {
            "value_machine": float(final_decimal),
            "value_display": final_str.replace('.', ','),
        },
        "hints_keys": ["HINT_ORDER_OF_OPERATIONS"],
    }
