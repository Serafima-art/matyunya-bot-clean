# matunya_bot_final/help_core/humanizers/template_humanizers/task_16_humanizer.py
# -*- coding: utf-8 -*-

"""
Humanizer for Task 16
Theme: Центральные и вписанные углы
Patterns:
- cyclic_quad_angles
- central_inscribed
"""

from typing import Dict, Any, Callable, Optional

from matunya_bot_final.utils.number_formatter import format_oge_number

# =============================================================================
# 1. ШАБЛОНЫ ТЕКСТОВ (TEMPLATES) — НЕ МЕНЯЕМ ФОРМУЛИРОВКИ
# =============================================================================

IDEA_TEMPLATES: Dict[str, str] = {
    # ------------------------------------------------------------------
    # # 🟩 ТЕМА 1. Центральные и вписанные углы (central_and_inscribed_angles)
    # ------------------------------------------------------------------

    # --- cyclic_quad_angles ---
    "opposite_sum": (
        "В любом четырёхугольнике, который вписан в окружность, "
        "сумма противоположных углов всегда равна <b>180°</b>. "
        "Зная один угол, мы легко найдём тот, что напротив."
    ),
    "part_sum": (
        "Искомый угол состоит из двух частей. "
        "Одну часть мы знаем, а вторую (недостающую) найдём через свойство вписанных углов: "
        "углы, опирающиеся на одну и ту же дугу, равны."
    ),
    "part_diff": (
        "Мы знаем весь угол и знаем «чужой» угол, который равен одной из его частей. "
        "Чтобы найти нужный угол, нужно <b>из целого вычесть известную часть</b>."
    ),
    # --- central_inscribed ---
    "find_inscribed_by_central": (
        "Вписанный угол и центральный угол опираются на одну и ту же дугу.\n"
        "В таком случае вписанный угол (вершина на окружности) всегда "
        "<b>в 2 раза меньше</b> центрального (вершина в центре окружности)."
    ),
    "find_central_by_inscribed": (
        "Центральный и вписанный углы опираются на одну и ту же дугу.\n"
        "В этом случае центральный угол <b>в 2 раза больше</b> вписанного."
    ),
    # --- radius_chord_angles ---
    "find_part_angle": (
        "Радиус, проведённый из центра окружности к вершине угла, "
        "разбивает этот угол на две части.\n"
        "Каждая часть находится через равнобедренный треугольник, "
        "а зная весь угол и одну часть, можно найти вторую."
    ),
    "find_whole_angle": (
        "Искомый угол разбит радиусом на два маленьких угла.\n"
        "Мы не знаем их сразу, но можем найти их через свойства "
        "равнобедренных треугольников (ведь радиусы равны).\n"
        "Затем просто сложим найденные части."
    ),
    # --- arc_length_ratio ---
    "small_to_large_arc": (
        "Длина дуги прямо пропорциональна её градусной мере.\n"
        "Это значит: <b>какую долю от 360° занимает угол, "
        "такую же долю от всей окружности занимает длина дуги</b>.\n"
        "Нам не нужно искать радиус! Достаточно составить пропорцию."
    ),
}

