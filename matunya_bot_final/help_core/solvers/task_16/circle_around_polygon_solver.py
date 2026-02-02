# matunya_bot_final/help_core/solvers/task_16/circle_around_polygon_solver.py
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, Callable

logger = logging.getLogger(__name__)


# -----------------------------
# Public API
# -----------------------------
async def solve(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    ТЕМА 3: Окружность, описанная вокруг многоугольника (circle_around_polygon)

    Вход task_data ожидаемо содержит:
      - task_type (или берём "16" по умолчанию)
      - pattern: str (например "right_triangle_circumradius")
      - task_context: dict (обязательно: narrative)
      - question_text, answer, image_file и т.п. (что есть — то есть)

    Выход: solution_core (канонический, плоский, как в эталоне задания 16)
    """
    pattern = (task_data.get("pattern") or "").strip()
    task_context = task_data.get("task_context") or {}
    narrative = (task_context.get("narrative") or "").strip()

    if not pattern:
        return _build_error_solution_core(
            task_data=task_data,
            error_message="В задаче не указан pattern.",
        )

    if not narrative:
        return _build_error_solution_core(
            task_data=task_data,
            error_message="В task_context не указан narrative.",
        )

    router: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
        "square_incircle_circumcircle": _solve_square_incircle_circumcircle,
        "eq_triangle_circles": _solve_eq_triangle_circles,
        "square_radius_midpoint": _solve_square_radius_midpoint,
        "right_triangle_circumradius": _solve_right_triangle_circumradius,
    }

    handler = router.get(pattern)
    if not handler:
        return _build_error_solution_core(
            task_data=task_data,
            error_message=f"Решатель для pattern='{pattern}' не найден.",
        )

    try:
        solution_core = handler(task_data)

        # Мини-проверка канона: humanizer должен получать уже solution_core
        _assert_solution_core_shape(solution_core)

        return solution_core

    except Exception as e:
        logger.exception("[Task16][Theme3] Solver crashed. pattern=%s narrative=%s", pattern, narrative)
        return _build_error_solution_core(
            task_data=task_data,
            error_message=f"Ошибка решателя: {type(e).__name__}: {e}",
        )

# =========================================================================
# ПАТТЕРН 3.1: square_incircle_circumcircle
# =========================================================================

def _solve_square_incircle_circumcircle(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Паттерн 3.1: square_incircle_circumcircle

    Поддерживаемые нарративы (НОВЫЕ, канонические):
      - circum_to_in
      - in_to_circum
      - circum_to_side
      - circum_to_perimeter

    Канон:
    - facts-only
    - без анализа текста
    - solver синхронизирован с валидатором и БД
    """

    context: Dict[str, Any] = task_data.get("task_context") or {}
    answer = task_data.get("answer")

    narrative = (
        context.get("narrative")
        or task_data.get("narrative")
        or ""
    ).strip()

    if narrative not in (
        "circum_to_in",
        "in_to_circum",
        "circum_to_side",
        "circum_to_perimeter",
    ):
        return _build_error_solution_core(
            task_data=task_data,
            error_message=f"square_incircle_circumcircle: unknown narrative '{narrative}'",
        )

    # ------------------------------------------------------------------
    # FACTS — единый контракт для humanizer
    # ------------------------------------------------------------------

    given = context.get("given")
    target = context.get("target")

    if not given or not target:
        return _build_error_solution_core(
            task_data=task_data,
            error_message=f"square_incircle_circumcircle: missing given/target for '{narrative}'",
        )

    facts: Dict[str, Any] = {
        "figure": "square",
        "narrative": narrative,          # ⬅️ КЛЮЧЕВО: humanizer читает именно это
        "answer": answer,

        # обязательные блоки
        "given": given,
        "target": target,

        # общая геометрия
        "geometry_facts": {
            "center_relation": "same_center",
            "diagonal_relation": "d = a√2",
        },
    }

    # --- relations строго по narrative ---
    if narrative == "circum_to_in":
        facts["relations"] = {
            "radius_relation": "r = R / √2",
        }

    elif narrative == "in_to_circum":
        facts["relations"] = {
            "radius_relation": "R = r · √2",
        }

    elif narrative == "circum_to_side":
        facts["relations"] = {
            "side_relation": "a = R · √2",
        }

    elif narrative == "circum_to_perimeter":
        facts["relations"] = {
            "side_relation": "a = R · √2",
            "perimeter_relation": "P = 4a",
        }

    # ------------------------------------------------------------------
    # help_image (по канону задания 16)
    # ------------------------------------------------------------------

    help_image = None
    help_image_file = task_data.get("help_image_file")
    if help_image_file:
        help_image = {
            "file": str(help_image_file),
            "schema": f"square_incircle_circumcircle__{narrative}",
            "params": {
                "figure": "square",
                "narrative": narrative,
            },
        }

    # ------------------------------------------------------------------
    # solution_core
    # ------------------------------------------------------------------

    idea_key = f"IDEA_{narrative.upper()}"

    return {
        "question_id": str(task_data.get("id")),
        "question_group": "GEOMETRY_16",
        "explanation_idea": idea_key,
        "calculation_steps": [],
        "final_answer": {
            "value_machine": answer,
            "value_display": str(answer) if answer is not None else "",
            "unit": "",
        },
        "variables": facts,
        "help_image": help_image,
        "hints": [],
    }


# =========================================================================
# ПАТТЕРН 3.2: eq_triangle_circles
# =========================================================================

def _solve_eq_triangle_circles(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Паттерн 3.2: eq_triangle_circles

    Канон (ВАЖНО):
    - facts-only
    - solver формирует единый контракт facts для humanizer
    - выравниваем given/target (в target добавляем value_str)
    - вводим variables["derived"] для промежуточных величин,
      которые используются в шагах, но не являются ни given, ни target.
    """

    context: Dict[str, Any] = task_data.get("task_context") or {}
    narrative = (context.get("narrative") or task_data.get("narrative") or "").strip()
    answer = task_data.get("answer")

    allowed = (
        "circum_diameter_to_side",
        "side_to_circum_diameter",
        "circum_radius_to_side",
        "side_to_circum_radius",
        "inradius_to_side",
        "side_to_inradius",
    )
    if narrative not in allowed:
        return _build_error_solution_core(
            task_data=task_data,
            error_message=f"eq_triangle_circles: unknown narrative '{narrative}'",
        )

    given = context.get("given")
    target = context.get("target")
    if not isinstance(given, dict) or not isinstance(target, dict):
        return _build_error_solution_core(
            task_data=task_data,
            error_message=f"eq_triangle_circles: missing given/target for '{narrative}'",
        )

    # ------------------------------------------------------------------
    # NORMALIZE given/target: делаем единый контракт (value_str в target обязателен)
    # ------------------------------------------------------------------

    norm_given = dict(given)
    norm_target = dict(target)

    # given.value_str должен быть строкой (в БД так и есть), но подстрахуемся
    if norm_given.get("value_str") is None and norm_given.get("value") is not None:
        norm_given["value_str"] = str(norm_given["value"])

    # target.value_str в БД отсутствует — добавляем (как строку)
    if norm_target.get("value_str") is None and norm_target.get("value") is not None:
        norm_target["value_str"] = str(norm_target["value"])

    # ------------------------------------------------------------------
    # DERIVED: промежуточные величины, которые нужны в шагах humanizer
    # (и только они; без вычислений в humanizer!)
    # ------------------------------------------------------------------

    derived: Dict[str, Any] = {}

    def _put_derived(symbol: str, element_type: str, value: Any, value_str: str) -> None:
        derived[symbol] = {
            "element_type": element_type,
            "symbol": symbol,
            "value": value,
            "value_str": value_str,
        }

    g_type = norm_given.get("element_type")
    g_coeff = norm_given.get("coeff")  # в БД это целое (коэффициент при √3 или "чистое" число)
    g_value_str = norm_given.get("value_str")

    # 1) circum_diameter_to_side: в шагах нужен R (R = D : 2), далее a = R·√3
    if narrative == "circum_diameter_to_side":
        # ожидаем D = k√3 (k = coeff), тогда R = (k/2)√3
        if g_type == "circumcircle_diameter" and isinstance(g_coeff, int):
            if g_coeff % 2 == 0:
                r_coeff = g_coeff // 2
                r_str = f"{r_coeff}√3" if r_coeff != 1 else "√3"
            else:
                # редкий случай (если когда-то появится нечетный coeff)
                r_str = f"({g_coeff}/2)√3"
            _put_derived("R", "circumcircle_radius", None, r_str)

    # 2) side_to_circum_diameter: в шагах нужен R (R = a : √3), потом D = 2R
    elif narrative == "side_to_circum_diameter":
        # ожидаем a = k√3 (k = coeff), тогда R = k
        if g_type == "side" and isinstance(g_coeff, int):
            _put_derived("R", "circumcircle_radius", g_coeff, str(g_coeff))

    # Остальные нарративы решаются прямой формулой в шагах (без промежуточного R),
    # поэтому derived не заполняем.

    # ------------------------------------------------------------------
    # RELATIONS: берём строго из БД (если есть), иначе — подставляем канон по narrative
    # ------------------------------------------------------------------

    relations = context.get("relations") or {}

    if not relations:
        # безопасная подстраховка, если где-то в данных relations пустые
        if narrative == "circum_diameter_to_side":
            relations = {
                "radius_from_diameter": "R = D : 2",
                "side_from_radius": "a = R · √3",
            }
        elif narrative == "side_to_circum_diameter":
            relations = {
                "radius_relation": "R = a : √3",
                "diameter_relation": "D = 2 · R",
            }
        elif narrative == "circum_radius_to_side":
            relations = {"side_relation": "a = R · √3"}
        elif narrative == "side_to_circum_radius":
            relations = {"radius_relation": "R = a : √3"}
        elif narrative == "inradius_to_side":
            relations = {"side_relation": "a = 6r / √3"}
        elif narrative == "side_to_inradius":
            relations = {"radius_relation": "r = a√3 / 6"}

    # ------------------------------------------------------------------
    # FACTS (variables): единый контракт для humanizer
    # ------------------------------------------------------------------

    facts: Dict[str, Any] = {
        "figure": "equilateral_triangle",
        "narrative": narrative,  # humanizer читает это поле
        "answer": answer,

        "geometry_facts": context.get("geometry_facts") or {"triangle_type": "equilateral"},
        "given": norm_given,
        "target": norm_target,
        "relations": relations,
        "derived": derived,  # ⬅️ ключевой слой для устранения None/TypeError
    }

    # ------------------------------------------------------------------
    # solution_core (канон через helper)
    # ------------------------------------------------------------------

    return _build_solution_core(
        task_data=task_data,
        explanation_idea=f"IDEA_{narrative.upper()}",
        final_answer=answer if answer is not None else "",
        variables=facts,
        help_image=_extract_help_image(task_data),
        hints=[],
    )

def _solve_square_radius_midpoint(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Паттерн 3.3: square_radius_midpoint
    """
    return _not_implemented_stub(task_data, pattern="square_radius_midpoint")


def _solve_right_triangle_circumradius(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Паттерн 3.4: right_triangle_circumradius
    """
    return _not_implemented_stub(task_data, pattern="right_triangle_circumradius")


# -----------------------------
# Helpers: canonical solution_core
# -----------------------------
def _not_implemented_stub(task_data: Dict[str, Any], pattern: str) -> Dict[str, Any]:
    task_context = task_data.get("task_context") or {}
    narrative = (task_context.get("narrative") or "").strip()

    # Пока нет фактов — отдаём безопасный, канонический skeleton.
    # Humanizer на этом этапе ещё не должен вызываться для этих паттернов,
    # но формат не ломаем.
    return _build_solution_core(
        task_data=task_data,
        explanation_idea=f"IDEA::{pattern}::{narrative or 'unknown'}",
        final_answer="",  # пока пусто
        variables={
            "pattern": pattern,
            "narrative": narrative,
            # дальше мы добавим реальные facts
        },
        help_image=_extract_help_image(task_data),
        hints=[
            "Этот паттерн ещё в разработке. Скоро будет полное решение 🤝",
        ],
    )


def _build_error_solution_core(task_data: Dict[str, Any], error_message: str) -> Dict[str, Any]:
    return _build_solution_core(
        task_data=task_data,
        explanation_idea="IDEA::error",
        final_answer="",
        variables={
            "narrative": (task_data.get("task_context") or {}).get("narrative"),
            "error": error_message,
        },
        help_image=_extract_help_image(task_data),
        hints=[
            "😔 Решение пока недоступно.",
            "Нажми «Назад к заданию» или «В главное меню».",
        ],
    )


def _build_solution_core(
    task_data: Dict[str, Any],
    explanation_idea: str,
    final_answer: str,
    variables: Dict[str, Any],
    help_image: str | None,
    hints: list[str],
) -> Dict[str, Any]:
    """
    Канонический solution_core для задания 16 (плоский словарь).
    """
    task_type = str(task_data.get("task_type") or "16")
    question_id = task_data.get("question_id") or task_data.get("id") or ""
    question_group = task_data.get("question_group") or "task_16"

    return {
        "task_type": task_type,
        "question_id": question_id,
        "question_group": question_group,

        "explanation_idea": explanation_idea,
        "calculation_steps": [],          # в 16 часто пусто (мы подставим позже, если нужно)
        "final_answer": str(final_answer) if final_answer is not None else "",

        "variables": variables,           # facts + narrative (и только!)
        "help_image": help_image,         # строка или None
        "hints": hints or [],
    }


def _extract_help_image(task_data: Dict[str, Any]) -> str | None:
    """
    В ТЕМЕ 3 мы потом чётко пропишем правила под картинки.
    Сейчас — максимально нейтрально: берём help_image из task_context,
    иначе None.
    """
    task_context = task_data.get("task_context") or {}
    return task_context.get("help_image") or None


def _assert_solution_core_shape(solution_core: Dict[str, Any]) -> None:
    """
    Мини-проверка: чтобы не словить потом KeyError в humanizer из-за неправильного уровня передачи.
    """
    required = ("explanation_idea", "final_answer", "variables", "help_image", "hints")
    for k in required:
        if k not in solution_core:
            raise ValueError(f"solution_core missing key: '{k}'")

    if not isinstance(solution_core.get("variables"), dict):
        raise ValueError("solution_core['variables'] must be a dict")
