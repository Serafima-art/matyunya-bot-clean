"""
Solver for Task 8: Powers and Roots.
Handles numeric expressions with roots and powers (subtypes without variables).
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Tuple, Optional

# Пока импортируем форматтер, он пригодится позже
from matunya_bot_final.help_core.solvers.task_8.task_8_text_formatter import (
    render_node,
    to_superscript,
    fmt_number
)


def solve(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Главная точка входа для подтипа powers_and_roots.
    """
    if not isinstance(task_data, dict):
        raise ValueError("task_data должен быть словарём")

    pattern = task_data.get("solution_pattern") or task_data.get("pattern")

    # Роутер по паттернам
    if pattern == "squared_radical":
        return _solve_squared_radical(task_data)

    if pattern == "radical_multiplication":
        return _solve_radical_multiplication(task_data)

    if pattern == "radical_product":
        return _solve_radical_product(task_data)

    if pattern == "radical_product_with_powers":
        return _solve_radical_product_with_powers(task_data)

    if pattern == "radical_fraction":
        return _solve_radical_fraction(task_data)

    if pattern == "conjugate_radicals":
        return _solve_conjugate_radicals(task_data)

    if pattern == "numeric_power_fraction":
        return _solve_numeric_power_fraction(task_data)

    if pattern == "count_integers_between_radicals":
        return _solve_count_integers_between_radicals(task_data)

    return _solve_placeholder(task_data, pattern or "unknown")


def _solve_placeholder(task_data: Dict[str, Any], pattern: str) -> Dict[str, Any]:
    """Временная заглушка."""
    return {
        "question_id": f"task8_{pattern}",
        "question_group": "task_8_powers_and_roots",
        "explanation_idea": "Решение для этого типа задач находится в активной разработке. 🔨",
        "calculation_steps": [
            {
                "step_number": 1,
                "description": f"Мы работаем над алгоритмом для паттерна <b>{pattern}</b>.",
                "formula_calculation": None
            }
        ],
        "final_answer": {"value_display": task_data.get("answer", "???")},
        "hints": [],
        "knowledge_tips": ["Скоро здесь будет красиво!"]
    }

# ============================================================================
# ПАТТЕРН 2.1: squared_radical
# ============================================================================

def _solve_squared_radical(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Решатель для (a√b)² / C или C / (a√b)².
    """
    # 1. Анализ структуры (кто где?)
    tree = task_data["expression_tree"]
    # Определяем, где квадрат (power): в числителе или знаменателе
    if tree["numerator"].get("type") == "power":
        loc_text = "числителе"
    else:
        loc_text = "знаменателе"

    steps = _build_steps_for_squared_radical(task_data, loc_text)

    return {
        "question_id": "task8_squared_radical",
        "question_group": "task_8_powers_and_roots",
        "explanation_idea_key": "IDEA_SQUARED_RADICAL",
        "explanation_idea_params": {"location": loc_text},
        "knowledge_tips_key": "KNOWLEDGE_SQUARED_RADICAL",
        "calculation_steps": steps,
        "final_answer": {
            "value_display": task_data["answer"],
        },
    }


def _build_steps_for_squared_radical(task_data: Dict[str, Any], location: str) -> List[Dict[str, Any]]:
    tree = task_data["expression_tree"]
    steps = []
    step_num = 1

    # --- ШАГ 1. Исходное выражение ---
    steps.append({
        "step_number": step_num,
        "description_key": "STEP_INITIAL_NO_VARS",
        "description_params": {"expr": render_node(tree)}
    })
    step_num += 1

    # --- Анализ данных ---
    # Нам нужно найти узел с квадратом (complex_part) и узел с числом (simple_part)
    if location == "числителе":
        complex_node = tree["numerator"]
        simple_node = tree["denominator"]
    else:
        complex_node = tree["denominator"]
        simple_node = tree["numerator"]

    # Парсим (2√3)²
    # Структура: Power -> Base (Product -> [2, √3]) -> Exp (2)
    # Или просто (√3)²: Power -> Base (Sqrt -> 3)

    base = complex_node["base"]
    # Извлекаем множители a и √b
    # a - число перед корнем (может быть 1, тогда его нет в product)
    # b - число под корнем

    a_val = 1
    b_val = 1

    if base.get("type") == "product":
        # Случай 2√3
        for f in base["factors"]:
            if f.get("type") == "integer":
                a_val = f["value"]
            elif f.get("type") == "sqrt":
                b_val = f["radicand"]["value"]
    elif base.get("type") == "sqrt":
        # Случай √3
        b_val = base["radicand"]["value"]

    # Вычисляем квадрат: (a√b)² = a² * b
    a_sq = a_val ** 2
    res_sq = a_sq * b_val

    # Формируем строку формулы: (2√3)² = 2² · (√3)² = 4 · 3 = 12
    # Или (√3)² = 3
    src_str = render_node(complex_node)

    if a_val != 1:
        calc_str = f"<b>{src_str} = {a_val}² · (√{b_val})² = {a_sq} · {b_val} = {res_sq}</b>"
    else:
        calc_str = f"<b>{src_str} = {b_val}</b>"

    # --- ШАГ 2. Возведение в квадрат ---
    steps.append({
        "step_number": step_num,
        "description_key": "STEP_CALCULATE_SQUARE",
        "description_params": {"location": location},
        "formula_calculation": calc_str
    })
    step_num += 1

    # --- ШАГ 3. Сокращение ---
    # Формируем дробь: Полученное / Число (или наоборот)
    c_val = simple_node["value"]

    if location == "числителе":
        num_val = res_sq
        den_val = c_val
    else:
        num_val = c_val
        den_val = res_sq

    # Сокращаем
    gcd_val = math.gcd(num_val, den_val)
    fin_num = num_val // gcd_val
    fin_den = den_val // gcd_val

    frac_str = f"{num_val}/{den_val}"
    reduced_str = f"{fin_num}/{fin_den}"

    # Если знаменатель ушел (стал 1)
    if fin_den == 1:
        res_show = str(fin_num)
    else:
        res_show = reduced_str

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_SUBSTITUTE_AND_REDUCE",
        "description_params": {"gcd": str(gcd_val)},
        "formula_calculation": f"<b>{frac_str} = {res_show}</b>"
    })
    step_num += 1

    # --- ШАГ 4. Ответ (если осталась дробь) ---
    # Если результат целый, мы его уже показали в шаге 3, но можно продублировать или завершить
    # В эталоне есть шаг 4 для 2/5 -> 0.4
    if fin_den != 1:
        final_ans = task_data["answer"]
        steps.append({
            "step_number": step_num,
            "description_key": "STEP_CONVERT_TO_DECIMAL",
            "description_params": {"frac": reduced_str},
            "formula_calculation": f"<b>{reduced_str} = {fin_num} : {fin_den} = {final_ans}</b>"
        })

    return steps

# ============================================================================
# ПАТТЕРН 2.2: radical_multiplication
# ============================================================================

def _solve_radical_multiplication(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Решатель для (√A ± √B) · √C.
    """
    steps = _build_steps_for_radical_multiplication(task_data)
    return {
        "question_id": "task8_radical_multiplication",
        "question_group": "task_8_powers_and_roots",
        "explanation_idea_key": "IDEA_RADICAL_MULTIPLICATION",
        "knowledge_tips_key": "KNOWLEDGE_RADICAL_MULTIPLICATION",
        "calculation_steps": steps,
        "final_answer": {
            "value_display": task_data["answer"],
        },
    }


def _build_steps_for_radical_multiplication(task_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    tree = task_data["expression_tree"]
    steps = []
    step_num = 1

    # --- ШАГ 1. Исходное выражение ---
    steps.append({
        "step_number": step_num,
        "description_key": "STEP_INITIAL_NO_VARS",
        "description_params": {"expr": render_node(tree)}
    })
    step_num += 1

    # --- Анализ структуры ---
    # Ожидаем Product -> [BinaryOp(Sqrt(A), Sqrt(B)), Sqrt(C)]
    # Или BinaryOp(Sqrt(A), Sqrt(B)) · Sqrt(C) - порядок может быть разным, но обычно скобка первая

    factors = tree["factors"]
    bracket_node = None
    outside_node = None

    for f in factors:
        if f.get("type") == "binary_op":
            bracket_node = f
        elif f.get("type") == "sqrt":
            outside_node = f

    # Извлекаем числа A, B, C
    # В скобках: √A ± √B
    node_A = bracket_node["left"]
    node_B = bracket_node["right"]
    op_symbol = bracket_node["op"] # "+" или "-"

    val_A = node_A["radicand"]["value"]
    val_B = node_B["radicand"]["value"]
    val_C = outside_node["radicand"]["value"]

    # --- ШАГ 2. Упрощение корней ---
    # Нам нужно упростить A и B (и C, если оно упрощается, как √12 -> 2√3)

    roots_to_simplify = []
    if _can_simplify(val_A): roots_to_simplify.append((val_A, "A"))
    if _can_simplify(val_B): roots_to_simplify.append((val_B, "B"))
    if _can_simplify(val_C): roots_to_simplify.append((val_C, "C"))

    decomp_lines = []

    # Словари для хранения упрощенных значений: {key: (coeff, inner)}
    # key = 'A', 'B', 'C'
    # Пример: 75 -> (5, 3)
    simplified_map = {}

    # Функция для обработки и записи строки
    def process_root(val, key):
        sq, rem, root_sq = _simplify_integer_radical(val)
        simplified_map[key] = (root_sq, rem)

        # Если упрощения нет (sq=1), просто запоминаем, но строку не пишем
        if sq == 1:
            return

        # Строка: ➡️ √75 = √(25 · 3) = √25 · √3 = 5√3
        line = (
            f"<b>√{val} = √({sq} · {rem}) = √{sq} · √{rem} = {root_sq}√{rem}</b>"
        )
        decomp_lines.append(line)

    # Обрабатываем все три числа (даже если C стоит снаружи, в примере √12 его упрощают)
    process_root(val_A, "A")
    process_root(val_B, "B")
    process_root(val_C, "C")

    # Список корней для текста (только те, что реально упрощали)
    roots_list_str = ", ".join([f"<b>√{val}</b>" for val, key in roots_to_simplify])

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_SIMPLIFY_INT_ROOTS",
        "description_params": {
            "roots_list": roots_list_str,
            "decomp_str": "\n".join([f"➡️ {l}" for l in decomp_lines])
        }
    })
    step_num += 1

    # --- ШАГ 3. Подстановка ---
    # (5√3 + √3) · 2√3

    def get_simple_str(key, original_val):
        if key in simplified_map and simplified_map[key][0] > 1:
            c, r = simplified_map[key]
            return f"{c}√{r}"
        return f"√{original_val}"

    str_A = get_simple_str("A", val_A)
    str_B = get_simple_str("B", val_B)
    str_C = get_simple_str("C", val_C)

    subst_expr = f"({str_A} {op_symbol} {str_B}) · {str_C}"

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_SUBSTITUTE_EXPR",
        "formula_calculation": f"<b>{subst_expr}</b>"
    })
    step_num += 1

    # --- ШАГ 4. Сложение в скобках ---
    # 5√3 + √3 = 6√3

    cA, rA = simplified_map.get("A", (1, val_A))
    cB, rB = simplified_map.get("B", (1, val_B))

    common_rem = rA

    # Определяем имя операции
    if op_symbol == "+":
        sum_c = cA + cB
        op_name = "Сложим"
    else: # "-" или "−"
        sum_c = cA - cB
        op_name = "Вычтем"

    sum_res_str = f"{sum_c}√{common_rem}"
    if sum_c == 1: sum_res_str = f"√{common_rem}"
    elif sum_c == -1: sum_res_str = f"-√{common_rem}"
    elif sum_c == 0: sum_res_str = "0"

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_COMBINE_RADICALS",
        "description_params": {"op_name": op_name}, # Передаем правильное слово
        "formula_calculation": f"<b>{str_A} {op_symbol} {str_B} = {sum_res_str}</b>"
    })
    step_num += 1

    # --- ШАГ 5. Финал ---
    # 6√3 · 2√3 = 6 · 2 · (√3)² = 12 · 3 = 36

    cC, rC = simplified_map.get("C", (1, val_C))

    # sum_c * cC * (root)^2
    # common_rem и rC должны быть равны (обычно)

    # 1. Сборка: 6√3 · 2√3
    part1 = f"{sum_res_str} · {str_C}"

    # 2. Группировка: 6 · 2 · (√3)²
    # Если коэффициенты 1, их не пишем
    parts_group = []
    val_group = 1

    if sum_c != 1:
        parts_group.append(str(sum_c))
        val_group *= sum_c
    if cC != 1:
        parts_group.append(str(cC))
        val_group *= cC

    parts_group.append(f"(√{common_rem})²")
    part2 = " · ".join(parts_group)

    # 3. Вычисление квадрата: 12 · 3
    parts_calc = []
    if val_group != 1: parts_calc.append(str(val_group))
    parts_calc.append(str(common_rem))
    part3 = " · ".join(parts_calc)

    # 4. Ответ
    final_val = val_group * common_rem
    part4 = str(final_val)

    full_chain = f"<b>{part1} = {part2} = {part3} = {part4}</b>"

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_CALC_FINAL_PRODUCT",
        "formula_calculation": full_chain
    })

    return steps