STEP_TEMPLATES: Dict[str, str] = {
    # ------------------------------------------------------------------
    # cyclic_quad_angles
    # ------------------------------------------------------------------
    "STEP_GIVEN_FIND": (
        "<b>Шаг 1.</b> Условие задачи.\n"
        "Дано: <b>{given_text}</b>.\n"
        "Найти: <b>{target_text}</b>."
    ),

    "STEP_OPPOSITE_RULE": (
        "<b>Шаг 2.</b> Вспомним главное свойство.\n"
        "Сумма противоположных углов вписанного четырёхугольника равна <b>180°</b>.\n"
        "Углы <b>{given} и {target}</b> лежат друг напротив друга, значит:\n"
        "➡️ <b>∠{given} + ∠{target} = 180°</b>"
    ),
    "STEP_OPPOSITE_CALC": (
        "<b>Шаг 3.</b> Выразим неизвестный угол и посчитаем.\n"
        "➡️ <b>∠{target} = 180° − ∠{given} = 180° − {given_val}° = {answer}°</b>"
    ),

    "STEP_SPLIT_ANGLE": (
        "<b>Шаг 2.</b> Разберём угол на части.\n"
        "Весь угол <b>∠{whole}</b> складывается из двух углов:\n"
        "➡️ <b>∠{whole} = ∠{part_known} + ∠{part_hidden}</b>"
    ),
    "STEP_EQUAL_ARC": (
        "<b>Шаг 3.</b> Найдём недостающую часть.\n"
        "Посмотри на рисунок, углы <b>∠{part_hidden} и ∠{alien}</b> "
        "опираются на одну и ту же дугу <b>{arc}</b>, значит они равны:\n"
        "➡️ <b>∠{part_hidden} = ∠{alien} = {alien_val}°</b>."
    ),
    "STEP_SUM_CALC": (
        "<b>Шаг 4.</b> Сложим части.\n"
        "➡️ <b>∠{whole} = {known_val}° + {alien_val}° = {answer}°</b>"
    ),

    "STEP_EQUAL_ARC_SIMPLE": (
        "<b>Шаг 2.</b> Найдём равные углы.\n"
        "<b>∠{alien}</b> и <b>∠{parasite}</b> "
        "опираются на одну и ту же дугу <b>{arc}</b>.\n"
        "Значит, они равны:\n"
        "➡️ <b>∠{parasite} = ∠{alien} = {alien_val}°</b>"
    ),
    "STEP_WHOLE_COMPOSITION": (
        "<b>Шаг 3.</b> Разложим большой угол.\n"
        "<b>∠{whole}</b> состоит из двух частей:\n"
        "➡️ <b>∠{whole} = ∠{target} + ∠{parasite}</b>"
    ),
    "STEP_DIFF_CALC": (
        "<b>Шаг 4.</b> Найдём искомый угол.\n"
        "➡️ <b>∠{target} = ∠{whole} − ∠{parasite} = "
        "{whole_val}° − {alien_val}° = {answer}°</b>"
    ),

    # ------------------------------------------------------------------
    # central_inscribed
    # ------------------------------------------------------------------

    "STEP_CI_GIVEN_FIND": (
        "<b>Шаг 1.</b> Условие задачи.\n"
        "Дано: <b>{given_text}</b>.\n"
        "Найти: <b>{target_text}</b>."
    ),

    "STEP_CI_RULE_HALF": (
        "<b>Шаг 2.</b> Оба угла опираются на одну и ту же дугу <b>{arc}</b>.\n"
        "По теореме о вписанном угле:\n"
        "Вписанный угол равен половине центрального.\n"
        "➡️ <b>∠{target} = ∠{given} : 2</b>"
    ),

    "STEP_CI_RULE_DOUBLE": (
        "<b>Шаг 2.</b> Оба угла опираются на одну и ту же дугу <b>{arc}</b>.\n"
        "Центральный угол в 2 раза больше вписанного.\n"
        "➡️ <b>∠{target} = 2 · ∠{given}</b>"
    ),

    "STEP_CI_CALC_DIV": (
        "<b>Шаг 3.</b> Вычислим неизвестный угол.\n"
        "➡️ <b>∠{target} = {given_val}° : 2 = {answer}°</b>"
    ),

    "STEP_CI_CALC_MUL": (
        "<b>Шаг 3.</b> Вычислим неизвестный угол.\n"
        "➡️ <b>∠{target} = 2 · {given_val}° = {answer}°</b>"
    ),

    # ------------------------------------------------------------------
    # radius_chord_angles
    # ------------------------------------------------------------------

    "STEP_RADIUS_GIVEN_FIND": (
        "<b>Шаг 1.</b> Условие задачи.\n"
        "Дано: <b>{given_text}</b>.\n"
        "Найти: <b>{target_text}</b>."
    ),

    "STEP_RADIUS_TRIANGLES": (
        "<b>Шаг 2.</b> Соединим центр <b>O</b> с точкой <b>{vertex}</b>.\n"
        "Мы получили два треугольника: <b>Δ{iso_tri_1}</b> и <b>Δ{iso_tri_2}</b>.\n"
        "Так как их стороны — это радиусы окружности, то они равны\n"
        "(<b>{radii_equality}</b>).\n"
        "Значит, эти треугольники — <b>равнобедренные</b>."
    ),

    # --- find_part_angle ---
    "STEP_RADIUS_WHOLE_SUM": (
        "<b>Шаг 3.</b> Угол <b>∠{whole}</b> состоит из двух частей:\n"
        "➡️ <b>∠{whole} = ∠{known_base_name} + ∠{target_base_name}</b>"
    ),

    "STEP_RADIUS_ISO_PROPS": (
        "<b>Шаг 4.</b> В равнобедренном треугольнике углы при основании равны.\n"
        "➡️ <b>∠{known_base_name} = ∠{known} = {known_val}°</b>\n"
        "➡️ <b>∠{target_base_name} = ∠{target}</b> (это угол, который ищем)"
    ),

     "STEP_RADIUS_SUBSTITUTION": (
        "<b>Шаг 5.</b> Заменим в формуле углы на им равные:\n"
        "➡️ <b>∠{whole} = ∠{known} + ∠{target}</b>\n"
        "Значит:\n"
        "➡️ <b>∠{target} = ∠{whole} − ∠{known}</b>"
    ),

    "STEP_RADIUS_FINAL_CALC": (
        "<b>Шаг 6.</b> Выполним вычисление.\n"
        "➡️ <b>∠{target} = {whole_val}° − {known_val}° = {answer}°</b>"
    ),

    # --- find_whole_angle ---

    "STEP_RADIUS_EQUAL_BASE_DOUBLE": (
        "<b>Шаг 3.</b> В равнобедренных треугольниках углы при основании равны:\n"
        "➡️ <b>∠{equal1_left} = ∠{equal1_right} = {equal1_val}°</b>\n"
        "➡️ <b>∠{equal2_left} = ∠{equal2_right} = {equal2_val}°</b>"
    ),

    "STEP_RADIUS_SUM_CALC": (
        "<b>Шаг 4.</b> Угол <b>∠{target}</b> состоит из суммы двух углов:\n"
        "➡️ <b>∠{target} = ∠{part1_base_name} + ∠{part2_base_name}</b>\n\n"
        "Заменим в формуле углы на им равные и вычислим:\n"
        "➡️ <b>∠{target} = ∠{part1} + ∠{part2}</b>\n"
        "➡️ <b>∠{target} = {part1_val}° + {part2_val}° = {answer}°</b>."
    ),

    # ------------------------------------------------------------------
    # arc_length_ratio
    # ------------------------------------------------------------------

    # --- small_to_large_arc ---
    "STEP_ARC_GIVEN_FIND": (
        "<b>Шаг 1.</b> Условие задачи.\n"
        "Дано: <b>Длина меньшей дуги {arc} = {small_len}, "
        "центральный угол равен {small_angle}°</b>.\n"
        "Найти: <b>Длину большей дуги {arc}</b>."
    ),

    "STEP_ARC_FIND_LARGE_ANGLE": (
        "<b>Шаг 2.</b> Найдём градусную меру большей дуги.\n"
        "Вся окружность — это <b>360°</b>.\n"
        "Меньшая дуга занимает <b>{small_angle}°</b>.\n"
        "Значит, на большую дугу остаётся:\n"
        "➡️ <b>360° − {small_angle}° = {large_angle}°</b>"
    ),

    "STEP_ARC_RATIO": (
        "<b>Шаг 3.</b> Составим пропорцию.\n"
        "Длины дуг относятся так же, как и их углы.\n"
        "Пусть x — длина большей дуги.\n\n"
        "➡️ Длина меньшей / Угол меньшей = Длина большей / Угол большей\n\n"
        "Подставим числа и перемножим крест-накрест:\n"
        "➡️ <b>{small_len}/{small_angle} = x/{large_angle}</b>\n"
        "➡️ <b>{large_angle} · {small_len} = {small_angle}x</b>\n\n"
        "Выразим x:\n"
        "➡️ <b>x = ({small_len} · {large_angle})/{small_angle}</b>"
    ),

    "STEP_ARC_FINAL_CALC": (
        "<b>Шаг 4.</b> Вычислим ответ.\n"
        "Чтобы не получать большие числа, сначала <b>сократим дробь</b> в выражении:\n"
        "➡️ <b>x = ({small_arc_length} · {large_arc_angle}) / {small_arc_angle}</b>\n\n"
        "Сокращай по шагам:\n"
        "1) сократи <b>{small_arc_length}</b> и <b>{small_arc_angle}</b>, если можно;\n"
        "2) затем сократи <b>{large_arc_angle}</b> и то, что осталось в знаменателе.\n\n"
        "После сокращения перемножить числа уже легко:\n"
        "➡️ <b>x = {final_calc}</b>"
    ),
}

