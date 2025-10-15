# -*- coding: utf-8 -*-
"""
Решатель для задания 1-5, подтип: tires_q2
Соответствует стандарту ГОСТ-2025 "Золотой Стандарт Решателей"

Описание: Расчет разницы в диаметрах/радиусах двух колес

Автор: Матюня 🤖
Версия: 2.0 (ГОСТ-2025, Специализация)
"""

from typing import Dict, Any
from matunya_bot_final.utils.text_formatters import bold_numbers


# =============================================================================
# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
# =============================================================================

def _parse_tire_marking(tire_str: str) -> tuple:
    """
    Парсит строку маркировки шины, например, '205/50 R17'.
    Возвращает кортеж (ширина, профиль, диаметр, исходная_строка).
    """
    if not tire_str or tire_str == "0/0 R0":
        return 0, 0, 0, ""
    try:
        parts = tire_str.replace('R', ' ').replace('/', ' ').split()
        if len(parts) < 3:
            return 0, 0, 0, tire_str

        width = int(parts[0])
        profile = int(parts[1])
        diameter = int(parts[2])
        return width, profile, diameter, tire_str
    except (ValueError, IndexError):
        return 0, 0, 0, tire_str


def calculate_tire_diameter(B: float, H: float, d: float) -> float:
    """
    Вспомогательная функция для расчета диаметра колеса в миллиметрах.

    Args:
        B (float): Ширина шины в мм
        H (float): Высота профиля в процентах
        d (float): Диаметр диска в дюймах

    Returns:
        float: Диаметр колеса в миллиметрах
    """
    return (B * H / 100) * 2 + d * 25.4


# =============================================================================
# --- ГЛАВНАЯ ФУНКЦИЯ РЕШАТЕЛЯ ---
# =============================================================================

def solve(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Решатель для подтипа tires_q2.

    Рассчитывает разницу в диаметрах или радиусах двух колес.

    Args:
        task_data: ВЕСЬ task_package из FSM state

    Returns:
        solution_core в формате ГОСТ-2025
    """

    # --- БЛОК РАСПАКОВКИ task_package ---
    plot_data = task_data.get("plot_data", {})
    task_specific_data = plot_data.get("task_specific_data", {})
    task_2_data = task_specific_data.get("task_2_data", {})
    # ---

    # Извлекаем маркировки шин
    tire_1_marking = task_2_data.get("tire_1", "0/0 R0")
    tire_2_marking = task_2_data.get("tire_2", "0/0 R0")
    comparison_type = task_2_data.get("comparison_type", "")

    # Парсим обе шины
    factory_B, factory_H, factory_d, factory_marking = _parse_tire_marking(tire_1_marking)
    new_B, new_H, new_d, new_marking = _parse_tire_marking(tire_2_marking)

    # Рассчитываем диаметры
    factory_diameter = calculate_tire_diameter(factory_B, factory_H, factory_d)
    new_diameter = calculate_tire_diameter(new_B, new_H, new_d)

    is_radius_question = "radius" in comparison_type.lower()

    if factory_diameter >= new_diameter:
        diameter_diff = factory_diameter - new_diameter
        diff_formula = f"{factory_diameter:.2f} - {new_diameter:.2f}"
    else:
        diameter_diff = new_diameter - factory_diameter
        diff_formula = f"{new_diameter:.2f} - {factory_diameter:.2f}"

    # Формируем шаги расчета
    calculation_steps = [
        {
            "step_number": 1,
            "description": bold_numbers(f"Сначала рассчитаем диаметр первого колеса ({factory_marking})."),
            "formula_representation": f"({factory_B} · {factory_H} ÷ 100) · 2 + {factory_d} · 25.4",
            "calculation_result": f"{factory_diameter:.2f} мм",
            "result_unit": "мм"
        },
        {
            "step_number": 2,
            "description": f"Теперь рассчитаем диаметр второго колеса ({new_marking}).",
            "formula_representation": f"({new_B} · {new_H} ÷ 100) · 2 + {new_d} · 25.4",
            "calculation_result": f"{new_diameter:.2f} мм",
            "result_unit": "мм"
        },
        {
            "step_number": 3,
            "description": "Теперь найдем разницу в диаметрах.",
            "formula_representation": diff_formula,
            "calculation_result": f"{diameter_diff:.2f} мм",
            "result_unit": "мм"
        }
    ]

    if is_radius_question:
        radius_diff = diameter_diff / 2
        calculation_steps.append({
            "step_number": 4,
            "description": "Вопрос был про разницу радиусов. Радиус — это половина диаметра, поэтому разницу диаметров нужно поделить на 2.",
            "formula_representation": f"{diameter_diff:.2f} ÷ 2",
            "calculation_result": f"{radius_diff:.2f} мм",
            "result_unit": "мм"
        })
        final_value = radius_diff
        question_id = "tires_q2_radius_diff"
        explanation_idea = "Чтобы сравнить радиусы двух колес, нам нужно найти полный диаметр каждого, найти разницу и поделить её на 2."
    else:
        final_value = diameter_diff
        question_id = "tires_q2_diameter_diff"
        explanation_idea = "Чтобы сравнить диаметры двух колес, нам нужно найти полный диаметр каждого из них, а затем найти разницу."

    final_value_rounded = round(final_value, 2)

    return {
        "question_group": "Q2_Tires_Comparison",
        "question_id": question_id,
        "explanation_idea": explanation_idea,
        "calculation_steps": calculation_steps,
        "final_answer": {
            "value_machine": final_value_rounded,
            "value_display": str(final_value_rounded).replace('.', ','),
            "unit": "мм"
        },
        "validation_code": f"return {final_value_rounded}",
        "hints": [
            "Формула диаметра колеса: (Ширина · Профиль / 100) · 2 + Диаметр диска · 25.4.",
            "1 дюйм = 25.4 мм.",
            "Внимательно читай вопрос: спрашивают про разницу диаметров или радиусов."
        ]
    }
