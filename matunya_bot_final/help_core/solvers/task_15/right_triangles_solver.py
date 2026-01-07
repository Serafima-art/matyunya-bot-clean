from typing import Dict, Any, List
import math

# ============================================================
# ПАТТЕРН 4.1: right_triangle_angles_sum
# Сумма острых углов прямоугольного треугольника
# ============================================================
def _solve_right_triangle_angles_sum(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Решает задачи на нахождение острого угла, если дан другой острый угол.
    Свойство: Сумма острых углов прямоугольного треугольника равна 90°.
    """
    variables = task.get("variables", {})
    given = variables.get("given", {})

    # 1. Извлечение данных (angle_alpha или angle)
    known_angle = given.get("angle_alpha")

    if known_angle is None:
        angle_obj = given.get("angle")
        if isinstance(angle_obj, (int, float)):
            known_angle = angle_obj
        elif isinstance(angle_obj, dict):
            known_angle = angle_obj.get("value")

    if known_angle is None:
        raise ValueError(f"right_triangle_angles_sum: не указано значение известного угла. Данные given: {given}")

    # 2. Математика
    result_val = 90 - known_angle

    if result_val <= 0:
        raise ValueError(f"right_triangle_angles_sum: некорректный угол {known_angle}, результат {result_val}")

    # 3. Форматирование
    def fmt(num):
        return int(num) if float(num).is_integer() else num

    # 4. Контекст
    context = {
        "known_angle": fmt(known_angle),
        "res": fmt(result_val)
    }

    # ВАЖНО: Принудительно ставим default, чтобы хьюмонайзер увидел "Идею решения"
    narrative = "default"

    return [{
        "action": f"{task['pattern']}:{narrative}",
        "data": context
    }]

# ============================================================
# ПАТТЕРН 4.2: pythagoras_find_leg
# Нахождение катета по гипотенузе и другому катету
# ============================================================
def _solve_pythagoras_find_leg(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    variables = task.get("variables", {})
    given = variables.get("given", {})

    c = given.get("hypotenuse")
    b = given.get("known_leg")

    if c is None or b is None:
        raise ValueError(f"pythagoras_find_leg: отсутствуют данные. given={given}")

    c_sq = c ** 2
    b_sq = b ** 2
    diff = c_sq - b_sq

    if diff <= 0:
        raise ValueError(f"pythagoras_find_leg: гипотенуза ({c}) должна быть больше катета ({b})")

    res = math.sqrt(diff)

    def fmt(num):
        return int(num) if float(num).is_integer() else num

    c_fmt = fmt(c)
    b_fmt = fmt(b)
    res_fmt = fmt(res)

    # Логика троек
    base_triples = [
        [3, 4, 5], [5, 12, 13], [8, 15, 17], [7, 24, 25],
        [20, 21, 29], [9, 40, 41], [11, 60, 61], [12, 35, 37]
    ]

    # Сортируем: [меньший_катет, больший_катет, гипотенуза]
    current_sides_sorted = sorted([int(b_fmt), int(res_fmt), int(c_fmt)])

    k_factor = math.gcd(current_sides_sorted[0], math.gcd(current_sides_sorted[1], current_sides_sorted[2]))

    triple_name = None
    base_unknown_leg = None

    if k_factor >= 1:
        reduced = [s // k_factor for s in current_sides_sorted]

        for t in base_triples:
            # t тоже отсортирован: [3, 4, 5]
            if reduced == sorted(t):
                triple_name = f"{t[0]}-{t[1]}-{t[2]}"

                # Нам нужно понять, какой из катетов в БАЗОВОЙ тройке неизвестен
                # reduced = [5, 12, 13] (базовая). Реальный res = 36 -> reduced_res = 12
                # Значит base_unknown_leg = 12
                base_unknown_leg = int(res_fmt) // k_factor
                break

    context = {
        "c": c_fmt,
        "b": b_fmt,
        "c_sq": fmt(c_sq),
        "b_sq": fmt(b_sq),
        "diff": fmt(diff),
        "res": res_fmt,
        "triple_name": triple_name,
        "k_factor": k_factor,
        # Доп переменные для шаблона
        "base_hypotenuse_calc": int(c_fmt) // k_factor,
        "base_leg_calc": int(b_fmt) // k_factor,
        "base_unknown_leg": base_unknown_leg,
        "is_scaled": k_factor > 1
    }

    return [{
        "action": f"{task['pattern']}:default",
        "data": context
    }]

# ============================================================
# ПАТТЕРН 4.3: pythagoras_find_hypotenuse
# Нахождение гипотенузы по двум катетам
# ============================================================
def _solve_pythagoras_find_hypotenuse(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Формула: c² = a² + b²
    """
    variables = task.get("variables", {})
    given = variables.get("given", {})

    # 1. Извлечение данных
    # В JSON приходят leg_1 и leg_2
    a = given.get("leg_1")
    b = given.get("leg_2")

    if a is None or b is None:
        raise ValueError(f"pythagoras_find_hypotenuse: отсутствуют данные. given={given}")

    # 2. Математика
    a_sq = a ** 2
    b_sq = b ** 2
    sum_sq = a_sq + b_sq
    res = math.sqrt(sum_sq)

    # 3. Форматирование
    def fmt(num):
        return int(num) if float(num).is_integer() else num

    a_fmt = fmt(a)
    b_fmt = fmt(b)
    res_fmt = fmt(res)

    # 4. Проверка на Пифагоровы тройки
    base_triples = [
        [3, 4, 5], [5, 12, 13], [8, 15, 17], [7, 24, 25],
        [20, 21, 29], [9, 40, 41], [11, 60, 61], [12, 35, 37]
    ]

    # Сортируем стороны: [катет1, катет2, гипотенуза]
    # res_fmt (гипотенуза) всегда будет последней после сортировки, но для порядка сортируем всё
    current_sides_sorted = sorted([int(a_fmt), int(b_fmt), int(res_fmt)])

    # Находим НОД
    k_factor = math.gcd(current_sides_sorted[0], math.gcd(current_sides_sorted[1], current_sides_sorted[2]))

    triple_name = None
    base_hyp_calc = None # Базовая гипотенуза (которую мы "вспоминаем")

    if k_factor >= 1:
        reduced = [s // k_factor for s in current_sides_sorted]

        for t in base_triples:
            if reduced == sorted(t):
                triple_name = f"{t[0]}-{t[1]}-{t[2]}"
                # В базовой тройке гипотенуза всегда самая большая (последний элемент)
                base_hyp_calc = t[-1]
                break

    # 5. Контекст
    context = {
        "a": a_fmt,
        "b": b_fmt,
        "a_sq": fmt(a_sq),
        "b_sq": fmt(b_sq),
        "sum_sq": fmt(sum_sq),
        "res": res_fmt,

        # Данные для Способа 2
        "triple_name": triple_name,
        "k_factor": k_factor,
        "is_scaled": k_factor > 1,

        # Переменные для шаблона (деление текущих катетов на к)
        "calc_leg1_base": int(a_fmt) // k_factor,
        "calc_leg2_base": int(b_fmt) // k_factor,
        "base_hyp_calc": base_hyp_calc
    }

    return [{
        "action": f"{task['pattern']}:default",
        "data": context
    }]


# ============================================================
# ПАТТЕРН 4.4: find_cos_sin_tg_from_sides
# Нахождение тригонометрических функций (sin, cos, tg) по сторонам
# ============================================================
def _solve_find_cos_sin_tg_from_sides(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    variables = task.get("variables", {})
    given = variables.get("given", {})
    target = variables.get("target", {})

    # 1. Берем нарратив из JSON (валидатор уже всё решил)
    narrative = task.get("narrative", "direct")

    # 2. Геометрия
    right_angle = target.get("right_angle")
    target_angle = target.get("angle")
    func_name = target.get("fn")

    vertex_set = {"A", "B", "C"}
    hyp_name = "".join(sorted(list(vertex_set - {right_angle})))
    opp_name = "".join(sorted(list(vertex_set - {target_angle})))
    adj_name = "".join(sorted([target_angle, right_angle]))

    def get_val(name):
        return given.get(name) or given.get(name[::-1])

    # Получаем все значения (даже если они вычислены валидатором)
    full_hyp = get_val(hyp_name)
    full_opp = get_val(opp_name)
    full_adj = get_val(adj_name)

    # 3. Настройка отображения (Что показывать в "Дано"?)
    show_hyp = False
    show_opp = False
    show_adj = False
    calc_step = None

    if narrative == "direct":
        # Показываем ТОЛЬКО то, что нужно для формулы
        if func_name == "sin":
            show_opp, show_hyp = True, True
        elif func_name == "cos":
            show_adj, show_hyp = True, True
        elif func_name == "tg":
            show_opp, show_adj = True, True

    elif narrative == "calc_hyp":
        # Даны два катета, ищем гипотенузу
        show_opp, show_adj = True, True

        calc_step = {
            "type": "find_hyp", # Для шаблона (если нужно условие)
            "formula": f"{hyp_name}² = {opp_name}² + {adj_name}²",
            "calc_str": f"{int(full_opp)}² + {int(full_adj)}² = {int(full_opp**2)} + {int(full_adj**2)} = {int(full_hyp**2)}",
            "res": int(full_hyp),
            "target_name": hyp_name
        }

    elif narrative == "calc_leg":
        # Дана гипотенуза и один катет
        show_hyp = True

        # Определяем, какой катет нам ИЗВЕСТЕН, а какой ИЩЕМ.
        # Логика:
        # Если нужен sin (opp/hyp) -> значит не хватало opp -> известен adj.
        # Если нужен cos (adj/hyp) -> значит не хватало adj -> известен opp.
        # Если нужен tg (opp/adj) -> тут сложнее. Валидатор мог решить по-разному.
        # Но для tg нам всё равно нужно показать один катет и найти другой.

        target_leg_name = None
        known_leg_name = None

        if func_name == "sin":
            known_leg_name = adj_name
            target_leg_name = opp_name
            show_adj = True
        elif func_name == "cos":
            known_leg_name = opp_name
            target_leg_name = adj_name
            show_opp = True
        else: # tg
            # Эвристика: считаем известным тот, который "красивый" (целый) или просто adj по дефолту
            # Но проще довериться валидатору: если в JSON есть opp и hyp, значит искали adj.
            # Но у нас в given есть ВСЁ.
            # Давай просто покажем ПРИЛЕЖАЩИЙ, а найдем ПРОТИВОЛЕЖАЩИЙ (или наоборот).
            # Для единообразия: пусть известен adj.
            known_leg_name = adj_name
            target_leg_name = opp_name
            show_adj = True

        known_val = get_val(known_leg_name)
        target_val = get_val(target_leg_name)

        calc_step = {
            "type": "find_leg",
            "formula": f"{target_leg_name}² = {hyp_name}² - {known_leg_name}²",
            "calc_str": f"{int(full_hyp)}² - {int(known_val)}² = {int(full_hyp**2)} - {int(known_val**2)} = {int(target_val**2)}",
            "res": int(target_val),
            "target_name": target_leg_name
        }

    # 4. Сборка ответа
    needed_map = {
        "sin": ("opp", "hyp"),
        "cos": ("adj", "hyp"),
        "tg": ("opp", "adj")
    }
    num_type, den_type = needed_map[func_name]
    vals = {"opp": full_opp, "adj": full_adj, "hyp": full_hyp}
    names = {"opp": opp_name, "adj": adj_name, "hyp": hyp_name}

    res_val = vals[num_type] / vals[den_type]

    def fmt(num):
        if num is None: return "?"
        return int(num) if float(num).is_integer() else num

    context = {
        "func_name": func_name,
        "angle": target_angle,
        "right_angle": right_angle,

        "is_sin": func_name == "sin",
        "is_cos": func_name == "cos",
        "is_tg": func_name == "tg",

        "num_name": names[num_type],
        "den_name": names[den_type],
        "num_val": fmt(vals[num_type]),
        "den_val": fmt(vals[den_type]),
        "res": res_val,

        "calc_step": calc_step,

        # ВАЖНО: Передаем только те переменные, которые разрешили флаги
        "given_hyp": fmt(full_hyp) if show_hyp else None,
        "given_opp": fmt(full_opp) if show_opp else None,
        "given_adj": fmt(full_adj) if show_adj else None,

        "hyp_name": hyp_name,
        "opp_name": opp_name,
        "adj_name": adj_name
    }

    return [{
        "action": f"{task['pattern']}:{narrative}",
        "data": context
    }]


# ============================================================
# ПАТТЕРН 4.5: find_side_from_trig_ratio
# Нахождение стороны через синус, косинус или тангенс
# ============================================================
def _solve_find_side_from_trig_ratio(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Решает задачи вида: "Найди катет BC, если AB=20 и sin A = 0.5"
    """
    variables = task.get("variables", {})
    given = variables.get("given", {})
    to_find = variables.get("to_find", {})

    # Пока заглушка
    raise NotImplementedError("Паттерн find_side_from_trig_ratio еще не реализован")


# ============================================================
# ПАТТЕРН 4.6: right_triangle_median_to_hypotenuse
# Свойство медианы, проведенной к гипотенузе
# ============================================================
def _solve_right_triangle_median_to_hypotenuse(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Свойство: Медиана, проведенная к гипотенузе, равна её половине.
    m = c / 2
    """
    variables = task.get("variables", {})
    given = variables.get("given", {})
    to_find = variables.get("to_find", {})

    # Пока заглушка
    raise NotImplementedError("Паттерн right_triangle_median_to_hypotenuse еще не реализован")


# ============================================================================
# ДИСПЕТЧЕР ТЕМЫ 4
# ============================================================================
HANDLERS = {
    "right_triangle_angles_sum": _solve_right_triangle_angles_sum,
    "pythagoras_find_leg": _solve_pythagoras_find_leg,
    "pythagoras_find_hypotenuse": _solve_pythagoras_find_hypotenuse,
    "find_cos_sin_tg_from_sides": _solve_find_cos_sin_tg_from_sides,
    "find_side_from_trig_ratio": _solve_find_side_from_trig_ratio,
    "right_triangle_median_to_hypotenuse": _solve_right_triangle_median_to_hypotenuse,
}


def solve(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Универсальный вход для ТЕМЫ 4 (Прямоугольные треугольники)
    """
    pattern = task.get("pattern")
    handler = HANDLERS.get(pattern)

    if not handler:
        raise ValueError(
            f"[Task 15 | Theme 4] Решатель для паттерна '{pattern}' не найден."
        )

    return handler(task)