TIPS_TEMPLATES: Dict[str, str] = {
    "common": (
        "❗️ В бланке ОГЭ в ответ записывай только число без значка градусов."
    ),
    "arc_hint": (
        "Посмотри на чертёж и найди фигуру, похожую на «бантик» (или «бабочку») — "
        "это две пересекающиеся диагонали.\n"
        "Углы, которые «смотрят» на одну и ту же дугу окружности в таком бантике, всегда равны.\n"
    ),

    # ------------------------------------------------------------------
    # central_inscribed
    # ------------------------------------------------------------------
    "central_inscribed_boss": (
        "🧠 Запомни:\n"
        "центральный угол (вершина в центре окружности) — это босс,\n"
        "а вписанный угол (вершина на окружности) — его подчинённый.\n\n"
        "👔 Босс всегда главнее:\n"
        "он ВСЕГДА ❗️ в 2 раза больше подчинённого,\n"
        "если оба угла опираются на одну и ту же дугу.\n\n"
        "📌 Поэтому:\n"
        "ищем вписанный → делим на 2\n"
        "ищем центральный → умножаем на 2\n\n"
        "❗️В бланке ОГЭ в ответ записывай только число, без значка градусов."
    ),
    # ------------------------------------------------------------------
    # radius_chord_angles
    # ------------------------------------------------------------------
    "radius_find_part_angle": (
        "Если радиус соединяет центр окружности с вершиной угла,\n"
        "то этот угол можно рассматривать как сумму двух частей.\n"
        "Каждая часть находится через равнобедренный треугольник.\n\n"
        "Зная весь угол и одну часть, вторую часть\n"
        "находим вычитанием."
    ),

    "radius_find_whole_angle": (
        "Радиус, проведённый из центра окружности к вершине угла,\n"
        "делит этот угол на две части.\n\n"
        "Чтобы найти весь угол,\n"
        "нужно сложить эти две части."
    ),
    # ------------------------------------------------------------------
    # arc_length_ratio
    # ------------------------------------------------------------------
    "small_to_large_arc": (
        "🍕 Представь, что окружность — это пицца.\n"
        "Правило простое: \n"
        "<b>«Корочка» (длина дуги) зависит только от угла куска.</b>.\n\n"
        "Чтобы не искать радиус, используй формулу связи: \n"
        "➡️ <b>Длина большей = Длина меньшей · (Угол больший / Угол меньший)</b>\n\n"
    ),
}