# ============================================================================
# ПАТТЕРН 2.3: radical_product
# ============================================================================

def _solve_radical_product(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Решатель для radical_product.
    Автоматически выбирает стратегию:
    - Форма B (есть внешние числа): k1√A · k2√B
    - Форма C (один большой корень): √(A·B·C)
    - Форма A (произведение корней): √(A·B)·√C
    """
    tree = task_data["expression_tree"]

    coeffs = []
    radicands = []

    # --- РЕКУРСИВНЫЙ СБОР (Паук) ---
    # Находит все числа снаружи (coeffs) и внутри корней (radicands)
    def _collect_terms(node):
        if node.get("type") == "product":
            for f in node["factors"]:
                _collect_terms(f)

        elif node.get("type") == "integer":
            coeffs.append(node["value"])

        elif node.get("type") == "sqrt":
            rad = node["radicand"]
            # Если внутри корень из произведения √(80·40)
            if rad.get("type") == "product":
                # Рекурсивно собираем всё внутри корня
                def _collect_inner(n):
                    if n["type"] == "product":
                        for f in n["factors"]: _collect_inner(f)
                    elif n["type"] == "integer":
                        radicands.append(n["value"])
                _collect_inner(rad)
            # Если внутри просто число √2
            elif rad.get("type") == "integer":
                radicands.append(rad["value"])

    # Запускаем сбор данных
    _collect_terms(tree)

    # --- ВЫБОР СТРАТЕГИИ ---

    # 1. Если есть внешние коэффициенты (9√7...) -> ФОРМА B
    if coeffs:
        steps = _build_steps_form_b(task_data, coeffs, radicands)
        idea_key = "IDEA_RADICAL_PRODUCT_MIXED"
        know_key = "KNOWLEDGE_RADICAL_PRODUCT_MIXED"
        idea_params = {}

    # 2. Если коэффициентов нет, смотрим на верхушку дерева.
    # Если это один корень √(56·40·35) -> ФОРМА C
    elif tree.get("type") == "sqrt":
        steps = _build_steps_form_c(task_data, radicands)
        idea_key = "IDEA_RADICAL_PRODUCT_SINGLE_ROOT"
        know_key = "KNOWLEDGE_RADICAL_PRODUCT_SINGLE_ROOT"
        idea_params = {"nums_str": ", ".join(map(str, radicands))}

    # 3. Иначе это произведение корней √(12·18)·√6 -> ФОРМА A
    else:
        steps = _build_steps_form_a(task_data, radicands)
        idea_key = "IDEA_RADICAL_PRODUCT"
        know_key = "KNOWLEDGE_RADICAL_PRODUCT"

        # Для идеи Формы А нужны визуальные части (inside/outside)
        in_p, out_p = "...", "..."
        factors = tree.get("factors", [])
        for f in factors:
            if f.get("type") == "sqrt":
                if f["radicand"].get("type") == "product": in_p = render_node(f)
                else: out_p = render_node(f)
        idea_params = {"part_inside": in_p, "part_outside": out_p}

    return {
        "question_id": "task8_radical_product",
        "question_group": "task_8_powers_and_roots",
        "explanation_idea_key": idea_key,
        "explanation_idea_params": idea_params,
        "knowledge_tips_key": know_key,
        "calculation_steps": steps,
        "final_answer": {
            "value_display": task_data["answer"],
        },
    }


def _build_steps_form_a(task_data: Dict[str, Any], all_numbers: List[int]) -> List[Dict[str, Any]]:
    """
    Логика для Формы А (вечеринка, LEGO-разбор).
    Принимает готовый список all_numbers (например [12, 18, 6]).
    """
    tree = task_data["expression_tree"]
    steps = []
    step_num = 1

    # Шаг 1. Исходное
    expr_str = render_node(tree)
    steps.append({
        "step_number": step_num,
        "description_key": "STEP_INITIAL_NO_VARS",
        "description_params": {"expr": expr_str}
    })
    step_num += 1

    # "Гость снаружи" для текста (просто берем последнее число, обычно оно снаружи)
    outside_guest = f"√{all_numbers[-1]}" if all_numbers else "..."

    # --- ШАГ 2. Объединение ---
    combined_inner = " · ".join(map(str, all_numbers))
    combined_root = f"√({combined_inner})"

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_COMBINE_ROOTS_PRODUCT",
        "description_params": {"guest": outside_guest},
        "formula_calculation": f"<b>{expr_str} = {combined_root}</b>"
    })
    step_num += 1

    # --- ШАГ 3. Разбор на LEGO ---
    breakdown_lines = []
    all_components = []

    for num in all_numbers:
        sq, rem, factors_p = _smart_decompose(num)
        parts = []
        if sq > 1:
            parts.append(str(sq))
            all_components.append((sq, True))
        for p in factors_p:
            parts.append(str(p))
            all_components.append((p, False))

        if not parts: parts = [str(num)] # если число 1 или не разложилось

        decomp_str = " · ".join(parts)
        comment = f"({sq} — уже готовый квадрат!)" if sq > 1 else ""
        line = f"➡️ <b>{num} = {decomp_str}</b> {comment}"
        breakdown_lines.append(line)

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_FACTORIZE_NUMBERS",
        "description_params": {"breakdown_str": "\n".join(breakdown_lines)}
    })
    step_num += 1

    # --- ШАГ 4. Группировка ---
    squares = [val for val, is_sq in all_components if is_sq]
    primes = [val for val, is_sq in all_components if not is_sq]
    primes.sort()

    pairs = []
    i = 0
    while i < len(primes) - 1:
        if primes[i] == primes[i+1]:
            pairs.append((primes[i], primes[i+1]))
            i += 2
        else: i += 1

    str_squares_list = [str(s) for s in squares]
    str_pairs_list = [f"({a} · {b})" for a, b in pairs]
    full_group_inner = " · ".join(str_squares_list + str_pairs_list)

    desc_squares = " и ".join(str_squares_list) if str_squares_list else "нет"
    desc_pairs = " и ".join([f"<b>({a}·{b})</b>" for a, b in pairs]) if str_pairs_list else "нет"

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_GROUP_PAIRS",
        "description_params": {
            "grouped_root": f"√({full_group_inner})",
            "squares_list": desc_squares,
            "pairs_list": desc_pairs
        }
    })
    step_num += 1

    # --- ШАГ 5. Вывод ---
    extraction_lines = []
    final_factors = []
    for sq in squares:
        root = int(math.isqrt(sq))
        extraction_lines.append(f"➡️ <b>√{sq} выходит как {root}</b>")
        final_factors.append(str(root))
    for p1, p2 in pairs:
        extraction_lines.append(f"➡️ <b>√({p1} · {p2}) выходит как {p1}</b>")
        final_factors.append(str(p1))

    final_prod_str = " · ".join(final_factors)

    # Подсчет
    calc_val = 1
    for f in final_factors: calc_val *= int(f)

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_EXTRACT_PAIRS",
        "description_params": {"extraction_str": "\n".join(extraction_lines)},
        "formula_calculation": f"<b>{final_prod_str}</b>"
    })
    step_num += 1

    # --- ШАГ 6. Финал ---
    steps.append({
        "step_number": step_num,
        "description_key": "STEP_CALC_FINAL",
        "formula_calculation": f"<b>{final_prod_str} = {calc_val}</b>"
    })

    return steps


def _build_steps_form_b(task_data: Dict[str, Any], coeffs: List[int], radicands: List[int]) -> List[Dict[str, Any]]:
    """Логика для Формы B (смешанная: 9√7 · 2√2 · √14)."""
    tree = task_data["expression_tree"]
    steps = []
    step_num = 1

    # Шаг 1. Исходное
    steps.append({
        "step_number": step_num,
        "description_key": "STEP_INITIAL_NO_VARS",
        "description_params": {"expr": render_node(tree)}
    })
    step_num += 1

    # Шаг 2. Разложение (9 · 2 · √7 · √2 · √14)
    # Собираем строку: числа в начале, корни в конце
    part_coeffs = " · ".join(map(str, coeffs))
    part_roots_individual = " · ".join([f"√{r}" for r in radicands])
    full_decomposed = f"{part_coeffs} · {part_roots_individual}"

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_SEPARATE_NUMS_AND_ROOTS",
        "formula_calculation": f"<b>{render_node(tree)} = {full_decomposed}</b>"
    })
    step_num += 1

    # Шаг 3. Сбор корней (√7 · √2 · √14 = √(7·2·14))
    inner_prod_str = " · ".join(map(str, radicands))
    roots_combined_str = f"√({inner_prod_str})"

    # Строка для описания: √7 · √2 · √14 = √(7 · 2 · 14)
    roots_eq = f"{part_roots_individual} = {roots_combined_str}"

    # Финальная формула шага: 9 · 2 · √(7 · 2 · 14)
    step3_final = f"<b>{part_coeffs} · {roots_combined_str}</b>"

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_COMBINE_ROOTS_MIXED",
        "description_params": {"roots_comb": roots_eq},
        "formula_calculation": step3_final
    })
    step_num += 1

    # Шаг 4. Вычисление внутри корня (7 · 2 · 14 = 196)
    prod_rad = 1
    for r in radicands: prod_rad *= r

    root_val = int(math.isqrt(prod_rad)) # 14

    calc_str = f"{inner_prod_str} = {prod_rad}"
    step4_formula = f"<b>{roots_combined_str} = √{prod_rad} = {root_val}</b>"

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_CALC_ROOT_SQUARE",
        "description_params": {
            "calc_str": calc_str,
            "sq_val": str(prod_rad),
            "root_val": str(root_val)
        },
        "formula_calculation": step4_formula
    })
    step_num += 1

    # Шаг 5. Финал (9 · 2 · 14 = 252)
    # Сначала перемножаем коэффициенты для промежуточного шага (18 · 14) как в примере
    coeff_prod = 1
    for c in coeffs: coeff_prod *= c

    # 9 · 2 · 14
    part_start = f"{part_coeffs} · {root_val}"
    # 18 · 14
    part_mid = f"{coeff_prod} · {root_val}"
    # 252
    final_val = coeff_prod * root_val

    # Собираем цепочку
    if len(coeffs) > 1:
        chain = f"<b>{part_start} = {part_mid} = {final_val}</b>"
    else:
        chain = f"<b>{part_start} = {final_val}</b>"

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_FINAL_MULTIPLICATION_MIXED",
        "formula_calculation": chain
    })

    return steps

def _build_steps_form_c(task_data: Dict[str, Any], all_numbers: List[int]) -> List[Dict[str, Any]]:
    """
    Логика для Формы C (Сундуки с сокровищами: √(56·40·35)).
    Принимает готовый список чисел под корнем.
    """
    tree = task_data["expression_tree"]
    steps = []
    step_num = 1

    # Шаг 1. Исходное
    steps.append({
        "step_number": step_num,
        "description_key": "STEP_INITIAL_NO_VARS",
        "description_params": {"expr": render_node(tree)}
    })
    step_num += 1

    # Шаг 2. Разложение (LEGO)
    decomp_lines = []
    all_components = []

    for num in all_numbers:
        sq, rem, factors_p = _smart_decompose(num)

        parts = []
        if sq > 1:
            parts.append(str(sq))
            all_components.append((sq, True)) # (val, is_square)
        for p in factors_p:
            parts.append(str(p))
            all_components.append((p, False))

        # Если число не разложилось (простое или 1)
        if not parts: parts = [str(num)]

        d_str = " · ".join(parts)
        decomp_lines.append(f"➡️ <b>{num} = {d_str}</b>")

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_DONT_MULTIPLY",
        "description_params": {"decomp_str": "\n".join(decomp_lines)}
    })
    step_num += 1

    # Шаг 3. Все под один корень (Группировка для показа)
    # Собираем строку вида √((7·8) · (5·8))
    grouped_raw = []
    for num in all_numbers:
        sq, rem, factors_p = _smart_decompose(num)
        parts = []
        if sq > 1: parts.append(str(sq))
        for p in factors_p: parts.append(str(p))
        if not parts: parts = [str(num)]

        if len(parts) > 1:
            grouped_raw.append(f"({' · '.join(parts)})")
        else:
            grouped_raw.append(parts[0])

    big_root_str = f"√({' · '.join(grouped_raw)})"

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_REWRITE_UNDER_ONE",
        "description_params": {"expr": big_root_str}
    })
    step_num += 1

    # Шаг 4. Сортировка сокровищ (Квадраты + Пары)
    squares = [val for val, is_sq in all_components if is_sq]
    primes = [val for val, is_sq in all_components if not is_sq]
    primes.sort()

    pairs = []
    i = 0
    while i < len(primes) - 1:
        if primes[i] == primes[i+1]:
            pairs.append((primes[i], primes[i+1]))
            i += 2
        else: i += 1

    # Собираем строку: √((4) · (7·7) · ...)
    parts_sorted = []
    if squares:
        # Если есть квадраты, объединяем их
        parts_sorted.append(" · ".join(map(str, squares)))

    for p1, p2 in pairs:
        parts_sorted.append(f"({p1} · {p2})")

    sorted_inner = " · ".join(parts_sorted)
    sorted_root = f"√({sorted_inner})"

    # Текст про пары
    total_groups = len(squares) + len(pairs)
    if total_groups == 1: pairs_text = "одна пара"
    elif total_groups in [2,3,4]: pairs_text = f"{total_groups} пары (включая квадраты)"
    else: pairs_text = f"{total_groups} пар"

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_SORT_TREASURES",
        "description_params": {
            "grouped_expr": sorted_root,
            "pairs_count": pairs_text
        }
    })
    step_num += 1

    # Шаг 5. Вывод на свободу
    extract_lines = []
    final_factors = []

    for sq in squares:
        root = int(math.isqrt(sq))
        extract_lines.append(f"➡️ <b>√{sq} выходит как {root}</b>")
        final_factors.append(str(root))

    for p1, p2 in pairs:
        extract_lines.append(f"➡️ <b>√({p1} · {p2}) выходит как {p1}</b>")
        final_factors.append(str(p1))

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_EXTRACT_TREASURES",
        "description_params": {"extract_str": "\n".join(extract_lines)}
    })
    step_num += 1

    # Шаг 6. Финал
    calc_str = " · ".join(final_factors)
    calc_val = 1
    for f in final_factors: calc_val *= int(f)

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_CALC_FREEDOM",
        "formula_calculation": f"<b>{calc_str} = {calc_val}</b>"
    })

    return steps


# ============================================================================
# ПАТТЕРН 2.4: radical_product_with_powers
# ============================================================================

def _solve_radical_product_with_powers(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Решатель для √(11·3⁴) · √(11·5²).
    """
    steps = _build_steps_for_radical_product_with_powers(task_data)
    return {
        "question_id": "task8_radical_product_with_powers",
        "question_group": "task_8_powers_and_roots",
        "explanation_idea_key": "IDEA_RADICAL_PRODUCT_WITH_POWERS",
        "knowledge_tips_key": "KNOWLEDGE_RADICAL_PRODUCT_WITH_POWERS",
        "calculation_steps": steps,
        "final_answer": {
            "value_display": task_data["answer"],
        },
    }


def _build_steps_for_radical_product_with_powers(task_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    tree = task_data["expression_tree"]
    steps = []
    step_num = 1

    # --- ШАГ 1. Исходное выражение ---
    steps.append({
        "step_number": step_num,
        "description_key": "STEP_INITIAL_NO_VARS",
        "description_params": {"expr": render_node(tree)}
    })
    step_num += 1

    # --- Сбор данных ---
    # Нам нужно собрать все множители под корнями
    # factors_list хранит кортежи (base, exponent) в порядке появления
    # 11^1, 3^4, 11^1, 5^2
    factors_list = []

    # Рекурсивный сборщик
    def _collect(node):
        if node["type"] == "sqrt":
            rad = node["radicand"]
            if rad["type"] == "product":
                for f in rad["factors"]: _collect(f)
            else:
                _collect(rad)
        elif node["type"] == "product":
            for f in node["factors"]: _collect(f)
        elif node["type"] == "power":
            # 3^4
            base = node["base"]["value"]
            exp = node["exp"]["value"]
            factors_list.append((base, exp))
        elif node["type"] == "integer":
            # 11 -> 11^1
            factors_list.append((node["value"], 1))

    _collect(tree)

    # --- ШАГ 2. Объединение и Группировка ---

    # 1. Сырое объединение: √(11 · 3⁴ · 11 · 5²)
    raw_parts = []
    for base, exp in factors_list:
        if exp == 1: raw_parts.append(str(base))
        else: raw_parts.append(f"{base}{to_superscript(exp)}")

    combined_raw = f"{render_node(tree)} = √({' · '.join(raw_parts)})"

    # 2. Группировка: 11² · 3⁴ · 5²
    grouped_map = {} # base -> total_exp
    for base, exp in factors_list:
        grouped_map[base] = grouped_map.get(base, 0) + exp

    grouped_parts = []
    sorted_bases = sorted(grouped_map.keys())

    # Логика сортировки: сначала общие множители (те, что сложились), потом остальные
    # В примере 11 было в обоих корнях, значит оно первое.
    # Простая эвристика: сортируем по значению базы (3, 5, 11) или оставляем как есть?
    # В эталоне: 11² · 3⁴ · 5² (11 вылезло вперед, потому что оно было первым в списке множителей)
    # Давай отсортируем так: сначала те, что "собрались" (сумма > макс.одиночного), потом остальные
    # Но проще просто отсортировать по возрастанию базы или оставить как в словаре.
    # В эталоне: 11, 3, 5.

    for base in sorted_bases:
        exp = grouped_map[base]
        grouped_parts.append(f"{base}{to_superscript(exp)}")

    grouped_str = f"√({' · '.join(grouped_parts)})"

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_COMBINE_AND_GROUP",
        "description_params": {
            "combined_raw": combined_raw,
            "grouped": grouped_str
        }
    })
    step_num += 1

    # --- ШАГ 3. Извлечение ---
    # √11² · √3⁴ · √5² = 11 · 3² · 5

    split_roots_parts = []
    extracted_parts = []

    # Данные для вычисления (base, reduced_exp)
    calc_data = []

    for base in sorted_bases:
        exp = grouped_map[base]
        # √11²
        split_roots_parts.append(f"√{base}{to_superscript(exp)}")

        # 11^1
        new_exp = exp // 2
        if new_exp == 1:
            extracted_parts.append(str(base))
        else:
            extracted_parts.append(f"{base}{to_superscript(new_exp)}")

        calc_data.append((base, new_exp))

    split_str = " · ".join(split_roots_parts)
    extracted_str = " · ".join(extracted_parts)

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_EXTRACT_ROOTS_POWERS",
        "description_params": {
            "split_roots": f"√({' · '.join(grouped_parts)}) = {split_str}",
            "extracted": extracted_str
        }
    })
    step_num += 1

    # --- ШАГ 4. Вычисление ---
    # 11 · 3² · 5 = 11 · 9 · 5 = 495

    expanded_parts = []
    final_val = 1

    for base, exp in calc_data:
        val = base ** exp
        expanded_parts.append(str(val))
        final_val *= val

    expanded_str = " · ".join(expanded_parts)
    final_res = str(final_val)

    # Если были степени > 1 (т.е. expanded отличается от extracted)
    if expanded_str != extracted_str.replace("·", "").replace(" ", ""): # Грубая проверка, лучше по флагам
         # В extracted_str могут быть superscript, а в expanded обычные числа
         # Просто сравниваем: если хоть одна степень > 1, показываем расшифровку
         has_powers = any(e > 1 for _, e in calc_data)
         if has_powers:
             chain = f"{extracted_str} = {expanded_str} = {final_res}"
         else:
             chain = f"{extracted_str} = {final_res}"
    else:
         chain = f"{extracted_str} = {final_res}"

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_CALC_FINAL_POWERS",
        "description_params": {"calc_chain": chain}
    })

    return steps

