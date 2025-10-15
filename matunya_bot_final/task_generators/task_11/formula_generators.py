"""
formula_generators.py
Генераторы формул для задания №11 (ОГЭ).
"""

import random
import numpy as np
from typing import Dict, Any


# ==============================
# Линейная функция
# ==============================
def _generate_linear() -> Dict[str, Any]:
    k = random.choice([-3, -2, -1, -0.5, 0.5, 1, 2, 3])
    b = random.choice([-6, -4, -2, -1, 0, 1, 2, 3, 4, 6])

    if b == 0:
        formula = f"y = {k}x"
    else:
        sign = "+" if b > 0 else "−"
        formula = f"y = {k}x {sign} {abs(b)}"

    return {
        "func": lambda x, k=k, b=b: k * x + b,
        "formula_str": formula.replace("−", "-"),
        "type": "linear"
    }


# ==============================
# Парабола
# ==============================
def _generate_parabola() -> Dict[str, Any]:
    a = random.choice([-2, -1, 1, 2])
    b = random.choice(range(-3, 4))
    c = random.choice(range(-3, 4))

    formula = "y = "
    formula += f"{'−' if a == -1 else ''}x²" if abs(a) == 1 else f"{a}x²"
    if b != 0:
        formula += f" + {b}x" if b > 0 else f" − {abs(b)}x"
    if c != 0:
        formula += f" + {c}" if c > 0 else f" − {abs(c)}"

    return {
    "func": lambda x, a=a, b=b, c=c: a * x * x + b * x + c,
    "formula_str": formula.replace("−", "-"),  # нормализуем минусы
    "type": "parabola"
    }


# ==============================
# Гипербола
# ==============================
def _generate_hyperbola() -> Dict[str, Any]:
    k = random.choice([-12, -6, -3, -2, -1, 1, 2, 3, 6, 12])

    if k == 1:
        formula = "y = 1/x"
    elif k == -1:
        formula = "y = −1/x"
    else:
        formula = f"y = {k}/x"

    return {
        "func": lambda x, k=k: np.where(x == 0, np.nan, k / x),
        "formula_str": formula,
        "type": "hyperbola"
    }


# ==============================
# Функция корня (Каноническая версия)
# ==============================
def _generate_sqrt() -> Dict[str, Any]:
    """
    Генерирует КЛАССИЧЕСКУЮ функцию квадратного корня y = √x.
    Без сдвигов.
    """
    formula = "y = √x"

    return {
        "func": lambda x: np.where(x >= 0, np.sqrt(x), np.nan),
        "formula_str": formula,
        "type": "sqrt"
    }


# ==============================
# Диспетчер
# ==============================
def generate_formula(func_type: str) -> Dict[str, Any]:
    """Вызывает нужный генератор по имени типа."""
    if func_type == "linear":
        return _generate_linear()
    elif func_type == "parabola":
        return _generate_parabola()
    elif func_type == "hyperbola":
        return _generate_hyperbola()
    elif func_type == "sqrt":
        return _generate_sqrt()
    else:
        raise ValueError(f"Неизвестный тип функции: {func_type}")


# ==============================
# Утилиты
# ==============================
def get_color(index: int) -> str:
    """Простой выбор цвета для графиков."""
    colors = ["blue", "red", "green", "orange", "purple", "brown"]
    return colors[index % len(colors)]