# =============================================================================
# 2. ПРОФИЛИ НАРРАТИВОВ (канон)
# =============================================================================

NARRATIVE_PROFILES: Dict[str, Dict[str, Any]] = {
    # --- cyclic_quad_angles ---
    "opposite_sum": {
        "steps": ["STEP_GIVEN_FIND", "STEP_OPPOSITE_RULE", "STEP_OPPOSITE_CALC"],
        "tips_key": "common",
        "required_fields": ["angle_given_name", "angle_given_val", "angle_target_name"],
    },
    "part_sum": {
        "steps": ["STEP_GIVEN_FIND", "STEP_SPLIT_ANGLE", "STEP_EQUAL_ARC", "STEP_SUM_CALC"],
        "tips_key": "arc_hint",
        "required_fields": [
            "angle_whole_name",
            "angle_known_part_name",
            "angle_known_part_val",
            "angle_hidden_part_name",
            "angle_alien_name",
            "angle_alien_val",
            "arc_name",
        ],
    },
    "part_diff": {
        "steps": ["STEP_GIVEN_FIND", "STEP_EQUAL_ARC_SIMPLE", "STEP_WHOLE_COMPOSITION", "STEP_DIFF_CALC"],
        "tips_key": "arc_hint",
        "required_fields": [
            "angle_target_name",
            "angle_whole_name",
            "angle_whole_val",
            "angle_alien_name",
            "angle_alien_val",
            "angle_parasite_name",
            "arc_name",
        ],
    },

    # --- central_inscribed ---
    "find_inscribed_by_central": {
        "steps": ["STEP_CI_GIVEN_FIND", "STEP_CI_RULE_HALF", "STEP_CI_CALC_DIV"],
        "tips_key": "central_inscribed_boss",
        "required_fields": ["angle_given_name", "angle_given_val", "angle_target_name", "arc_name"],
    },
    "find_central_by_inscribed": {
        "steps": ["STEP_CI_GIVEN_FIND", "STEP_CI_RULE_DOUBLE", "STEP_CI_CALC_MUL"],
        "tips_key": "central_inscribed_boss",
        "required_fields": ["angle_given_name", "angle_given_val", "angle_target_name", "arc_name"],
    },

    # --- radius_chord_angles ---
    "find_part_angle": {
        "steps": [
            "STEP_GIVEN_FIND",
            "STEP_RADIUS_TRIANGLES", # Шаг 2
            "STEP_RADIUS_WHOLE_SUM",
            "STEP_RADIUS_ISO_PROPS",
            "STEP_RADIUS_SUBSTITUTION",
            "STEP_RADIUS_FINAL_CALC"
        ],
        # ВНИМАНИЕ: Исправлен ключ на тот, что есть в словаре TIPS_TEMPLATES
        "tips_key": "radius_find_part_angle"
    },

    "find_whole_angle": {
        "steps": [
            "STEP_RADIUS_GIVEN_FIND",
            "STEP_RADIUS_TRIANGLES",
            "STEP_RADIUS_EQUAL_BASE_DOUBLE",
            "STEP_RADIUS_SUM_CALC",
        ],
        "tips_key": "radius_find_whole_angle",
    },

    # --- arc_length_ratio ---
    "small_to_large_arc": {
        "steps": [
            "STEP_ARC_GIVEN_FIND",
            "STEP_ARC_FIND_LARGE_ANGLE",
            "STEP_ARC_RATIO",
            "STEP_ARC_FINAL_CALC",
        ],
        "tips_key": "small_to_large_arc",
        "required_fields": [
            "arc_name",
            "small_arc_length",
            "small_arc_angle",
            "large_arc_angle",
        ],
    },
}

