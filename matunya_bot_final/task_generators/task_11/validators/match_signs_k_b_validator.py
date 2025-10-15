"""
Валидатор подтипа match_signs_k_b для задания 11 (линейные функции).
Проверяет корректность формата JSON, наличие нужных полей, правильность опций.
"""

from typing import Dict, List, Tuple


def validate_task_11_match_signs_k_b(task: Dict) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    if "topic" not in task:
        errors.append("Missing required key 'topic'.")

    # --- Основные обязательные поля ---
    required_fields = [
        "id", "task_id", "task_type", "subtype",
        "category", "subcategory", "text", "answer",
        "func_data", "x_lim", "y_lim", "source_plot"
    ]
    for field in required_fields:
        if field not in task:
            errors.append(f"❌ Нет обязательного поля: {field}")

    if task.get("task_type") != 11:
        errors.append("❌ task_type должен быть 11")

    if task.get("subtype") != "match_signs_k_b":
        errors.append("❌ subtype должен быть match_signs_k_b")

    # --- Проверка структуры answer ---
    answer = task.get("answer")
    if not isinstance(answer, list) or len(answer) != 3:
        errors.append("❌ answer должен быть списком из трёх элементов (для A, Б, В)")
    else:
        if not all(isinstance(x, str) for x in answer):
            errors.append("❌ answer должен содержать только строки")
        # ✅ ИСПРАВЛЕНО: допускаем '1','2','3','4' - любые локальные номера
        if not all(x in ["1", "2", "3", "4"] for x in answer):
            errors.append("❌ answer должен содержать только '1','2','3','4' (локальные номера)")

    # --- Проверка func_data ---
    func_data = task.get("func_data", [])
    if not isinstance(func_data, list) or len(func_data) != 3:
        errors.append("❌ func_data должен быть списком из трёх функций")
    else:
        for i, fd in enumerate(func_data):
            # Проверка наличия коэффициентов (для JSON-структуры)
            if "coeffs" not in fd:
                errors.append(f"❌ func_data[{i}] отсутствует ключ coeffs")
            else:
                coeffs = fd["coeffs"]
                if not isinstance(coeffs, dict) or "k" not in coeffs or "b" not in coeffs:
                    errors.append(f"❌ func_data[{i}].coeffs должен содержать k и b")
                else:
                    # Проверка диапазонов коэффициентов
                    k = coeffs.get("k")
                    b = coeffs.get("b")
                    if k not in [-3, -2, -1, 1, 2, 3]:
                        errors.append(f"❌ func_data[{i}].k должен быть из {{-3,-2,-1,1,2,3}}, получен: {k}")
                    if b not in [-5, -4, -3, -2, 2, 3, 4, 5]:
                        errors.append(f"❌ func_data[{i}].b должен быть из {{-5,-4,-3,-2,2,3,4,5}}, получен: {b}")

    # --- Проверка уникальности комбинаций знаков ---
    if len(func_data) == 3 and all("coeffs" in fd for fd in func_data):
        sign_pairs = []
        for fd in func_data:
            k = fd["coeffs"].get("k", 0)
            b = fd["coeffs"].get("b", 0)
            sign_pairs.append((1 if k > 0 else -1, 1 if b > 0 else -1))

        if len(set(sign_pairs)) != 3:
            errors.append("❌ Три графика должны иметь разные комбинации знаков (k,b)")

    # --- Проверка source_plot ---
    source_plot = task.get("source_plot", {})
    if "params" not in source_plot:
        errors.append("❌ В source_plot должен быть params")
    else:
        params = source_plot["params"]
        if "labels" not in params or len(params.get("labels", [])) != 3:
            errors.append("❌ params.labels должен содержать три метки (A, Б, В)")
        if "graphs" not in params or len(params.get("graphs", [])) != 3:
            errors.append("❌ params.graphs должен содержать три пути к графикам")
        if "options" not in params or not isinstance(params["options"], dict):
            errors.append("❌ params.options должен быть словарём")
        else:
            opt_keys = set(params["options"].keys())
            # ✅ ИСПРАВЛЕНО: допускаем 3 или 4 варианта (локальная перенумерация)
            if not opt_keys.issubset({"1", "2", "3", "4"}):
                errors.append("❌ options должны иметь ключи из {'1','2','3','4'}")
            if len(opt_keys) < 3 or len(opt_keys) > 4:
                errors.append("❌ options должен содержать 3-4 варианта")

            # Проверка значений опций
            valid_option_values = [
                "k > 0, b < 0",
                "k < 0, b > 0",
                "k < 0, b < 0",
                "k > 0, b > 0"
            ]
            for key, value in params["options"].items():
                if value not in valid_option_values:
                    errors.append(f"❌ Неверное значение опции '{key}': {value}")

    return (len(errors) == 0, errors)
