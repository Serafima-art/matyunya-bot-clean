# matunya_bot_final/help_core/solvers/task_16/central_and_inscribed_angles_solver.py
# -*- coding: utf-8 -*-

from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


async def solve(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Решатель для Темы 1: Центральные и вписанные углы.

    Вход: task_data (pattern, task_context, answer, id, ...).
    Выход: solution_core (по ГОСТ-2026), без анализа текста задачи.
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
    if narrative_type == "opposite_sum":
        facts.update(
            angle_given_name=context.get("angle_given_name"),
            angle_given_val=context.get("angle_given_val"),
            angle_target_name=context.get("angle_target_name"),
        )

    elif narrative_type == "part_sum":
        facts.update(
            angle_whole_name=context.get("angle_whole_name"),
            angle_known_part_name=context.get("angle_known_part_name"),
            angle_known_part_val=context.get("angle_known_part_val"),
            angle_hidden_part_name=context.get("angle_hidden_part_name"),
            angle_alien_name=context.get("angle_alien_name"),
            angle_alien_val=context.get("angle_alien_val"),
            arc_name=context.get("arc_name"),
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
        )

    else:
        # Не ломаем пайплайн, но явно подсвечиваем проблему.
        logger.error("Unknown narrative_type for cyclic_quad_angles: %r", narrative_type)
        return _get_error_solution(task_data, reason=f"Unknown narrative_type: {narrative_type}")

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
        "variables": facts,  # передаём факты, а не текст
        "hints": [],
    }


# =========================================================================
# ЗАГЛУШКИ ДЛЯ ОСТАЛЬНЫХ ПАТТЕРНОВ
# =========================================================================

def _solve_central_inscribed(task_data: Dict[str, Any]) -> Dict[str, Any]:
    return _get_stub_solution(task_data, "central_inscribed")


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
        "hints": [],
    }


# -----------------------------------------------------------------------------
# Почему эта версия лучше (коротко):
# 1) Solver больше не "рисует текст" (given_text/target_text) — он отдаёт только факты.
# 2) explanation_idea отделён от narrative_type (IDEA_*) — гибче для будущих идей/вариантов.
# 3) Ошибки/заглушки возвращают единый формат solution_core — меньше шансов словить legacy-хаос.
# -----------------------------------------------------------------------------
