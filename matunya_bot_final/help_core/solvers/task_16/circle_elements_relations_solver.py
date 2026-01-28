# matunya_bot_final/help_core/solvers/task_16/circle_elements_relations_solver.py
# -*- coding: utf-8 -*-

from __future__ import annotations

import logging
import math
from typing import Any, Dict, Optional

from matplotlib.style import context

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

    # -------------------------------------------------
    # Формулы для шага 2 (канон через 180°)
    # -------------------------------------------------
    if narrative_type.startswith("abcd_"):
        cyclic_angles_sum_1 = "∠ABC"
        cyclic_angles_sum_2 = "∠ADC"
        linear_angles_sum = "∠FBC"   # смежный с ∠ABC
    elif narrative_type.startswith("prst_"):
        cyclic_angles_sum_1 = "∠PRS"
        cyclic_angles_sum_2 = "∠PTS"
        linear_angles_sum = "∠URS"   # смежный с ∠PRS
    else:
        cyclic_angles_sum_1 = ""
        cyclic_angles_sum_2 = ""
        linear_angles_sum = ""

    # -----------------------------
    # 2) ПРОПОРЦИЯ (источник правды)
    # -----------------------------
    # В эталоне:
    #   find_small:  short/long = target/known   (пример: BF/DF = BC/AD)
    #   find_large:  short/long = known/target   (пример: UR/UT = RS/PT)
    #
    # Чтобы humanizer не гадал, задаём явную "схему" и сразу нужные дроби:
    # ratio_left_num / ratio_left_den / ratio_right_num / ratio_right_den
    ratio_left_num = context.get("secant_segment_short_name") or ""
    ratio_left_den = context.get("secant_segment_long_name") or ""

    # 🔥 ЧИСЛОВЫЕ значения для шага 4
    ratio_right_num_val = None
    ratio_right_den_val = None

    if narrative_type.endswith("find_small"):
        # short/long = target/known
        ratio_right_num = context.get("base_target_name")   # RS / BC
        ratio_right_den = context.get("base_known_name")    # PT / AD
        ratio_mode = "SHORT_LONG_EQ_TARGET_KNOWN"

        base_small_name = context.get("base_target_name")
        base_large_name = context.get("base_known_name")

        # ⬇️ числовое известно в знаменателе
        ratio_right_den_val = context.get("base_known_val")

    elif narrative_type.endswith("find_large"):
        # short/long = known/target
        ratio_right_num = context.get("base_known_name")    # BC / RS
        ratio_right_den = context.get("base_target_name")   # AD / PT
        ratio_mode = "SHORT_LONG_EQ_KNOWN_TARGET"

        base_small_name = context.get("base_known_name")
        base_large_name = context.get("base_target_name")

        # ⬇️ числовое известно в числителе
        ratio_right_num_val = context.get("base_known_val")

    else:
        ratio_right_num = ""
        ratio_right_den = ""
        ratio_mode = "UNKNOWN"

        base_small_name = ""
        base_large_name = ""

    # -----------------------------
    # 3) FACTS ONLY
    # -----------------------------
    facts: Dict[str, Any] = {
        "narrative_type": narrative_type,
        "answer": answer,

        # Геометрические якоря
        "intersection_point": context.get("intersection_point"),
        "common_vertex": context.get("common_vertex"),

        # Подобные треугольники
        "triangle_small_name": context.get("triangle_small_name"),
        "triangle_large_name": context.get("triangle_large_name"),

        # Равные углы
        "vertex_angle_small": context.get("vertex_angle_small"),
        "vertex_angle_large": context.get("vertex_angle_large"),

        # Вписанный четырёхугольник
        "cyclic_quad_name": (
            "ABCD" if narrative_type.startswith("abcd_")
            else "PRST" if narrative_type.startswith("prst_")
            else ""
        ),

        # 🔥 Формулы для шага 2
        "cyclic_angles_sum_1": cyclic_angles_sum_1,
        "cyclic_angles_sum_2": cyclic_angles_sum_2,
        "linear_angles_sum": linear_angles_sum,

        # Секущие
        "secant_segment_short_name": context.get("secant_segment_short_name"),
        "secant_segment_short_val": context.get("secant_segment_short_val"),
        "secant_segment_long_name": context.get("secant_segment_long_name"),
        "secant_segment_long_val": context.get("secant_segment_long_val"),

        # Основания
        "base_known_name": context.get("base_known_name"),
        "base_known_val": context.get("base_known_val"),
        "base_target_name": context.get("base_target_name"),

        # Пропорция
        "ratio_mode": ratio_mode,
        "ratio_left_num": ratio_left_num,
        "ratio_left_den": ratio_left_den,
        "ratio_right_num": ratio_right_num,
        "ratio_right_den": ratio_right_den,
        "ratio_right_num_val": ratio_right_num_val,
        "ratio_right_den_val": ratio_right_den_val,

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

    # -----------------------------
    # 5) help_image (по стандартному контракту)
    # -----------------------------
    help_image_file = task_data.get("help_image_file")
    help_image: Optional[Dict[str, Any]] = None

    if help_image_file:
        params: Dict[str, Any] = {}

        # --- 2.2.1 inradius_find_height ---
        if narrative == "inradius_find_height":
            params = {
                "figure": "trapezoid",
                "inradius": context.get("radius_name"),
                "height": context.get("height_name"),
            }

        # --- 2.2.2 midline via sides ---
        elif narrative == "tangent_trapezoid_find_midline_via_sides":
            params = {
                "figure": "trapezoid",
                "vertices": context.get("vertices"),        # KLMN
                "bases": [
                    context.get("base_1_name"),
                    context.get("base_2_name"),
                ],
                "legs": [
                    context.get("side_1_name"),
                    context.get("side_2_name"),
                ],
                "midline": context.get("midline_name"),     # PR
            }

        # --- 2.2.3 midline via bases ---
        elif narrative == "tangent_trapezoid_find_midline_via_bases":
            params = {
                "figure": "trapezoid",
                "vertices": context.get("vertices"),
                "bases": [
                    context.get("base_1_name"),
                    context.get("base_2_name"),
                ],
                "midline": context.get("midline_name"),
            }

        # --- 2.2.4 find base ---
        elif narrative == "tangent_trapezoid_find_base":
            params = {
                "figure": "trapezoid",
                "vertices": context.get("vertices"),
                "known_sides": [
                    context.get("side_known_1_name"),
                    context.get("side_known_2_name"),
                    context.get("side_known_3_name"),
                ],
                "target_side": context.get("side_target_name"),
            }

        help_image = {
            "file": str(help_image_file),
            "schema": f"tangent_trapezoid__{narrative}",
            "params": params,
        }

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
        "help_image": help_image,
        "hints": [],
    }

