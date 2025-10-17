import pytest
import asyncio

from matunya_bot_final.help_core.solvers.task_20.rational_inequalities_solver import solve


@pytest.mark.asyncio
@pytest.mark.parametrize("pattern, task_data", [
    # --- 1. compare_unit_fractions_linear ---
    (
        "compare_unit_fractions_linear",
        {
            "answer": ["(0; 5)"],
            "variables": {
                "solution_pattern": "compare_unit_fractions_linear",
                "coefficients": {"a": 5, "sign": "≥"},
                "axis_data": {"points": [], "intervals": [], "shading_ranges": []}
            }
        }
    ),
    # --- 2. const_over_quadratic_nonpos_nonneg ---
    (
        "const_over_quadratic_nonpos_nonneg",
        {
            "answer": ["(−∞; -4) ∪ (3; +∞)"],
            "variables": {
                "solution_pattern": "const_over_quadratic_nonpos_nonneg",
                "coefficients": {"b": 1, "c": -12, "C": -19, "roots": [-4, 3], "sign": "≤"},
                "axis_data": {"points": [], "intervals": [], "shading_ranges": []}
            }
        }
    ),
    # --- 3. x_vs_const_over_x ---
    (
        "x_vs_const_over_x",
        {
            "answer": ["(−∞; −5] ∪ (0; 5]"],
            "variables": {
                "solution_pattern": "x_vs_const_over_x",
                "coefficients": {"K": 25, "m": 5, "sign": "≤"},
                "axis_data": {"points": [], "intervals": [], "shading_ranges": []}
            }
        }
    ),
    # --- 4. neg_const_over_shifted_square_minus_const ---
    (
        "neg_const_over_shifted_square_minus_const",
        {
            "answer": ["(2−√3; 2+√3)"],
            "variables": {
                "solution_pattern": "neg_const_over_shifted_square_minus_const",
                "coefficients": {"a": 2, "d": 3, "C": -11, "sign": "≥"},
                "axis_data": {"points": [], "intervals": [], "shading_ranges": []}
            }
        }
    ),
])
async def test_rational_inequalities_solver(pattern, task_data):
    """Базовый smoke-тест для Решателя дробно-рациональных неравенств."""

    result = await solve(task_data)

    # 1️⃣ Проверяем базовую структуру
    assert isinstance(result, dict)
    assert "question_id" in result
    assert "calculation_steps" in result
    assert "final_answer" in result
    assert "explanation_idea" in result

    # 2️⃣ Проверяем ID и соответствие паттерну
    assert pattern in result["question_id"], f"ID не содержит паттерн: {pattern}"

    # 3️⃣ Проверяем наличие шага с визуализацией
    vis_steps = [
        s for s in result["calculation_steps"]
        if "visual_instruction" in s
    ]
    assert vis_steps, f"Нет шага с visual_instruction для {pattern}"

    # 4️⃣ Проверяем корректность финального ответа
    assert result["final_answer"]["value_display"] == task_data["answer"][0]

    print(f"✅ {pattern} → {result['final_answer']['value_display']}")
