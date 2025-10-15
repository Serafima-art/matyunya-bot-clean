# -*- coding: utf-8 -*-
"""
Решатель для задания 1-5, подтип: tires_q1
Соответствует стандарту ГОСТ-2025 "Золотой Стандарт Решателей"

Описание: Поиск минимальной/максимальной ширины шины или диаметра диска
         по таблице допустимых размеров.

Автор: Матюня 🤖
Версия: 2.0 (ГОСТ-2025, Специализация)
"""

import re
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


# =============================================================================
# --- ГЛАВНАЯ ФУНКЦИЯ РЕШАТЕЛЯ ---
# =============================================================================

def solve(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Решатель для подтипа tires_q1.

    Ищет минимальную/максимальную ширину шины или диаметр диска
    по таблице допустимых размеров.

    Args:
        task_data: ВЕСЬ task_package из FSM state

    Returns:
        solution_core в формате ГОСТ-2025
    """

    # --- БЛОК РАСПАКОВКИ task_package ---
    plot_data = task_data.get("plot_data", {})
    task_specific_data = plot_data.get("task_specific_data", {})
    task_1_data = task_specific_data.get("task_1_data", {})
    allowed_sizes_table = plot_data.get("allowed_tire_sizes", {})
    # ---

    question_type = task_1_data.get("question_type", "")

    # Определяем, что ищем
    if question_type in ["minimum_width", "maximum_width"]:
        column_to_search = "tire_width"
        disk_in = task_1_data.get("target_diameter", 0)
        tire_width_mm = None
    elif question_type in ["minimum_diameter", "maximum_diameter"]:
        column_to_search = "disk_diameter"
        tire_width_mm = task_1_data.get("target_width", 0)
        disk_in = None
    else:
        error_msg = f"Неизвестный question_type для Q1: '{question_type}'. "
        error_msg += f"Ожидаемые значения: minimum_width, maximum_width, minimum_diameter, maximum_diameter"
        raise ValueError(error_msg)

    search_type = "min" if "minimum" in question_type else "max"
    question_id = task_1_data.get("question_id", "tires_q1_unknown")
    calculation_steps = []

    # ЛОГИКА ПОИСКА ПО ШИРИНЕ ШИНЫ
    if column_to_search == "tire_width":
        disk_key = str(disk_in)
        tire_sizes = []
        widths = []

        for width_str, diameter_data in allowed_sizes_table.items():
            if isinstance(diameter_data, dict) and disk_key in diameter_data:
                sizes_for_diameter = diameter_data.get(disk_key, [])
                tire_sizes.extend(sizes_for_diameter)

                for size in sizes_for_diameter:
                    if size:
                        width_match = re.match(r'(\d+)/', str(size))
                        if width_match:
                            widths.append(int(width_match.group(1)))
                        else:
                            try:
                                widths.append(int(width_str))
                            except ValueError:
                                pass

        if not tire_sizes:
            raise ValueError(f"Диаметр диска {disk_in} дюймов не найден в таблице")

        calculation_steps.append({
            "step_number": 1,
            "description": f"Находим все размеры шин для диска диаметром {disk_in} дюймов",
            "formula_representation": "Не требуется",
            "calculation_result": f"Размеры: {', '.join(tire_sizes)}",
            "result_unit": ""
        })

        calculation_steps.append({
            "step_number": 2,
            "description": "Извлекаем ширины шин из размеров",
            "formula_representation": "Не требуется",
            "calculation_result": f"Ширины: {', '.join(map(str, widths))} мм",
            "result_unit": "мм"
        })

        if not widths:
            raise ValueError(f"Не удалось извлечь ширины для диаметра {disk_in} дюймов")

        if search_type == "min":
            result_width = min(widths)
            step3_desc = "Находим наименьшую ширину среди найденных значений"
            explanation_idea = f"Для диска диаметром {disk_in} дюймов ищем шину с наименьшей шириной среди доступных размеров."
        else:
            result_width = max(widths)
            step3_desc = "Находим наибольшую ширину среди найденных значений"
            explanation_idea = f"Для диска диаметром {disk_in} дюймов ищем шину с наибольшей шириной среди доступных размеров."

        calculation_steps.append({
            "step_number": 3,
            "description": step3_desc,
            "formula_representation": "Не требуется",
            "calculation_result": f"{result_width} мм",
            "result_unit": "мм"
        })

        final_value = result_width
        final_unit = "мм"
        validation_code = f"return {result_width}"
        hints = [
            f"Для диска {disk_in}\" доступны размеры: {', '.join(tire_sizes)}",
            "Ширина шины указывается первым числом в размере (например, в размере 205/45 ширина = 205 мм)"
        ]

    # ЛОГИКА ПОИСКА ПО ДИАМЕТРУ ДИСКА
    else:
        target_width_str = str(tire_width_mm)
        found_diameters = []
        found_sizes = []

        for width_str, diameter_data in allowed_sizes_table.items():
            if isinstance(diameter_data, dict):
                width_matches = False

                if width_str == target_width_str:
                    width_matches = True

                if not width_matches:
                    for diameter, sizes in diameter_data.items():
                        for size in sizes:
                            if size:
                                width_match = re.match(r'(\d+)/', str(size))
                                if width_match and width_match.group(1) == target_width_str:
                                    width_matches = True
                                    break
                        if width_matches:
                            break

                if width_matches:
                    for diameter, sizes in diameter_data.items():
                        if sizes:
                            try:
                                diameter_int = int(diameter)
                                if diameter_int not in found_diameters:
                                    found_diameters.append(diameter_int)
                                    found_sizes.append(f"{diameter}\" (ширина {width_str})")
                            except ValueError:
                                pass

        calculation_steps.append({
            "step_number": 1,
            "description": f"Ищем все диаметры дисков, для которых доступна ширина шины {tire_width_mm} мм",
            "formula_representation": "Не требуется",
            "calculation_result": f"Найдены диаметры: {', '.join(found_sizes)}",
            "result_unit": ""
        })

        if not found_diameters:
            raise ValueError(f"Ширина шины {tire_width_mm} мм не найдена в таблице")

        calculation_steps.append({
            "step_number": 2,
            "description": "Извлекаем значения диаметров дисков",
            "formula_representation": "Не требуется",
            "calculation_result": f"Диаметры: {', '.join(map(str, found_diameters))} дюймов",
            "result_unit": "дюймы"
        })

        if search_type == "min":
            result_diameter = min(found_diameters)
            step3_desc = "Находим наименьший диаметр среди найденных значений"
            explanation_idea = f"Для шины шириной {tire_width_mm} мм ищем диск с наименьшим диаметром среди доступных размеров."
        else:
            result_diameter = max(found_diameters)
            step3_desc = "Находим наибольший диаметр среди найденных значений"
            explanation_idea = f"Для шины шириной {tire_width_mm} мм ищем диск с наибольшим диаметром среди доступных размеров."

        calculation_steps.append({
            "step_number": 3,
            "description": step3_desc,
            "formula_representation": "Не требуется",
            "calculation_result": f"{result_diameter} дюймов",
            "result_unit": "дюймы"
        })

        final_value = result_diameter
        final_unit = "дюймы"
        validation_code = f"return {result_diameter}"
        hints = [
            f"Ширина шины {tire_width_mm} мм доступна для дисков: {', '.join(map(str, found_diameters))}\"",
            "Диаметр диска указывается в дюймах и определяет совместимость с размером шины"
        ]

    return {
        "question_group": "Q1_TABLE",
        "question_id": question_id,
        "explanation_idea": explanation_idea,
        "calculation_steps": calculation_steps,
        "final_answer": {
            "value_machine": final_value,
            "value_display": f"{final_value}",
            "unit": final_unit
        },
        "validation_code": validation_code,
        "hints": hints
    }
