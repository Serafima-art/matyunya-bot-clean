from typing import Dict, Any, List


# ============================================================
# ПАТТЕРН 3.1: isosceles_triangle_angles
# ============================================================
def _solve_isosceles_triangle_angles(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Решает задачи на углы в равнобедренном треугольнике.
    Формы:
    - find_base_angle      (дан угол при вершине)
    - find_vertex_angle   (дан угол при основании)
    """

    variables = task.get("variables", {})
    given = variables.get("given", {})
    to_find = variables.get("to_find", {})
    humanizer_data = variables.get("humanizer_data", {})

    narrative = variables.get("narrative")
    context: Dict[str, Any] = {
        "res": task.get("answer")
    }

    # --------------------------------------------------
    # ФОРМА 1: find_base_angle
    # Дан угол при вершине → найти угол при основании
    # --------------------------------------------------
    if narrative == "find_base_angle":
        vertex_angle = given.get("angles", {}).get("vertex")

        if vertex_angle is None:
            raise ValueError("isosceles_triangle_angles: не задан угол при вершине")

        two_base_sum = 180 - vertex_angle
        res = two_base_sum // 2

        context.update({
            "vertex_angle": vertex_angle,
            "two_base_sum": two_base_sum,
            "res": res,
            "base_angle_name": to_find.get("name", "C")
        })

        return [{
            "action": "isosceles_triangle_angles:find_base_angle",
            "data": context
        }]

    # --------------------------------------------------
    # ФОРМА 2: find_vertex_angle
    # Дан угол при основании → найти угол при вершине
    # --------------------------------------------------
    elif narrative == "find_vertex_angle":
        base_angle = given.get("angles", {}).get("base")

        if base_angle is None:
            raise ValueError("isosceles_triangle_angles: не задан угол при основании")

        double_base = base_angle * 2
        res = 180 - double_base

        context.update({
            "base_angle": base_angle,
            "double_base": double_base,
            "res": res,
            "vertex_name": to_find.get("name", "A"),
            "base_angle_name": given.get("base_angle_name", "B"),
            "second_base_angle_name": given.get("second_base_angle_name", "C"),
            "equal_sides": given.get("equal_sides", "AB = AC")
        })

        return [{
            "action": "isosceles_triangle_angles:find_vertex_angle",
            "data": context
        }]

    else:
        raise ValueError(
            f"isosceles_triangle_angles: неизвестная форма '{narrative}'"
        )


# ============================================================================
# ПАТТЕРН 3.2: equilateral_height_to_side
# ============================================================================
def _solve_equilateral_height_to_side(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    variables = task.get("variables", {})
    humanizer_data = variables.get("humanizer_data", {})

    context = {
        "res": task.get("answer"),
        "task_text": task.get("text"),
        **humanizer_data,
    }

    action = f"{task['pattern']}:{task.get('narrative', 'default')}"

    return [{
        "action": action,
        "data": context,
    }]


# ============================================================================
# ПАТТЕРН 3.3: equilateral_side_to_element
# ============================================================================
def _solve_equilateral_side_to_element(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    variables = task.get("variables", {})
    humanizer_data = variables.get("humanizer_data", {})

    context = {
        # обязательное
        "res": task.get("answer"),
        "task_text": task.get("text"),

        # данные для сценариев humanizer
        **humanizer_data,
    }

    action = f"{task['pattern']}:{task.get('narrative', 'default')}"

    return [{
        "action": action,
        "data": context,
    }]


# ============================================================================
# ДИСПЕТЧЕР ТЕМЫ 3
# ============================================================================
HANDLERS = {
    "isosceles_triangle_angles": _solve_isosceles_triangle_angles,
    "equilateral_height_to_side": _solve_equilateral_height_to_side,
    "equilateral_side_to_element": _solve_equilateral_side_to_element,
}


def solve(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Универсальный вход для ТЕМЫ 3 (Равнобедренные треугольники)
    """
    pattern = task.get("pattern")
    handler = HANDLERS.get(pattern)

    if not handler:
        raise ValueError(
            f"[Task 15 | Theme 3] Решатель для паттерна '{pattern}' не найден."
        )

    return handler(task)
