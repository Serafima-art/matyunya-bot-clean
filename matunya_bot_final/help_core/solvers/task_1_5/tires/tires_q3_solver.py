# -*- coding: utf-8 -*-
"""
Решатель для задания 1-5, подтип: tires_q3
Соответствует стандарту ГОСТ-2025 "Золотой Стандарт Решателей"

Описание: Расчет диаметра колеса в миллиметрах

Автор: Матюня 🤖
Версия: 2.0 (ГОСТ-2025, Специализация)
"""

from typing import Dict, Any


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
    Решатель для подтипа tires_q3.

    Рассчитывает диаметр колеса в миллиметрах.

    Args:
        task_data: ВЕСЬ task_package из FSM state

    Returns:
        solution_core в формате ГОСТ-2025
    """

    # --- БЛОК РАСПАКОВКИ task_package ---
    plot_data = task_data.get("plot_data", {})
    task_specific_data = plot_data.get("task_specific_data", {})
    task_3_data = task_specific_data.get("task_3_data", {})
    # ---

    tire_marking = task_3_data.get("tire_marking", "0/0 R0")

    # Парсим маркировку
    factory_B, factory_H, factory_d, factory_marking = _parse_tire_marking(tire_marking)

    # Рассчитываем диаметр в мм
    factory_diameter_mm = calculate_tire_diameter(factory_B, factory_H, factory_d)

    # Формируем шаги расчета
    calculation_steps = [
        {
            "step_number": 1,
            "description": f"Рассчитаем диаметр колеса ({factory_marking}) в миллиметрах, используя стандартную формулу.",
            "formula_representation": f"({factory_B} · {factory_H} ÷ 100) · 2 + {factory_d} · 25.4",
            "calculation_result": f"{factory_diameter_mm:.2f} мм",
            "result_unit": "мм"
        }
    ]

    final_value_rounded = round(factory_diameter_mm, 2)

    return {
        "question_group": "Q3_Tires_Diameter_Calculation",
        "question_id": "tires_q3_factory_diameter_mm",
        "explanation_idea": "Нам нужно найти диаметр заводского колеса. Для этого используем стандартную формулу для расчета диаметра в миллиметрах.",
        "calculation_steps": calculation_steps,
        "final_answer": {
            "value_machine": final_value_rounded,
            "value_display": str(final_value_rounded).replace('.', ','),
            "unit": "мм"
        },
        "validation_code": f"return {final_value_rounded}",
        "hints": [
            "Формула диаметра колеса: (Ширина · Профиль / 100) · 2 + Диаметр диска · 25.4.",
            "Внимательно проверь, в каких единицах (мм или см) требуется дать ответ в задании."
        ]
    }
