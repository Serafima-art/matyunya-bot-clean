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
}

STEP_TEMPLATES: Dict[str, str] = {
    # --- cyclic_quad_angles ---
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

    # --- central_inscribed ---
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


_CONTEXT_BUILDERS: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
    "opposite_sum": _ctx_opposite_sum,
    "part_sum": _ctx_part_sum,
    "part_diff": _ctx_part_diff,
    "find_inscribed_by_central": _ctx_central_inscribed,
    "find_central_by_inscribed": _ctx_central_inscribed,
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

    tips_key = profile.get("tips_key", "common")
    tips_text = TIPS_TEMPLATES.get(tips_key, TIPS_TEMPLATES["common"])
    if tips_key == "arc_hint":
        tips_text = f"{TIPS_TEMPLATES['arc_hint']}\n{TIPS_TEMPLATES['common']}"

    parts.append(f"\n\n✨ <b>Полезно знать</b>\n{tips_text}")

    return "\n".join(parts)
