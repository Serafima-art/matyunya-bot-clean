from __future__ import annotations

import pytest

from matunya_bot_final.help_core.solvers.task_6 import (
    common_fractions_solver,
    decimal_fractions_solver,
    mixed_fractions_solver,
    powers_solver_dubl,
)


@pytest.mark.asyncio
async def test_solve_common_fractions_addition() -> None:
    task_data = {
        "id": "test_cf_add",
        "task_number": 6,
        "topic": "common_fractions",
        "subtype": "cf_addition_subtraction",
        "variables": {
            "expression_tree": {
                "operation": "add",
                "operands": [
                    {"type": "common", "value": [1, 2], "text": "1/2"},
                    {"type": "common", "value": [1, 4], "text": "1/4"},
                ],
            }
        },
        "meta": {"pattern_id": "1.1", "difficulty": "easy"},
    }

    result = await common_fractions_solver.solve(task_data)

    assert result["status"] == "success"
    primary = result["final_block"]["primary_value"]
    assert primary["fraction"] == "3/4"
    assert primary["decimal"] == "0,75"
    assert result["final_answer"]["value_machine"] == [3, 4]
    answer_fraction = result["answer"]["fraction"]
    assert answer_fraction["numerator"] == 3
    assert answer_fraction["denominator"] == 4
    assert len(result["steps"]) == 2


@pytest.mark.asyncio
async def test_solve_decimal_fractions_linear_operations() -> None:
    task_data = {
        "id": "test_df_linear",
        "task_number": 6,
        "topic": "decimal_fractions",
        "subtype": "linear_operations",
        "variables": {
            "expression_tree": {
                "operation": "add",
                "operands": [
                    {
                        "operation": "mul",
                        "operands": [
                            {"type": "integer", "value": 3, "text": "3"},
                            {"type": "decimal", "value": 1.2, "text": "1,2"},
                        ],
                    },
                    {"type": "decimal", "value": 0.5, "text": "0,5"},
                ],
            }
        },
        "meta": {"pattern_id": "2.2", "difficulty": "medium"},
    }

    result = await decimal_fractions_solver.solve(task_data)

    assert result["status"] == "success"
    primary = result["final_block"]["primary_value"]
    assert primary["display"] == "4,1"
    assert result["final_answer"]["value_machine"] == "4.1"
    assert result["answer"]["fraction"]["numerator"] == 41
    assert result["answer"]["fraction"]["denominator"] == 10


@pytest.mark.asyncio
async def test_solve_mixed_fractions_operations() -> None:
    task_data = {
        "id": "test_mixed",
        "task_number": 6,
        "topic": "mixed_fractions",
        "subtype": "mixed_types_operations",
        "variables": {
            "expression_tree": {
                "operation": "mul",
                "operands": [
                    {
                        "operation": "sub",
                        "operands": [
                            {"type": "mixed", "value": [1, 1, 2], "text": "1 1/2"},
                            {"type": "decimal", "value": 1.0, "text": "1,0"},
                        ],
                    },
                    {"type": "mixed", "value": [1, 1, 2], "text": "1 1/2"},
                ],
            }
        },
        "meta": {"pattern_id": "3.1", "difficulty": "hard"},
    }

    result = await mixed_fractions_solver.solve(task_data)

    assert result["status"] == "success"
    primary = result["final_block"]["primary_value"]
    assert primary["display"] == "0,75"
    assert result["answer"]["fraction"]["numerator"] == 3
    assert result["answer"]["fraction"]["denominator"] == 4
    assert result["final_block"]["primary_value"]["fraction"] == "3/4"


@pytest.mark.asyncio
async def test_solve_powers_of_ten() -> None:
    task_data = {
        "id": "test_powers",
        "task_number": 6,
        "topic": "powers",
        "subtype": "powers_of_ten",
        "variables": {
            "expression_tree": {
                "operation": "div",
                "operands": [
                    {
                        "operation": "mul",
                        "operands": [
                            {"type": "power_of_ten", "value": 2, "text": "10^2"},
                            {"type": "decimal", "value": 0.03, "text": "0,03"},
                        ],
                    },
                    {"type": "power_of_ten", "value": 1, "text": "10"},
                ],
            }
        },
        "meta": {"pattern_id": "4.2", "difficulty": "medium"},
    }

    result = await powers_solver_dubl.solve(task_data)

    assert result["status"] == "success"
    primary = result["final_block"]["primary_value"]
    assert primary["display"] == "0,3"
    assert result["answer"]["decimal"]["value"] == "0,3"
    assert result["final_block"]["summary"].startswith("Итоговое значение")


@pytest.mark.asyncio
async def test_division_by_zero_error() -> None:
    task_data = {
        "id": "test_error_div_zero",
        "task_number": 6,
        "topic": "common_fractions",
        "subtype": "complex_fraction",
        "variables": {
            "expression_tree": {
                "operation": "div",
                "operands": [
                    {"type": "integer", "value": 1, "text": "1"},
                    {"type": "decimal", "value": 0.0, "text": "0,0"},
                ],
            }
        },
        "meta": {"pattern_id": "1.4", "difficulty": "hard"},
    }

    result = await common_fractions_solver.solve(task_data)

    assert result["status"] == "error"
    assert "Деление на ноль" in result["final_block"]["summary"]
    assert not result["steps"]
