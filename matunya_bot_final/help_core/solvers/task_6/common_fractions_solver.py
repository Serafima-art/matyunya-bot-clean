# ============================================================
#  TASK 6 — common_fractions
#  Полный решатель для всех 4 паттернов:
#  1. cf_addition_subtraction
#  2. multiplication_division
#  3. parentheses_operations
#  4. complex_fraction
# ============================================================

from __future__ import annotations
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Dict, List, Optional
import math
import re


# ============================================================
#  StepBuilder — стандартный
# ============================================================

@dataclass
class StepBuilder:
    steps: List[Dict[str, Any]] = field(default_factory=list)
    counter: int = 1
    context: Dict[str, Any] = field(default_factory=dict)   # ← ДОБАВИТЬ!

    def add(
        self,
        description_key: str,
        description_params: Optional[Dict[str, Any]] = None,
        formula_calculation: Optional[str] = None,
    ):
        step = {
            "step_number": self.counter,
            "description_key": description_key,
            "description_params": description_params or {},
        }
        if formula_calculation:
            step["formula_calculation"] = f"<b>{formula_calculation}</b>"
        self.steps.append(step)
        self.counter += 1

# ============================================================
#  Главная функция-роутер
# ============================================================

def solve(task_data: Dict[str, Any]) -> Dict[str, Any]:
    pattern = task_data.get("pattern")
    tree = task_data["variables"]["expression_tree"]
    question_text = task_data.get("question_text", "")
    answer_type = task_data.get("answer_type", "fraction")

    builder = StepBuilder()

    # Добавляем исходное выражение
    builder.add(
        "INITIAL_EXPRESSION",
        {"expression": _extract_expression_preview(question_text, tree)}
    )

    # ---------------------------
    # РЕЖИМ ФИНАЛЬНОГО ШАГА: числитель/знаменатель
    # ---------------------------
    text_lower = (question_text or "").lower()

    # If in wording: "запиши только числитель/знаменатель"
    if "только знаменатель" in text_lower:
        builder.context["final_mode"] = "denominator"
    elif "только числитель" in text_lower:
        builder.context["final_mode"] = "numerator"

    # ---------------------------
    # ПАТТЕРНЫ
    # ---------------------------
    if pattern == "cf_addition_subtraction":
        subtype = task_data.get("subtype", "")

        # Берём то, что уже установлено по тексту
        final_mode = getattr(builder, "context", {}).get("final_mode")

        # Если по подтипу есть уточнение — переопределяем
        if subtype.endswith("_numerator"):
            final_mode = "numerator"
        elif subtype.endswith("_denominator"):
            final_mode = "denominator"

        # Если в итоге режим определён — сохраняем его в контекст
        if final_mode is not None:
            builder.context["final_mode"] = final_mode

        # Основной расчёт
        frac = _solve_add_sub(tree, builder)
        idea_key = "ADD_SUB_FRACTIONS_IDEA"
        idea_params = {
            "operation_name": "сложить" if tree["operation"] == "add" else "вычесть"
        }
        hints = ["HINT_FIND_LCM"]

    elif pattern == "multiplication_division":
        frac = _solve_mult_div(tree, builder)
        idea_key = "MULTIPLY_DIVIDE_FRACTIONS_IDEA"
        idea_params = {}
        hints = ["HINT_CROSS_CANCEL"]

    elif pattern == "parentheses_operations":
        frac = _solve_parentheses(
        tree,
        builder,
        task_data.get("question_text", "")
        )
        idea_key = "PARENTHESES_OPERATIONS_IDEA"
        idea_params = {}
        hints = ["HINT_ORDER_OF_OPERATIONS"]

    elif pattern == "complex_fraction":
        frac = _solve_complex_fraction(tree, builder)
        idea_key = "COMPLEX_FRACTION_IDEA"
        idea_params = {}
        hints = ["HINT_DIVIDE_AS_MULTIPLY"]

    else:
        raise NotImplementedError(f"Неизвестный паттерн: {pattern}")

    # ======================================================
    #  Финальный ответ
    # ======================================================
    final_mode = getattr(builder, "context", {}).get("final_mode")  # может быть None

    if answer_type == "decimal":
        val_display = f"{float(frac):g}".replace(".", ",")
    elif answer_type == "integer":
        if final_mode == "denominator":
            val_display = str(frac.denominator)
        else:
            # по умолчанию — числитель (как было раньше)
            val_display = str(frac.numerator)
    else:
        val_display = _format_fraction(frac)

    return {
        "question_id": task_data.get("id"),
        "question_group": "TASK6_COMMON",
        "explanation_idea_key": idea_key,
        "explanation_idea_params": idea_params,
        "calculation_steps": builder.steps,
        "final_answer": {
            "value_machine": float(frac),
            "value_display": val_display,
        },
        "hints_keys": hints,
    }


