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

    # =================================================
    # ШАГ 1: РАЗДЕЛЕНИЕ ДАННЫХ (КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ)
    # =================================================

    # 1А: ДАННЫЕ ДЛЯ ОТОБРАЖЕНИЯ ("ДАНО")
    # Создаем context и наполняем его СЫРЫМИ данными, как они пришли из JSON.
    # Это решает проблему с CN/NC и появлением вычисленных значений в "Дано".
    context = {}
    raw_sides_display = {**given.get("sides", {}), **given.get("elements", {})}
    for key, value in raw_sides_display.items():
        if value is not None:
            context[f"{key.lower()}_val"] = format_number(_parse_value(value))

    # 1Б: ДАННЫЕ ДЛЯ ВЫЧИСЛЕНИЙ
    # Создаем рабочий словарь 's', в котором будем проводить все вычисления.
    raw_sides_calc = {**given.get("sides", {}), **given.get("elements", {})}
    s = {k: _parse_value(v) for k, v in raw_sides_calc.items() if v is not None}

    # Нормализуем имена в рабочем словаре для единообразия.
    if "CN" in s and "NC" not in s: s["NC"] = s["CN"]
    if "MA" in s and "AM" not in s: s["AM"] = s["MA"]

    # 1В: РАННЯЯ ДЕДУКЦИЯ (ДЛЯ ВЫЧИСЛЕНИЯ k)
    # Вычисляем недостающие части сторон, если это необходимо для нахождения 'k'.
    if "AB" in s and "AM" in s and "BM" not in s: s["BM"] = s["AB"] - s["AM"]
    if "BC" in s and "BN" in s and "NC" not in s: s["NC"] = s["BC"] - s["BN"]

    # 1Г: СБОР ПЛОЩАДЕЙ
    relations = given.get("relations", {}) or {}
    s_abc = _get_area_relation(relations, "S_ABC")
    s_mbn = _get_area_relation(relations, "S_MBN")
    if s_abc is None and given.get("S_ABC") is not None: s_abc = _parse_value(given["S_ABC"])
    if s_mbn is None and given.get("S_MBN") is not None: s_mbn = _parse_value(given["S_MBN"])

    # =================================================
    # ШАГ 2: ОБЩИЕ ВЫЧИСЛЕНИЯ (k)
    # =================================================
    def _compute_k() -> Dict[str, Any] | None:
        # Возвращает словарь: {"value": k, "num": numerator, "den": denominator}
        # Это позволит humanizer'у показать исходную дробь
        def result(val, num, den): return {"value": val, "num": num, "den": den}

        if "MN" in s and "AC" in s and s["AC"]: return result(s["MN"] / s["AC"], s["MN"], s["AC"])

        ratio_str = given.get("MN_to_AC_ratio")
        if ratio_str:
            t = str(ratio_str).strip().replace(" ", "").replace(",", ".")
            if ":" in t: a, b = t.split(":", 1); return result(float(a) / float(b), float(a), float(b))
            if "/" in t: a, b = t.split("/", 1); return result(float(a) / float(b), float(a), float(b))

        if "BN" in s and "BC" in s and s["BC"]: return result(s["BN"] / s["BC"], s["BN"], s["BC"])
        if "BM" in s and "AB" in s and s["AB"]: return result(s["BM"] / s["AB"], s["BM"], s["AB"])

        if "NC" in s and "BC" in s and s["BC"]:
            # k = (BC-NC)/BC
            return result(1 - (s["NC"] / s["BC"]), s["BC"] - s["NC"], s["BC"])

        if s_mbn is not None and s_abc is not None and s_abc:
            # Здесь у нас нет исходной дроби, только результат
            val = math.sqrt(s_mbn / s_abc)
            return result(val, None, None)

        return None

    k_data = _compute_k()
    k = k_data["value"] if k_data else None

    # =================================================
    # ШАГ 3: ОПРЕДЕЛЕНИЕ СЦЕНАРИЯ
    # =================================================
    to_find_type = to_find.get("type")
    to_find_name = to_find.get("name")

    if to_find_type == "area": narrative = "area_by_similarity"
    elif to_find_type == "ratio": narrative = "ratio_by_similarity"
    elif to_find_type == "side": narrative = "segments_by_similarity"
    else: raise ValueError(f"Неизвестный тип искомой величины: {to_find_type}")

    # =================================================
    # ШАГ 4: ДОБАВЛЕНИЕ ОБЩИХ ДАННЫХ В КОНТЕКСТ
    # =================================================
    context.update({
        "res": task.get("answer"),
        "s_abc_val": format_number(s_abc),
        "s_mbn_val": format_number(s_mbn),
        "to_find_name": to_find_name,
        "k_num": format_number(k_data.get("num")) if k_data else None,
        "k_den": format_number(k_data.get("den")) if k_data else None,
    })

    # =================================================
    # ШАГ 5: ЛОГИКА ПО ФОРМАМ
    # =================================================
    if narrative == "area_by_similarity":
        if k is None: raise ValueError("Недостаточно данных для вычисления k")

        # Получаем отформатированное значение k (например, "2/3")
        k_val_formatted = format_number(k)

        # Формируем строку для k² из УЖЕ СОКРАЩЕННОЙ дроби
        k_squared_str = f"({k_val_formatted})²"

        if to_find_name == "S_MBN": known_area_name, known_area_val, target_area_name = "S(ABC)", format_number(s_abc), "S(MBN)"
        elif to_find_name == "S_ABC": known_area_name, known_area_val, target_area_name = "S(MBN)", format_number(s_mbn), "S(ABC)"
        else: raise ValueError(f"Искомая величина не относится к площадям: {to_find_name}")

        # Добавляем в context и k_val, и k_squared_str
        context.update({
            "k_val": k_val_formatted,
            "known_area_name": known_area_name,
            "known_area_val": known_area_val,
            "target_area_name": target_area_name,
            "k_squared_str": k_squared_str
        })

    elif narrative == "segments_by_similarity":
        # --- 5.1 ОПРЕДЕЛЕНИЕ ПЛАТФОРМЫ РЕШЕНИЯ ---
        has_top_part = (to_find_name == "AB" and "AM" in s) or (to_find_name == "BC" and "NC" in s)
        is_find_top = (to_find_name == "AM" and "AB" in s) or (to_find_name == "NC" and "BC" in s)
        if has_top_part: platform = "restore_whole_side"
        elif is_find_top: platform = "find_top_part"
        else: platform = "direct_by_k"
        context["platform"] = platform

        if k is None: raise ValueError("Нет данных для k")

        # --- 5.2 ПОЛНАЯ ДЕДУКЦИЯ ДЛЯ РЕШЕНИЯ ---
        # Здесь мы вычисляем ВСЕ возможные стороны, чтобы гарантированно найти ответ.
        # Это не влияет на "Дано", т.к. работа идет только со словарем 's'.
        if "AC" not in s and "MN" in s: s["AC"] = s["MN"] / k
        if "MN" not in s and "AC" in s: s["MN"] = s["AC"] * k
        if "BM" not in s and "AB" in s: s["BM"] = s["AB"] * k
        if "BN" not in s and "BC" in s: s["BN"] = s["BC"] * k
        if "AB" not in s and "BM" in s: s["AB"] = s["BM"] / k
        if "BC" not in s and "BN" in s: s["BC"] = s["BN"] / k
        if "AB" in s and "BM" in s and "AM" not in s: s["AM"] = s["AB"] - s["BM"]
        if "BC" in s and "BN" in s and "NC" not in s: s["NC"] = s["BC"] - s["BN"]
        if platform == "restore_whole_side" and to_find_name not in s:
            if to_find_name == "AB" and "AM" in s: s["AB"] = s["AM"] / (1 - k)
            if to_find_name == "BC" and "NC" in s: s["BC"] = s["NC"] / (1 - k)

        # --- 5.3 ДОБАВЛЕНИЕ УНИКАЛЬНЫХ КЛЮЧЕЙ ДЛЯ ШАБЛОНОВ ---
        context.update({"k_val": format_number(k), "one_minus_k": format_number(1 - k), "final_value": format_number(s.get(to_find_name))})
        if platform == "restore_whole_side":
            whole, part, unknown_part, point_name = to_find_name, ("AM" if to_find_name == "AB" else "NC"), ("BM" if to_find_name == "AB" else "BN"), ("M" if to_find_name == "AB" else "N")
            context.update({"restore_whole_name": whole, "restore_part_name": part, "restore_part_val": format_number(s.get(part)), "restore_unknown_part_name": unknown_part, "restore_point_name": point_name})
        elif platform == "find_top_part":
            whole, bottom_part = ("AB" if to_find_name == "AM" else "BC"), ("BM" if to_find_name == "AM" else "BN")
            context.update({"find_top_whole_name": whole, "find_top_whole_val": format_number(s.get(whole)), "find_top_bottom_part_name": bottom_part, "find_top_bottom_part_val": format_number(s.get(bottom_part))})
        elif platform == "direct_by_k":
            if "MN" in to_find_name or "AC" in to_find_name: small, big = "MN", "AC"
            elif "BM" in to_find_name or "AB" in to_find_name: small, big = "BM", "AB"
            else: small, big = "BN", "BC"
            big_val = "" if to_find_name == big else format_number(s.get(big))
            context.update({"direct_small_side": small, "direct_big_side": big, "direct_small_side_val": format_number(s.get(small)), "direct_big_side_val": big_val})

    elif narrative == "ratio_by_similarity":
        if k is None: raise ValueError("Для отношения нужны данные для вычисления k")
        ratio_req = _norm_ratio_request(to_find.get("name"))
        ratio_val = 1 / k if ratio_req == "AC/MN" else k
        context.update({"k_val": format_number(k), "ratio_str": format_number(ratio_val), "ratio_req": ratio_req or "MN/AC"})

    return [{"action": f"{task.get('pattern')}:{narrative}", "data": context}]

