from typing import Dict, Any


def solve_stoves(task_context: Dict[str, Any]) -> Dict[str, Any]:

    task: Dict[str, Any] = task_context["task"]
    variant: Dict[str, Any] = task_context["variant"]

    question_id = task["q_number"]
    pattern = task["pattern"]
    narrative = task["narrative"]

    base_variables: Dict[str, Any] = (task.get("solution_data") or {}).copy()
    variables: Dict[str, Any] = base_variables.copy()

    # =========================================================
    # 🔵 PATTERN: stove_match_table
    # =========================================================

    if pattern == "stove_match_table":

        input_data = task.get("input_data") or {}

        columns = input_data.get("columns_order")
        column_label = input_data.get("column_label")
        mapping = base_variables.get("stove_no_to_value_mapping")
        answer = base_variables.get("answer_sequence") or task.get("answer")

        required = {
            "columns_order": columns,
            "column_label": column_label,
            "mapping": mapping,
            "answer": answer,
        }

        missing = [k for k, v in required.items() if v is None]
        if missing:
            raise ValueError(f"SOLVER Q1: missing fields: {', '.join(missing)}")

        variables.update({
            "column_label": column_label,
            "columns": columns,
            "stove_no_to_value_mapping": mapping,
            "answer": answer,
        })

        # 👇 narrative-specific explanation idea
        if narrative == "match_volume":
            explanation_idea = "IDEA_STOVE_MATCH_VOLUME"
        elif narrative == "match_weight":
            explanation_idea = "IDEA_STOVE_MATCH_WEIGHT"
        elif narrative == "match_cost":
            explanation_idea = "IDEA_STOVE_MATCH_COST"
        else:
            raise ValueError(f"Unsupported narrative for stove_match_table: {narrative}")

    else:
        raise ValueError(f"SOLVER: unsupported pattern: {pattern}")

    # =========================================================
    # 📦 Канонический solution_core
    # =========================================================

    solution_core: Dict[str, Any] = {
        "question_id": question_id,
        "pattern": pattern,
        "narrative": narrative,
        "skill_source_id": task.get("skill_source_id"),
        "explanation_idea": explanation_idea,
        "calculation_steps": [],
        "final_answer": task.get("answer"),
        "variables": variables,
        "hints": [],
    }

    return {
        "solution_core": solution_core
    }
