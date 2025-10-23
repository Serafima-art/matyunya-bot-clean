from __future__ import annotations

import pytest

from matunya_bot_final.help_core.humanizers.template_humanizers.task_6_humanizer import (
    humanize_task_6_solution,
)


@pytest.fixture
def base_solution_core() -> dict:
    return {
        "status": "success",
        "meta": {"topic": "common_fractions"},
        "steps": [
            {
                "explanation": "Приводим дроби к общему знаменателю: НОК(4, 6) = 12.",
                "expression": "3/4 = 9/12, 1/6 = 2/12",
            },
            {
                "explanation": "Складываем числители и оставляем общий знаменатель.",
                "expression": "9/12 + 2/12 = 11/12",
            },
        ],
        "final_block": {
            "primary_value": {
                "display": "11/12",
            }
        },
    }


def test_humanizer_matches_template(base_solution_core: dict):
    html = humanize_task_6_solution(base_solution_core)

    assert "💡 <b>Идея решения:</b>" in html
    assert "<i>Работаем с обыкновенными дробями, соблюдая строгий порядок действий.</i>" in html
    assert "📝 <b>Пошаговое решение:</b>" in html
    assert "<b>Шаг 1:</b> Приводим дроби к общему знаменателю: НОК(4, 6) = 12.\n<code>3/4 = 9/12, 1/6 = 2/12</code>" in html
    assert "<b>Шаг 2:</b> Складываем числители и оставляем общий знаменатель.\n<code>9/12 + 2/12 = 11/12</code>" in html
    assert "⚠️ <b>Полезно помнить:</b>" in html
    assert "• Всегда начинайте с действий в скобках." in html
    assert "• Приводите дроби к общему знаменателю для сложения и вычитания." in html
    assert "• При делении на дробь — умножайте на перевернутую." in html
    assert "✅ <b>Ответ:</b> <code>11/12</code>" in html

    sections = html.split("\n\n")
    assert any(section.startswith("💡 <b>Идея решения:</b>") for section in sections)
    assert any(section.startswith("📝 <b>Пошаговое решение:</b>") for section in sections)
    assert any(section.startswith("⚠️ <b>Полезно помнить:</b>") for section in sections)
    assert any(section.startswith("✅ <b>Ответ:</b>") for section in sections)


def test_humanizer_decimal_topic(base_solution_core: dict):
    base_solution_core["meta"]["topic"] = "decimal_fractions"
    html = humanize_task_6_solution(base_solution_core)
    assert "<i>Работаем с десятичными дробями, соблюдая строгий порядок действий.</i>" in html


def test_humanizer_error_case():
    solution_core = {
        "status": "error",
        "final_block": {"summary": "Деление на ноль недопустимо."},
    }
    html = humanize_task_6_solution(solution_core)
    assert html == "❌ Ошибка: Деление на ноль недопустимо."


@pytest.mark.parametrize(
    "topic, expected",
    [
        ("common_fractions", "обыкновенными дробями"),
        ("decimal_fractions", "десятичными дробями"),
        ("mixed_fractions", "смешанными дробями"),
        ("powers", "степенями и дробями"),
        ("unknown", "арифметическими выражениями"),
    ],
)
def test_topic_descriptions(base_solution_core: dict, topic: str, expected: str):
    base_solution_core["meta"]["topic"] = topic
    html = humanize_task_6_solution(base_solution_core)
    assert f"<i>Работаем с {expected}, соблюдая строгий порядок действий.</i>" in html
