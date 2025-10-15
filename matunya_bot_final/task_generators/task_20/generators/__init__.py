"""Generators registry for task 20."""

from typing import Callable, Dict

from matunya_bot_final.task_generators.task_20.generators.polynomial_factorization_generator import (
    generate_task_20_polynomial_factorization,
)

GENERATOR_MAP: Dict[str, Callable[[], dict]] = {
    "polynomial_factorization": generate_task_20_polynomial_factorization,
}


def generate_task_20_by_subtype(subtype: str) -> dict:
    """Return generated task payload for a given task 20 subtype."""
    if subtype not in GENERATOR_MAP:
        raise ValueError(f"Неизвестный подтип задания 20: {subtype}")
    return GENERATOR_MAP[subtype]()


__all__ = ["GENERATOR_MAP", "generate_task_20_by_subtype"]