# ============================================================
#  ПАТТЕРН 1 — ADDITION / SUBTRACTION
# ============================================================

def _solve_add_sub(tree: Dict, builder: StepBuilder) -> Fraction:
    op = tree["operation"]
    operands = tree["operands"]

    # -----------------------------------------------
    # Шаг 0: найти все смешанные и показать преобразование
    # -----------------------------------------------
    mixed_conversions: List[str] = []

    for operand in operands:
        txt = operand.get("text", "")
        if " " in txt and "/" in txt:
            # пример: "2 1/3"
            try:
                whole_str, frac_str = txt.split(" ", 1)
                num_str, den_str = frac_str.split("/", 1)

                whole = int(whole_str)
                num = int(num_str)
                den = int(den_str)

                improper_num = whole * den + num
                improper_den = den

                mixed_conversions.append(
                    f"{txt} = ({whole} · {den} + {num}) / {den} = {improper_num} / {improper_den}"
                )
            except (ValueError, TypeError):
                # если вдруг текст не парсится — молча пропускаем
                continue

    if mixed_conversions:
        builder.add(
            "CONVERT_ALL_MIXED",
            {},
            "\n".join(mixed_conversions)  # \n, чтобы Telegram не ругался на <br>
        )

    # -----------------------------------------------
    # Дальше — твоя стандартная логика сложения/вычитания
    # -----------------------------------------------
    left = _to_fraction(operands[0])
    right = _to_fraction(operands[1])

    common_den = _lcm(left.denominator, right.denominator)

    builder.add(
        "CF_FIND_LCM",
        {"den1": left.denominator, "den2": right.denominator, "lcm": common_den},
    )

    left_mult = common_den // left.denominator
    right_mult = common_den // right.denominator
    left_scaled_num = left.numerator * left_mult
    right_scaled_num = right.numerator * right_mult

    # Подготовим удобные переменные для формулы
    l_num = left.numerator
    l_den = left.denominator
    r_num = right.numerator
    r_den = right.denominator

    m1 = left_mult
    m2 = right_mult
    n1 = left_scaled_num
    n2 = right_scaled_num
    lcm = common_den

    builder.add(
        "CF_SCALE_FRACTIONS",
        {
            "l_mult": m1,
            "r_mult": m2,
            "l_num": l_num,
            "l_den": l_den,
            "r_num": r_num,
            "r_den": r_den,
            "n1": n1,
            "n2": n2,
            "lcm": lcm,
        },
        (
            f"{l_num}/{l_den} = ({l_num} · {m1}) / ({l_den} · {m1}) = {n1}/{lcm}\n"
            f"{r_num}/{r_den} = ({r_num} · {m2}) / ({r_den} · {m2}) = {n2}/{lcm}"
        )
    )

    if op == "add":
        result_num = left_scaled_num + right_scaled_num
        op_symbol = "+"
        op_name = "складываем"
    else:
        result_num = left_scaled_num - right_scaled_num
        op_symbol = "−"
        op_name = "вычитаем"

    builder.add(
        "CF_COMBINE_NUMERATORS",
        {"operation_name": op_name},
        f"({left_scaled_num} {op_symbol} {right_scaled_num}) / {common_den} = {result_num}/{common_den}",
    )

    # --- Сокращение вручную, без использования Fraction ---
    raw_num = result_num
    raw_den = common_den

    gcd = math.gcd(raw_num, raw_den)
    if gcd > 1:
        # Показываем педагогический шаг сокращения
        builder.add(
            "CF_REDUCE_FINAL",
            {
                "num": raw_num,
                "den": raw_den,
                "gcd": gcd,
            },
            f"{raw_num}/{raw_den} = {raw_num//gcd}/{raw_den//gcd}"
        )

    # Теперь создаём конечную дробь (только сейчас Fraction!):
    result_frac = Fraction(raw_num, raw_den)

    # --- Новый блок: взять числитель или знаменатель, если требуется ---
    final_mode = builder.context.get("final_mode")

    if final_mode == "numerator":
        builder.add(
            "EXTRACT_NUMERATOR",
            {"num": result_frac.numerator, "den": result_frac.denominator},
            None   # ← формулы нет!
        )

    elif final_mode == "denominator":
        builder.add(
            "EXTRACT_DENOMINATOR",
            {"num": result_frac.numerator, "den": result_frac.denominator},
            None   # ← формулы нет!
        )

    return result_frac