# =============================================================================
# 3. КОНТЕКСТ-БИЛДЕРЫ (facts -> context) — без legacy-логики
# =============================================================================

def _require_fields(narrative_key: str, raw_vars: Dict[str, Any]) -> Optional[str]:
    profile = NARRATIVE_PROFILES.get(narrative_key)
    if not profile:
        return f"🔴 Ошибка: Не найден шаблон для типа '{narrative_key}'"

    missing = []
    for k in profile.get("required_fields", []):
        if raw_vars.get(k) is None:
            missing.append(k)

    if missing:
        return f"🔴 Ошибка: не хватает данных для '{narrative_key}': {', '.join(missing)}"
    return None


def _base_context(raw_vars: Dict[str, Any]) -> Dict[str, Any]:
    # Общие поля: answer всегда форматируем красиво
    ctx = dict(raw_vars)
    ctx["answer"] = format_oge_number(raw_vars.get("answer"))
    return ctx


def _ctx_opposite_sum(raw_vars: Dict[str, Any]) -> Dict[str, Any]:
    ctx = _base_context(raw_vars)
    given = raw_vars.get("angle_given_name")
    given_val = format_oge_number(raw_vars.get("angle_given_val"))
    target = raw_vars.get("angle_target_name")

    ctx.update(
        given=given,
        given_val=given_val,
        target=target,
        given_text=f"Четырёхугольник вписан в окружность, ∠{given} = {given_val}°",
        target_text=f"∠{target}",
    )
    return ctx


