# matunya_bot_final/help_core/solvers/task_16/central_and_inscribed_angles_solver.py
# -*- coding: utf-8 -*-

from __future__ import annotations

import logging
import math
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# =========================================================================
# CENTRAL_INSCRIBED: нормализация "картинко-нарративов" (16) -> (2)
# =========================================================================
_CENTRAL_INSCRIBED_NARRATIVE_MAP: Dict[str, str] = {
    # центральный -> найти вписанный
    "central_acute_inner_aoc_to_abc": "find_inscribed_by_central",
    "central_acute_outer_aoc_to_abc": "find_inscribed_by_central",
    "central_obtuse_inner_aoc_to_abc": "find_inscribed_by_central",
    "central_obtuse_outer_aoc_to_abc": "find_inscribed_by_central",
    "central_acute_inner_dof_to_def": "find_inscribed_by_central",
    "central_acute_outer_dof_to_def": "find_inscribed_by_central",
    "central_obtuse_inner_dof_to_def": "find_inscribed_by_central",
    "central_obtuse_outer_dof_to_def": "find_inscribed_by_central",

    # вписанный -> найти центральный
    "central_acute_inner_abc_to_aoc": "find_central_by_inscribed",
    "central_acute_outer_abc_to_aoc": "find_central_by_inscribed",
    "central_obtuse_inner_abc_to_aoc": "find_central_by_inscribed",
    "central_obtuse_outer_abc_to_aoc": "find_central_by_inscribed",
    "central_acute_inner_def_to_dof": "find_central_by_inscribed",
    "central_acute_outer_def_to_dof": "find_central_by_inscribed",
    "central_obtuse_inner_def_to_dof": "find_central_by_inscribed",
    "central_obtuse_outer_def_to_dof": "find_central_by_inscribed",
}


def _normalize_central_inscribed_narrative(raw: Any) -> Optional[str]:
    """
    Возвращает ТОЛЬКО один из двух обобщённых нарративов:
      - find_inscribed_by_central
      - find_central_by_inscribed
    Принимает как уже-нормализованное значение, так и "сырой" (16 вариантов).
    """
    if not raw:
        return None
    s = str(raw).strip()
    if s in ("find_inscribed_by_central", "find_central_by_inscribed"):
        return s
    return _CENTRAL_INSCRIBED_NARRATIVE_MAP.get(s)


