# matunya_bot_final/non_generators/task_15/task_15_requirements.py

from typing import Dict, Any


def _has_all(data: dict, *keys: str) -> bool:
    return all(k in data and data[k] is not None for k in keys)


def _can_compute_k(given: Dict[str, Any]) -> bool:
    sides = given.get("sides", {})
    elements = given.get("elements", {})
    relations = given.get("relations", {})

    if _has_all(sides | elements, "MN", "AC"):
        return True
    if _has_all(sides | elements, "BM", "AB"):
        return True
    if _has_all(sides | elements, "BN", "BC"):
        return True
    if _has_all(relations, "S_MBN", "S_ABC"):
        return True

    return False


def check_triangle_area_by_parallel_line(task: Dict[str, Any]) -> None:
    given = task["variables"]["given"]
    to_find = task["variables"]["to_find"]

    relations = given.get("relations", {})
    target = to_find.get("name")

    # --- AREA TASKS ---
    if to_find["type"] == "area":

        if target == "S_MBN":
            if "S_ABC" not in relations:
                raise ValueError(
                    "Task 15: для нахождения S(MBN) обязана быть известна S(ABC)"
                )
            if not _can_compute_k(given):
                raise ValueError(
                    "Task 15: невозможно вычислить коэффициент подобия k "
                    "(нет пар сторон или площадей)"
                )

        elif target == "S_ABC":
            if "S_MBN" not in relations:
                raise ValueError(
                    "Task 15: для нахождения S(ABC) обязана быть известна S(MBN)"
                )
            if not _can_compute_k(given):
                raise ValueError(
                    "Task 15: невозможно вычислить коэффициент подобия k"
                )

        else:
            raise ValueError(
                f"Task 15: неизвестная искомая площадь: {target}"
            )

    # --- RATIO TASKS ---
    elif to_find["type"] == "ratio":
        if not _can_compute_k(given):
            raise ValueError(
                "Task 15: невозможно вычислить отношение — нет коэффициента k"
            )

    # --- SIDE TASKS ---
    elif to_find["type"] == "side":
        if not _can_compute_k(given):
            raise ValueError(
                "Task 15: невозможно найти сторону — нет коэффициента k"
            )

    else:
        raise ValueError(
            f"Task 15: неподдерживаемый тип to_find: {to_find['type']}"
        )