def _ctx_part_sum(raw_vars: Dict[str, Any]) -> Dict[str, Any]:
    ctx = _base_context(raw_vars)

    whole = raw_vars.get("angle_whole_name")
    part_known = raw_vars.get("angle_known_part_name")
    known_val = format_oge_number(raw_vars.get("angle_known_part_val"))
    alien = raw_vars.get("angle_alien_name")
    alien_val = format_oge_number(raw_vars.get("angle_alien_val"))
    part_hidden = raw_vars.get("angle_hidden_part_name")
    arc = raw_vars.get("arc_name")

    ctx.update(
        whole=whole,
        part_known=part_known,
        known_val=known_val,
        alien=alien,
        alien_val=alien_val,
        part_hidden=part_hidden,
        arc=arc,
        given_text=(
            f"Четырёхугольник вписан в окружность, "
            f"∠{part_known} = {known_val}°, ∠{alien} = {alien_val}°"
        ),
        target_text=f"∠{whole}",
    )
    return ctx


def _ctx_part_diff(raw_vars: Dict[str, Any]) -> Dict[str, Any]:
    ctx = _base_context(raw_vars)

    target = raw_vars.get("angle_target_name")
    whole = raw_vars.get("angle_whole_name")
    whole_val = format_oge_number(raw_vars.get("angle_whole_val"))
    alien = raw_vars.get("angle_alien_name")
    alien_val = format_oge_number(raw_vars.get("angle_alien_val"))
    parasite = raw_vars.get("angle_parasite_name")
    arc = raw_vars.get("arc_name")

    ctx.update(
        target=target,
        whole=whole,
        whole_val=whole_val,
        alien=alien,
        alien_val=alien_val,
        parasite=parasite,
        arc=arc,
        given_text=(
            f"Четырёхугольник вписан в окружность, "
            f"∠{whole} = {whole_val}°, ∠{alien} = {alien_val}°"
        ),
        target_text=f"∠{target}",
    )
    return ctx


def _ctx_central_inscribed(raw_vars: Dict[str, Any]) -> Dict[str, Any]:
    """
    ✅ НОВЫЙ КАНОН: central_inscribed работает с универсальными фактами:
    angle_given_name / angle_given_val / angle_target_name / arc_name
    (solver уже нормализовал к двум нарративам)
    """
    ctx = _base_context(raw_vars)

    given = raw_vars.get("angle_given_name")
    given_val = format_oge_number(raw_vars.get("angle_given_val"))
    target = raw_vars.get("angle_target_name")
    arc = raw_vars.get("arc_name")

    # Формулировки Шага 1 оставляем прежними — это просто подстановка данных.
    ctx.update(
        given=given,
        given_val=given_val,
        target=target,
        arc=arc,
        given_text=f"в окружность с центром в точке O вписан треугольник, ∠{given} = {given_val}°",
        target_text=f"∠{target}",
    )
    return ctx