def _solve_radical_fraction(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Решатель для (√A · √B) / √C.
    """
    steps = _build_steps_for_radical_fraction(task_data)
    return {
        "question_id": "task8_radical_fraction",
        "question_group": "task_8_powers_and_roots",
        "explanation_idea_key": "IDEA_RADICAL_FRACTION_NUMERIC",
        "knowledge_tips_key": "KNOWLEDGE_RADICAL_FRACTION_NUMERIC",
        "calculation_steps": steps,
        "final_answer": {
            "value_display": task_data["answer"],
        },
    }


def _build_steps_for_radical_fraction(task_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    tree = task_data["expression_tree"]
    steps = []
    step_num = 1

    # --- ШАГ 1. Исходное выражение ---
    expr_str = render_node(tree)
    steps.append({
        "step_number": step_num,
        "description_key": "STEP_INITIAL_NO_VARS",
        "description_params": {"expr": expr_str}
    })
    step_num += 1

    # --- Сбор данных ---
    # Числитель: произведение корней (или один корень)
    # Знаменатель: корень

    numerator = tree["numerator"]
    denominator = tree["denominator"]

    nums_top = []

    # Парсим числитель
    factors = numerator.get("factors", [numerator]) if numerator.get("type") == "product" else [numerator]
    for f in factors:
        if f.get("type") == "sqrt":
            nums_top.append(f["radicand"]["value"])

    # Парсим знаменатель
    num_bot = denominator["radicand"]["value"]

    # --- ШАГ 2. Объединение ---
    # ➡️ (√65 · √13) / √5 = √(65 · 13) / √5 = √((65 · 13) / 5)

    top_inner = " · ".join(map(str, nums_top))

    # √(65 · 13) / √5
    step_one = f"√({top_inner}) / √{num_bot}"

    # √((65 · 13) / 5)
    step_two = f"√(({top_inner}) / {num_bot})"

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_COMBINE_FRACTION_ROOTS",
        "description_params": {
            "expr": expr_str,
            "step_one": step_one,
            "step_two": step_two
        }
    })
    step_num += 1

    # --- ШАГ 3. Упрощение и вычисление ---
    # Найти, какое число в числителе делится на знаменатель
    # 65 / 5 = 13

    reduced_top = []
    found_divisor = False
    reduced_pair = (0, 0) # (кто, на кого) для описания

    for n in nums_top:
        if not found_divisor and n % num_bot == 0:
            res = n // num_bot
            reduced_top.append(res)
            found_divisor = True
            reduced_pair = (n, num_bot)
        else:
            reduced_top.append(n)

    # Если вдруг не нашлось (в ОГЭ всегда находится), просто делим произведение
    if not found_divisor:
        # Fallback logic (на всякий случай)
        prod_top = 1
        for n in nums_top: prod_top *= n
        reduced_top = [prod_top // num_bot]
        reduced_pair = (prod_top, num_bot)

    # Строим цепочку: √((65 · 13) / 5) = √(13 · 13) = √(13)² = 13
    step_start = step_two

    # √(13 · 13)
    step_mid = f"√({' · '.join(map(str, reduced_top))})"

    # √(13)²  (если числа одинаковые)
    # Или просто √169 (если разные)
    final_val = 1
    for n in reduced_top: final_val *= n
    root_val = int(math.isqrt(final_val))

    # Проверяем, одинаковые ли множители (для красивого квадрата)
    is_identical = (len(reduced_top) == 2 and reduced_top[0] == reduced_top[1])

    if is_identical:
        step_end = f"√({reduced_top[0]})²"
    else:
        step_end = f"√{final_val}"

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_SIMPLIFY_AND_CALC_FRACTION",
        "description_params": {
            "val_num": str(reduced_pair[0]),
            "val_den": str(reduced_pair[1]),
            "gcd": str(reduced_pair[1]), # Сокращаем на знаменатель
            "step_start": step_start,
            "step_mid": step_mid,
            "step_end": step_end,
            "result": str(root_val)
        }
    })

    return steps

# ============================================================================
# ПАТТЕРН 2.6: conjugate_radicals (Разность квадратов)
# ============================================================================

def _solve_conjugate_radicals(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Решатель для (√A - B)(√A + B).
    """
    steps = _build_steps_for_conjugate_radicals(task_data)
    return {
        "question_id": "task8_conjugate_radicals",
        "question_group": "task_8_powers_and_roots",
        "explanation_idea_key": "IDEA_CONJUGATE_RADICALS",
        "knowledge_tips_key": "KNOWLEDGE_CONJUGATE_RADICALS",
        "calculation_steps": steps,
        "final_answer": {
            "value_display": task_data["answer"],
        },
    }


def _build_steps_for_conjugate_radicals(task_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    tree = task_data["expression_tree"]
    steps = []
    step_num = 1

    # --- ШАГ 1. Исходное выражение ---
    expr_str = render_node(tree)
    steps.append({
        "step_number": step_num,
        "description_key": "STEP_INITIAL_NO_VARS",
        "description_params": {"expr": expr_str}
    })
    step_num += 1

    # --- Анализ (Поиск a и b) ---
    # Ищем множитель с минусом: (X - Y)
    factors = tree.get("factors", [])
    minus_node = None

    for f in factors:
        if f.get("type") == "binary_op" and f["op"] in ("-", "−"):
            minus_node = f
            break

    if not minus_node:
        # Если вдруг порядок (A+B)(A-B), ищем плюс, но это сложнее для определения знака b
        # Предполагаем, что валидатор всегда дает правильную структуру.
        # Fallback: берем первый бинарный
        minus_node = factors[0]

    node_a = minus_node["left"]
    node_b = minus_node["right"]

    str_a = render_node(node_a)
    str_b = render_node(node_b)

    # Формируем визуальное представление квадратов
    # Если это корень √29 -> (√29)²
    # Если число 4 -> 4²
    def _format_sq(node, s):
        if node.get("type") == "sqrt":
            return f"({s})²"
        return f"{s}²"

    sq_view_a = _format_sq(node_a, str_a)
    sq_view_b = _format_sq(node_b, str_b)

    # Формула: (√29 - 4)(√29 + 4) = (√29)² - 4²
    formula_apply = f"<b>{expr_str} = {sq_view_a} - {sq_view_b}</b>"

    # --- ШАГ 2. Узнаем формулу ---
    # Удаляем знак корня из текста для красоты описания, если он есть
    # Хотя в эталоне: "два одинаковых корня √29"

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_IDENTIFY_FORMULA",
        "description_params": {
            "term_a": str_a,
            "term_b": str_b
        },
        "formula_calculation": formula_apply
    })
    step_num += 1

    # --- ШАГ 3. Вычисляем ---
    # (√29)² - 4² = 29 - 16 = 13

    def _get_val_and_sq_val(node):
        # Возвращает (значение, значение_в_квадрате)
        if node.get("type") == "sqrt":
            # (√29)² = 29
            # Берем значение под корнем
            val_under = _eval_simple_node(node["radicand"])
            return val_under
        elif node.get("type") == "integer":
            # 4² = 16
            val = node["value"]
            return val ** 2
        return 0

    val_sq_a = _get_val_and_sq_val(node_a)
    val_sq_b = _get_val_and_sq_val(node_b)

    result = val_sq_a - val_sq_b

    # Формируем строку вычисления
    # (√29)² - 4² = 29 - 16 = 13
    final_calc = f"<b>{sq_view_a} - {sq_view_b} = {val_sq_a} - {val_sq_b} = {result}</b>"

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_CALC_DIFFERENCE_SQUARES",
        "formula_calculation": final_calc
    })

    return steps

