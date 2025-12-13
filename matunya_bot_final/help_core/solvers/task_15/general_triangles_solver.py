# matunya_bot_final/help_core/solvers/task_15/general_triangles_solver.py
"""
Решатель (Solver) для всех подтипов темы "Произвольные треугольники" Задания 15.
"""
import math
from typing import Dict, Any, List
from matunya_bot_final.help_core.solvers.task_15.task_15_text_formatter import format_number


# Нормализация названий площадей
def _norm_area_name(name: str | None) -> str | None:
    if name in ("S(MBN)", "S_MBN"):
        return "S_MBN"
    if name in ("S(ABC)", "S_ABC"):
        return "S_ABC"
    return name

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

def _get_area_relation(relations: Dict[str, Any], key: str) -> float | None:
    """
    Надёжно достаёт площадь из relations с учётом разных ключей:
    S_ABC / S(ABC), S_MBN / S(MBN)
    """
    if not relations:
        return None

    aliases = {
        "S_ABC": ("S_ABC", "S(ABC)"),
        "S_MBN": ("S_MBN", "S(MBN)"),
    }.get(key, (key,))

    for k in aliases:
        if relations.get(k) is not None:
            return _parse_value(relations[k])

    return None


def _norm_ratio_request(name: str | None) -> str | None:
    """
    Нормализует запрос отношения к двум каноническим вариантам:
    - 'MN/AC'
    - 'AC/MN'
    Поддерживает 'MN : AC', 'AC : MN', пробелы, разные двоеточия.
    """
    if not name:
        return None

    s = str(name).upper().replace(" ", "")
    s = s.replace("∶", ":").replace("：", ":")
    s = s.replace(":", "/")

    if "MN" in s and "AC" in s:
        return "AC/MN" if s.find("AC") < s.find("MN") else "MN/AC"

    return None

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
# ПАТТЕРН 2.2: triangle_area_by_dividing_point
# ============================================================
def _solve_area_by_dividing_point(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Решает задачу на отношение площадей треугольников с общей высотой."""
    variables = task.get("variables", {})
    given = variables.get("given", {})
    to_find = variables.get("to_find", {})
    points = given.get("points", {}).get("D_on_AC", {})
    relations = given.get("relations", {})

    ad_val = _parse_value(points.get("AD", 0))
    dc_val = _parse_value(points.get("DC", 0))
    s_abc_val = _parse_value(relations.get("S_ABC")) if relations.get("S_ABC") else None
    s_abd_val = _parse_value(relations.get("S_ABD")) if relations.get("S_ABD") else None
    s_bcd_val = _parse_value(relations.get("S_BCD")) if relations.get("S_BCD") else None

    to_find_name = to_find.get("name")
    context = {"res": task.get("answer")}
    narrative = ""

    if s_abc_val:
        narrative = "find_small_from_big"
        context["tips_key"] = "find_small_from_big"
        base_total = ad_val + dc_val
        target_area_name, target_base_name, target_base_val = ("S(ABD)", "AD", ad_val)
        if to_find_name == "S_BCD": target_area_name, target_base_name, target_base_val = ("S(BCD)", "DC", dc_val)
        if to_find_name in ("S_small", "S_big"):
            area_abd, area_bcd = s_abc_val * ad_val / base_total, s_abc_val * dc_val / base_total
            is_abd_target = (area_abd < area_bcd and to_find_name == "S_small") or (area_abd > area_bcd and to_find_name == "S_big")
            if not is_abd_target: target_area_name, target_base_name, target_base_val = ("S(BCD)", "DC", dc_val)
        context.update({"s_abc_val": format_number(s_abc_val), "ad_val": format_number(ad_val), "dc_val": format_number(dc_val), "target_area_name": target_area_name,
                        "target_base_name": target_base_name, "base_total_val": format_number(base_total),
                        "target_base_share_str": f"{format_number(target_base_val)}/{format_number(base_total)}"})

    elif s_abd_val or s_bcd_val:
        narrative = "find_from_small"

        known_area_name = "S(ABD)" if s_abd_val else "S(BCD)"
        known_area_val = s_abd_val or s_bcd_val

        known_base_parts = ad_val if s_abd_val else dc_val
        one_part_val = known_area_val / known_base_parts

        # какое основание и какой треугольник ищем
        if to_find_name == "S_ABC":
            target_triangle_name = "S(ABC)"
            target_base_parts = ad_val + dc_val
        else:
            # всегда ищем второй маленький треугольник
            if known_area_name == "S(ABD)":
                target_triangle_name = "S(BCD)"
                target_base_parts = dc_val
            else:
                target_triangle_name = "S(ABD)"
                target_base_parts = ad_val

        total_parts = ad_val + dc_val

        context.update({
            "known_area_name": known_area_name,
            "known_area_val": format_number(known_area_val),

            "ad_val": format_number(ad_val),
            "dc_val": format_number(dc_val),

            "known_base_parts": format_number(known_base_parts),
            "one_part_val": format_number(one_part_val),

            "is_find_big": to_find_name == "S_ABC",

            "total_parts": format_number(total_parts),

            # ✅ ПРАВИЛЬНОЕ ИМЯ
            "target_area_name": target_triangle_name,
            "target_base_parts": format_number(target_base_parts),

            "other_small_area_val": format_number(one_part_val * target_base_parts),
            "total_area_val": format_number(one_part_val * total_parts),

            # ⬇ можно оставить, они не мешают
            "target_parts": format_number(target_base_parts),
            "target_area_val": format_number(one_part_val * target_base_parts)
        })

    pre_image_filename = ""
    if ad_val is not None and dc_val is not None:
        image_base = "T4_AD_DC.svg" if ad_val > dc_val else "T4_DC_AD.svg"
        pre_image_filename = image_base.replace(".svg", "_with_height.svg")

    solution_core = [{"action": f"{task.get('pattern')}:{narrative}", "data": context, "pre_image_filename": pre_image_filename}]
    return solution_core

# ============================================================
# ПАТТЕРН 2.3: triangle_area_by_parallel_line
# ============================================================
def _solve_area_by_parallel_line(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Паттерн 2.3: triangle_area_by_parallel_line
    Формы:
    - area_by_similarity
    - segments_by_similarity
    - ratio_by_similarity
    """

    import math

    variables = task.get("variables", {})
    given = variables.get("given", {})
    to_find = variables.get("to_find", {})

    # -------------------------------------------------
    # 1. СБОР ИСХОДНЫХ ДАННЫХ
    # -------------------------------------------------
    raw_sides = {**given.get("sides", {}), **given.get("elements", {})}
    s = {k: _parse_value(v) for k, v in raw_sides.items() if v is not None}

    # дедукция отрезков
    if "AB" in s and "AM" in s and "BM" not in s:
        s["BM"] = s["AB"] - s["AM"]
    if "AB" in s and "BM" in s and "AM" not in s:
        s["AM"] = s["AB"] - s["BM"]
    if "AM" in s and "BM" in s and "AB" not in s:
        s["AB"] = s["AM"] + s["BM"]

    if "BC" in s and "BN" in s and "NC" not in s:
        s["NC"] = s["BC"] - s["BN"]
    if "BC" in s and "NC" in s and "BN" not in s:
        s["BN"] = s["BC"] - s["NC"]
    if "BN" in s and "NC" in s and "BC" not in s:
        s["BC"] = s["BN"] + s["NC"]

    # площади (устойчиво к S_ABC/S(ABC) и S_MBN/S(MBN))
    relations = given.get("relations", {}) or {}
    s_abc = _get_area_relation(relations, "S_ABC")
    s_mbn = _get_area_relation(relations, "S_MBN")

    if s_abc is None and given.get("S_ABC") is not None:
        s_abc = _parse_value(given["S_ABC"])

    if s_mbn is None and given.get("S_MBN") is not None:
        s_mbn = _parse_value(given["S_MBN"])

    def _compute_k() -> float | None:
        # 1) прямое отношение MN/AC
        if "MN" in s and "AC" in s and s["AC"]:
            return s["MN"] / s["AC"]

        # 2) заданное отношение MN_to_AC_ratio (например "1:2" или "1/2")
        ratio_str = given.get("MN_to_AC_ratio")
        if ratio_str:
            t = str(ratio_str).strip().replace(" ", "")
            t = t.replace(",", ".")
            if ":" in t:
                a, b = t.split(":", 1)
                return float(a) / float(b)
            if "/" in t:
                a, b = t.split("/", 1)
                return float(a) / float(b)

        # 3) другие стороны малого/большого
        if "BN" in s and "BC" in s and s["BC"]:
            return s["BN"] / s["BC"]

        if "BM" in s and "AB" in s and s["AB"]:
            return s["BM"] / s["AB"]

        if "NC" in s and "BC" in s and s["BC"]:
            return s["NC"] / s["BC"]

        # 4) из площадей, если обе известны
        if s_mbn is not None and s_abc is not None and s_abc:
            return math.sqrt(s_mbn / s_abc)

        return None

    k = _compute_k()

    # -------------------------------------------------
    # 2. ОПРЕДЕЛЯЕМ FORM (narrative) — строго по to_find.type
    # -------------------------------------------------
    to_find_type = to_find.get("type")
    to_find_name = to_find.get("name")

    if to_find_type == "area":
        narrative = "area_by_similarity"

    elif to_find_type == "ratio":
        narrative = "ratio_by_similarity"

    elif to_find_type == "side":
        narrative = "segments_by_similarity"

    else:
        raise ValueError(f"Неизвестный тип искомой величины: {to_find_type}")

    # -------------------------------------------------
    # 4. ПОДГОТОВКА CONTEXT (БЕЗ МУСОРА)
    # -------------------------------------------------
    context = {
        "res": task.get("answer"),
        "ac_val": format_number(s.get("AC")),
        "mn_val": format_number(s.get("MN")),
        "ab_val": format_number(s.get("AB")),
        "am_val": format_number(s.get("AM")),
        "bm_val": format_number(s.get("BM")),
        "bc_val": format_number(s.get("BC")),
        "bn_val": format_number(s.get("BN")),
        "nc_val": format_number(s.get("NC")),
        "s_abc_val": format_number(s_abc),
        "s_mbn_val": format_number(s_mbn),
        "to_find_name": to_find_name,
    }

    # -------------------------------------------------
    # 5. ЛОГИКА ПО ФОРМАМ
    # -------------------------------------------------

    # 🔵 AREA BY SIMILARITY
    if narrative == "area_by_similarity":

        if k is None:
            # пробуем взять k из текстового отношения MN:AC
            ratio_str = given.get("MN_to_AC_ratio")
            if ratio_str:
                t = str(ratio_str).replace(" ", "")
                if ":" in t:
                    a, b = t.split(":", 1)
                    k = float(a) / float(b)
                elif "/" in t:
                    a, b = t.split("/", 1)
                    k = float(a) / float(b)

        if k is None:
            raise ValueError("Недостаточно данных для вычисления k")

        # Как показываем k² в шагах
        if s.get("MN") is not None and s.get("AC") is not None:
            k_squared_str = f"({format_number(s['MN'])}/{format_number(s['AC'])})²"
        else:
            k_squared_str = f"{format_number(k)}²"

        # Чётко определяем, что ищем
        if to_find_name == "S_MBN":
            if s_abc is None:
                raise ValueError("Недостаточно данных: неизвестна площадь S(ABC)")
            known_area_name = "S(ABC)"
            known_area_val = format_number(s_abc)
            target_area_name = "S(MBN)"

        elif to_find_name == "S_ABC":
            if s_mbn is None:
                raise ValueError("Недостаточно данных: неизвестна площадь S(MBN)")
            known_area_name = "S(MBN)"
            known_area_val = format_number(s_mbn)
            target_area_name = "S(ABC)"

        else:
            raise ValueError(
                f"Искомая величина не относится к площадям: {to_find_name}"
            )

        context.update({
            "known_area_name": known_area_name,
            "known_area_val": known_area_val,
            "target_area_name": target_area_name,
            "k_squared_str": k_squared_str,
        })

    # 🟡 SEGMENTS BY SIMILARITY — ЧИСТЫЙ SOLVER
    elif narrative == "segments_by_similarity":

        if to_find_name in ("BM", "BN", "MN"):
            platform = "direct_by_k"
        else:
            platform = "restore_whole_side"

        context["platform"] = platform

        # 0. Проверка коэффициента подобия
        if k is None:
            raise ValueError("Недостаточно данных для коэффициента подобия")

        # 1. Восстановление MN / AC через k
        if "AC" not in s and "MN" in s:
            s["AC"] = s["MN"] / k
        if "MN" not in s and "AC" in s:
            s["MN"] = s["AC"] * k

        # 2. Восстановление частей через k
        if "BM" not in s and "AB" in s:
            s["BM"] = s["AB"] * k
        if "BN" not in s and "BC" in s:
            s["BN"] = s["BC"] * k

        # 3. Восстановление частей через разность
        if "AM" not in s and "AB" in s and "BM" in s:
            s["AM"] = s["AB"] - s["BM"]
        if "NC" not in s and "BC" in s and "BN" in s:
            s["NC"] = s["BC"] - s["BN"]

        # 4. Восстановление целых сторон
        if "AB" not in s and "BM" in s:
            s["AB"] = s["BM"] / k
        if "AB" not in s and "AM" in s:
            s["AB"] = s["AM"] / (1 - k)

        if "BC" not in s and "BN" in s:
            s["BC"] = s["BN"] / k
        if "BC" not in s and "NC" in s:
            s["BC"] = s["NC"] / (1 - k)

        # 5. Финальная проверка
        if to_find_name not in s or s[to_find_name] is None:
            raise ValueError(f"Невозможно найти отрезок {to_find_name}")

        # 6. Подготовка ЧИСТОГО контекста (только числа)
        temp_context = {
            f"{side.lower()}_val": format_number(s.get(side))
            for side in ["AC", "MN", "AB", "AM", "BM", "BC", "BN", "NC"]
            if side in s
        }

        context.update(temp_context)

        # 7. Числа, нужные humanizer'у
        context.update({
            "k_val": format_number(k),
            "one_minus_k": format_number(1 - k),
            "final_value": format_number(s[to_find_name])
        })

    # 🟣 RATIO BY SIMILARITY
    elif narrative == "ratio_by_similarity":

        if k is None and s_mbn is not None and s_abc is not None and s_abc != 0:
            k = math.sqrt(s_mbn / s_abc)

        # 1️⃣ k должен быть уже посчитан в _compute_k()
        local_k = k

        # 2️⃣ если вдруг не найден — допускаем ТОЛЬКО вывод через площади
        if local_k is None and s_mbn is not None and s_abc is not None and s_abc != 0:
            local_k = math.sqrt(s_mbn / s_abc)

        # 3️⃣ если всё ещё нет — честная ошибка
        if local_k is None:
            raise ValueError("Для отношения нужны данные для вычисления k")

        # 4️⃣ определяем направление отношения (по исходному name!)
        ratio_req = _norm_ratio_request(to_find.get("name"))

        # 5️⃣ считаем итоговое отношение
        if ratio_req == "AC/MN":
            ratio_val = 1 / local_k
        else:
            # по умолчанию MN/AC
            ratio_val = local_k

        context.update({
            "k_val": format_number(local_k),
            "ratio_str": format_number(ratio_val),
        })

        context.update({
            "k_val": format_number(local_k),
            "ratio_str": format_number(ratio_val),
            "ratio_req": ratio_req or "MN/AC",
        })


    # -------------------------------------------------
    # 6. ВОЗВРАТ SOLUTION_CORE
    # -------------------------------------------------
    return [{
        "action": f"{task.get('pattern')}:{narrative}",
        "data": context
    }]


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