def _ctx_radius_find_part(raw_vars: Dict[str, Any]) -> Dict[str, Any]:
    ctx = _base_context(raw_vars)

    known_name = raw_vars["angle_known_part_name"]  # OAB
    target_name = raw_vars["angle_target_name"]      # BCO
    whole_name = raw_vars["angle_whole_name"]        # ABC

    # 1. Определяем Главную Вершину (середина целого угла)
    # Если ABC, то B. Если MNK, то N.
    vertex = whole_name[1] if len(whole_name) > 1 else "B"

    # 2. Формируем строку равенства радиусов (OA = OB = OC)
    p1, p2, p3 = whole_name[0], whole_name[1], whole_name[2]
    radii_equality = f"O{p1} = O{p2} = O{p3}"

    # 3. Функция для правильного имени угла при основании (O + Vertex + Other)
    def make_base_name(angle_name, vert):
        # Удаляем O и Vertex, остается третья буква
        chars = list(angle_name)
        if "O" in chars: chars.remove("O")
        if vert in chars: chars.remove(vert)
        other = chars[0] if chars else ""
        return f"O{vert}{other}"

    # 4. Генерируем правильные имена
    known_base_name = make_base_name(known_name, vertex)   # OAB -> OBA
    target_base_name = make_base_name(target_name, vertex) # BCO -> OBC

    # 5. Имена треугольников (AOB, BOC)
    # Берем "Other" из base_name (последняя буква)
    iso_tri_1 = f"{known_base_name[-1]}O{vertex}"
    iso_tri_2 = f"{target_base_name[-1]}O{vertex}"

    ctx.update(
        whole=whole_name,
        whole_val=format_oge_number(raw_vars["angle_whole_val"]),

        known_part=known_name, # Как в условии
        known=known_name,
        known_val=format_oge_number(raw_vars["angle_known_part_val"]),

        target=target_name, # Как в условии
        target_name=target_name,

        # Сгенерированные ПРАВИЛЬНЫЕ имена для решения
        known_base_name=known_base_name,
        target_base_name=target_base_name,

        iso_tri_1=iso_tri_1,
        iso_tri_2=iso_tri_2,
        vertex=vertex,
        radii_equality=radii_equality,

        given_text=(
            f"∠{raw_vars['angle_whole_name']} = "
            f"{format_oge_number(raw_vars['angle_whole_val'])}°, "
            f"∠{raw_vars['angle_known_part_name']} = "
            f"{format_oge_number(raw_vars['angle_known_part_val'])}°"
        ),
        target_text=f"∠{raw_vars['angle_target_name']}",
    )
    return ctx

def _ctx_radius_find_whole(raw_vars: Dict[str, Any]) -> Dict[str, Any]:
    ctx = _base_context(raw_vars)

    part1 = raw_vars["angle_part1_name"] # OAB
    part2 = raw_vars["angle_part2_name"] # BCO
    target = raw_vars["angle_target_name"] # ABC

    # 1. Вершина (B)
    vertex = target[1] if len(target) > 1 else "B"

    # 2. Радиусы
    p1, p2, p3 = target[0], target[1], target[2]
    radii_equality = f"O{p1} = O{p2} = O{p3}"

    # 3. Функция-помощник (строит имя угла при вершине: O + Vertex + Other)
    def make_base_name(angle_name, vert):
        chars = list(angle_name)
        if "O" in chars: chars.remove("O")
        if vert in chars: chars.remove(vert)
        other = chars[0] if chars else ""
        return f"O{vert}{other}"

    # 4. Генерируем имена
    # part1 (OAB) -> base1 (OBA)
    base1 = make_base_name(part1, vertex)
    # part2 (BCO) -> base2 (OBC)
    base2 = make_base_name(part2, vertex)

    # Имена треугольников (AOB, BOC)
    tri1_display = f"{base1[-1]}O{vertex}"
    tri2_display = f"{base2[-1]}O{vertex}"

    ctx.update(
        part1=part1,
        part1_val=format_oge_number(raw_vars["angle_part1_val"]),

        part2=part2,
        part2_val=format_oge_number(raw_vars["angle_part2_val"]),

        target=target,

        # Переменные для шагов
        vertex=vertex,
        radii_equality=radii_equality,
        iso_tri_1=tri1_display,
        iso_tri_2=tri2_display,

        # Углы при основании (для формулы суммы)
        part1_base_name=base1,
        part2_base_name=base2,

        # Для шага с равенством (Слева база = Справа известно)
        equal1_left=base1,
        equal1_right=part1,
        equal1_val=format_oge_number(raw_vars["angle_part1_val"]),

        equal2_left=base2,
        equal2_right=part2,
        equal2_val=format_oge_number(raw_vars["angle_part2_val"]),

        given_text=(
            f"∠{part1} = {format_oge_number(raw_vars['angle_part1_val'])}°, "
            f"∠{part2} = {format_oge_number(raw_vars['angle_part2_val'])}°"
        ),
        target_text=f"∠{target}",
    )
    return ctx

