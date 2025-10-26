# matunya_bot_final/tests/solvers/task_6/test_common_fractions_solver.py
import pytest

from matunya_bot_final.help_core.solvers.task_6.common_fractions_solver import solve


def test_cf_addition_subtraction_solver_nok_flow():
    """
    Критерии приёмки (ФИПИ/ГОСТ-2026) для паттерна cf_addition_subtraction:
    1) Шаг 1: упоминание НОК и корректный НОК(10,18)=90
    2) Шаг 2: домножение дробей и приведение к 9/90 и 55/90
    3) Шаг 3: сокращение 64/90 → 32/45
    4) Шаг 4: фиксация, что в ответ идёт числитель 32
    + финальный ответ в solution_core.final_answer.value_machine == 32
    """
    task_data = {
        "id": "qc_cf_add_sub_1",
        "task_number": 6,
        "topic": "fractions",
        "subtype": "common_fractions",
        "pattern": "cf_addition_subtraction",
        "question_text": "Вычисли: 1/10 + 11/18. "
                         "Получи результат в виде обыкновенной несократимой дроби, "
                         "в ответ запиши только числитель.",
        # В нашей методике для подтипа cf_addition_subtraction в answer хранится только числитель.
        "answer": 32,
        # variables опциональны; решатель должен уметь разбирать из текста
        # оставляем пустым, чтобы тест проверял «методический» конвейер
        "variables": {}
    }

    solution_core = solve(task_data)

    # Базовая структура
    assert isinstance(solution_core, dict)
    for key in ("calculation_steps", "final_answer", "hints", "explanation_idea"):
        assert key in solution_core, f"Отсутствует ключ {key} в solution_core"

    steps = solution_core["calculation_steps"]
    assert isinstance(steps, list)
    assert len(steps) == 4, "Должно быть ровно 4 шага по методике ФИПИ"

    # Шаг 1 — НОК
    step1 = steps[0]
    desc1 = step1.get("description", "")
    assert "НОК" in desc1 or "наименьший общий знаменатель" in desc1.lower()
    # Дополнительно зафиксируем корректность НОК(10, 18) = 90
    text_all_1 = (desc1 + " " + step1.get("formula_calculation", "")).replace(" ", "")
    assert "10" in text_all_1 and "18" in text_all_1
    assert "90" in text_all_1, "В первом шаге должен фигурировать НОК=90"

    # Шаг 2 — домножение и приведение к общему знаменателю
    step2 = steps[1]
    desc2 = step2.get("description", "")
    form2 = step2.get("formula_calculation", "")
    assert "Домножим" in desc2 or "домножим" in desc2
    # Проверим ключевые фрагменты приведения:
    # (1·9)/(10·9) + (11·5)/(18·5) = 9/90 + 55/90 = 64/90
    form2_no_space = form2.replace(" ", "")
    assert "9/90" in form2_no_space, "Ожидается частичное выражение 9/90"
    assert "55/90" in form2_no_space, "Ожидается частичное выражение 55/90"
    assert "64/90" in form2_no_space, "Ожидается суммарный результат 64/90"

    # Шаг 3 — сокращение дроби
    step3 = steps[2]
    desc3 = step3.get("description", "")
    form3 = step3.get("formula_calculation", "")
    assert "Сократим" in desc3 or "сокращ" in desc3.lower()
    form3_no_space = form3.replace(" ", "")
    assert "64/90" in form3_no_space and "32/45" in form3_no_space, \
        "Ожидается сокращение 64/90 → 32/45"

    # Шаг 4 — фиксация, что в ответ идёт только числитель
    step4 = steps[3]
    desc4 = step4.get("description", "")
    assert "числител" in desc4.lower(), \
        "Финальный шаг должен явно фиксировать, что в ответ идёт числитель"
    # Желательно, чтобы упоминался сам числитель 32
    assert "32" in (desc4 + " " + step4.get("formula_calculation", "")), \
        "В финальном шаге должен фигурировать числитель 32"

    # Финальный ответ
    final_answer = solution_core["final_answer"]
    assert "value_machine" in final_answer
    assert final_answer["value_machine"] == 32, "Числитель финального ответа должен быть 32"
    # (не обязательно, но если есть value_display — проверим человекочитаемую форму)
    if "value_display" in final_answer:
        assert "32" in str(final_answer["value_display"])

    # Методическая часть: идея и подсказки
    explanation = solution_core.get("explanation_idea", "").lower()
    assert ("общий знаменатель" in explanation) or ("нок" in explanation), \
        "В explanation_idea должна быть сформулирована основная идея про общий знаменатель"

    hints = solution_core.get("hints", [])
    assert isinstance(hints, list) and len(hints) > 0
    joined_hints = " ".join(hints).lower()
    assert ("нок" in joined_hints) or ("домнож" in joined_hints) or ("сократ" in joined_hints), \
        "В подсказках должны быть методические маркеры: НОК / домножение / сокращение"
