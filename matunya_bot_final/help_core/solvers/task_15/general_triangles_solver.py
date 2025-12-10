# matunya_bot_final/help_core/solvers/task_15/general_triangles_solver.py
"""
Решатель (Solver) для всех подтипов темы "Произвольные треугольники" Задания 15.
"""
import math
from typing import Dict, Any, List
from matunya_bot_final.help_core.solvers.task_15.task_15_text_formatter import format_number

# НОВАЯ, БОЛЕЕ МОЩНАЯ ФУНКЦИЯ ПАРСИНГА
def _parse_value_components(val: str | int | float) -> Dict[str, float]:
    """Разбирает строку ('5√2', '√2/2', '10') на компоненты."""
    s_val = str(val).replace(",", ".")

    coef, radicand, denominator = 1.0, 1.0, 1.0

    if "/" in s_val:
        num_part, den_part = s_val.split('/', 1)
        denominator = float(den_part)
        s_val = num_part

    if "√" in s_val:
        coef_part, root_part = s_val.split("√", 1)
        radicand = float(root_part)
        if coef_part:
            coef = float(coef_part)
    else:
        coef = float(s_val)

    return {"coef": coef, "radicand": radicand, "denominator": denominator}

def _parse_value(val: str | int | float) -> float:
    """Старая функция для простого вычисления итогового значения."""
    parts = _parse_value_components(val)
    return (parts["coef"] * math.sqrt(parts["radicand"])) / parts["denominator"]