async def solve(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Решатель для Темы 1: Центральные и вписанные углы.

    Вход: task_data (pattern, task_context, answer, id, ...).
    Выход: solution_core (по ГОСТ-2026), без анализа текста задачи.

    Важно:
    - Handler выбирает solver по ТЕМЕ (central_and_inscribed_angles).
    - Этот solver внутри темы маршрутизирует по pattern.
    - По pattern + task_context формируем facts и help_image (контракт).
    """
    pattern = task_data.get("pattern")

    # Роутер по паттернам (уровень "Тема/Pattern" верхнего уровня)
    if pattern == "cyclic_quad_angles":
        return _solve_cyclic_quad_angles(task_data)

    if pattern == "central_inscribed":
        return _solve_central_inscribed(task_data)

    if pattern == "radius_chord_angles":
        return _solve_radius_chord_angles(task_data)

    if pattern == "arc_length_ratio":
        return _solve_arc_length_ratio(task_data)

    if pattern == "diameter_right_triangle":
        return _solve_diameter_right_triangle(task_data)

    if pattern == "two_diameters_angles":
        return _solve_two_diameters_angles(task_data)

    logger.error("Unknown pattern: %r", pattern)
    return _get_error_solution(task_data, reason=f"Unknown pattern: {pattern}")


# =========================================================================
# ПАТТЕРН 1.1: cyclic_quad_angles
# =========================================================================

def _solve_cyclic_quad_angles(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Подготовка данных для humanizer'а по вписанному четырёхугольнику.

    Важно:
    - НЕ формируем здесь текстовые куски (given_text/target_text).
    - Передаём факты (углы/дуги/части), humanizer сам собирает "Дано/Найти" и шаги.
    - Формируем help_image по контракту (file + schema + params), без description.
    """
    context: Dict[str, Any] = task_data.get("task_context") or {}
    narrative_type = context.get("narrative_type")

    answer = task_data.get("answer")

    # Канонический набор "facts" (минимум алиасов, максимум фактов).
    facts: Dict[str, Any] = {
        "narrative_type": narrative_type,
        "answer": answer,
    }

    # Нормализация фактов под каждый narrative_type (без текста и без "угадываний").
    # Поддерживаем и "старые" названия (opposite_sum/part_sum/part_diff),
    # и "новые" (same_arc_angles/find_diagonal_angle_abd), чтобы не сломать БД/сырьё.
    if narrative_type in ("opposite_sum", "same_arc_angles"):
        facts.update(
            angle_given_name=context.get("angle_given_name"),
            angle_given_val=context.get("angle_given_val"),
            angle_target_name=context.get("angle_target_name"),
            arc_name=context.get("arc_name"),
            vertices=context.get("vertices"),
        )

    elif narrative_type in ("part_sum", "find_diagonal_angle_abd"):
        facts.update(
            angle_whole_name=context.get("angle_whole_name"),
            angle_known_part_name=context.get("angle_known_part_name"),
            angle_known_part_val=context.get("angle_known_part_val"),
            angle_hidden_part_name=context.get("angle_hidden_part_name"),
            angle_alien_name=context.get("angle_alien_name"),
            angle_alien_val=context.get("angle_alien_val"),
            arc_name=context.get("arc_name"),
            vertices=context.get("vertices"),
            diagonal_name=context.get("diagonal_name"),
        )

    elif narrative_type == "part_diff":
        facts.update(
            angle_target_name=context.get("angle_target_name"),
            angle_whole_name=context.get("angle_whole_name"),
            angle_whole_val=context.get("angle_whole_val"),
            angle_alien_name=context.get("angle_alien_name"),
            angle_alien_val=context.get("angle_alien_val"),
            angle_parasite_name=context.get("angle_parasite_name"),
            arc_name=context.get("arc_name"),
            vertices=context.get("vertices"),
        )

    else:
        # Не ломаем пайплайн, но явно подсвечиваем проблему.
        logger.error("Unknown narrative_type for cyclic_quad_angles: %r", narrative_type)
        return _get_error_solution(task_data, reason=f"Unknown narrative_type: {narrative_type}")

    # help_image по контракту: file + schema + params.
    # ФАЙЛ берём строго из сырья (task_data/help_image_file), чтобы соответствовать конкретной картинке.
    help_image = _build_help_image(task_data=task_data, context=context, pattern="cyclic_quad_angles")

    # Ключ "explanation_idea" НЕ обязан совпадать с narrative_type.
    # Сейчас делаем стабильный нейминг под humanizer: IDEA_<NARRATIVE_TYPE>.
    idea_key = f"IDEA_{str(narrative_type).upper()}"

    return {
        "question_id": str(task_data.get("id")),
        "question_group": "GEOMETRY_16",
        "explanation_idea": idea_key,
        "calculation_steps": [],  # шаги строит humanizer по facts
        "final_answer": {
            "value_machine": answer,
            "value_display": str(answer) if answer is not None else "",
            "unit": "°",
        },
        "variables": facts,      # передаём факты, а не текст
        "help_image": help_image,  # 👈 контракт help_image (без description)
        "hints": [],
    }


def _build_help_image(
    *,
    task_data: Dict[str, Any],
    context: Dict[str, Any],
    pattern: str,
) -> Optional[Dict[str, Any]]:
    """
    Формирует help_image для solution_core по контракту:
    {
      "file": "string",
      "schema": "string",
      "params": { ... }
    }

    Важно:
    - file берём из сырья (help_image_file), чтобы соответствовать конкретной картинке.
    - schema/params формируем из pattern+narrative+контекстных фактов.
    - Никакого description здесь не делаем.
    """
    help_image_file = task_data.get("help_image_file") or context.get("help_image_file")
    if not help_image_file:
        return None

    narrative = context.get("narrative_type") or "unknown"
    schema = f"{pattern}__{narrative}"

    # params — только факты, никаких текстов
    params: Dict[str, Any] = {
        # базовые
        "pattern": pattern,
        "narrative_type": narrative,
        "vertices": context.get("vertices"),  # ожидаем ["A","B","C","D"] или ["K","L","M","N"]
        # дуги/углы
        "arc_name": context.get("arc_name"),
        "angle_given_name": context.get("angle_given_name"),
        "angle_given_val": context.get("angle_given_val"),
        "angle_target_name": context.get("angle_target_name"),
        # части/доп.элементы (могут быть None — это нормально)
        "angle_whole_name": context.get("angle_whole_name"),
        "angle_whole_val": context.get("angle_whole_val"),
        "angle_known_part_name": context.get("angle_known_part_name"),
        "angle_known_part_val": context.get("angle_known_part_val"),
        "angle_hidden_part_name": context.get("angle_hidden_part_name"),
        "angle_alien_name": context.get("angle_alien_name"),
        "angle_alien_val": context.get("angle_alien_val"),
        "angle_parasite_name": context.get("angle_parasite_name"),
        "diagonal_name": context.get("diagonal_name"),
        "arc_marked": context.get("arc_marked"),
    }

    return {
        "file": str(help_image_file),
        "schema": schema,
        "params": params,
    }

# =========================================================================
# ПАТТЕРН 1.2: central_inscribed  (НОВАЯ АРХИТЕКТУРА, facts-only)
# =========================================================================

def _solve_central_inscribed(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Решатель для паттерна central_inscribed.

    Канон:
    - facts-only
    - 2 нарратива:
      * find_inscribed_by_central  (дан центральный -> найти вписанный)
      * find_central_by_inscribed  (дан вписанный -> найти центральный)

    Важно:
    - Мы НЕ анализируем текст.
    - Но мы обязаны нормализовать факты, потому что сырьё/валидатор
      иногда путает central/inscribed местами.
    """

    context: Dict[str, Any] = task_data.get("task_context") or {}
    answer = task_data.get("answer")

    narrative_general = _normalize_central_inscribed_narrative(context.get("narrative_type"))
    if not narrative_general:
        narrative_general = _normalize_central_inscribed_narrative(task_data.get("narrative"))

    if narrative_general not in ("find_inscribed_by_central", "find_central_by_inscribed"):
        logger.error("Unknown narrative for central_inscribed (expected 2): %r", narrative_general)
        return _get_error_solution(
            task_data,
            reason=f"Unknown narrative for central_inscribed: {narrative_general}",
        )

    pair = _extract_ci_pair(context)

    central_name = pair.get("central_name")
    central_val = pair.get("central_val")
    inscribed_name = pair.get("inscribed_name")
    inscribed_val = pair.get("inscribed_val")
    arc_name = pair.get("arc_name")
    vertices = pair.get("vertices")

    # --- (1) Чиним перепутанные пары central/inscribed ---
    # Ожидаем: central содержит 'O', inscribed обычно без 'O'
    central_looks_central = _is_central_angle_name(central_name)
    inscribed_looks_central = _is_central_angle_name(inscribed_name)

    # Если "central" не похож на центральный, а "inscribed" похож — значит перепутали.
    if (not central_looks_central) and inscribed_looks_central:
        central_name, inscribed_name = inscribed_name, central_name
        central_val, inscribed_val = inscribed_val, central_val

    # --- (2) Если дуги нет — восстанавливаем ---
    if not arc_name:
        # предпочтительно по центральному (он однозначнее)
        arc_name = _arc_from_angle_name(central_name) or _arc_from_angle_name(inscribed_name)

    # --- (3) Финальная проверка минимальных данных ---
    if narrative_general == "find_inscribed_by_central":
        if not central_name or central_val is None or not inscribed_name or not arc_name:
            return _get_error_solution(
                task_data,
                reason="central_inscribed: missing facts for find_inscribed_by_central",
            )

    else:  # find_central_by_inscribed
        if not inscribed_name or inscribed_val is None or not central_name or not arc_name:
            return _get_error_solution(
                task_data,
                reason="central_inscribed: missing facts for find_central_by_inscribed",
            )

    # --- FACTS (контракт humanizer'а) ---
    facts: Dict[str, Any] = {
        "narrative_type": narrative_general,
        "answer": answer,
        "vertices": vertices,
        "arc_name": arc_name,
    }

    # Нарратив 1: дан центральный -> найти вписанный
    if narrative_general == "find_inscribed_by_central":
        facts.update(
            angle_given_name=central_name,
            angle_given_val=central_val,
            angle_target_name=inscribed_name,
        )
    # Нарратив 2: дан вписанный -> найти центральный
    else:
        facts.update(
            angle_given_name=inscribed_name,
            angle_given_val=inscribed_val,
            angle_target_name=central_name,
        )

    # help_image: schema должен быть по ОБОБЩЕННОМУ нарративу
    context_for_image = dict(context)
    context_for_image.update(facts)
    context_for_image["narrative_type"] = narrative_general

    help_image = _build_help_image(
        task_data=task_data,
        context=context_for_image,
        pattern="central_inscribed",
    )

    idea_key = f"IDEA_{narrative_general.upper()}"

    return {
        "question_id": str(task_data.get("id")),
        "question_group": "GEOMETRY_16",
        "explanation_idea": idea_key,
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
# ПАТТЕРН 1.3: radius_chord_angles
# =========================================================================

def _solve_radius_chord_angles(task_data: Dict[str, Any]) -> Dict[str, Any]:
    context: Dict[str, Any] = task_data.get("task_context") or {}
    answer = task_data.get("answer")
    narrative_general = context.get("narrative_type") or "" # (упрощено для краткости)

    # Нормализуем нарратив, если он длинный (из старых запасов)
    if "find_part" in narrative_general: narrative_general = "find_part_angle"
    if "find_whole" in narrative_general: narrative_general = "find_whole_angle"

    facts: Dict[str, Any] = {
        "narrative_type": narrative_general,
        "answer": answer,
    }

    # Общая логика для радиусов (AO = BO = CO)
    # Берем буквы из angle_whole_name (например ABC)
    whole_name = context.get("angle_whole_name") or context.get("angle_target_name") or "ABC"
    p1, vertex, p3 = whole_name[0], whole_name[1], whole_name[2]
    facts["radii_equality"] = f"O{p1} = O{vertex} = O{p3}"
    facts["vertex"] = vertex

    if narrative_general == "find_part_angle":
        known = context.get("angle_known_part_name")
        target = context.get("angle_target_name")

        facts.update(
            angle_whole_name=context.get("angle_whole_name"),
            angle_whole_val=context.get("angle_whole_val"),
            angle_known_part_name=known,
            angle_known_part_val=context.get("angle_known_part_val"),
            angle_target_name=target,

            # Генерируем зеркальные имена для объяснения (OBA, OBC)
            angle_known_base_name=_swap_letters(known),
            angle_target_base_name=_swap_letters(target),

            # Имена треугольников (AOB, BOC)
            iso_tri_1=_swap_letters(known).replace("O", "") + "O" + vertex, # AOB (примерно) - упростим в humanizer если надо
            # Проще передать просто "O"+буквы. Humanizer сам разберется или передадим готовые:
            iso_tri_1_name=f"{known.replace('O','').replace(vertex,'')}O{vertex}",
            iso_tri_2_name=f"{target.replace('O','').replace(vertex,'')}O{vertex}",
        )

    else:  # find_whole_angle
        part1 = context.get("angle_part1_name")
        part2 = context.get("angle_part2_name")

        facts.update(
            angle_part1_name=part1,
            angle_part1_val=context.get("angle_part1_val"),
            angle_part2_name=part2,
            angle_part2_val=context.get("angle_part2_val"),
            angle_target_name=context.get("angle_target_name"),

            # Зеркальные имена
            angle_part1_base_name=_swap_letters(part1),
            angle_part2_base_name=_swap_letters(part2),

            iso_tri_1_name=f"{part1.replace('O','').replace(vertex,'')}O{vertex}",
            iso_tri_2_name=f"{part2.replace('O','').replace(vertex,'')}O{vertex}",
        )

    # Упаковка
    idea_key = f"IDEA_{narrative_general.upper()}"

    # ------------------------------------------------------------------
    # help_image (КАНОН задания 16)
    # ------------------------------------------------------------------
    help_image = None
    help_image_file = task_data.get("help_image_file")

    if help_image_file:
        # определяем острый / тупой случай
        angle_type = context.get("angle_type")  # "acute" / "obtuse" — уже есть в БД
        help_image = {
            "file": str(help_image_file),
            "schema": f"radius_chord_angles__{narrative_general}__{angle_type}",
            "params": {
                "figure": "circle",
                "center": "O",
                "vertex": facts.get("vertex"),
                "narrative": narrative_general,
                "angle_type": angle_type,
            },
        }

    return {
        "question_id": str(task_data.get("id")),
        "question_group": "GEOMETRY_16",
        "explanation_idea": idea_key,
        "calculation_steps": [],
        "final_answer": {
            "value_machine": answer,
            "value_display": str(answer),
            "unit": "°",
        },
        "variables": facts,
        "help_image": help_image,
        "hints": [],
    }


# -------------------------------------------------------------------------
# Нормализация narrative_type из сырья/валидатора -> общий нарратив
# -------------------------------------------------------------------------

def _normalize_radius_chord_narrative(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None

    s = str(raw).strip()

    # сырьевые narrative_type (как у тебя в JSON примерах)
    if s.endswith("_find_part"):
        return "find_part_angle"
    if s.endswith("_find_whole"):
        return "find_whole_angle"

    # если вдруг уже общий
    if s in ("find_part_angle", "find_whole_angle"):
        return s

    return None

# =========================================================================
# ПАТТЕРН 1.4: arc_length_ratio
# =========================================================================

def _solve_arc_length_ratio(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Паттерн 1.4: arc_length_ratio
    Нарратив: small_to_large_arc
    FIX: Используем \n вместо <br> для корректного отображения в Telegram.
    """
    import math

    context: Dict[str, Any] = task_data.get("task_context") or {}
    answer = task_data.get("answer")

    raw_narrative = context.get("narrative_type") or ""
    if "small_to_large_arc" in raw_narrative:
        narrative_type = "small_to_large_arc"
    else:
        narrative_type = raw_narrative

    len_small = context.get("small_arc_length")
    angle_small = context.get("small_arc_angle")
    angle_large = context.get("large_arc_angle")

    reduce_steps = []

    # --- сокращение углов ---
    gcd_angles = math.gcd(angle_large, angle_small)
    num = angle_large
    den = angle_small

    if gcd_angles > 1:
        reduce_steps.append({
            "by": gcd_angles,
            "before": f"{len_small} · {angle_large}/{angle_small}",
            "after": f"{len_small} · {angle_large // gcd_angles}/{angle_small // gcd_angles}"
        })
        num //= gcd_angles
        den //= gcd_angles

    # --- сокращение длины и знаменателя ---
    if den > 1:
        gcd_len = math.gcd(len_small, den)
        if gcd_len > 1:
            reduce_steps.append({
                "by": gcd_len,
                "before": f"{len_small} · {num}/{den}",
                "after": f"{len_small // gcd_len} · {num}"
            })
            len_small //= gcd_len

    # вычисляем ответ, если он не пришёл
    if answer is None:
        answer = (context["small_arc_length"] * context["large_arc_angle"]) // context["small_arc_angle"]

    calc = {
        "small_len": context.get("small_arc_length"),
        "small_angle": angle_small,
        "large_angle": angle_large,
        "reduce_steps": reduce_steps,
        "final": answer
    }

    facts = {
        "narrative_type": narrative_type,
        "arc_name": context.get("arc_name"),

        "small_arc_length": context.get("small_arc_length"),
        "small_arc_angle": context.get("small_arc_angle"),
        "large_arc_angle": context.get("large_arc_angle"),

        "answer": answer,          # ← ВОТ ЭТО КРИТИЧНО
        "calc": calc,
    }

    idea_key = "IDEA_ARC_LENGTH_RATIO"

    return {
        "question_id": str(task_data.get("id")),
        "question_group": "GEOMETRY_16",
        "explanation_idea": idea_key,
        "calculation_steps": [],
        "final_answer": {
            "value_machine": answer,
            "value_display": str(answer) if answer is not None else "",
            "unit": "",
        },
        "variables": facts,
        "help_image": None,
        "hints": [],
    }

# =========================================================================
# ПАТТЕРН 1.5: diameter_right_triangle
# =========================================================================

def _solve_diameter_right_triangle(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Паттерн 1.5: diameter_right_triangle
    Нарратив: center_on_side
    """

    context: Dict[str, Any] = task_data.get("task_context", {}) or {}
    answer = task_data.get("answer")

    # --- факты из контекста (контракт валидатора) ---
    diameter_side = context.get("diameter_side")            # "AC"
    radius_point = context.get("radius_point")              # "A" или "C"
    radius_value = context.get("radius_value")              # R (int/float)
    right_angle_vertex = context.get("right_angle_vertex")  # "B"

    known_leg_name = context.get("known_leg_name")          # "AB" или "BC"
    known_leg_value = context.get("known_leg_value")        # число
    target_leg_name = context.get("target_leg_name")        # "AB" или "BC"

    if radius_value is None or known_leg_value is None:
        return _get_error_solution(task_data, reason="diameter_right_triangle: missing radius_value/known_leg_value")

    # --- вычисляем диаметр (гипотенузу) ---
    diameter_value = 2 * float(radius_value)
    hypotenuse = diameter_value  # алиас по смыслу

    # --- Пифагор: target^2 = hyp^2 - known^2 ---
    target_sq = hypotenuse ** 2 - float(known_leg_value) ** 2
    if target_sq < 0:
        return _get_error_solution(task_data, reason="diameter_right_triangle: negative under sqrt")

    target_val = math.sqrt(target_sq)

    # если получилось "почти целое" — приводим к int (красивый ответ)
    if abs(target_val - round(target_val)) < 1e-9:
        target_val = int(round(target_val))

    # если answer не пришёл из БД — берём вычисленный
    if answer is None:
        answer = target_val

    # --- FACTS для humanizer (важно: ключи, которые он ждёт) ---
    facts = {
        "narrative_type": "center_on_side",

        "radius_point": radius_point,      # ✅ ОБЯЗАТЕЛЬНО
        "radius_value": radius_value,

        "diameter_side": diameter_side,
        "diameter_value": diameter_value,

        "right_angle_vertex": right_angle_vertex,

        "known_leg_name": known_leg_name,
        "known_leg_value": known_leg_value,
        "target_leg_name": target_leg_name,

        "hypotenuse": hypotenuse,
        "hypotenuse_sq": hypotenuse ** 2,
        "known_leg_sq": known_leg_value ** 2,
        "target_leg_sq": target_sq,

        "answer": answer,
    }

    # help_image по контракту (добавляем file)
    help_image_file = task_data.get("help_image_file") or context.get("help_image_file")
    help_image = None
    if help_image_file:
        help_image = {
            "file": str(help_image_file),
            "schema": "diameter_right_triangle__center_on_side",
            "params": {
                "triangle": context.get("triangle"),
                "center": context.get("center"),
                "diameter_side": diameter_side,
                "right_angle_vertex": right_angle_vertex,
            }
        }

    return {
        "question_id": str(task_data.get("id")),
        "question_group": "GEOMETRY_16",
        "explanation_idea": "IDEA_DIAMETER_RIGHT_TRIANGLE",
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
# ПАТТЕРН 1.6: two_diameters_angles
# =========================================================================

def _solve_two_diameters_angles(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Паттерн 1.6: two_diameters_angles
    Нарративы:
      - find_inscribed
      - find_central
    """

    context: Dict[str, Any] = task_data.get("task_context") or {}
    answer = task_data.get("answer")

    narrative = context.get("narrative_type")

    if narrative not in ("find_inscribed", "find_central"):
        return _get_error_solution(
            task_data,
            reason=f"two_diameters_angles: unknown narrative '{narrative}'"
        )

    # --- базовые факты ---
    facts = {
        "narrative_type": narrative,
        "center": context.get("center"),
        "diameters": context.get("diameters"),
        "triangle_name": context.get("triangle_name"),
        "isosceles_sides": context.get("isosceles_sides"),
        "vertical_pair": context.get("vertical_pair"),
        "answer": answer,
    }

    # --- find_inscribed ---
    if narrative == "find_inscribed":
        facts.update(
            central_angle_name=context.get("central_angle_name"),
            central_angle_value=context.get("central_angle_value"),
            target_angle_name=context.get("target_angle_name"),
        )

    # --- find_central ---
    else:
        facts.update(
            base_angle_name=context.get("base_angle_name"),
            base_angle_value=context.get("base_angle_value"),
            target_angle_name=context.get("target_angle_name"),
        )

    help_image_file = task_data.get("help_image_file") or context.get("help_image_file")
    help_image = None
    if help_image_file:
        help_image = {
            "file": str(help_image_file),
            "schema": f"two_diameters_angles__{narrative}",
            "params": {
                "diameters": context.get("diameters"),
                "center": context.get("center"),
                "triangle": context.get("triangle_name"),
            }
        }

    return {
        "question_id": str(task_data.get("id")),
        "question_group": "GEOMETRY_16",
        "explanation_idea": f"IDEA_TWO_DIAMETERS_{narrative.upper()}",
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
# УТИЛИТЫ
# =========================================================================

def _get_error_solution(task_data: Dict[str, Any], *, reason: str) -> Dict[str, Any]:
    # Возвращаем структуру, максимально похожую на нормальный solution_core,
    # чтобы UI/логика вывода не падали на "особом" формате.
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
            "unit": "°",
        },
        "variables": {"error_reason": reason},
        "help_image": None,
        "hints": [],
    }


def _get_stub_solution(task_data: Dict[str, Any], pattern_name: str) -> Dict[str, Any]:
    # Заглушки делаем той же формы, что и боевой solution_core.
    answer = task_data.get("answer")
    return {
        "question_id": str(task_data.get("id")),
        "question_group": "GEOMETRY_16",
        "explanation_idea": f"IDEA_TODO_{pattern_name.upper()}",
        "calculation_steps": [],
        "final_answer": {
            "value_machine": answer,
            "value_display": str(answer) if answer is not None else "",
            "unit": "°",
        },
        "variables": {"pattern": pattern_name},
        "help_image": None,
        "hints": [],
    }

def _other_base_angle(angle: str) -> str:
    """
    Возвращает второй равный угол в равнобедренном треугольнике.
    Пример:
    OAB -> OBA
    OMN -> ONM
    """
    if not angle or len(angle) != 3:
        return angle
    return angle[0] + angle[2] + angle[1]

# =========================================================================
# HELPERS
# =========================================================================

def _is_central_angle_name(name: Optional[str]) -> bool:
    """
    Эвристика: центральный угол имеет вершину в центре окружности,
    обычно буква O присутствует в названии (AOC, DOF).
    """
    if not name:
        return False
    return "O" in str(name).upper()


def _arc_from_angle_name(angle_name: Optional[str]) -> Optional[str]:
    """
    Восстановление дуги по названию угла:
    - AOC -> AC
    - ABC -> AC (дуга по сторонам, не включая вершину)
    - DEF -> DF
    - DOF -> DF
    """
    if not angle_name:
        return None
    s = str(angle_name).strip().upper()
    if len(s) < 3:
        return None
    # берём 1-ю и 3-ю буквы
    return f"{s[0]}{s[2]}"


def _extract_ci_pair(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Достаём "как есть" из контекста. Поддерживаем несколько возможных ключей,
    чтобы не зависеть от версии валидатора/сырья.
    """
    return {
        "central_name": context.get("angle_central_name") or context.get("central_angle_name"),
        "central_val": context.get("angle_central_val") or context.get("central_angle_val"),
        "inscribed_name": context.get("angle_inscribed_name") or context.get("inscribed_angle_name"),
        "inscribed_val": context.get("angle_inscribed_val") or context.get("inscribed_angle_val"),
        "arc_name": context.get("arc_name"),
        "vertices": context.get("vertices"),
    }

# =========================================================================
# Вспомогательная функция для radius_chord_angles
# =========================================================================

def _swap_letters(angle_name: str) -> str:
    """Меняет местами 2-ю и 3-ю буквы (OAB -> OBA)."""
    if len(angle_name) == 3 and angle_name.startswith("O"):
        return f"O{angle_name[2]}{angle_name[1]}"
    return angle_name


# -----------------------------------------------------------------------------
# Коротко про изменения:
# 1) Добавлен help_image (file+schema+params) в solution_core (без description).
# 2) file берётся строго из сырья (help_image_file), чтобы совпадал с показанной картинкой.
# 3) Поддержаны алиасы narrative_type, чтобы не ломать БД/сырьё (same_arc_angles/find_diagonal_angle_abd).
# 4) Архитектура сохранена: solver отдаёт факты, humanizer строит текст, handler показывает UI.
# -----------------------------------------------------------------------------
