from typing import Dict, Any, List


# ============================================================
# ПАТТЕРН 3.1: isosceles_triangle_angles
# ============================================================
def _solve_isosceles_triangle_angles(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Решает задачи на углы в равнобедренном треугольнике.

    Формы:
    - find_base_angle      (дан угол при вершине → найти угол при основании)
    - find_vertex_angle   (дан угол при основании → найти угол при вершине)

    Legacy-совместим с существующим humanizer.
    """

    # --------------------------------------------------
    # Извлечение данных
    # --------------------------------------------------
    variables = task.get("variables", {})
    given = variables.get("given", {})
    to_find = variables.get("to_find", {})
    humanizer_data = variables.get("humanizer_data", {})

    narrative = task.get("narrative")

    triangle_name = given.get("triangle_name", "ABC")

    angle_data = given.get("angle", {})
    given_angle_value = angle_data.get("value")
    given_angle_role = angle_data.get("role")        # "vertex" | "base"
    given_angle_letter = angle_data.get("letter", "")

    if given_angle_value is None:
        raise ValueError("isosceles_triangle_angles: не задано значение угла")

    # --------------------------------------------------
    # Определяем вершину и основания ЯВНО
    # --------------------------------------------------
    vertex = humanizer_data.get("vertex_letter")

    if not vertex:
        raise ValueError(
            "isosceles_triangle_angles: не указана вершина треугольника"
        )

    triangle = triangle_name.strip()
    if len(triangle) != 3:
        raise ValueError(
            "isosceles_triangle_angles: некорректное имя треугольника"
        )

    base_letters = [c for c in triangle if c != vertex]

    if len(base_letters) != 2:
        raise ValueError(
            "isosceles_triangle_angles: не удалось определить углы при основании"
        )

    base_1, base_2 = base_letters

    target_letter = to_find.get("letter") or base_1

    # --------------------------------------------------
    # Общий context для humanizer
    # --------------------------------------------------
    context: Dict[str, Any] = {
        "triangle_name": triangle_name,
        "given_angle_value": given_angle_value,
        "given_angle_letter": given_angle_letter,
        "target_angle_letter": target_letter,
        "equal_sides": humanizer_data.get(
            "equal_sides",
            f"{vertex}{base_1} = {vertex}{base_2}"
        ),
        "res": task.get("answer"),
    }

    # ==================================================
    # ФОРМА 1: find_base_angle
    # Дан угол при вершине → ищем угол при основании
    # ==================================================
    if narrative == "find_base_angle":

        if given_angle_role != "vertex":
            raise ValueError(
                "isosceles_triangle_angles: ожидался угол при вершине"
            )

        # 180° − угол при вершине
        two_base_sum = 180 - given_angle_value

        # каждый угол при основании
        base_angle = two_base_sum / 2

        context.update({
            "vertex_angle": given_angle_value,
            "two_base_sum": two_base_sum,
            "context_base_angle": base_angle,
            "base_angle_name": target_letter,
            "second_base_angle_name": (
                base_2 if target_letter != base_2 else base_1
            ),
            "vertex_name": vertex,          # ← ВОТ ЭТО
        })

        return [{
            "action": "isosceles_triangle_angles:find_base_angle",
            "data": context
        }]

    # ==================================================
    # ФОРМА 2: find_vertex_angle
    # Дан угол при основании → ищем угол при вершине
    # ==================================================
    elif narrative == "find_vertex_angle":

        if given_angle_role != "base":
            raise ValueError(
                "isosceles_triangle_angles: ожидался угол при основании"
            )

        # сумма двух углов при основании
        double_base = 2 * given_angle_value

        # угол при вершине
        vertex_angle = 180 - double_base

        context.update({
            "base_angle": given_angle_value,
            "double_base": double_base,                    # ← для humanizer
            "context_vertex_angle": vertex_angle,
            "vertex_name": vertex,
            "base_angle_name": base_1,
            "second_base_angle_name": base_2,
        })

        return [{
            "action": "isosceles_triangle_angles:find_vertex_angle",
            "data": context
        }]

    # ==================================================
    # Неизвестная форма
    # ==================================================
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