# ============================================================
# ПАТТЕРН 2.1: triangle_area_by_sin
# ============================================================
def _solve_area_by_sin(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Решает задачу на площадь, генерируя "умные" шаги вычислений."""
    given = task["variables"]["given"]
    h_data = task["variables"]["humanizer_data"]

    sides = given["sides"]
    side_names = list(sides.keys())
    s1_name, s2_name = side_names[0], side_names[1]

    s1_val_str = h_data.get("element_names", {}).get(s1_name, str(sides[s1_name]))
    s2_val_str = h_data.get("element_names", {}).get(s2_name, str(sides[s2_name]))

    angle_letter = list(h_data["angle_names"].keys())[0]
    angle_name_human = h_data["angle_names"][angle_letter]
    angle_name_formula = angle_name_human.replace("∠", "")

    context = { "res": task["answer"] }

    # --- Выбор сценария и подготовка данных ---
    if given.get("trig"):
        narrative = "from_sin_value"
        sin_val_str = given["trig"][f"sin_{angle_letter}"]
    else:
        narrative = "from_degrees"
        angle_val = given["angles"][angle_letter]
        sin_map = {30: "1/2", 45: "√2/2", 60: "√3/2", 90: "1", 120: "√3/2", 135: "√2/2", 150: "1/2"}
        sin_val_str = sin_map.get(angle_val)
        context.update({"angle_val": angle_val, "sin_val_str": sin_val_str})

    # --- Общая логика для обоих сценариев ---
    context.update({
        "side1_name": s1_name, "side1_val": s1_val_str,
        "side2_name": s2_name, "side2_val": s2_val_str,
        "angle_name": angle_name_formula, "angle_name_human": angle_name_human,
        "sin_val": sin_val_str,
    })

    # --- Генерация "умной" строки вычислений ---
    c_half = {"coef": 0.5, "radicand": 1.0, "denominator": 1.0}
    c1 = _parse_value_components(s1_val_str)
    c2 = _parse_value_components(s2_val_str)
    c_sin = _parse_value_components(sin_val_str)

    has_roots = c1["radicand"] > 1 or c2["radicand"] > 1 or c_sin["radicand"] > 1

    if has_roots:
        # Собираем все "некорневые" части
        all_coefs = [c_half["coef"], c1["coef"], c2["coef"], c_sin["coef"]]
        numeric_product = 1
        for c in all_coefs: numeric_product *= c

        # Собираем все "корневые" части
        roots_list = [f"√{format_number(c['radicand'])}" for c in [c1, c2, c_sin] if c['radicand'] > 1]
        roots_part = f"({ ' · '.join(roots_list) })" if len(roots_list) > 1 else (roots_list[0] if roots_list else "")

        # Собираем знаменатели
        all_denominators = [c_half["denominator"], c1["denominator"], c2["denominator"], c_sin["denominator"]]
        denominator_product = 1
        for d in all_denominators: denominator_product *= d

        # Формируем строку
        parts = [str(format_number(numeric_product))]
        if roots_part: parts.append(roots_part)

        comp_line = f"➡️ <b>S = { ' · '.join(parts) }"
        if denominator_product > 1:
            comp_line += f" / {format_number(denominator_product)}"

        context["detailed_computation_line"] = comp_line + f" = {task['answer']}</b>"
    else:
        # Простой случай без корней
        prod = _parse_value(s1_val_str) * _parse_value(s2_val_str)
        context["sides_product"] = format_number(prod)
        context["detailed_computation_line"] = f"➡️ <b>S = 1/2 · {context['sides_product']} · {context['sin_val']} = {task['answer']}</b>"

    return [{"action": f"{task['pattern']}:{narrative}", "data": context}]

# ============================================================
# РЫБА-ЗАГОТОВКА ДЛЯ ПАТТЕРНА 2.2: triangle_area_by_dividing_point
# ============================================================
def _solve_area_by_dividing_point(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Решает задачу на отношение площадей треугольников с общей высотой."""
    # TODO: Реализовать логику
    return [{"description_key": "TODO", "variables": {}}]

# ============================================================
# РЫБА-ЗАГОТОВКА ДЛЯ ПАТТЕРНА 2.3: triangle_area_by_parallel_line
# ============================================================
def _solve_area_by_parallel_line(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Решает задачу на площади подобных треугольников."""
    # TODO: Реализовать логику
    return [{"description_key": "TODO", "variables": {}}]

# ============================================================
# РЫБА-ЗАГОТОВКА ДЛЯ ПАТТЕРНА 2.4: triangle_area_by_midpoints
# ============================================================
def _solve_area_by_midpoints(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Решает задачу на площадь треугольника, отсекаемого средней линией."""
    # TODO: Реализовать логику
    return [{"description_key": "TODO", "variables": {}}]

# ============================================================
# РЫБА-ЗАГОТОВКА ДЛЯ ПАТТЕРНА 2.5: cosine_law_find_cos
# ============================================================
def _solve_cosine_law_find_cos(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Решает задачу на нахождение косинуса угла по трем сторонам."""
    # TODO: Реализовать логику
    return [{"description_key": "TODO", "variables": {}}]

# ============================================================
# РЫБА-ЗАГОТОВКА ДЛЯ ПАТТЕРНА 2.6: triangle_by_two_angles_and_side
# ============================================================
def _solve_triangle_by_two_angles_and_side(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Решает задачу на нахождение стороны по теореме синусов."""
    # TODO: Реализовать логику
    return [{"description_key": "TODO", "variables": {}}]

# ============================================================
# ГЛАВНЫЙ ДИСПЕТЧЕР
# ============================================================
HANDLERS = {
    "triangle_area_by_sin": _solve_area_by_sin,
    "triangle_area_by_dividing_point": _solve_area_by_dividing_point,
    "triangle_area_by_parallel_line": _solve_area_by_parallel_line,
    "triangle_area_by_midpoints": _solve_area_by_midpoints,
    "cosine_law_find_cos": _solve_cosine_law_find_cos,
    "triangle_by_two_angles_and_side": _solve_triangle_by_two_angles_and_side,
}

def solve(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    # ... (код диспетчера не меняется) ...
    pattern = task.get("pattern")
    handler = HANDLERS.get(pattern)
    if not handler:
        raise ValueError(f"Решатель для паттерна '{pattern}' не найден.")
    return handler(task)
