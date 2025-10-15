"""
ВАЛИДАТОР ДЛЯ ЗАДАНИЯ 11 (match_signs_a_c)
Совместим с генератором v3.0 (graphs в func_data, не в source_plot)
"""

from typing import Tuple, List


def validate_task_11_match_signs_a_c(task: dict) -> Tuple[bool, List[str]]:
    """Главная функция валидатора."""
    errors = []

    if "topic" not in task:
        errors.append("Missing required key 'topic'.")
    
    if task.get("task_type") != 11:
        errors.append("task_type != 11")
        return len(errors) == 0, errors
    
    if task.get("subtype") != "match_signs_a_c":
        errors.append("Неизвестный подтип")
        return len(errors) == 0, errors
    
    return _validate_task_11_match_signs_a_c(task)


def _validate_task_11_match_signs_a_c(task: dict) -> Tuple[bool, List[str]]:
    """Валидация для подтипа match_signs_a_c с локальной перенумеровкой (1,2,3)."""
    errors = []

    # 1. Общие проверки
    if "func_data" not in task or not isinstance(task["func_data"], list):
        errors.append("Нет func_data или не список")
    if len(task["func_data"]) != 3:
        errors.append("Должно быть 3 графика")
    if not (isinstance(task.get("x_lim"), list) and len(task["x_lim"]) == 2):
        errors.append("x_lim должен быть списком длины 2")
    if not (isinstance(task.get("y_lim"), list) and len(task["y_lim"]) == 2):
        errors.append("y_lim должен быть списком длины 2")

    # 2. Проверка source_plot
    sp = task.get("source_plot")
    if not sp:
        errors.append("source_plot отсутствует")
    else:
        params = sp.get("params", {})
        if "labels" not in params or len(params.get("labels", [])) != 3:
            errors.append("labels должен быть списком из 3 элементов")
        if "options" not in params or len(params.get("options", {})) != 3:
            errors.append("options должен быть словарём из 3 элементов (после перенумеровки)")

    # 3. Проверка ответов
    answer = task.get("answer")
    if answer is None:
        errors.append("Отсутствует answer")
    else:
        answer_list = answer if isinstance(answer, list) else str(answer).split()
        if len(answer_list) != 3:
            errors.append("Должно быть 3 ответа")
        else:
            # 4. Логическая проверка (только если нет критических ошибок)
            if not errors:
                params = sp.get("params", {})
                displayed_options = params["options"]  # {"1": "...", "2": "...", "3": "..."}
                global_to_local: dict[str, str] = {}
                
                for local_num, desc in displayed_options.items():
                    if "a > 0, c > 0" in desc:
                        global_to_local["1"] = local_num
                    elif "a > 0, c < 0" in desc:
                        global_to_local["2"] = local_num
                    elif "a < 0, c > 0" in desc:
                        global_to_local["3"] = local_num
                    elif "a < 0, c < 0" in desc:
                        global_to_local["4"] = local_num

                for i, func_data in enumerate(task["func_data"]):
                    coeffs = func_data.get("coeffs")
                    if not isinstance(coeffs, dict):
                        errors.append(f"func_data[{i}] не содержит coeffs")
                        continue
                    
                    missing_keys = [key for key in ("a", "c") if key not in coeffs]
                    if missing_keys:
                        errors.append(f"func_data[{i}] отсутствуют коэффициенты: {', '.join(missing_keys)}")
                        continue

                    a = coeffs["a"]
                    c = coeffs["c"]

                    try:
                        expected_global = (
                            "1" if (a > 0 and c > 0) else
                            "2" if (a > 0 and c < 0) else
                            "3" if (a < 0 and c > 0) else "4"
                        )
                    except TypeError as exc:
                        errors.append(f"func_data[{i}] содержит некорректные коэффициенты: {exc}")
                        continue

                    expected_local = global_to_local.get(expected_global)
                    if not expected_local:
                        errors.append(f"Не найдено отображение для глобального варианта {expected_global}")
                        continue

                    if answer_list[i] != expected_local:
                        errors.append(
                            f"Ответ {i + 1} неверен: ожидали {expected_local}, получено {answer_list[i]} (a={a}, c={c})"
                        )

    return len(errors) == 0, errors
