#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for powers_solver module"""

import pytest
import json
from .powers_solver_dubl import solve


def test_solve_powers_with_fractions_common_factor():
    """Test powers_with_fractions pattern with common factor - should generate 2 paths"""
    task_data = {
        "id": "6_powers_with_fractions_ibhd7r",
        "task_number": 6,
        "pattern": "powers_with_fractions",
        "question_text": "Вычисли выражение:\n28 · (2/7)² - 8 · (2/7)\n\nОтвет: ____________",
        "answer": "0",
        "answer_type": "integer",
        "variables": {
            "expression_tree": {
                "operation": "subtract",
                "operands": [
                    {
                        "operation": "multiply",
                        "operands": [
                            {"type": "integer", "value": 28, "text": "28"},
                            {
                                "operation": "power",
                                "operands": [
                                    {
                                        "operation": "divide",
                                        "operands": [
                                            {"type": "integer", "value": 2, "text": "2"},
                                            {"type": "integer", "value": 7, "text": "7"}
                                        ]
                                    },
                                    {"type": "integer", "value": 2, "text": "2"}
                                ]
                            }
                        ]
                    },
                    {
                        "operation": "multiply",
                        "operands": [
                            {"type": "integer", "value": 8, "text": "8"},
                            {
                                "operation": "divide",
                                "operands": [
                                    {"type": "integer", "value": 2, "text": "2"},
                                    {"type": "integer", "value": 7, "text": "7"}
                                ]
                            }
                        ]
                    }
                ]
            },
            "has_common_factor": True,
            "solution_paths": ["standard", "rational"],
            "operation": "subtract"
        }
    }

    result = solve(task_data)

    # Should have 2 paths when common factor exists
    assert "calculation_paths" in result
    assert len(result["calculation_paths"]) == 2

    # Each path should have title and steps
    for path in result["calculation_paths"]:
        assert "path_title" in path
        assert "steps" in path
        assert isinstance(path["steps"], list)
        assert len(path["steps"]) > 0

    # Should have final answer
    assert "final_answer" in result


def test_solve_powers_of_ten():
    """Test powers_of_ten pattern - should generate 1 path"""
    task_data = {
        "id": "6_powers_of_ten_test",
        "task_number": 6,
        "pattern": "powers_of_ten",
        "question_text": "Вычисли выражение:\n(3 · 10⁻¹)³ · (2 · 10⁴)\n\nОтвет: ____________",
        "answer": "300",
        "answer_type": "integer",
        "variables": {
            "expression_tree": {
                "operation": "multiply",
                "operands": [
                    {
                        "operation": "power",
                        "operands": [
                            {
                                "operation": "multiply",
                                "operands": [
                                    {"type": "integer", "value": 3, "text": "3"},
                                    {
                                        "operation": "power",
                                        "operands": [
                                            {"type": "integer", "value": 10, "text": "10"},
                                            {"type": "integer", "value": -1, "text": "-1"}
                                        ]
                                    }
                                ]
                            },
                            {"type": "integer", "value": 3, "text": "3"}
                        ]
                    },
                    {
                        "operation": "multiply",
                        "operands": [
                            {"type": "integer", "value": 2, "text": "2"},
                            {
                                "operation": "power",
                                "operands": [
                                    {"type": "integer", "value": 10, "text": "10"},
                                    {"type": "integer", "value": 4, "text": "4"}
                                ]
                            }
                        ]
                    }
                ]
            },
            "operation": "multiply"
        }
    }

    result = solve(task_data)

    # Should have calculation_steps for single path
    assert "calculation_steps" in result or "calculation_paths" in result
    assert "final_answer" in result


def test_solve_returns_structure():
    """Test that solve returns proper structure with final_answer"""
    task_data = {
        "id": "6_test",
        "task_number": 6,
        "pattern": "powers_with_fractions",
        "question_text": "Вычисли выражение:\n28 · (2/7)² - 8 · (2/7)\n\nОтвет: ____________",
        "answer": "0",
        "answer_type": "integer",
        "variables": {
            "expression_tree": {
                "operation": "subtract",
                "operands": [
                    {
                        "operation": "multiply",
                        "operands": [
                            {"type": "integer", "value": 28, "text": "28"},
                            {
                                "operation": "power",
                                "operands": [
                                    {
                                        "operation": "divide",
                                        "operands": [
                                            {"type": "integer", "value": 2, "text": "2"},
                                            {"type": "integer", "value": 7, "text": "7"}
                                        ]
                                    },
                                    {"type": "integer", "value": 2, "text": "2"}
                                ]
                            }
                        ]
                    },
                    {
                        "operation": "multiply",
                        "operands": [
                            {"type": "integer", "value": 8, "text": "8"},
                            {
                                "operation": "divide",
                                "operands": [
                                    {"type": "integer", "value": 2, "text": "2"},
                                    {"type": "integer", "value": 7, "text": "7"}
                                ]
                            }
                        ]
                    }
                ]
            },
            "has_common_factor": True,
            "solution_paths": ["standard", "rational"],
            "operation": "subtract"
        }
    }

    result = solve(task_data)

    # Verify required fields exist
    assert isinstance(result, dict)
    assert "final_answer" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
