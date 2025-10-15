from __future__ import annotations

import math
from typing import Union

Number = Union[int, float]


def format_answer(value: Number) -> str:
    value_float = float(value)
    if math.isclose(value_float, round(value_float), rel_tol=1e-9, abs_tol=1e-9):
        return str(int(round(value_float)))
    return f"{value_float:.6f}".rstrip("0").rstrip(".").replace(".", ",")
