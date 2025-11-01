# matunya_bot_final/tests/solvers/task_6/test_common_fractions_solver.py
import pytest
from matunya_bot_final.help_core.solvers.task_6.common_fractions_solver import solve


@pytest.mark.fipi_etalon
def test_cf_addition_subtraction_solver_fipi_etalon():
    """
    Эталонный тест для подтипа common_fractions (паттерн cf_addition_subtraction).

    Проверяем:
    1) Решатель возвращает корректный словарь solution_core.
    2) Есть шаг поиска наименьшего общего знаменателя (FIND_LCM).
    3) Есть шаг приведения к общему знаменателю (SCALE_TO_COMMON_DENOM).
    4) Есть шаг сложения или вычитания числителей (ADD_OR_SUB_NUMERATORS).
    5) Есть сокращение дроби или отметка, что дробь несократима.
    6) Есть финальный шаг извлечения числителя или перевода в десятичную форму.
    7) Финальный ответ равен 32.
    """

    task_data = {
        "id": "qc_cf_add_sub_1",
        "task_number": 6,
        "topic": "fractions",
        "subtype": "common_fractions",
        "pattern": "cf_addition_subtraction",
        "question_text": (
            "Вычисли: 1/10 + 11/18. "
            "Получи результат в виде обыкновенной несократимой дроби, "
            "в ответ запиши только числитель."
        ),
        "answer": 32,
        "variables": {
            "expression_tree": {
                "operation": "add",
                "operands": [
                    {"type": "common", "value": [1, 10], "text": "1/10"},
                    {"type": "common", "value": [11, 18], "text": "11/18"}
                ]
            }
        },
    }

    solution_core = solve(task_data)

    # --- Базовая структура ---
    assert isinstance(solution_core, dict), "Решатель должен возвращать словарь"
    for key in ("calculation_steps", "final_answer", "explanation_idea"):
        assert key in solution_core, f"Отсутствует ключ {key}"

    steps = solution_core["calculation_steps"]
    assert isinstance(steps, list), "calculation_steps должен быть списком"
    assert 4 <= len(steps) <= 12, f"Неожиданное количество шагов: {len(steps)}"

    # --- Проверяем наличие ключевых этапов ---
    keys = [step["description_key"] for step in steps]

    required_keys = {
        "INITIAL_EXPRESSION",
        "FIND_LCM",
        "SCALE_TO_COMMON_DENOM",
        "ADD_OR_SUB_NUMERATORS",
    }
    missing = required_keys - set(keys)
    assert not missing, f"Не найдены обязательные шаги: {missing}"

    assert any(k in keys for k in ("REDUCE_FRACTION", "FRACTION_ALREADY_REDUCED")), \
        "Ожидается шаг сокращения дроби или отметка, что дробь несократима"

    assert any(k in keys for k in ("EXTRACT_NUMERATOR", "CONVERT_TO_DECIMAL")), \
        "Ожидается финальный шаг преобразования или извлечения части дроби"

    # --- Проверяем наличие операции сложения/вычитания ---
    step_params = " ".join(str(s.get("description_params", "")) for s in steps).lower()
    assert any(word in step_params for word in ("add", "subtract", "складываем", "вычитаем")), \
        "Не найдено упоминание сложения/вычитания числителей"

    # --- Финальный ответ ---
    final_answer = solution_core["final_answer"]
    assert isinstance(final_answer, dict)
    val = final_answer.get("value_machine")
    assert round(val) == 32, f"Числитель финального ответа должен быть 32, получено {val}"

    print(f"[✅] Эталон пройден: {len(steps)} шаг(ов), итог = {val}")