# ============================================================
# ПАТТЕРН 2.4: triangle_area_by_midpoints
# ============================================================
def _solve_area_by_midpoints(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Решает задачу на площадь треугольника, отсекаемого средней линией."""

    variables = task.get("variables", {})
    given = variables.get("given", {})
    to_find = variables.get("to_find", {})
    relations = given.get("relations", {})

    # Определяем искомую площадь ОДИН РАЗ
    to_find_name = to_find.get("name")

    s_abc, s_mbn, s_amnc = None, None, None
    from_part = None

    # --- 1. Определяем, что дано, и вычисляем остальные площади ---
    if "S_ABC" in relations:
        from_part = "from_big_triangle"
        s_abc = _parse_value(relations["S_ABC"])
        s_mbn = s_abc / 4
        s_amnc = s_abc * 3 / 4
    elif "S_MBN" in relations:
        from_part = "from_small_triangle"
        s_mbn = _parse_value(relations["S_MBN"])
        s_abc = s_mbn * 4
        s_amnc = s_mbn * 3
    elif "S_AMNC" in relations:
        from_part = "from_trapezoid"
        s_amnc = _parse_value(relations["S_AMNC"])
        s_mbn = s_amnc / 3
        s_abc = s_amnc * 4 / 3
    else:
        raise ValueError("midpoints_solver: не найдена известная площадь в given.relations")

    # --- 2. ФОРМИРУЕМ NARRATIVE ИЗ ДВУХ ЧАСТЕЙ ---
    to_part = {
        "S_ABC": "find_big_triangle",
        "S_MBN": "find_small_triangle",
        "S_AMNC": "find_trapezoid"
    }.get(to_find_name)

    if not from_part or not to_part:
        raise ValueError("midpoints_solver: не удалось определить from/to части narrative")

    final_narrative = f"{from_part}:{to_part}"

    # --- 3. Формируем контекст для Humanizer'а ---
    context = {
        "res": task.get("answer"),
        "s_abc_val": format_number(s_abc),
        "s_mbn_val": format_number(s_mbn),
        "s_amnc_val": format_number(s_amnc),
        "to_find_name_human": to_find_name.replace("_", "(") + ")",
    }

    # --- 4. Возвращаем solution_core ---
    return [{
        # Используем ПОЛНЫЙ, составной narrative
        "action": f"{task.get('pattern')}:{final_narrative}",
        "data": context
    }]

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
