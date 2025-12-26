"""
Solver for Task 15 — Theme 1: Angles.
Возвращает данные для сценариев (Narrative Style).
"""

from typing import Any, Dict, List

def solve(task_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Возвращает solution_core в формате:
    [ { "action": "pattern_name", "data": { ... } } ]
    """
    pattern = task_data.get("pattern")

    context = {}
    if pattern == "triangle_external_angle":
        narrative = "external_angle"
        context = _solve_triangle_external_angle(task_data)

    elif pattern == "angle_bisector_find_half_angle":
        narrative = "bisector_half"
        context = _solve_angle_bisector(task_data)

    else:
        return []

    return [{
        "action": f"{pattern}:{narrative}",
        "data": context
    }]

# ============================================================================
# ЛОГИКА ВЫЧИСЛЕНИЙ
# ============================================================================

def _solve_triangle_external_angle(task: Dict[str, Any]) -> Dict[str, Any]:
    vars = task["variables"]
    given = vars["given"]
    hum_data = vars["humanizer_data"]

    angles = given["angles"]
    # Берем значения углов
    val_a = angles.get("A")
    val_b = angles.get("B")
    if val_a is None or val_b is None:
        vals = list(angles.values())
        val_a = val_a if val_a is not None else vals[0]
        val_b = val_b if val_b is not None else vals[1]

    res_val = val_a + val_b

    # Имена (жестко из humanizer_data, так как в базе они A и B)
    name_a = hum_data["angle_names"].get("A", "∠A")
    name_b = hum_data["angle_names"].get("B", "∠B")
    triangle_name = given.get("triangle_name", "ABC")
    target_vertex = vars.get("to_find", {}).get("name", "external_C")
    if isinstance(target_vertex, str) and "_" in target_vertex:
        target_vertex = target_vertex.split("_")[-1]

    return {
        "triangle_name": triangle_name,
        "angle_a_name": name_a,
        "angle_a_val": _fmt(val_a),
        "angle_b_name": name_b,
        "angle_b_val": _fmt(val_b),
        "target_vertex": target_vertex,
        "res": _fmt(res_val),
        "internal_c_val": _fmt(180 - res_val)
    }

def _solve_angle_bisector(task: Dict[str, Any]) -> Dict[str, Any]:
    vars = task["variables"]
    given = vars["given"]
    hum_data = vars["humanizer_data"]

    # Определяем, какую половинку угла нужно найти
    to_find_name = vars.get("to_find", {}).get("name")
    half_from_humanizer = hum_data["angle_names"].get("half")
    text = task.get("text", "")

    if to_find_name and to_find_name != "half_angle":
        target_half_name = to_find_name
    elif "CAD" in text:
        target_half_name = "CAD"
    elif "BAD" in text:
        target_half_name = "BAD"
    elif half_from_humanizer and isinstance(half_from_humanizer, str):
        target_half_name = half_from_humanizer.replace("∠", "")
    else:
        target_half_name = "BAD"

    full_val = given["angles"]["full_angle"]
    res_val = full_val / 2

    # Имена
    full_name = hum_data["angle_names"]["full"]
    bisector_name = hum_data["element_names"].get("bisector", "AD")

    # Вторая половинка (эвристика для красивого текста)
    if "B" in target_half_name:
        second_half_name = target_half_name.replace("B", "C")
    elif "C" in target_half_name:
        second_half_name = target_half_name.replace("C", "B")
    else:
        second_half_name = "CAD"

    return {
        "triangle_name": given.get("triangle_name", "ABC"),
        "full_angle_name": full_name,
        "full_angle_val": _fmt(full_val),
        "bisector_name": bisector_name,
        "target_half_name": target_half_name,
        "second_half_name": second_half_name,
        "res": _fmt(res_val)
    }

def _fmt(num: float) -> str:
    if num == int(num):
        return str(int(num))
    return str(num)
