# matunya_bot_final/help_core/humanizers/template_humanizers/task_16_humanizer.py
# -*- coding: utf-8 -*-

"""
Humanizer for Task 16
Pattern: cyclic_quad_angles
Theme: Центральные и вписанные углы
"""

from typing import Dict, List, Any

# =============================================================================
# 1. ШАБЛОНЫ ТЕКСТОВ (TEMPLATES)
# =============================================================================

IDEA_TEMPLATES: Dict[str, str] = {
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
}

STEP_TEMPLATES: Dict[str, str] = {
    # --- COMMON ---
    "STEP_GIVEN_FIND": (
        "<b>Шаг 1.</b> Условие задачи.\n"
        "Дано: <b>{given_text}</b>.\n"
        "Найти: <b>{target_text}</b>."
    ),

    # --- opposite_sum ---
    "STEP_OPPOSITE_RULE": (
        "<b>Шаг 2.</b> Вспомним главное свойство.\n"
        "Сумма противоположных углов вписанного четырёхугольника равна <b>180°</b>.\n"
        "Углы <b>{given} и {target}</b> лежат друг напротив друга, значит:\n"
        "➡️ <b>∠{given} + ∠{target} = 180°</b>"
    ),
    "STEP_OPPOSITE_CALC": (
        "<b>Шаг 3.</b> Выразим неизвестный угол и посчитаем.\n"
        # ДОБАВИЛИ: Сначала формула буквами (∠C = 180° - ∠A)
        "➡️ <b>∠{target} = 180° − ∠{given} = 180° − {given_val}° = {answer}°</b>"
    ),

    # --- part_sum ---
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

    # --- part_diff ---
    "STEP_EQUAL_ARC_SIMPLE": (
        "<b>Шаг 2.</b> Найдём равные углы.\n"
        "<b>∠{alien}</b> и <b>∠{parasite}</b> "
        "опираются на одну и ту же дугу <b>{arc}</b>.\n"
        "Значит, они равны:\n"
        "➡️ <b>∠{parasite} = ∠{alien} = {alien_val}°</b>"
    ),
    "STEP_WHOLE_COMPOSITION": (
        # НОВЫЙ ШАГ для соответствия эталону (Шаг 3)
        "<b>Шаг 3.</b> Разложим большой угол.\n"
        "<b>∠{whole}</b> состоит из двух частей:\n"
        "➡️ <b>∠{whole} = ∠{target} + ∠{parasite}</b>"
    ),
    "STEP_DIFF_CALC": (
        "<b>Шаг 4.</b> Найдём искомый угол.\n"
        "➡️ <b>∠{target} = ∠{whole} − ∠{parasite} = "
        "{whole_val}° − {alien_val}° = {answer}°</b>"
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
    )
}

NARRATIVE_PROFILES: Dict[str, Dict[str, Any]] = {
    "opposite_sum": {
        "steps": ["STEP_GIVEN_FIND", "STEP_OPPOSITE_RULE", "STEP_OPPOSITE_CALC"],
        "tips_key": "common"
    },
    "part_sum": {
        "steps": ["STEP_GIVEN_FIND", "STEP_SPLIT_ANGLE", "STEP_EQUAL_ARC", "STEP_SUM_CALC"],
        "tips_key": "arc_hint"
    },
    "part_diff": {
        # Теперь здесь 4 шага, как в эталоне
        "steps": ["STEP_GIVEN_FIND", "STEP_EQUAL_ARC_SIMPLE", "STEP_WHOLE_COMPOSITION", "STEP_DIFF_CALC"],
        "tips_key": "arc_hint"
    },
}


# =============================================================================
# 2. ЛОГИКА (LOGIC LAYER)
# =============================================================================

def humanize(solution_core: Dict[str, Any]) -> str:
    """
    Главная функция. Собирает текст решения по профилю.
    """
    full_idea_key = solution_core.get("explanation_idea", "")

    if full_idea_key == "IDEA_ERROR":
        return f"🔴 Ошибка генерации решения: {solution_core.get('variables', {}).get('error_reason')}"
    if full_idea_key.startswith("IDEA_TODO"):
        return f"🛠 Решение для этого типа задач пока в разработке."

    narrative_key = full_idea_key.replace("IDEA_", "").lower()
    raw_vars = solution_core.get("variables", {})

    profile = NARRATIVE_PROFILES.get(narrative_key)
    if not profile:
        return f"🔴 Ошибка: Не найден шаблон для типа '{narrative_key}'"

    # --- ПОДГОТОВКА КОНТЕКСТА ---
    context = raw_vars.copy()
    context["answer"] = raw_vars.get("answer")

    if narrative_key == "opposite_sum":
        given = raw_vars.get("angle_given_name")
        val = raw_vars.get("angle_given_val")
        target = raw_vars.get("angle_target_name")

        context["given"] = given
        context["given_val"] = val
        context["target"] = target
        context["given_text"] = f"Четырёхугольник вписан в окружность, ∠{given} = {val}°"
        context["target_text"] = f"∠{target}"

    elif narrative_key == "part_sum":
        whole = raw_vars.get("angle_whole_name")
        known = raw_vars.get("angle_known_part_name")
        known_val = raw_vars.get("angle_known_part_val")
        alien = raw_vars.get("angle_alien_name")
        alien_val = raw_vars.get("angle_alien_val")

        context["whole"] = whole
        context["part_known"] = known
        context["known_val"] = known_val
        context["alien"] = alien
        context["alien_val"] = alien_val
        context["part_hidden"] = raw_vars.get("angle_hidden_part_name")
        context["arc"] = raw_vars.get("arc_name")

        context["given_text"] = f"Четырёхугольник вписан в окружность, ∠{known} = {known_val}°, ∠{alien} = {alien_val}°"
        context["target_text"] = f"∠{whole}"

    elif narrative_key == "part_diff":
        target = raw_vars.get("angle_target_name")
        whole = raw_vars.get("angle_whole_name")
        whole_val = raw_vars.get("angle_whole_val")
        alien = raw_vars.get("angle_alien_name")
        alien_val = raw_vars.get("angle_alien_val")

        context["target"] = target
        context["whole"] = whole
        context["whole_val"] = whole_val
        context["alien"] = alien
        context["alien_val"] = alien_val
        context["parasite"] = raw_vars.get("angle_parasite_name")
        context["arc"] = raw_vars.get("arc_name")

        context["given_text"] = f"Четырёхугольник вписан в окружность, ∠{whole} = {whole_val}°, ∠{alien} = {alien_val}°"
        context["target_text"] = f"∠{target}"

    # --- СБОРКА ТЕКСТА ---
    parts = []

    idea_text = IDEA_TEMPLATES.get(narrative_key)
    if idea_text:
        parts.append(f"💡 <b>Идея решения</b>\n{idea_text}")

    parts.append("\n🪜 <b>Пошаговое решение</b>")

    for step_name in profile["steps"]:
        template = STEP_TEMPLATES.get(step_name)
        if template:
            try:
                parts.append(f"\n{template.format(**context)}")
            except KeyError as e:
                parts.append(f"\n⚠️ Ошибка шаблона: не найдена переменная {e}")

    parts.append(f"\n🎯 Ответ: <b>{context['answer']}</b>.")

    tips_key = profile.get("tips_key", "common")
    tips_text = TIPS_TEMPLATES["common"]
    if tips_key == "arc_hint":
        tips_text = f"{TIPS_TEMPLATES['arc_hint']}\n{tips_text}"

    parts.append(f"\n\n✨ <b>Полезно знать</b>\n{tips_text}")

    return "\n".join(parts)
