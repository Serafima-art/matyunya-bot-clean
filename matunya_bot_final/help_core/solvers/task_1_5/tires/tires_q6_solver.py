# -*- coding: utf-8 -*-
"""
Решатель для задания 1-5, подтип: tires_q6
Соответствует стандарту ГОСТ-2025 "Золотой Стандарт Решателей"

Описание: Выбор наиболее выгодного шиномонтажа

Автор: Матюня 🤖
Версия: 2.0 (ГОСТ-2025, Специализация)
"""

from typing import Dict, Any


# =============================================================================
# --- ГЛАВНАЯ ФУНКЦИЯ РЕШАТЕЛЯ ---
# =============================================================================

def solve(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Решатель для подтипа tires_q6.

    Выбирает наиболее выгодный шиномонтаж по минимальной общей стоимости.

    Args:
        task_data: ВЕСЬ task_package из FSM state

    Returns:
        solution_core в формате ГОСТ-2025
    """

    # --- БЛОК РАСПАКОВКИ task_package ---
    plot_data = task_data.get("plot_data", {})
    task_specific_data = plot_data.get("task_specific_data", {})
    # Данные для Q6 могут лежать в task_6_data или task_5_data
    task_data_q6 = task_specific_data.get("task_6_data", task_specific_data.get("task_5_data", {}))
    service_data = task_data_q6.get("service_choice_data", {})
    # ---

    services = service_data.get("services", [])
    wheels_count = service_data.get("wheels_count", 4)

    calculation_steps = []
    step_number = 1
    total_costs = {}

    # Рассчитываем стоимость для каждого шиномонтажа
    for service in services:
        name = service.get("name", "N/A")
        road_cost = service.get("road_cost", 0)
        ops = service.get("operations", {})
        work_per_wheel = sum(ops.values())

        # Шаг: стоимость работы
        total_work_cost = work_per_wheel * wheels_count
        calculation_steps.append({
            "step_number": step_number,
            "description": f"Считаем стоимость работы в шиномонтаже '{name}'.",
            "formula_representation": f"{work_per_wheel} · {wheels_count}",
            "calculation_result": f"{total_work_cost:.2f} руб",
            "result_unit": "руб"
        })
        step_number += 1

        # Шаг: общая стоимость (дорога + работа)
        total_cost = total_work_cost + road_cost
        total_costs[name] = total_cost
        calculation_steps.append({
            "step_number": step_number,
            "description": f"Суммарная стоимость для '{name}' (работа + дорога).",
            "formula_representation": f"{total_work_cost:.2f} + {road_cost}",
            "calculation_result": f"{total_cost:.2f} руб",
            "result_unit": "руб"
        })
        step_number += 1

    # Шаг: сравнение и выбор минимальной стоимости
    if total_costs:
        min_cost = min(total_costs.values())
        costs_str = ", ".join([f"{cost:.2f}" for cost in total_costs.values()])
        calculation_steps.append({
            "step_number": step_number,
            "description": "Сравниваем общие затраты и выбираем минимальную.",
            "formula_representation": f"min({costs_str})",
            "calculation_result": f"{min_cost:.2f} руб",
            "result_unit": "руб"
        })
    else:
        min_cost = 0

    final_value_rounded = round(min_cost)

    return {
        "question_group": "Q6_Tires_Service_Optimization",
        "question_id": "tires_q6_cheapest_service",
        "explanation_idea": "Чтобы выбрать самый выгодный шиномонтаж, нужно для каждого варианта посчитать полную стоимость: работа плюс дорога. А потом сравнить.",
        "calculation_steps": calculation_steps,
        "final_answer": {
            "value_machine": final_value_rounded,
            "value_display": str(final_value_rounded).replace('.', ','),
            "unit": "руб"
        },
        "validation_code": f"return {final_value_rounded}",
        "hints": [
            "Не забудь учесть стоимость дороги.",
            "Стоимость работы нужно умножить на количество колес."
        ]
    }
