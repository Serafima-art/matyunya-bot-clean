"""
Валидатор подтипа form_match_mixed для задания №11 ОГЭ.
"""

import re
import numpy as np
from typing import Dict, Any, List, Tuple


def validate_task_11_form_match_mixed(task: Dict[str, Any]) -> Tuple[bool, List[str]]:
    errors = []

    if "topic" not in task:
        errors.append("Missing required key 'topic'.")

    # --- 1. Базовая структура
    if task.get("task_type") != 11:
        errors.append("task_type должен быть 11")
    if task.get("subtype") != "form_match_mixed":
        errors.append("subtype должен быть 'form_match_mixed'")

    # --- 2. Проверка source_plot
    source_plot = task.get("source_plot", {})
    params = source_plot.get("params", {})

    if source_plot.get("plot_id") != "form_match_mixed":
        errors.append("plot_id должен быть 'form_match_mixed'")

    labels = params.get("labels", [])
    if labels != ["A", "Б", "В"]:
        errors.append("labels должны быть ['A','Б','В']")

    graphs = params.get("graphs", [])
    if not isinstance(graphs, list) or len(graphs) != 3:
        errors.append("graphs должно быть списком из 3 элементов")

    options = params.get("options", {})
    if not isinstance(options, dict) or set(options.keys()) != {"1", "2", "3"}:
        errors.append("options должны содержать ключи '1'...'3'")
    if len(set(options.values())) != 3:
        errors.append("options должны содержать 3 уникальные формулы")

    # --- 3. Проверка answer
    answer = task.get("answer", [])
    if not isinstance(answer, list) or len(answer) != 3:
        errors.append("answer должен быть списком из 3 строк")
    else:
        for a in answer:
            if a not in {"1", "2", "3"}:
                errors.append(f"answer содержит некорректное значение: {a}")

    # --- 4. Проверка func_data
    func_data = task.get("func_data", [])
    if not isinstance(func_data, list) or len(func_data) != 3:
        errors.append("func_data должен содержать 3 элемента")
    else:
        for i, f in enumerate(func_data):
            if "func" not in f or not callable(f["func"]):
                errors.append(f"func_data[{i}] должен содержать вызываемую функцию")
            if "label" not in f or not isinstance(f["label"], str):
                errors.append(f"func_data[{i}] должен содержать строку label")
            if "color" not in f or not isinstance(f["color"], str):
                errors.append(f"func_data[{i}] должен содержать строку color")
            else:
                try:
                    xx = np.linspace(-3, 3, 10)
                    _ = f["func"](xx)
                except Exception as e:
                    errors.append(f"func_data[{i}].func вызвал ошибку: {e}")

    # --- 5. Проверка типов функций
    option_types = {_classify_formula(v) for v in options.values()}
    answer_types = {_classify_formula(options[a]) for a in answer}

    if len(answer_types) != 3:
        errors.append(f"в ответах должно быть 3 разных типа функций, найдено: {answer_types}")
    if len(option_types) != 3:
        errors.append("в options должно быть 3 уникальных типа (без дистрактора)")

    return len(errors) == 0, errors


def _classify_formula(formula: str) -> str:
    """Определяет тип функции по строке."""
    f = formula.replace(" ", "")
    if "√x" in f:
        return "sqrt"
    if "/x" in f:
        return "hyperbola"
    if "x²" in f:
        return "parabola"
    if "x" in f:
        return "linear"
    return "unknown"
