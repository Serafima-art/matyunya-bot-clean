# -*- coding: utf-8 -*-
"""
Решатель для задания 1-5, подтип: tires_q5
Соответствует стандарту ГОСТ-2025 "Золотой Стандарт Решателей"

Описание: Расчет процентного изменения пробега за один оборот колеса

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
    Решатель для подтипа tires_q5.

    Рассчитывает процентное изменение пробега за один оборот колеса.

    Args:
        task_data: ВЕСЬ task_package из FSM state

    Returns:
        solution_core в формате ГОСТ-2025
    """

    # --- БЛОК РАСПАКОВКИ task_package ---
    plot_data = task_data.get("plot_data", {})
    task_specific_data = plot_data.get("task_specific_data", {})
    task_5_data = task_specific_data.get("task_5_data", {})
    # ---

    original_marking = task_5_data.get("original_tire", "0/0 R0")
    replacement_marking = task_5_data.get("replacement_tire", "0/0 R0")
    pi = plot_data.get("constants", {}).get("pi", 3.14159)

    # Парсим и считаем диаметры
    original_B, original_H, original_d, _ = _parse_tire_marking(original_marking)
    replacement_B, replacement_H, replacement_d, _ = _parse_tire_marking(replacement_marking)
    original_diameter = calculate_tire_diameter(original_B, original_H, original_d)
    replacement_diameter = calculate_tire_diameter(replacement_B, replacement_H, replacement_d)

    # Считаем длины окружностей
    original_circumference = pi * original_diameter
    replacement_circumference = pi * replacement_diameter

    # Считаем процентное изменение
    if original_circumference == 0:
        percentage_change = 0.0
    else:
        percentage_change = ((replacement_circumference - original_circumference) / original_circumference) * 100

    # Формируем шаги
    calculation_steps = [
        {
            "step_number": 1,
            "description": f"Рассчитываем диаметр исходного колеса ({original_marking}).",
            "formula_representation": f"({original_B} · {original_H} ÷ 100) · 2 + {original_d} · 25.4",
            "calculation_result": f"{original_diameter:.2f} мм",
            "result_unit": "мм"
        },
        {
            "step_number": 2,
            "description": f"Рассчитываем диаметр нового колеса ({replacement_marking}).",
            "formula_representation": f"({replacement_B} · {replacement_H} ÷ 100) · 2 + {replacement_d} · 25.4",
            "calculation_result": f"{replacement_diameter:.2f} мм",
            "result_unit": "мм"
        },
        {
            "step_number": 3,
            "description": "Находим длину окружности исходного колеса (L = πD).",
            "formula_representation": f"{pi:.4f} · {original_diameter:.2f}",
            "calculation_result": f"{original_circumference:.2f} мм",
            "result_unit": "мм"
        },
        {
            "step_number": 4,
            "description": "Находим длину окружности нового колеса.",
            "formula_representation": f"{pi:.4f} · {replacement_diameter:.2f}",
            "calculation_result": f"{replacement_circumference:.2f} мм",
            "result_unit": "мм"
        },
        {
            "step_number": 5,
            "description": "Считаем, на сколько процентов новая длина больше/меньше старой.",
            "formula_representation": f"(({replacement_circumference:.2f} - {original_circumference:.2f}) ÷ {original_circumference:.2f}) · 100",
            "calculation_result": f"{percentage_change:.2f} %",
            "result_unit": "%"
        }
    ]

    final_value_rounded = round(percentage_change, 1)

    return {
        "question_group": "Q5_Tires_Mileage_Percentage",
        "question_id": "tires_q5_mileage_increase_percent",
        "explanation_idea": "Пробег за один оборот колеса — это его длина окружности. Чтобы найти процентное изменение, нужно сравнить длины окружностей нового и старого колес.",
        "calculation_steps": calculation_steps,
        "final_answer": {
            "value_machine": final_value_rounded,
            "value_display": str(final_value_rounded).replace('.', ','),
            "unit": "%"
        },
        "validation_code": f"return {final_value_rounded}",
        "hints": [
            "Длина окружности L = π · D.",
            "Для нахождения процента используй формулу: ((Новое - Старое) / Старое) · 100."
        ]
    }
