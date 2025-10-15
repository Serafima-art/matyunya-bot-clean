import asyncio

from matunya_bot_final.help_core.solvers.task_20.radical_equations_solver import solve


def _run_solver(task_data):
    return asyncio.run(solve(task_data))


def test_sum_zero_pattern_no_common_roots():
    task_data = {
        "id": "qc_radical_sum_zero",
        "task_number": 20,
        "topic": "algebraic_expressions",
        "subtype": "radical_equations",
        "question_text": "Решите уравнение:\n√(x-1) + √(9-x) = 0",
        "answer": [],
        "variables": {
            "solution_pattern": "sum_zero",
            "radicals": {
                "A": {"text": "x - 1", "roots": [1]},
                "B": {"text": "9 - x", "roots": [9]},
            },
        },
    }

    solution = _run_solver(task_data)

    assert solution["final_answer"]["value_machine"] == []
    steps = solution["calculation_steps"]
    assert len(steps) == 4
    assert "сумма неотрицательных" in steps[0]["description"].lower()
    assert steps[1]["formula_representation"] == "{ x - 1 = 0; 9 - x = 0 }"
    assert "общие корни" in ((steps[3]["formula_calculation"] or "").lower())
    assert "подкоренных выражений нулю" in solution["explanation_idea"].lower()


def test_same_radical_cancel_pattern_with_check():
    task_data = {
        "id": "qc_radical_same",
        "task_number": 20,
        "topic": "algebraic_expressions",
        "subtype": "radical_equations",
        "question_text": "Решите уравнение:\n√(x+3) = √(2x-1)",
        "answer": [4],
        "variables": {
            "solution_pattern": "same_radical_cancel",
            "radicals": {
                "A": {"text": "x + 3"},
                "B": {"text": "2x - 1"},
            },
            "extraneous_roots": [7],
        },
    }

    solution = _run_solver(task_data)

    assert solution["final_answer"]["value_machine"] == [4]
    steps = solution["calculation_steps"]
    assert len(steps) == 3
    assert "возведём обе части" in steps[0]["description"].lower()
    assert steps[0]["formula_general"] == "(√A)² = (√B)² ⇒ A = B (при A ≥ 0, B ≥ 0)"
    assert "проверку" in steps[2]["description"].lower()
    assert "посторонние корни" in (steps[2]["calculation_result"] or "").lower()
    assert "посторонние корни" in solution["explanation_idea"].lower()


def test_cancel_identical_radicals_pattern_with_odz():
    task_data = {
        "id": "qc_radical_cancel_identical",
        "task_number": 20,
        "topic": "algebraic_expressions",
        "subtype": "radical_equations",
        "question_text": "Решите уравнение:\n√(x-1) + √(x-1) = 6",
        "answer": [5],
        "variables": {
            "solution_pattern": "cancel_identical_radicals",
            "identical_radical": "√(x-1)",
            "od_inequality": "x ≥ 1",
            "resulting_equation": {
                "text": "(x - 5)^2 = 0",
                "coeffs": [25, -10, 1],
                "roots": [5, 5],
            },
            "extraneous_roots": [8],
        },
    }

    solution = _run_solver(task_data)

    assert solution["final_answer"]["value_machine"] == [5]
    steps = solution["calculation_steps"]
    assert len(steps) == 5
    assert "равносильный переход" in steps[0]["description"].lower()
    assert "смешанную систему" in steps[1]["description"].lower()
    assert steps[2]["formula_calculation"] == "⇔ x ≥ 1"
    assert "отберём корни" in steps[4]["description"].lower()
    assert "допустимые" in (steps[4]["calculation_result"] or "").lower()
    assert "одз" in solution["explanation_idea"].lower()