# ============================================================
#  ПАТТЕРН 2 — MULTIPLICATION / DIVISION
# ============================================================

def _solve_mult_div(tree: Dict, builder: StepBuilder) -> Fraction:
    op = tree["operation"]
    l = _to_fraction(tree["operands"][0])
    r = _to_fraction(tree["operands"][1])

    # -----------------------------------------------
    # Шаг 0: Найти все смешанные и показать преобразование
    # -----------------------------------------------
    mixed_conversions = []

    for operand in tree["operands"]:
        txt = operand.get("text", "")
        if " " in txt and "/" in txt:
            whole_str, frac_str = txt.split(" ", 1)
            num_str, den_str = frac_str.split("/", 1)

            whole = int(whole_str)
            num = int(num_str)
            den = int(den_str)

            improper_num = whole * den + num
            improper_den = den

            mixed_conversions.append(
                f"{txt} = ({whole} · {den} + {num}) / {den} = {improper_num}/{improper_den}"
            )

    if mixed_conversions:
        builder.add(
            "CONVERT_ALL_MIXED",
            {},
            "\n".join(mixed_conversions)
        )

    # -----------------------------------------------
    # 1. МНОЖЕНИЕ
    # -----------------------------------------------
    if op == "multiply":
        result = l * r
        builder.add(
            "CALCULATE_MULTIPLICATION_DEFAULT",
            {"left": _format_fraction(l), "right": _format_fraction(r)},
            f"{_format_fraction(l)} · {_format_fraction(r)} = {_format_fraction(result)}"
        )

    else:
        # -----------------------------------------------
        # 2. ДЕЛЕНИЕ
        # -----------------------------------------------
        flipped = Fraction(r.denominator, r.numerator)
        result = l / r

        builder.add(
            "MIXED_DIVIDE",
            {
                "left": _format_fraction(l),
                "right": _format_fraction(r),
                "flipped": _format_fraction(flipped),
                "left_num": l.numerator,
                "left_den": l.denominator,
                "right_num": r.numerator,
                "right_den": r.denominator,
                "result": _format_fraction(result)
            },
            f"{_format_fraction(l)} : {_format_fraction(r)} = "
            f"{_format_fraction(l)} · {_format_fraction(flipped)} = {_format_fraction(result)}"
        )

    # -----------------------------------------------
    # 3. Сокращение результата
    # -----------------------------------------------
    g = math.gcd(result.numerator, result.denominator)
    if g > 1:
        builder.add(
            "CF_REDUCE_FINAL",
            {"num": result.numerator, "den": result.denominator, "gcd": g},
            f"{result.numerator}/{result.denominator} = "
            f"{result.numerator // g}/{result.denominator // g}"
        )
        result = Fraction(result.numerator // g, result.denominator // g)

    # -----------------------------------------------
    # 4. Перевод в десятичный формат
    # -----------------------------------------------
    if result.denominator != 1:
        decimal_value = result.numerator / result.denominator
        builder.add(
            "CONVERT_TO_DECIMAL",
            {"num": result.numerator, "den": result.denominator, "decimal": decimal_value},
            f"{result.numerator}/{result.denominator} = {str(decimal_value).replace('.', ',')}"
        )

    return result


# ============================================================
#  ПАТТЕРН 3 — (A ± B) · C
# ============================================================

def _solve_parentheses(tree: Dict, builder: StepBuilder, question_text: str) -> Fraction:
    """
    Универсальный решатель для паттерна parentheses_operations:
    (A ± B) ⋅ C   или   (A ± B) : C
    включая случаи со смешанными числами в скобках.

    Логика:
    1) Перевод всех смешанных чисел по question_text → шаг 2
    2) Обновляем expression_tree значениями improper-дробей
    3) Выполняем вычисление в скобках одним шагом
    4) Выполняем умножение / деление
    5) Сокращаем результат
    """

    # -----------------------------------------------------
    # 0. Шаг: перевод всех смешанных чисел (по question_text)
    # -----------------------------------------------------
    mixed_conversions = []

    for whole_str, frac_str in re.findall(r'(\d+)\s+(\d+/\d+)', question_text):
        num_str, den_str = frac_str.split("/", 1)
        whole = int(whole_str)
        num = int(num_str)
        den = int(den_str)

        improper_num = whole * den + num
        improper_den = den

        mixed_conversions.append(
            f"{whole} {num}/{den} = ({whole} · {den} + {num})/{den} = {improper_num}/{improper_den}"
        )

    if mixed_conversions:
        builder.add(
            "CONVERT_ALL_MIXED",
            {},  # параметры для шаблона не нужны
            "\n".join(mixed_conversions)
        )

    # 🔥 ВАЖНО: просто определяем inner_node,
    # но НЕ лезем в inner_node["operands"] на этом этапе
    inner_node = tree["operands"][0]

    # ------------------------------------------------------------------
    # 1. Обновляем expression_tree, заменяя mixed → improper
    # ------------------------------------------------------------------
    all_nodes = []

    if "operands" in inner_node:       # (A ± B)
        all_nodes.extend(inner_node["operands"])
    else:                              # (A)
        all_nodes.append(inner_node)

    all_nodes.append(tree["operands"][1])

    for node in all_nodes:
        txt = node.get("text", "")
        m = re.match(r'(\d+)\s+(\d+)/(\d+)', txt)
        if m:
            whole = int(m.group(1))
            num = int(m.group(2))
            den = int(m.group(3))

            improper_num = whole * den + num
            improper_den = den
            node["value"] = [improper_num, improper_den]

    # ------------------------------------------------------------------
    # 2. Внутреннее выражение в скобках
    # ------------------------------------------------------------------
    # Возможны два случая:
    #   (A ± B)
    #   (A)
    inner_node = tree["operands"][0]
    op = inner_node["operation"]
    left_node, right_node = inner_node["operands"]

    left = _to_fraction(left_node)
    right = _to_fraction(right_node)

    b1 = left.denominator
    b2 = right.denominator
    lcm_val = math.lcm(b1, b2)

    m1 = lcm_val // b1
    m2 = lcm_val // b2

    n1 = left.numerator * m1
    n2 = right.numerator * m2

    if op == "add":
        result_num = n1 + n2
        op_symbol = "+"
    else:
        result_num = n1 - n2
        op_symbol = "−"

    inner_fraction = Fraction(result_num, lcm_val)

    full_formula = (
        f"{left.numerator}/{left.denominator} {op_symbol} {right.numerator}/{right.denominator} = "
        f"({left.numerator} · {m1})/({left.denominator} · {m1}) "
        f"{op_symbol} ({right.numerator} · {m2})/({right.denominator} · {m2}) = "
        f"{n1}/{lcm_val} {op_symbol} {n2}/{lcm_val} = "
        f"{inner_fraction.numerator}/{inner_fraction.denominator}"
    )

    builder.add(
        "PARENTHESES_INNER_ADD_SUB",
        {
            "expression": f"{_format_fraction(left)} {op_symbol} {_format_fraction(right)}",
            "lcm": lcm_val,
        },
        full_formula
    )

    # ------------------------------------------------------------------
    # 3. Внешняя операция умножения или деления
    # ------------------------------------------------------------------
    outer_op = tree["operation"]
    right_operand = _to_fraction(tree["operands"][1])

    if outer_op == "multiply":
        builder.add(
            "CALCULATE_MULTIPLICATION_DEFAULT",
            {
                "left": _format_fraction(inner_fraction),
                "right": _format_fraction(right_operand),
            },
            f"{_format_fraction(inner_fraction)} · {_format_fraction(right_operand)} = "
            f"{_format_fraction(inner_fraction * right_operand)}"
        )
        res = inner_fraction * right_operand

    else:
        # Деление
        flipped = Fraction(right_operand.denominator, right_operand.numerator)
        result_tmp = inner_fraction / right_operand

        builder.add(
            "MIXED_DIVIDE",
            {
                "left": _format_fraction(inner_fraction),
                "right": _format_fraction(right_operand),
                "flipped": _format_fraction(flipped),
                "left_num": inner_fraction.numerator,
                "left_den": inner_fraction.denominator,
                "right_num": right_operand.numerator,
                "right_den": right_operand.denominator,
                "result": _format_fraction(result_tmp),
            },
            f"{_format_fraction(inner_fraction)} : {_format_fraction(right_operand)} = "
            f"{_format_fraction(inner_fraction)} · {_format_fraction(flipped)} = "
            f"{_format_fraction(result_tmp)}"
        )
        res = result_tmp

    # -----------------------------------------------------
    # 3. Сокращение результата
    # -----------------------------------------------------
    g = math.gcd(res.numerator, res.denominator)
    if g > 1:
        builder.add(
            "CF_REDUCE_FINAL",
            {"num": res.numerator, "den": res.denominator, "gcd": g},
            f"{res.numerator}/{res.denominator} = {res.numerator // g}/{res.denominator // g}"
        )
        res = Fraction(res.numerator // g, res.denominator // g)

    # -----------------------------------------------------
    # 4. Переводим дробь в десятичную, если требуется форматом ОГЭ
    # -----------------------------------------------------
    if res.denominator != 1:
        decimal_value = res.numerator / res.denominator
        builder.add(
            "CONVERT_TO_DECIMAL",
            {"num": res.numerator, "den": res.denominator, "decimal": decimal_value},
            f"{res.numerator}/{res.denominator} = {decimal_value}"
        )

    return res

def _solve_complex_fraction(tree: Dict, builder: StepBuilder) -> Fraction:
    top = tree["operands"][0]
    bottom = tree["operands"][1]

    # 1. В числителе всегда add/sub
    inner_tree = {
        "operation": top["operation"],
        "operands": top["operands"]
    }
    # 1. ЧИСЛИТЕЛЬ: объединённый шаг add/sub с НОЗ
    op = inner_tree["operation"]
    left_node, right_node = inner_tree["operands"]

    left = _to_fraction(left_node)
    right = _to_fraction(right_node)

    b1 = left.denominator
    b2 = right.denominator
    lcm_val = math.lcm(b1, b2)

    m1 = lcm_val // b1
    m2 = lcm_val // b2

    n1 = left.numerator * m1
    n2 = right.numerator * m2

    if op == "add":
        result_num = n1 + n2
        op_symbol = "+"
    else:
        result_num = n1 - n2
        op_symbol = "−"

    num = Fraction(result_num, lcm_val)

    # Формула в одну строку (как в parentheses_operations)
    full_formula = (
        f"{left.numerator}/{left.denominator} {op_symbol} "
        f"{right.numerator}/{right.denominator} = "
        f"({left.numerator} · {m1})/({left.denominator} · {m1}) "
        f"{op_symbol} ({right.numerator} · {m2})/({right.denominator} · {m2}) = "
        f"{n1}/{lcm_val} {op_symbol} {n2}/{lcm_val} = "
        f"{num.numerator}/{num.denominator}"
    )

    builder.add(
        "PARENTHESES_INNER_ADD_SUB",
        {
            "expression": f"{_format_fraction(left)} {op_symbol} {_format_fraction(right)}",
            "lcm": lcm_val,
        },
        full_formula
    )

    # 2. Знаменатель
    den = _to_fraction(bottom)

    # ⭐ ОСОБЫЙ СЛУЧАЙ: деление дроби самой на себя
    if num == den:
        builder.add(
            "DIVIDE_SAME_VALUE",
            {"value": _format_fraction(num)},
            f"{_format_fraction(num)} : {_format_fraction(den)} = 1"
        )
        return Fraction(1, 1)

    # 3. Обычное деление
    flipped = Fraction(den.denominator, den.numerator)

    builder.add(
        "MIXED_DIVIDE",
        {
            "left": _format_fraction(num),
            "right": _format_fraction(den),
            "flipped": _format_fraction(flipped),
            "left_num": num.numerator,
            "left_den": num.denominator,
            "right_num": den.numerator,
            "right_den": den.denominator,
            "result": _format_fraction(num / den)
        },
        f"{_format_fraction(num)} : {_format_fraction(den)} = "
        f"{_format_fraction(num)} · {_format_fraction(flipped)}"
    )

    res = num / den

    # сокращение
    g = math.gcd(res.numerator, res.denominator)
    if g > 1:
        builder.add(
            "CF_REDUCE_FINAL",
            {"num": res.numerator, "den": res.denominator, "gcd": g},
            f"{res.numerator}/{res.denominator} = {res.numerator // g}/{res.denominator // g}"
        )
        res = Fraction(res.numerator // g, res.denominator // g)

    # -----------------------------------------------------
    # 4. Если результат — обыкновенная дробь, добавляем шаг перевода в десятичную
    # -----------------------------------------------------
    if res.denominator != 1:
        builder.add(
            "CONVERT_TO_DECIMAL",
            {"num": res.numerator, "den": res.denominator},
            f"{res.numerator}/{res.denominator} = {float(res)}"
        )

    return res


# ============================================================
#  Утилиты
# ============================================================

def _to_fraction(node: Dict) -> Fraction:
    t = node.get("type")

    # БАЗОВЫЕ ТИПЫ
    if t == "common":
        return Fraction(node["value"][0], node["value"][1])
    if t == "integer":
        return Fraction(node["value"])

    # ЕСЛИ ЭТО ВЫРАЖЕНИЕ (add/sub/mult/div)
    if "operation" in node:
        op = node["operation"]
        left = _to_fraction(node["operands"][0])
        right = _to_fraction(node["operands"][1])

        if op == "add":
            return left + right
        elif op == "subtract":
            return left - right
        elif op == "multiply":
            return left * right
        elif op == "divide":
            return left / right
        else:
            raise ValueError(f"Неизвестная операция: {op}")

    raise ValueError(f"Неизвестный тип узла: {node}")

def _lcm(a: int, b: int) -> int:
    return abs(a * b) // math.gcd(a, b)

def _format_fraction(fr: Fraction) -> str:
    if fr.denominator == 1:
        return str(fr.numerator)
    return f"{fr.numerator}/{fr.denominator}"

def _extract_expression_preview(text: str, tree: Dict) -> str:
    # берём строку вопроса или fallback по дереву
    for line in text.splitlines():
        if "/" in line:
            return line.strip()
    # fallback
    a = tree["operands"][0]["text"]
    b = tree["operands"][1]["text"]
    op = tree["operation"]
    sym = {"add": "+", "subtract": "−", "multiply": "·", "divide": ":"}[op]
    return f"{a} {sym} {b}"
