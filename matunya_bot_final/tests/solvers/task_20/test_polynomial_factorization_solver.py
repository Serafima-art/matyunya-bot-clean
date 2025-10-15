import pytest

from matunya_bot_final.help_core.solvers.task_20.polynomial_factorization_solver import solve


@pytest.mark.asyncio
async def test_solver_common_poly_pattern():
    task_data = {
        "id": "qc_common_poly",
        "task_number": 20,
        "topic": "algebraic_expressions",
        "subtype": "polynomial_factorization",
        "question_text": "Решите уравнение:\n(5x + 1)(x^2 - 4x + 4) = 12x - 6x^2",
        "answer": [-0.8, 2],
        "variables": {
            "solution_pattern": "common_poly",
            "linear_factor": {"a": 5, "b": 1, "text": "5x + 1", "root": -0.8},
            "common_factor": {
                "coeffs": [1, -4, 4],
                "text": "x^2 - 4x + 4",
                "roots": [2, 2],
            },
            "rhs": {"multiplier": -3, "coeffs": [-3, 12, -12], "text": "-3(x^2 - 4x + 4)"},
        },
    }

    solution_core = await solve(task_data)

    assert solution_core["final_answer"]["value_machine"] == [-0.8, 2]

    steps = solution_core["calculation_steps"]
    assert len(steps) == 8
    assert steps[5]["description"] == "Используем свойство нулевого произведения."
    assert steps[4]["formula_calculation"] == "(x^2 - 4x + 4)[(5x + 1) - -3] = 0"
    assert "множитель" in solution_core["hints"][0].lower()
    assert "перенос" in solution_core["explanation_idea"].lower()


@pytest.mark.asyncio
async def test_solver_diff_squares_pattern():
    task_data = {
        "id": "qc_diff_squares",
        "task_number": 20,
        "topic": "algebraic_expressions",
        "subtype": "polynomial_factorization",
        "question_text": "Решите уравнение:\n(x^2 - 7x + 10)^2 = (x^2 + 3x - 18)^2",
        "answer": [-6, -5, 2, 3, 5],
        "variables": {
            "solution_pattern": "diff_squares",
            "difference_of_squares": {
                "A": {"text": "x^2 - 2x - 8"},
                "B": {"text": "x^2 + 5x - 10"},
            },
            "factored_form": {
                "poly_minus": {"text": "x^2 - 7x + 10", "roots": [2, 5]},
                "poly_plus": {"text": "x^2 + 3x - 18", "roots": [-6, 3]},
            },
        },
    }

    solution_core = await solve(task_data)

    expected_roots = [-6, -5, 2, 3, 5]
    assert sorted(solution_core["final_answer"]["value_machine"]) == sorted(expected_roots)

    steps = solution_core["calculation_steps"]
    assert len(steps) == 8
    assert "разность квадратов" in steps[3]["description"].lower() or "разности квадратов" in steps[3]["description"].lower()
    assert steps[6]["formula_calculation"].startswith("x")
    assert steps[3].get("formula_general") == "A² - B² = (A - B)(A + B)"
    assert "формула" in solution_core["hints"][0].lower()


@pytest.mark.asyncio
async def test_solver_grouping_pattern():
    task_data = {
        "id": "qc_grouping",
        "task_number": 20,
        "topic": "algebraic_expressions",
        "subtype": "polynomial_factorization",
        "question_text": "Решите уравнение:\n2x^3 - 5x^2 - x + 2 = 0",
        "answer": [-1, 0.5, 2],
        "variables": {
            "solution_pattern": "grouping",
            "coefficients": {"a": 2, "b": -5, "c": -1, "d": 2},
            "roots": [-1, 0.5, 2],
            "grouping": {
                "group1_multiplier": "x^2",
                "group2_multiplier": -0.5,
                "common_factor": {"text": "x + 2"},
            },
        },
    }

    solution_core = await solve(task_data)

    assert solution_core["final_answer"]["value_machine"] == [-1, 0.5, 2]

    steps = solution_core["calculation_steps"]
    assert len(steps) == 7
    assert steps[5]["formula_calculation"].replace("= 0 = 0", "= 0") == "2(x + 2)(x - 1) = 0"
    assert steps[6]["formula_calculation"] == "x₁ = -1, x₂ = 0.5, x₃ = 2"
    assert "групп" in solution_core["explanation_idea"].lower()
    assert "скобк" in solution_core["hints"][1].lower()