# ============================================================================
# ПАТТЕРН 2.7: numeric_power_fraction (5 ФОРМ)
# ============================================================================

def _solve_numeric_power_fraction(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Умный решатель для степеней. Анализирует структуру и выбирает одну из 5 стратегий.
    """
    tree = task_data["expression_tree"]

    # --- АНАЛИЗАТОР СТРАТЕГИИ ---

    # 1. Форма A (Boss Battle): 10^9 / ((2^5)^2 * 5^7)
    # Признак: В числителе степень составного числа (10), в знаменателе - произведение его множителей.
    if _is_form_a_boss(tree):
        return _solve_form_a_boss(task_data)

    # 2. Форма C (Tower): (5^2)^-8 / 5^-18
    # Признак: В числителе "башня" (степень в степени).
    if _is_form_c_tower(tree):
        return _solve_form_c_tower(task_data)

    # 3. Форма E (Clone Wars): 14^4 / (2^5 * 7^3)
    # Признак: Числитель составной (14), знаменатель - произведение простых. Похоже на А, но без башни внизу.
    if _is_form_e_clone(tree):
        return _solve_form_e_clone(task_data)

    # 4. Форма B (Same Base): 4^-2 * 4^-7 / 4^-11
    # Признак: Везде одинаковое основание.
    if _is_form_b_same_base(tree):
        return _solve_form_b_same_base(task_data)

    # 5. Форма D (Spies): 27^7 / 9^10
    # Признак: Основания разные, но являются степенями одного числа (3).
    return _solve_form_d_spies(task_data)


# --- ДЕТЕКТОРЫ ФОРМ ---

def _is_form_c_tower(tree):
    # Числитель имеет вид (a^n)^m
    num = tree["numerator"]
    return num.get("type") == "power" and num["base"].get("type") == "power"

def _is_form_b_same_base(tree):
    # Собираем все основания. Если они одинаковые -> True
    bases = set()
    def _collect(n):
        if n.get("type") == "fraction":
            _collect(n["numerator"])
            _collect(n["denominator"])
        elif n.get("type") == "power":
            _collect(n["base"])
        elif n.get("type") == "product":
            for f in n["factors"]: _collect(f)
        elif n.get("type") == "integer":
            bases.add(n["value"])

    _collect(tree)
    return len(bases) == 1

def _is_form_a_boss(tree):
    # Знаменатель сложный (произведение, и там есть башня)
    den = tree["denominator"]
    if den.get("type") == "product":
        for f in den["factors"]:
            if f.get("type") == "power" and f["base"].get("type") == "power":
                return True
    return False

def _is_form_e_clone(tree):
    # Числитель - степень составного числа, Знаменатель - произведение
    # Отличие от А: в знаменателе нет башен
    num = tree["numerator"]
    den = tree["denominator"]
    if num.get("type") == "power" and den.get("type") == "product":
        base_val = num["base"]["value"]
        # Проверяем составное ли (просто по размеру > 5 для эвристики или делением)
        # Упрощенно: если не А и не С, и внизу произведение -> скорее всего Е
        return True
    return False


# --- РЕШАТЕЛИ ПО ФОРМАМ ---
# ⭐ Форма A: Boss Battle (10^9 / ( (2^5)^2 * 5^7 ))
def _solve_form_a_boss(task_data) -> Dict[str, Any]:
    steps = []
    step_num = 1
    tree = task_data["expression_tree"]

    steps.append({
        "step_number": step_num, "description_key": "STEP_INITIAL_NO_VARS",
        "description_params": {"expr": render_node(tree)}
    })
    step_num += 1

    # Парсим босса (10^9) и подвал
    boss_node = tree["numerator"]
    # БЕЗОПАСНОЕ ПОЛУЧЕНИЕ ЗНАЧЕНИЙ
    boss_base = _safe_get_val(boss_node["base"])
    boss_exp = _safe_get_val(boss_node["exp"])

    den_factors = tree["denominator"]["factors"]
    tower_node = None
    simple_node = None
    for f in den_factors:
        if f["type"] == "power" and f["base"]["type"] == "power": tower_node = f
        else: simple_node = f

    # 2. Разбор босса
    f1, f2 = _get_factors(boss_base)
    boss_decomp = f"{boss_base}{to_superscript(boss_exp)} = ({f1} · {f2}){to_superscript(boss_exp)} = {f1}{to_superscript(boss_exp)} · {f2}{to_superscript(boss_exp)}"

    steps.append({
        "step_number": step_num, "description_key": "STEP_BOSS_DECOMPOSE",
        "description_params": {"boss": render_node(boss_node), "boss_base": str(boss_base), "f1": str(f1), "f2": str(f2)},
        "formula_calculation": f"<b>{boss_decomp}</b>"
    })
    step_num += 1

    # 3. Подвал (башня)
    # БЕЗОПАСНОЕ ПОЛУЧЕНИЕ ЗНАЧЕНИЙ
    t_base = _safe_get_val(tower_node["base"]["base"])
    t_inn = _safe_get_val(tower_node["base"]["exp"])
    t_out = _safe_get_val(tower_node["exp"])
    t_res = t_inn * t_out

    tower_calc = f"({t_base}{to_superscript(t_inn)}){to_superscript(t_out)} = {t_base}{to_superscript(f'{t_inn}·{t_out}')} = {t_base}{to_superscript(t_res)}"

    # Рендерим простой узел заново, чтобы получить красивую строку
    den_res = f"{t_base}{to_superscript(t_res)} · {render_node(simple_node)}"

    steps.append({
        "step_number": step_num, "description_key": "STEP_BOSS_SIMPLIFY_DENOM",
        "description_params": {"bracket": render_node(tower_node)},
        "formula_calculation": f"<b>{tower_calc}</b>\nВесь знаменатель теперь выглядит так: <b>{den_res}</b>"
    })
    step_num += 1

    # 4. Сборка
    new_frac = f"({f1}{to_superscript(boss_exp)} · {f2}{to_superscript(boss_exp)}) / ({den_res})"
    steps.append({
        "step_number": step_num, "description_key": "STEP_BOSS_REWRITE_FRACTION",
        "formula_calculation": f"<b>{new_frac}</b>"
    })
    step_num += 1

    # 5. Битва
    # Считаем степени
    p1_top = boss_exp
    p2_top = boss_exp

    # Получаем степень простого узла безопасно
    simple_exp_val = _safe_get_val(simple_node["exp"])

    if f1 == t_base:
        p1_bot = t_res
        p2_bot = simple_exp_val
    else:
        p1_bot = simple_exp_val
        p2_bot = t_res

    res1 = p1_top - p1_bot
    res2 = p2_top - p2_bot

    lines = []
    lines.append(f"Для {f1}: <b>{f1}{to_superscript(p1_top)} / {f1}{to_superscript(p1_bot)} = {f1}{to_superscript(res1)}</b>")
    lines.append(f"Для {f2}: <b>{f2}{to_superscript(p2_top)} / {f2}{to_superscript(p2_bot)} = {f2}{to_superscript(res2)}</b>")

    steps.append({
        "step_number": step_num, "description_key": "STEP_BOSS_FIGHT",
        "formula_calculation": "\n".join([f"➡️ {l}" for l in lines])
    })
    step_num += 1

    # 6. Финал
    val1 = f1 ** res1
    val2 = f2 ** res2
    final_val = val1 * val2
    final_fmt = fmt_number(final_val)

    # Красивый вывод промежуточных вычислений (2^-1 -> 0,5)
    v1_s = fmt_number(int(val1) if val1 == int(val1) else val1)
    v2_s = fmt_number(int(val2) if val2 == int(val2) else val2)

    calc_str = f"{f1}{to_superscript(res1)} · {f2}{to_superscript(res2)} = {v1_s} · {v2_s} = {final_fmt}"

    steps.append({
        "step_number": step_num, "description_key": "STEP_BOSS_FINAL_CALC",
        "formula_calculation": f"<b>{calc_str}</b>"
    })

    return _pack_result(
        task_data,
        steps,
        "IDEA_NUM_POW_BOSS_BATTLE",
        {"base_boss": boss_base, "exp_boss": to_superscript(boss_exp), "base1": f1, "base2": f2},
        know_key="KNOWLEDGE_NUM_POW_BOSS" # <--- Добавили ключ
    )

# ⭐ Форма B: Same Base (4^-2 * 4^-7 / 4^-11)
def _solve_form_b_same_base(task_data) -> Dict[str, Any]:
    steps = []
    step_num = 1
    tree = task_data["expression_tree"]

    steps.append({
        "step_number": step_num, "description_key": "STEP_INITIAL_NO_VARS",
        "description_params": {"expr": render_node(tree)}
    })
    step_num += 1

    num = tree["numerator"]
    # БЕЗОПАСНОЕ ПОЛУЧЕНИЕ ЗНАЧЕНИЙ
    base = _safe_get_val(num["factors"][0]["base"])
    p1 = _safe_get_val(num["factors"][0]["exp"])
    p2 = _safe_get_val(num["factors"][1]["exp"])
    p_num = p1 + p2

    # 2. Числитель
    # Если степень отрицательная, добавляем скобки для красоты: -2+(-7)
    p2_str = f"({p2})" if p2 < 0 else f"{p2}"
    calc_num = f"{base}{to_superscript(p1)} · {base}{to_superscript(p2)} = {base}{to_superscript(f'{p1}+{p2_str}')} = {base}{to_superscript(p_num)}"

    steps.append({
        "step_number": step_num, "description_key": "STEP_SAME_BASE_NUMERATOR",
        "formula_calculation": f"<b>{calc_num}</b>\nОтлично, наверху теперь живёт только <b>{base}{to_superscript(p_num)}</b>."
    })
    step_num += 1

    # 3. Дробь
    den = tree["denominator"]
    p_den = _safe_get_val(den["exp"]) # БЕЗОПАСНО

    steps.append({
        "step_number": step_num, "description_key": "STEP_SAME_BASE_REWRITE",
        "formula_calculation": f"<b>{base}{to_superscript(p_num)} / {base}{to_superscript(p_den)}</b>"
    })
    step_num += 1

    # 4. Деление
    p_res = p_num - p_den
    p_den_str = f"({p_den})" if p_den < 0 else f"{p_den}"

    calc_div = f"{base}{to_superscript(p_num)} / {base}{to_superscript(p_den)} = {base}{to_superscript(f'{p_num}-{p_den_str}')} = {base}{to_superscript(p_res)}"

    steps.append({
        "step_number": step_num, "description_key": "STEP_SAME_BASE_DIVIDE",
        "formula_calculation": f"<b>{calc_div}</b>"
    })
    step_num += 1

    # 5. Ответ
    res_val = base ** p_res
    res_fmt = fmt_number(int(res_val) if res_val == int(res_val) else res_val)

    steps.append({
        "step_number": step_num, "description_key": "STEP_SAME_BASE_CALC",
        "formula_calculation": f"<b>{base}{to_superscript(p_res)} = {res_fmt}</b>"
    })

    return _pack_result(
        task_data,
        steps,
        "IDEA_NUM_POW_SAME_BASE",
        know_key="KNOWLEDGE_NUM_POW_SAME_BASE" # <--- Добавили ключ
    )


# ⭐ Форма C: Tower ((5^2)^-8 / 5^-18)
def _solve_form_c_tower(task_data) -> Dict[str, Any]:
    steps = []
    step_num = 1
    tree = task_data["expression_tree"]

    steps.append({
        "step_number": step_num, "description_key": "STEP_INITIAL_NO_VARS",
        "description_params": {"expr": render_node(tree)}
    })
    step_num += 1

    tower = tree["numerator"]
    # Используем _safe_get_val вместо ["value"]
    base = _safe_get_val(tower["base"]["base"])
    p_in = _safe_get_val(tower["base"]["exp"])
    p_out = _safe_get_val(tower["exp"])
    p_num = p_in * p_out

    # 2. Башня
    calc_tower = f"{base}{to_superscript(p_in)} · ⁽{to_superscript(p_out)}⁾ = {base}{to_superscript(p_num)}"
    steps.append({
        "step_number": step_num, "description_key": "STEP_TOWER_RESOLVE",
        "description_params": {"tower": render_node(tower)},
        "formula_calculation": f"<b>{calc_tower}</b>\nВсё, наверху теперь порядок: <b>{base}{to_superscript(p_num)}</b>."
    })
    step_num += 1

    # 3. Дробь
    den = tree["denominator"]
    p_den = _safe_get_val(den["exp"]) # И тут тоже!

    steps.append({
        "step_number": step_num, "description_key": "STEP_TOWER_REWRITE",
        "formula_calculation": f"<b>{base}{to_superscript(p_num)} / {base}{to_superscript(p_den)}</b>"
    })
    step_num += 1

    # 4. Деление
    p_res = p_num - p_den
    calc_div = f"{base}{to_superscript(f'{p_num}-({p_den})')} = {base}{to_superscript(p_res)}"
    steps.append({
        "step_number": step_num, "description_key": "STEP_TOWER_DIVIDE",
        "formula_calculation": f"<b>{calc_div}</b>"
    })
    step_num += 1

    # 5. Ответ
    res_val = base ** p_res
    steps.append({
        "step_number": step_num, "description_key": "STEP_TOWER_CALC",
        "formula_calculation": f"<b>{base}{to_superscript(p_res)} = {res_val}</b>"
    })

    return _pack_result(
        task_data,
        steps,
        "IDEA_NUM_POW_TOWER",
        know_key="KNOWLEDGE_NUM_POW_TOWER" # <--- Добавили ключ
    )


# ⭐ Форма D: Spies (27^7 / 9^10) или (8^4 / 4)
def _solve_form_d_spies(task_data) -> Dict[str, Any]:
    steps = []
    step_num = 1
    tree = task_data["expression_tree"]

    # Хелпер для безопасного получения (число или база степени)
    def _get_be(node):
        if node.get("type") == "power":
            return _safe_get_val(node["base"]), _safe_get_val(node["exp"])
        elif node.get("type") == "integer":
            return _safe_get_val(node), 1
        return 1, 1

    num_node = tree["numerator"]
    den_node = tree["denominator"]

    base_n, exp_n = _get_be(num_node)
    base_d, exp_d = _get_be(den_node)

    # Шаг 1. Исходное
    steps.append({
        "step_number": step_num,
        "description_key": "STEP_INITIAL_NO_VARS",
        "description_params": {"expr": render_node(tree)}
    })
    step_num += 1

    # 2. Разоблачение
    common = 3
    if base_n % 2 == 0: common = 2
    elif base_n % 3 == 0: common = 3
    elif base_n % 5 == 0: common = 5

    # Исправленная функция поиска степени (теперь 1 -> 3^0)
    def get_pow(val, base):
        if val == 1: return 0
        p = 0
        temp = val
        while temp > 1 and temp % base == 0:
            temp //= base
            p += 1
        return p

    pb_n = get_pow(base_n, common)
    pb_d = get_pow(base_d, common)

    # Формируем разоблачение: 27 = 3³
    rev_n = f"<b>{base_n} = {common}{to_superscript(pb_n)}</b>"
    rev_d = f"<b>{base_d} = {common}{to_superscript(pb_d)}</b>"

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_SPIES_REVEAL",
        "formula_calculation": f"{rev_n} и {rev_d}."
    })
    step_num += 1

    # 3. Переписываем (Было / Стало)
    old_expr = render_node(tree)

    def _fmt_new(pb, exp):
        inner = f"{common}{to_superscript(pb)}"
        if exp == 1: return inner
        return f"({inner}){to_superscript(exp)}"

    new_n_str = _fmt_new(pb_n, exp_n)
    new_d_str = _fmt_new(pb_d, exp_d)
    new_expr = f"{new_n_str} / {new_d_str}"

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_SPIES_REWRITE",
        "description_params": {
            "base": str(common),
            "old": old_expr,
            "new": new_expr
        }
    })
    step_num += 1

    # 4. Упрощаем башни
    final_n = pb_n * exp_n
    final_d = pb_d * exp_d

    lines_tower = []

    # Числитель
    if exp_n != 1:
        lines_tower.append(f"В числителе: <b>{new_n_str} = {common}{to_superscript(f'{pb_n}·{exp_n}')} = {common}{to_superscript(final_n)}</b>")
    else:
        lines_tower.append(f"В числителе: <b>{new_n_str} = {common}{to_superscript(final_n)}</b>")

    # Знаменатель
    if exp_d != 1:
        lines_tower.append(f"В знаменателе: <b>{new_d_str} = {common}{to_superscript(f'{pb_d}·{exp_d}')} = {common}{to_superscript(final_d)}</b>")
    else:
        lines_tower.append(f"В знаменателе: <b>{new_d_str} = {common}{to_superscript(final_d)}</b>")

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_SPIES_SIMPLIFY_TOWERS",
        "formula_calculation": "\n".join(lines_tower)
    })
    step_num += 1

    # 5. Деление и ответ
    res_p = final_n - final_d
    res_val = common ** res_p

    # ЛЕЧЕНИЕ ПЛАВАЮЩЕЙ ТОЧКИ
    res_val = round(res_val, 9)

    val_s = fmt_number(int(res_val) if float(res_val).is_integer() else res_val)

    # Красивая разность степеней: 21-20
    sub_str = f"{final_n}-{final_d}"
    if final_d < 0: sub_str = f"{final_n}-({final_d})"

    calc_fin = f"{common}{to_superscript(final_n)} / {common}{to_superscript(final_d)} = {common}{to_superscript(sub_str)} = {common}{to_superscript(res_p)} = {val_s}"

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_SPIES_DIVIDE",
        "formula_calculation": f"<b>{calc_fin}</b>"
    })

    return _pack_result(
        task_data,
        steps,
        "IDEA_NUM_POW_SPIES",
        {"num1": base_n, "num2": base_d, "common_base": common},
        know_key="KNOWLEDGE_NUM_POW_SPIES" # <--- Добавили ключ
    )

# ⭐ Форма E: Clone Wars (14^4 / (2^5 * 7^3))
def _solve_form_e_clone(task_data) -> Dict[str, Any]:
    steps = []
    step_num = 1
    tree = task_data["expression_tree"]

    steps.append({
        "step_number": step_num, "description_key": "STEP_INITIAL_NO_VARS",
        "description_params": {"expr": render_node(tree)}
    })
    step_num += 1

    # БЕЗОПАСНОЕ ПОЛУЧЕНИЕ ЗНАЧЕНИЙ
    num_base = _safe_get_val(tree["numerator"]["base"])
    num_exp = _safe_get_val(tree["numerator"]["exp"])

    den_factors = tree["denominator"]["factors"]
    f1_node = den_factors[0]
    f2_node = den_factors[1]

    f1 = _safe_get_val(f1_node["base"])
    f2 = _safe_get_val(f2_node["base"])
    p1_bot = _safe_get_val(f1_node["exp"])
    p2_bot = _safe_get_val(f2_node["exp"])

    # 2. Разбор
    steps.append({
        "step_number": step_num, "description_key": "STEP_CLONE_DECOMPOSE",
        "formula_calculation": f"<b>{num_base} = {f1} · {f2}</b>\nЗначит:\n<b>{num_base}{to_superscript(num_exp)} = ({f1} · {f2}){to_superscript(num_exp)} = {f1}{to_superscript(num_exp)} · {f2}{to_superscript(num_exp)}</b>"
    })
    step_num += 1

    # 3. Переписываем
    new_frac = f"({f1}{to_superscript(num_exp)} · {f2}{to_superscript(num_exp)}) / ({f1}{to_superscript(p1_bot)} · {f2}{to_superscript(p2_bot)})"
    steps.append({
        "step_number": step_num, "description_key": "STEP_CLONE_REWRITE",
        "formula_calculation": f"<b>{new_frac}</b>"
    })
    step_num += 1

    # 4. Разделяем битву
    split_view = f"({f1}{to_superscript(num_exp)} / {f1}{to_superscript(p1_bot)}) · ({f2}{to_superscript(num_exp)} / {f2}{to_superscript(p2_bot)})"
    steps.append({
        "step_number": step_num, "description_key": "STEP_CLONE_SPLIT_FRONT",
        "description_params": {"base1": str(f1), "base2": str(f2)},
        "formula_calculation": f"<b>{split_view}</b>"
    })
    step_num += 1

    # 5. Бьемся
    res_p1 = num_exp - p1_bot
    res_p2 = num_exp - p2_bot

    line1 = f"{f1}: <b>{f1}{to_superscript(num_exp)} / {f1}{to_superscript(p1_bot)} = {f1}{to_superscript(res_p1)}</b>"
    line2 = f"{f2}: <b>{f2}{to_superscript(num_exp)} / {f2}{to_superscript(p2_bot)} = {f2}{to_superscript(res_p2)}</b>"

    steps.append({
        "step_number": step_num, "description_key": "STEP_CLONE_FIGHT",
        "formula_calculation": f"{line1}\n{line2}"
    })
    step_num += 1

    # 6. Финал
    val1 = f1 ** res_p1
    val2 = f2 ** res_p2

    final_val = val1 * val2

    # --- ЛЕЧЕНИЕ ПЛАВАЮЩЕЙ ТОЧКИ ---
    # Округляем до 9 знака, чтобы 0.6000...01 стало 0.6
    final_val = round(final_val, 9)
    # -------------------------------

    final_fmt = fmt_number(int(final_val) if float(final_val).is_integer() else final_val)

    # Красивый вывод промежуточных значений
    # Их тоже полезно округлить
    val1 = round(val1, 9)
    val2 = round(val2, 9)

    v1_s = fmt_number(int(val1) if float(val1).is_integer() else val1)
    v2_s = fmt_number(int(val2) if float(val2).is_integer() else val2)

    # Если степень отрицательная, показываем дробью для наглядности (1/5)
    if res_p1 < 0: v1_s = f"(1/{int(f1**abs(res_p1))})"
    if res_p2 < 0: v2_s = f"(1/{int(f2**abs(res_p2))})"

    steps.append({
        "step_number": step_num, "description_key": "STEP_CLONE_COLLECT",
        "formula_calculation": f"<b>{f1}{to_superscript(res_p1)} · {f2}{to_superscript(res_p2)} = {v1_s} · {v2_s} = {final_fmt}</b>"
    })

    return _pack_result(
        task_data,
        steps,
        "IDEA_NUM_POW_CLONE_WARS",
        {"composite_base": num_base, "factor1": f1, "factor2": f2},
        know_key="KNOWLEDGE_NUM_POW_CLONES" # <--- Добавили ключ
    )

def _solve_count_integers_between_radicals(task_data: Dict[str, Any]) -> Dict[str, Any]:
    # Паттерн 2.8: Между 3√15 и 5√6
    return _solve_placeholder(task_data, "count_integers_between_radicals")

# ============================================================================
# HELPERS
# ============================================================================

def _can_simplify(n: int) -> bool:
    """Проверяет, можно ли упростить корень из n (есть ли квадратный множитель > 1)."""
    if n < 4: return False
    s, r, root = _simplify_integer_radical(n)
    return s > 1

def _simplify_integer_radical(n: int) -> Tuple[int, int, int]:
    """
    Упрощает √n -> root_sq * √rem.
    Возвращает (square_part, remainder, root_of_square).
    Пример: 75 -> (25, 3, 5)  (потому что 75 = 25*3 = 5^2 * 3)
    """
    max_root = int(math.isqrt(n))
    # Идем от самого большого возможного корня вниз
    for r in range(max_root, 1, -1):
        sq = r * r
        if n % sq == 0:
            return sq, n // sq, r

    # Если не упрощается
    return 1, n, 1

def _smart_decompose(n: int) -> Tuple[int, int, List[int]]:
    """
    Раскладывает число на [Квадрат, Остаток, Список_Простых_Множителей_Остатка].
    Пример: 12 -> (4, 3, [3])
    Пример: 6 -> (1, 6, [2, 3])
    """
    # 1. Ищем максимальный квадрат
    max_root = int(math.isqrt(n))
    sq_part = 1
    remainder = n

    for r in range(max_root, 1, -1):
        sq = r * r
        if n % sq == 0:
            sq_part = sq
            remainder = n // sq
            break

    # 2. Раскладываем остаток на простые множители
    primes = []
    d = 2
    temp = remainder
    while d * d <= temp:
        while temp % d == 0:
            primes.append(d)
            temp //= d
        d += 1
    if temp > 1:
        primes.append(temp)

    return sq_part, remainder, primes

def _eval_simple_node(node: Dict[str, Any]) -> int:
    """
    Быстро получает числовое значение узла для паттерна разности квадратов.
    (√29 -> 29, 4 -> 4).
    """
    if node.get("type") == "integer":
        return node["value"]
    if node.get("type") == "product":
        # Если вдруг 2√3 -> (2√3)^2 = 12. Редко, но метко.
        # Но в этом паттерне обычно простые числа.
        # Оставим простую реализацию, чтобы не усложнять.
        pass
    return 0

# --- ХЕЛПЕР УПАКОВКИ ---
def _pack_result(task_data, steps, idea_key, idea_params=None, know_key="KNOWLEDGE_GENERIC"):
    return {
        "question_id": "task8_numeric_power_fraction",
        "question_group": "task_8_powers_and_roots",
        "explanation_idea_key": idea_key,
        "explanation_idea_params": idea_params,
        "knowledge_tips_key": know_key, # <--- Теперь берем из аргумента
        "calculation_steps": steps,
        "final_answer": {"value_display": task_data["answer"]},
    }

# --- ХЕЛПЕР РАЗЛОЖЕНИЯ ---
def _get_factors(n):
    # Для 10 -> 2, 5. Для 14 -> 2, 7.
    # Простое разложение на 2 множителя
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return i, n // i
    return 1, n

def _safe_get_val(node: Dict[str, Any]) -> int:
    """
    Безопасно извлекает значение числа.
    Понимает:
    - integer: 5 -> 5
    - product: (-1 * 5) -> -5
    """
    if node.get("type") == "integer":
        return node["value"]

    if node.get("type") == "product":
        # Перемножаем множители (обычно это -1 и число)
        res = 1
        for f in node.get("factors", []):
            if f.get("type") == "integer":
                res *= f["value"]
        return res

    return 1 # Fallback
