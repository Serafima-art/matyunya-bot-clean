"""Utility helpers that return short motivational phrases for the help flow."""

from __future__ import annotations

import random
from typing import Dict, List

# Short text blocks grouped by the help level that triggers them.
_PHRASES_BY_LEVEL: Dict[str, List[str]] = {
    "hint": [
        "Попробуй начать с простого наблюдения: что здесь бросается в глаза?",
        "Сделай маленький шаг — иногда именно он приводит к разгадке.",
        "Возьми лист бумаги и зафиксируй то, что уже известно.",
    ],
    "partial": [
        "Мы уже близко! Проверь промежуточные вычисления, чтобы не упустить мелочь.",
        "Сравни полученное выражение с условием — может, осталось только упростить?",
        "Отличный прогресс. Дальше дело за аккуратным доведением до ответа.",
    ],
    "step": [
        "Сконцентрируйся на текущем шаге — решай задачу по частям.",
        "Каждое действие приближает к цели: давай выполним следующий шаг спокойно и точно.",
        "Представь, что объясняешь ход решения другу — так легче увидеть, чего не хватает.",
    ],
    "solution": [
        "Готово! Решение на ладони — осталось лишь внимательно его перечитать.",
        "Отличная работа. Ты справился — можешь гордиться результатом!",
        "Уверенный финиш! Сохрани решение, чтобы при случае вернуться и повторить.",
    ],
}

_FALLBACK_PHRASES: List[str] = [
    "Продолжай в том же духе — шаг за шагом мы приходим к решению.",
    "Если что-то не складывается, сделай паузу и посмотри ещё раз свежим взглядом.",
    "Ты на правильном пути. Чуть больше внимания к деталям — и всё получится.",
]


def get_random_phrase(level: str | None = None) -> str:
    """Return a randomly chosen phrase for the requested help level."""
    if level:
        phrases = _PHRASES_BY_LEVEL.get(level.lower())
        if phrases:
            return random.choice(phrases)

    return random.choice(_FALLBACK_PHRASES)


__all__ = ["get_random_phrase"]
