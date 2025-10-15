import math
from typing import Any, Dict, Optional


def is_perfect_square(n: int) -> bool:
    root = int(math.sqrt(n))
    return root * root == n


def parse_sqrt_option(opt: str) -> Optional[int]:
    """
    Преобразует строку типа '√17' → 17.
    Если не подходит — возвращает None.
    """
    if opt.startswith("√"):
        try:
            return int(opt[1:])
        except:
            return None
    return None


def extract_point_pos(img: Dict[str, Any], label: str) -> Optional[float]:
    """
    Возвращает координату точки по её label из image_params
    """
    points = img.get("points", [])
    for pt in points:
        if pt.get("label") == label:
            return pt.get("pos")
    return None


def validate_axis(img: Dict[str, Any]) -> Optional[tuple[float, float]]:
    """
    Проверка и возврат (min_val, max_val) из image_params
    """
    try:
        min_val = img["min_val"]
        max_val = img["max_val"]
        if isinstance(min_val, (int, float)) and isinstance(max_val, (int, float)) and min_val < max_val:
            return min_val, max_val
    except:
        pass
    return None


def strictly_between(x: float, a: float, b: float, tol: float = 1e-9) -> bool:
    """
    Проверка: находится ли x строго внутри (a; b), с учётом допуска tol
    """
    return (x - a) > tol and (b - x) > tol


def unique(lst: list) -> bool:
    return len(lst) == len(set(lst))