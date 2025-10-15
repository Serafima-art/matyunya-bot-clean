# -*- coding: utf-8 -*-
"""
Решатель для задания 1-5, подтип: tires_q4
Соответствует стандарту ГОСТ-2025 "Золотой Стандарт Решателей"

Описание: Расчет изменения диаметра колеса при замене шин

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
    Решатель для подтипа tires_q4.

    Рассчитывает изменение диаметра колеса при замене шин.

    Args:
        task_data: ВЕСЬ task_package из FSM state

    Returns:
        solution_core в формате ГОСТ-2025
    """

    # --- БЛОК РАСПАКОВКИ task_package ---
    plot_data = task_data.get("plot_data", {})
    task_specific_data = plot_data.get("task_specific_data", {})
    task_4_data = task_specific_data.get("task_4_data", {})
    # ---

    original_marking = task_4_data.get("original_tire", "0/0 R0")
    replacement_marking = task_4_data.get("replacement_tire", "0/0 R0")

    # Парсим обе шины
    original_B, original_H, original_d, _ = _parse_tire_marking(original_marking)
    replacement_B, replacement_H, replacement_d, _ = _parse_tire_marking(replacement_marking)

    # Рассчитываем диаметры
    original_diameter = calculate_tire_diameter(original_B, original_H, original_d)
    replacement_diameter = calculate_tire_diameter(replacement_B, replacement_H, replacement_d)

    # Находим изменение (может быть положительным или отрицательным)
    diameter_change = replacement_diameter - original_diameter

    # Формируем шаги расчета
    calculation_steps = [
        {
            "step_number": 1,
            "description": f"Сначала рассчитаем диаметр исходного колеса ({original_marking}).",
            "formula_representation": f"({original_B} · {original_H} ÷ 100) · 2 + {original_d} · 25.4",
            "calculation_result": f"{original_diameter:.2f} мм",
            "result_unit": "мм"
        },
        {
            "step_number": 2,
            "description": f"Теперь рассчитаем диаметр нового колеса ({replacement_marking}).",
            "formula_representation": f"({replacement_B} · {replacement_H} ÷ 100) · 2 + {replacement_d} · 25.4",
            "calculation_result": f"{replacement_diameter:.2f} мм",
            "result_unit": "мм"
        },
        {
            "step_number": 3,
            "description": "Находим, на сколько новый диаметр больше или меньше старого.",
            "formula_representation": f"{replacement_diameter:.2f} - {original_diameter:.2f}",
            "calculation_result": f"{diameter_change:.2f} мм",
            "result_unit": "мм"
        }
    ]

    final_value_rounded = round(diameter_change, 1)

    return {
        "question_group": "Q4_Tires_Diameter_Increase",
        "question_id": "tires_q4_diameter_increase_mm",
        "explanation_idea": "Чтобы узнать, на сколько изменится диаметр колеса, нам нужно рассчитать диаметр старого и нового колеса, а затем найти разницу между ними.",
        "calculation_steps": calculation_steps,
        "final_answer": {
            "value_machine": final_value_rounded,
            "value_display": str(final_value_rounded).replace('.', ','),
            "unit": "мм"
        },
        "validation_code": f"return {final_value_rounded}",
        "hints": [
            "Эта задача очень похожа на Q2, но здесь всегда ищется разница диаметров.",
            "Положительное значение означает увеличение диаметра, отрицательное - уменьшение."
        ]
    }
