# matunya_bot_final/help_core/solvers/task_16/central_and_inscribed_angles_solver.py
# -*- coding: utf-8 -*-

from __future__ import annotations

import logging
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
# ЗАГЛУШКИ ДЛЯ ОСТАЛЬНЫХ ПАТТЕРНОВ
# =========================================================================


def _solve_radius_chord_angles(task_data: Dict[str, Any]) -> Dict[str, Any]:
    return _get_stub_solution(task_data, "radius_chord_angles")


def _solve_arc_length_ratio(task_data: Dict[str, Any]) -> Dict[str, Any]:
    return _get_stub_solution(task_data, "arc_length_ratio")


def _solve_diameter_right_triangle(task_data: Dict[str, Any]) -> Dict[str, Any]:
    return _get_stub_solution(task_data, "diameter_right_triangle")


def _solve_two_diameters_angles(task_data: Dict[str, Any]) -> Dict[str, Any]:
    return _get_stub_solution(task_data, "two_diameters_angles")


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


# -----------------------------------------------------------------------------
# Коротко про изменения:
# 1) Добавлен help_image (file+schema+params) в solution_core (без description).
# 2) file берётся строго из сырья (help_image_file), чтобы совпадал с показанной картинкой.
# 3) Поддержаны алиасы narrative_type, чтобы не ломать БД/сырьё (same_arc_angles/find_diagonal_angle_abd).
# 4) Архитектура сохранена: solver отдаёт факты, humanizer строит текст, handler показывает UI.
# -----------------------------------------------------------------------------