def _ctx_arc_length_ratio(raw_vars: Dict[str, Any]) -> Dict[str, Any]:
    ctx = _base_context(raw_vars)

    ctx.update(
        arc=raw_vars.get("arc_name"),
        small_len=format_oge_number(raw_vars.get("small_arc_length")),
        small_angle=format_oge_number(raw_vars.get("small_arc_angle")),
        large_angle=format_oge_number(raw_vars.get("large_arc_angle")),
    )

    # --- финальное вычисление (для STEP_ARC_FINAL_CALC) ---
    a = raw_vars.get("small_arc_length")
    b = raw_vars.get("large_arc_angle")
    c = raw_vars.get("small_arc_angle")

    # строка для ученика: показываем КАК считать, а не считаем здесь
    ctx["final_calc"] = f"({a} · {b}) / {c}"

    return ctx

_CONTEXT_BUILDERS: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
    "opposite_sum": _ctx_opposite_sum,
    "part_sum": _ctx_part_sum,
    "part_diff": _ctx_part_diff,
    "find_inscribed_by_central": _ctx_central_inscribed,
    "find_central_by_inscribed": _ctx_central_inscribed,
    "find_part_angle": _ctx_radius_find_part,
    "find_whole_angle": _ctx_radius_find_whole,
    "small_to_large_arc": _ctx_arc_length_ratio,
}

# =============================================================================
# 4. ГЛАВНАЯ ФУНКЦИЯ (humanize) — без if-цепочек и без try/except
# =============================================================================

def humanize(solution_core: Dict[str, Any]) -> str:
    """
    Собирает текст решения строго по профилю narrative_key.
    Никаких догадок, никаких legacy-полей, никаких fallback-шаблонов.
    """

    full_idea_key = solution_core.get("explanation_idea", "") or ""

    if full_idea_key == "IDEA_ERROR":
        return f"🔴 Ошибка генерации решения: {solution_core.get('variables', {}).get('error_reason')}"
    if full_idea_key.startswith("IDEA_TODO"):
        return "🛠 Решение для этого типа задач пока в разработке."

    raw_vars: Dict[str, Any] = solution_core.get("variables", {}) or {}

    # ✅ Источник правды — narrative_type в facts.
    # Если по какой-то причине его нет, берём из explanation_idea.
    narrative_key = (raw_vars.get("narrative_type") or "").strip().lower()
    if not narrative_key:
        narrative_key = full_idea_key.replace("IDEA_", "").strip().lower()

    if narrative_key not in NARRATIVE_PROFILES:
        return f"🔴 Ошибка: Не найден шаблон для типа '{narrative_key}'"

    err = _require_fields(narrative_key, raw_vars)
    if err:
        return err

    builder = _CONTEXT_BUILDERS.get(narrative_key)
    if not builder:
        return f"🔴 Ошибка: Не найден context-builder для типа '{narrative_key}'"

    context = builder(raw_vars)

    profile = NARRATIVE_PROFILES[narrative_key]

    parts = []

    idea_text = IDEA_TEMPLATES.get(narrative_key)
    if idea_text:
        parts.append(f"💡 <b>Идея решения</b>\n{idea_text}")

    parts.append("\n🪜 <b>Пошаговое решение</b>")

    for step_name in profile["steps"]:
        template = STEP_TEMPLATES.get(step_name)
        if template:
            parts.append(f"\n{template.format(**context)}")

    parts.append(f"\n🎯 Ответ: <b>{context.get('answer')}</b>.")

    # Блок СОВЕТЫ (Универсальная логика)
    tips_key = profile.get("tips_key", "common")

    # Берем специфичный совет, если он есть, иначе общий
    specific_tip = TIPS_TEMPLATES.get(tips_key, TIPS_TEMPLATES["common"])

    # Если ключ не "common", значит это спец. совет -> добавляем к нему общий хвост
    if tips_key != "common":
        tips_text = f"{specific_tip}\n{TIPS_TEMPLATES['common']}"
    else:
        tips_text = specific_tip

    parts.append(f"\n\n✨ <b>Полезно знать</b>\n{tips_text}")

    return "\n".join(parts)
