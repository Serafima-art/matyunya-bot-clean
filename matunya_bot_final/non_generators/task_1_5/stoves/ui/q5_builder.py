# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Dict, Any
from matunya_bot_final.utils.display.display import format_number


def build_q5_text(task: Dict[str, Any]) -> str:
    """
    Формирует текст вопроса Q5 (арка кожуха печи).
    Работает только с текстом — никаких вычислений.
    """

    input_data = task.get("input_data", {})

    a = input_data.get("a")
    b = input_data.get("b")

    # красивое форматирование чисел
    a = format_number(a)
    b = format_number(b)

    return (
        "Хозяин выбрал дровяную печь с кожухом вокруг дверцы топки. "
        "Верхняя часть кожуха выполнена в виде арки, приваренной к передней "
        "стенке печи по дуге окружности с центром в середине нижней части кожуха.\n\n"
        f"Высота a кожуха равна {a} см, а его ширина b — {b} см.\n\n"
        "Найди радиус R дуги окружности, образующей арку кожуха.\n"
        "Ответ дай в сантиметрах."
    )
