from typing import Dict, Any


# ============================================================
# Public API
# ============================================================

def solve_stoves_question(container: Dict[str, Any], q_number: int) -> Dict[str, Any]:
    """
    Единый solver для stoves (вопросы 1–5).
    Solver facts-only: ничего не считает, не анализирует тексты.
    Источник истины: container["questions"][...]["solution_data"] (валидатор).

    :param container: JSON-контейнер варианта stoves
    :param q_number: номер вопроса (1..5)
    :return: solution_core (канонический)
    """

    question = _get_question(container, q_number)

    pattern = question.get("pattern")
    narrative = question.get("narrative")
    skill_source_id = question.get("skill_source_id")

    if not pattern or not narrative:
        raise ValueError("SOLVER: missing pattern/narrative in question")

    # --------------------------------------------------------
    # Q1: stove_match_table
    # --------------------------------------------------------
    if pattern == "stove_match_table":
        return _solve_q1_match_table(question, q_number=q_number, skill_source_id=skill_source_id)

    # --------------------------------------------------------
    # Q2–Q5 добавим позже:
    # if pattern == "...": return _solve_q2(...)
    # --------------------------------------------------------

    raise ValueError(f"SOLVER: unsupported pattern: {pattern}")


# ============================================================
# Internal helpers
# ============================================================

def _get_question(container: Dict[str, Any], q_number: int) -> Dict[str, Any]:
    questions = container.get("questions") or []
    for q in questions:
        if q.get("q_number") == q_number:
            return q
    raise ValueError(f"SOLVER: question {q_number} not found in container")


def solve_stoves(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Универсальный вход для help_core.
    Вызывает нужный решатель по номеру вопроса.
    """

    task = data.get("task")
    variant = data.get("variant")

    q_number = task.get("q_number")

    if q_number == 1:
        return _solve_q1_match_table(task, variant)

    raise ValueError(f"Решатель для Q{q_number} ещё не реализован")


# ============================================================
# Q1 — stove_match_table (facts-only)
# ============================================================

def _solve_q1_match_table(task: Dict[str, Any], variant: Dict[str, Any]) -> Dict[str, Any]:
    """
    Q1 — stove_match_table

    Solver НЕ считает.
    Он только аккуратно упаковывает данные из JSON в solution_core.

    Берём из task:
      - input_data.columns_order
      - solution_data.stove_no_to_value_mapping
      - solution_data.answer_sequence
      - skill_source_id
      - narrative
      - q_number
    """

    narrative = task.get("narrative")
    q_number = task.get("q_number")
    skill_source_id = task.get("skill_source_id")

    input_data = task.get("input_data") or {}
    solution_data = task.get("solution_data") or {}

    columns = input_data.get("columns_order")
    mapping = solution_data.get("stove_no_to_value_mapping")
    answer = solution_data.get("answer_sequence") or task.get("answer")

    # --- Минимальная защита (без вычислений!) ---
    required = {
        "columns_order": columns,
        "stove_no_to_value_mapping": mapping,
        "answer": answer,
        "narrative": narrative,
        "q_number": q_number,
        "skill_source_id": skill_source_id,
    }

    missing = [k for k, v in required.items() if v is None]
    if missing:
        raise ValueError(f"SOLVER Q1: missing fields: {', '.join(missing)}")

    label_by_narrative = {
        "match_volume": "Наибольший объём, м³",
        "match_weight": "Масса, кг",
        "match_cost": "Стоимость, руб.",
    }

    column_label = label_by_narrative.get(narrative)
    if column_label is None:
        raise ValueError(f"SOLVER Q1: unknown narrative for label: {narrative}")

    # --- Канонический solution_core ---

    solution_core: Dict[str, Any] = {
        "question_id": q_number,
        "pattern": "stove_match_table",
        "narrative": narrative,
        "skill_source_id": skill_source_id,
        "explanation_idea": "IDEA_STOVE_MATCH",
        "calculation_steps": [],
        "final_answer": answer,
        "variables": {
            "column_label": column_label,
            "columns": columns,
            "stove_no_to_value_mapping": mapping,
            "answer": answer,
        },
        "hints": [],
    }

    # help_core ожидает обёртку
    return {
        "solution_core": solution_core
    }
