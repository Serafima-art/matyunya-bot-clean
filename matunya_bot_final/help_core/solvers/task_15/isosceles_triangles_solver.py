from typing import Dict, Any, List
from unittest import result


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
# Сторона равностороннего треугольника по высоте
# ============================================================================
def _solve_equilateral_height_to_side(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Решает задачи вида:
    equilateral_height_to_side (дана высота → найти сторону)

    Формула:
    h = a · √3 / 2  →  a = (2 · h) / √3

    Поддерживает legacy-JSON вида:
    given: {
        "element": "height",
        "value_raw": "15√3",
        "coefficient": 15,
        "has_root": true
    }
    """

    # --------------------------------------------------
    # Извлечение данных
    # --------------------------------------------------
    variables = task.get("variables", {})
    given = variables.get("given", {})
    to_find = variables.get("to_find", {})
    humanizer_data = variables.get("humanizer_data", {})

    # --------------------------------------------------
    # Проверка корректности входных данных
    # --------------------------------------------------
    if given.get("element") != "height":
        raise ValueError(
            "equilateral_height_to_side: ожидался элемент height"
        )

    h_coeff = given.get("coefficient")
    has_root = given.get("has_root", False)
    h_value_raw = given.get("value_raw")

    if h_coeff is None:
        raise ValueError(
            "equilateral_height_to_side: не задан коэффициент высоты"
        )

    # --------------------------------------------------
    # Вычисление стороны
    # --------------------------------------------------
    # h = a * √3 / 2  →  a = 2h / √3
    # Если h = k√3 → a = 2k
    if has_root:
        side = 2 * h_coeff
    else:
        # запасной вариант (на будущее)
        import math
        side = (2 * h_coeff) / math.sqrt(3)

    # --------------------------------------------------
    # Контекст для humanizer
    # --------------------------------------------------
    context: Dict[str, Any] = {
        "task_text": task.get("text"),

        # 🔑 ключи, которые ждёт humanizer
        "k": h_coeff,
        "h": h_value_raw or f"{h_coeff}√3",

        # можно оставить для совместимости
        "h_coeff": h_coeff,
        "h_value_raw": h_value_raw or f"{h_coeff}√3",

        "formula": humanizer_data.get("formula", "a = (2 · h) / √3"),
        "res": side,
    }

    action = f"{task['pattern']}:{task.get('narrative', 'default')}"

    return [{
        "action": action,
        "data": context,
    }]

# ============================================================================
# ПАТТЕРН 3.3: equilateral_side_to_element
# Высота / медиана / биссектриса по стороне
# ============================================================================

def _solve_equilateral_side_to_element(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    variables = task.get("variables", {})
    given = variables.get("given", {})
    to_find = variables.get("to_find", {})

    side_value = given.get("side_value")
    k = given.get("k")
    has_root = given.get("has_root", False)

    if side_value is None or k is None or not has_root:
        raise ValueError("equilateral_side_to_element: некорректные данные стороны")

    target = to_find.get("element")
    if target is None:
        raise ValueError("equilateral_side_to_element: не указан искомый элемент")

    # 1. СЛОВАРЬ СКЛОНЕНИЙ И СИМВОЛОВ
    # acc - Винительный (Найти кого/что? -> Медиану)
    # gen - Родительный (Формула для нахождения кого/чего? -> Медианы)
    # lower - Именительный с маленькой (вспомним: медиана равна высоте)
    # acc_lower - Винительный с маленькой (найти медиану)

    ELEMENT_MAP = {
        "height": {
            "label": "Высота",
            "symbol": "h",
            "acc": "Высоту",
            "gen": "Высоты",
            "lower": "высота",
            "acc_lower": "высоту"
        },
        "median": {
            "label": "Медиана",
            "symbol": "m",
            "acc": "Медиану",
            "gen": "Медианы",
            "lower": "медиана",
            "acc_lower": "медиану"
        },
        "bisector": {
            "label": "Биссектриса",
            "symbol": "l",
            "acc": "Биссектрису",
            "gen": "Биссектрисы",
            "lower": "биссектриса",
            "acc_lower": "биссектрису"
        },
    }

    if target not in ELEMENT_MAP:
         raise ValueError(f"equilateral_side_to_element: неизвестный элемент '{target}'")

    meta = ELEMENT_MAP[target]

    # 2. МАТЕМАТИКА
    # a = k√3 → h = a√3 / 2 = (k√3 * √3) / 2 = 3k / 2

    # Приводим k к числу (может прийти строкой "6")
    try:
        k_val = float(k)
        if k_val.is_integer():
            k_val = int(k_val)
    except ValueError:
         raise ValueError(f"equilateral_side_to_element: коэффициент k='{k}' не является числом")

    # Промежуточное вычисление для Шага 5 (числитель дроби после умножения корней)
    k_times_3 = k_val * 3

    # Итоговый результат
    result_val = k_times_3 / 2

    # Форматирование результата (убираем .0, если число целое)
    if result_val.is_integer():
        res_formatted = int(result_val)
    else:
        res_formatted = result_val

    # 3. КОНТЕКСТ ДЛЯ ШАБЛОНА
    context = {
        # Данные из условия
        "k": k_val,
        "a_value_raw": side_value,  # Например "6√3"

        # Целевой элемент и его склонения
        "target_label": meta["label"],          # "Медиана"
        "target_label_acc": meta["acc"],        # "Медиану" (для Шага 1)
        "target_label_gen": meta["gen"],        # "Медианы" (для Шага 3)
        "target_label_lower": meta["lower"],    # "медиана" (для Шага 2)
        "target_label_acc_lower": meta["acc_lower"], # "медиану"
        "target_symbol": meta["symbol"],        # "m"

        # Вычисленные значения
        "k_times_3": k_times_3,                 # 18 (для Шага 5)
        "res": res_formatted,                   # 9 (для Ответа)

        # Логика ветвления
        "target_is_not_height": meta["symbol"] != "h",
    }

    return [{
        "action": f"{task['pattern']}:{task.get('narrative', 'default')}",
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
