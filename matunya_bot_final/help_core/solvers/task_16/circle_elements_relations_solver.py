# matunya_bot_final/help_core/solvers/task_16/circle_elements_relations_solver.py
# -*- coding: utf-8 -*-

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# =========================================================================
# ТЕМА 2: Касательная, хорда, секущая, радиус
# circle_elements_relations
# =========================================================================

async def solve(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Решатель для Темы 2: circle_elements_relations.

    Вход:
      task_data:
        - pattern
        - narrative
        - task_context
        - answer
        - id
        - image_file / help_image_file

    Выход:
      solution_core (facts-only, без анализа текста).
    """

    pattern = task_data.get("pattern")

    # ---------------------------------------------------------------------
    # Роутер по паттернам ТЕМЫ 2
    # ---------------------------------------------------------------------

    if pattern == "secant_similarity":
        return _solve_secant_similarity(task_data)

    if pattern == "tangent_trapezoid_properties":
        return _solve_tangent_trapezoid_properties(task_data)

    if pattern == "tangent_quad_sum":
        return _solve_tangent_quad_sum(task_data)

    if pattern == "tangent_arc_angle":
        return _solve_tangent_arc_angle(task_data)

    if pattern == "angle_tangency_center":
        return _solve_angle_tangency_center(task_data)

    if pattern == "sector_area":
        return _solve_sector_area(task_data)

    if pattern == "power_point":
        return _solve_power_point(task_data)

    logger.error("Unknown pattern for circle_elements_relations: %r", pattern)
    return _get_error_solution(task_data, reason=f"Unknown pattern: {pattern}")


# =============================================================================
# ПАТТЕРН 2.1: secant_similarity
# =============================================================================

def _solve_secant_similarity(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Паттерн 2.1: secant_similarity

    Канон:
    - Solver отдаёт ТОЛЬКО facts (никаких вычислений текста).
    - Humanizer НИЧЕГО не угадывает: пропорция и порядок дробей задаются solver'ом.
    - Для 4 нарративов:
        abcd_find_small / abcd_find_large
        prst_find_small / prst_find_large
    """

    context: Dict[str, Any] = task_data.get("task_context") or {}
    answer = task_data.get("answer")

    narrative_type = (context.get("narrative_type") or "").strip()

    # -----------------------------
    # 1) НОРМАЛИЗАЦИЯ НАРРАТИВА
    # -----------------------------
    allowed = {"abcd_find_small", "abcd_find_large", "prst_find_small", "prst_find_large"}
    if narrative_type not in allowed:
        narrative_type = "unknown"

    # -----------------------------
    # 2) ПРОПОРЦИЯ (источник правды)
    # -----------------------------
    # В эталоне:
    #   find_small:  short/long = target/known   (пример: BF/DF = BC/AD)
    #   find_large:  short/long = known/target   (пример: UR/UT = RS/PT)
    #
    # Чтобы humanizer не гадал, задаём явную "схему" и сразу нужные дроби:
    # ratio_left_num / ratio_left_den / ratio_right_num / ratio_right_den
    ratio_left_num = context.get("secant_segment_short_name")
    ratio_left_den = context.get("secant_segment_long_name")

    if narrative_type.endswith("find_small"):
        ratio_right_num = context.get("base_target_name")
        ratio_right_den = context.get("base_known_name")
        ratio_mode = "SHORT_LONG_EQ_TARGET_KNOWN"

        base_small_name = context.get("base_target_name")
        base_large_name = context.get("base_known_name")

    elif narrative_type.endswith("find_large"):
        ratio_right_num = context.get("base_known_name")
        ratio_right_den = context.get("base_target_name")
        ratio_mode = "SHORT_LONG_EQ_KNOWN_TARGET"

        base_small_name = context.get("base_known_name")
        base_large_name = context.get("base_target_name")

    else:
        base_small_name = None
        base_large_name = None

    # -----------------------------
    # 3) FACTS ONLY
    # -----------------------------
    facts: Dict[str, Any] = {
        "narrative_type": narrative_type,
        "answer": answer,

        # Геометрические якоря
        "intersection_point": context.get("intersection_point"),  # F / U
        "common_vertex": context.get("common_vertex"),            # F / U

        # Подобные треугольники (имена для вывода в шагах)
        "triangle_small_name": context.get("triangle_small_name"),  # FBC / URS
        "triangle_large_name": context.get("triangle_large_name"),  # FDA / UTP

        # Равные углы (для текста шага 2)
        "vertex_angle_small": context.get("vertex_angle_small"),  # B / R
        "vertex_angle_large": context.get("vertex_angle_large"),  # D / T

        # Секущие (имя и значение короткого/длинного отрезка)
        "secant_segment_short_name": context.get("secant_segment_short_name"),  # BF / UR
        "secant_segment_short_val": context.get("secant_segment_short_val"),
        "secant_segment_long_name": context.get("secant_segment_long_name"),    # DF / UT
        "secant_segment_long_val": context.get("secant_segment_long_val"),

        # Основания (что известно и что ищем)
        "base_known_name": context.get("base_known_name"),    # AD / RS
        "base_known_val": context.get("base_known_val"),
        "base_target_name": context.get("base_target_name"),  # BC / PT

        # Пропорция (явно, чтобы humanizer не гадал)
        "ratio_mode": ratio_mode,
        "ratio_left_num": ratio_left_num,
        "ratio_left_den": ratio_left_den,
        "ratio_right_num": ratio_right_num,
        "ratio_right_den": ratio_right_den,

        "base_small_name": base_small_name,
        "base_large_name": base_large_name,
    }

    # -----------------------------
    # 4) help_image (по стандартному контракту)
    # -----------------------------
    help_image_file = task_data.get("help_image_file") or context.get("help_image_file")
    help_image: Optional[Dict[str, Any]] = None

    if help_image_file:
        help_image = {
            "file": str(help_image_file),
            "schema": f"secant_similarity__{narrative_type}",
            "params": {
                "intersection_point": context.get("intersection_point"),
                "triangle_small": context.get("triangle_small_name"),
                "triangle_large": context.get("triangle_large_name"),
                "short_segment": context.get("secant_segment_short_name"),
                "long_segment": context.get("secant_segment_long_name"),
                "base_known": context.get("base_known_name"),
                "base_target": context.get("base_target_name"),
            },
        }

    # -----------------------------
    # 5) solution_core (канон)
    # -----------------------------
    return {
        "question_id": str(task_data.get("id")),
        "question_group": "GEOMETRY_16",
        "explanation_idea": "IDEA_SECANT_SIMILARITY",
        "calculation_steps": [],
        "final_answer": {
            "value_machine": answer,
            "value_display": str(answer) if answer is not None else "",
            "unit": "",
        },
        "variables": facts,
        "help_image": help_image,
        "hints": [],
    }


# =============================================================================
# ПАТТЕРН 2.2: tangent_trapezoid_properties
# =============================================================================

def _solve_tangent_trapezoid_properties(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Паттерн 2.2: Свойства трапеции, описанной около окружности.

    Актуальные нарративы (источник правды — task_context["narrative"]):
    - inradius_find_height
    - tangent_trapezoid_find_midline_via_sides
    - tangent_trapezoid_find_midline_via_bases
    - tangent_trapezoid_find_base

    Канон:
    - Solver отдаёт ТОЛЬКО facts (variables)
    - Никакого текста, никаких догадок
    """

    context: Dict[str, Any] = task_data.get("task_context") or {}
    narrative_type = context.get("narrative_type")
    narrative = (context.get("narrative") or "").strip().lower()
    answer = task_data.get("answer")

    facts: Dict[str, Any] = {
        "narrative": task_data.get("narrative"),
        "narrative_type": narrative_type,
        "answer": answer,
    }

    explanation_idea = "IDEA_ERROR"

    # -------------------------------------------------------------------------
    # 1) inradius_find_height
    # -------------------------------------------------------------------------
    if narrative == "inradius_find_height":
        facts.update({
            "radius_name": context.get("radius_name"),
            "radius_value": context.get("radius_value"),
            "height_name": context.get("height_name"),
        })
        explanation_idea = "IDEA_INRADIUS_HEIGHT"

    # -------------------------------------------------------------------------
    # 2) tangent_trapezoid_find_midline_via_sides
    # -------------------------------------------------------------------------
    elif narrative == "tangent_trapezoid_find_midline_via_sides":
        facts.update({
            "midline_name": context.get("midline_name"),

            "side_1_name": context.get("side_1_name"),
            "side_1_val": context.get("side_1_val"),

            "side_2_name": context.get("side_2_name"),
            "side_2_val": context.get("side_2_val"),

            # ✨ ДОБАВЛЯЕМ ИМЕНА ОСНОВАНИЙ
            "base_1_name": context.get("base_1_name"),
            "base_2_name": context.get("base_2_name"),
        })
        explanation_idea = "IDEA_TANGENT_TRAPEZOID_FIND_MIDLINE"

    # -------------------------------------------------------------------------
    # 3) tangent_trapezoid_find_midline_via_bases
    # -------------------------------------------------------------------------
    elif narrative == "tangent_trapezoid_find_midline_via_bases":
        facts.update({
            "midline_name": context.get("midline_name"),

            "base_1_name": context.get("base_1_name"),
            "base_1_val": context.get("base_1_val"),

            "base_2_name": context.get("base_2_name"),
            "base_2_val": context.get("base_2_val"),
        })
        explanation_idea = "IDEA_TANGENT_TRAPEZOID_FIND_MIDLINE"

    # -------------------------------------------------------------------------
    # 4) tangent_trapezoid_find_base
    # -------------------------------------------------------------------------
    elif narrative == "tangent_trapezoid_find_base":
        facts.update({
            "side_known_1_name": context.get("side_known_1_name"),
            "side_known_1_val": context.get("side_known_1_val"),

            "side_known_2_name": context.get("side_known_2_name"),
            "side_known_2_val": context.get("side_known_2_val"),

            "side_known_3_name": context.get("side_known_3_name"),
            "side_known_3_val": context.get("side_known_3_val"),

            "side_target_name": context.get("side_target_name"),
        })
        explanation_idea = "IDEA_TANGENT_QUAD_BALANCE"

    else:
        facts["error_reason"] = f"Unknown narrative: {narrative or '<empty>'}"

    # -------------------------------------------------------------------------
    # solution_core (канон)
    # -------------------------------------------------------------------------
    return {
        "question_id": str(task_data.get("id")),
        "question_group": "GEOMETRY_16",
        "explanation_idea": explanation_idea,
        "calculation_steps": [],
        "final_answer": {
            "value_machine": answer,
            "value_display": str(answer) if answer is not None else "",
            "unit": "",
        },
        "variables": facts,
        "help_image": (
            {
                "file": str(task_data.get("help_image_file")),
                "schema": narrative,  # важно: совпадает с humanizer narrative_key
                "params": {},
            }
            if task_data.get("help_image_file")
            else None
        ),
        "hints": [],
    }


# =========================================================================
# ПАТТЕРН 2.3: tangent_quad_sum
# =========================================================================

def _solve_tangent_quad_sum(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Паттерн 2.3: tangent_quad_sum

    Канон:
    - четырёхугольник
    - сумма противоположных сторон
    - касательная
    """
    return _get_stub_solution(task_data, "tangent_quad_sum")


# =========================================================================
# ПАТТЕРН 2.4: tangent_arc_angle
# =========================================================================

def _solve_tangent_arc_angle(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Паттерн 2.4: tangent_arc_angle

    Канон:
    - угол между касательной и хордой
    """
    return _get_stub_solution(task_data, "tangent_arc_angle")


# =========================================================================
# ПАТТЕРН 2.5: angle_tangency_center
# =========================================================================

def _solve_angle_tangency_center(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Паттерн 2.5: angle_tangency_center

    Канон:
    - радиус перпендикулярен касательной
    - угол при точке касания
    """
    return _get_stub_solution(task_data, "angle_tangency_center")


# =========================================================================
# ПАТТЕРН 2.6: sector_area
# =========================================================================

def _solve_sector_area(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Паттерн 2.6: sector_area

    Канон:
    - площадь сектора
    - пропорция по центральному углу
    """
    return _get_stub_solution(task_data, "sector_area")


# =========================================================================
# ПАТТЕРН 2.7: power_point
# =========================================================================

def _solve_power_point(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Паттерн 2.7: power_point

    Канон:
    - степень точки
    - касательная–секущая / секущая–секущая
    """
    return _get_stub_solution(task_data, "power_point")


# =========================================================================
# ОБЩИЕ ЗАГЛУШКИ И ОШИБКИ
# =========================================================================

def _get_stub_solution(task_data: Dict[str, Any], pattern_name: str) -> Dict[str, Any]:
    """
    Заглушка решения.
    Используется до реализации конкретного паттерна.
    """
    answer = task_data.get("answer")

    return {
        "question_id": str(task_data.get("id")),
        "question_group": "GEOMETRY_16",
        "explanation_idea": f"IDEA_TODO_{pattern_name.upper()}",
        "calculation_steps": [],
        "final_answer": {
            "value_machine": answer,
            "value_display": str(answer) if answer is not None else "",
            "unit": "",
        },
        "variables": {
            "pattern": pattern_name,
            "narrative_type": (task_data.get("task_context") or {}).get("narrative_type"),
        },
        "help_image": None,
        "hints": [],
    }


def _get_error_solution(task_data: Dict[str, Any], *, reason: str) -> Dict[str, Any]:
    logger.error("Could not solve task. Reason: %s", reason)

    answer = task_data.get("answer")

    return {
        "question_id": str(task_data.get("id")),
        "question_group": "GEOMETRY_16",
        "explanation_idea": "IDEA_ERROR",
        "calculation_steps": [],
        "final_answer": {
            "value_machine": answer,
            "value_display": str(answer) if answer is not None else "",
            "unit": "",
        },
        "variables": {
            "error_reason": reason,
        },
        "help_image": None,
        "hints": [],
    }