# =============================================================================
# ПАТТЕРН 2.3: tangent_quad_sum
# =============================================================================

def _solve_tangent_quad_sum(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Паттерн 2.3: tangent_quad_sum

    Канон:
    - четырёхугольник, описанный около окружности
    - суммы противоположных сторон равны
    - solver отдаёт ТОЛЬКО facts
    """

    context: Dict[str, Any] = task_data.get("task_context") or {}
    narrative = (task_data.get("narrative") or "").strip().lower()
    narrative_type = context.get("narrative_type")
    answer = task_data.get("answer")

    # ------------------------------------------------------------------
    # facts — источник правды для humanizer
    # ------------------------------------------------------------------
    facts: Dict[str, Any] = {
        "narrative": narrative,
        "narrative_type": narrative_type,
        "answer": answer,
    }

    explanation_idea = "IDEA_ERROR"

    # ------------------------------------------------------------------
    # find_missing_side (единственный нарратив паттерна)
    # ------------------------------------------------------------------
    if narrative == "find_missing_side":
        left_a_name = context.get("sum_left_1_name")
        left_a_val = context.get("sum_left_1_val")

        left_b_name = context.get("sum_left_2_name")
        left_b_val = context.get("sum_left_2_val")

        right_1_name = context.get("sum_right_1_name")
        right_1_val = context.get("sum_right_1_val")

        right_2_name = context.get("sum_right_2_name")
        right_2_val = context.get("sum_right_2_val")

        # вычисляем сумму левой пары
        sum_left = left_a_val + left_b_val

        # определяем известную и искомую сторону справа
        if right_1_val is None and right_2_val is not None:
            side_known_name = right_2_name
            side_known_val = right_2_val
            side_target_name = right_1_name

        elif right_2_val is None and right_1_val is not None:
            side_known_name = right_1_name
            side_known_val = right_1_val
            side_target_name = right_2_name

        else:
            facts["error_reason"] = (
                "tangent_quad_sum: должна быть ровно одна неизвестная сторона"
            )
            explanation_idea = "IDEA_ERROR"

        facts.update({
            "side_a_name": left_a_name,
            "side_a_val": left_a_val,

            "side_b_name": left_b_name,
            "side_b_val": left_b_val,

            "side_known_name": side_known_name,
            "side_known_val": side_known_val,

            "side_target_name": side_target_name,

            "sum_left": sum_left,
        })

        explanation_idea = "IDEA_TANGENT_QUAD_SUM"

    else:
        facts["error_reason"] = f"Unknown narrative: {narrative or '<empty>'}"

    # ------------------------------------------------------------------
    # help_image (по стандартному контракту)
    # ------------------------------------------------------------------
    help_image_file = task_data.get("help_image_file")
    help_image = None

    if help_image_file:
        help_image = {
            "file": str(help_image_file),
            "schema": "tangent_quad_sum",
            "params": {
                "figure": "quadrilateral",
                "left_sides": [
                    context.get("sum_left_1_name"),
                    context.get("sum_left_2_name"),
                ],
                "right_sides": [
                    context.get("sum_right_1_name"),
                    context.get("sum_right_2_name"),
                ],
            },
        }

    # ------------------------------------------------------------------
    # solution_core (КАНОН)
    # ------------------------------------------------------------------
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
        "help_image": help_image,
        "hints": [],
    }

# =========================================================================
# ПАТТЕРН 2.4: tangent_arc_angle
# =========================================================================

def _solve_tangent_arc_angle (task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Паттерн 2.4: tangent_arc_angle

    Нарративы:
      - arc_to_tangent_angle
      - tangent_angle_to_arc
    """

    context: Dict[str, Any] = task_data.get("task_context") or {}
    answer = task_data.get("answer")

    narrative = context.get("narrative")

    if narrative not in ("arc_to_tangent_angle", "tangent_angle_to_arc"):
        return _get_error_solution(
            task_data,
            reason=f"tangent_arc_angle: unknown narrative '{narrative}'"
        )

    # --- базовые facts ---
    facts = {
        "narrative": narrative,
        "answer": answer,
        "tangent_point": context.get("tangent_point"),
        "arc_name": context.get("arc_name"),
    }

    # --- arc → angle ---
    if narrative == "arc_to_tangent_angle":
        facts.update(
            arc_value=context.get("arc_value"),
            angle_name=context.get("angle_name"),
            chord_name=context.get("chord_name"),
        )

    # --- angle → arc ---
    else:
        facts.update(
            angle_name=context.get("angle_name"),
            angle_value=context.get("angle_value"),
        )

    help_image_file = task_data.get("help_image_file")
    help_image = None

    if help_image_file:
        help_image = {
            "file": str(help_image_file),
            "schema": f"tangent_arc_angle__{narrative}",
            "params": {
                "arc": context.get("arc_name"),
                "tangent_point": context.get("tangent_point"),
            }
        }

    return {
        "question_id": str(task_data.get("id")),
        "question_group": "GEOMETRY_16",
        "explanation_idea": f"IDEA_TANGENT_ARC_ANGLE_{narrative.upper()}",
        "calculation_steps": [],
        "final_answer": {
            "value_machine": answer,
            "value_display": str(answer) if answer is not None else "",
            "unit": "°",
        },
        "variables": facts,
        "help_image": help_image,
        "hints": [],
    }

# =========================================================================
# ПАТТЕРН 2.5: angle_tangency_center
# =========================================================================

def _solve_angle_tangency_center(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Паттерн 2.5: angle_tangency_center

    Нарративы:
      - find_center_angle
      - find_corner_angle
    """

    context: Dict[str, Any] = task_data.get("task_context") or {}
    answer = task_data.get("answer")

    narrative = context.get("narrative")

    if narrative not in ("find_center_angle", "find_corner_angle"):
        return _get_error_solution(
            task_data,
            reason=f"angle_tangency_center: unknown narrative '{narrative}'"
        )

    # --- базовые facts (общие для обоих нарративов) ---
    facts = {
        "narrative": narrative,
        "answer": answer,
        "vertex_point": context.get("vertex_point"),
        "center": context.get("center"),
        "touch_point_1": context.get("touch_point_1"),
        "touch_point_2": context.get("touch_point_2"),
        "tangent_1": context.get("tangent_1"),
        "tangent_2": context.get("tangent_2"),
        "corner_angle_name": context.get("corner_angle_name"),
        "central_angle_name": context.get("central_angle_name"),
    }

    # --- что именно дано ---
    if narrative == "find_center_angle":
        facts.update(
            corner_angle_value=context.get("corner_angle_value"),
        )
    else:  # find_corner_angle
        facts.update(
            central_angle_value=context.get("central_angle_value"),
        )

    # --- help_image ---
    help_image_file = task_data.get("help_image_file")
    help_image = None

    if help_image_file:
        help_image = {
            "file": str(help_image_file),
            "schema": f"angle_tangency_center__{narrative}",
            "params": {
                "vertex": context.get("vertex_point"),
                "center": context.get("center"),
                "touch_1": context.get("touch_point_1"),
                "touch_2": context.get("touch_point_2"),
            }
        }

    return {
        "question_id": str(task_data.get("id")),
        "question_group": "GEOMETRY_16",
        "explanation_idea": "angle_tangency_center",
        "calculation_steps": [],
        "final_answer": {
            "value_machine": answer,
            "value_display": str(answer) if answer is not None else "",
            "unit": "°",
        },
        "variables": facts,
        "help_image": help_image,
        "hints": [],
    }

# =========================================================================
# ПАТТЕРН 2.6: sector_area
# =========================================================================

def _solve_sector_area(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Паттерн 2.6: sector_area
    """

    context = task_data.get("task_context") or {}
    answer = task_data.get("answer")

    base_narrative = context.get("narrative")
    angle = context.get("angle_value")

    if base_narrative not in ("find_sector_area", "find_disk_area"):
        return _get_error_solution(
            task_data,
            reason=f"sector_area: unknown narrative '{base_narrative}'"
        )

    # --------------------------------------------------
    # find_sector_area
    # --------------------------------------------------
    if base_narrative == "find_sector_area":
        circle_area = context.get("circle_area")

        raw_num = angle
        raw_den = 360
        g = math.gcd(raw_num, raw_den)

        reduced_num = raw_num // g
        reduced_den = raw_den // g

        narrative = (
            "find_sector_area_short"
            if reduced_num == 1 or reduced_den == 1
            else "find_sector_area_general"
        )

        facts = {
            "narrative": narrative,
            "angle_value": angle,
            "circle_area": circle_area,

            "fraction_num": raw_num,
            "fraction_den": raw_den,
            "reduced_num": reduced_num,
            "reduced_den": reduced_den,

            "answer": answer,
        }

    # --------------------------------------------------
    # find_disk_area
    # --------------------------------------------------
    else:
        sector_area = context.get("sector_area")

        raw_num = 360
        raw_den = angle
        g = math.gcd(raw_num, raw_den)

        reduced_num = raw_num // g
        reduced_den = raw_den // g

        narrative = (
            "find_disk_area_short"
            if reduced_num == 1 or reduced_den == 1
            else "find_disk_area_general"
        )

        facts = {
            "narrative": narrative,
            "angle_value": angle,
            "sector_area": sector_area,

            "fraction_num": raw_num,
            "fraction_den": raw_den,
            "reduced_num": reduced_num,
            "reduced_den": reduced_den,

            "answer": answer,
        }

    return {
        "question_id": str(task_data.get("id")),
        "question_group": "GEOMETRY_16",
        "explanation_idea": "IDEA_SECTOR_AREA",
        "calculation_steps": [],
        "final_answer": {
            "value_machine": answer,
            "value_display": str(answer),
            "unit": "",
        },
        "variables": facts,
        "hints": [],
    }

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
