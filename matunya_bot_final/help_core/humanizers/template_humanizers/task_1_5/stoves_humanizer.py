from typing import Dict, Any


# ============================================================
# IDEA / STEP / TIPS templates
# ============================================================

IDEA_TEMPLATES: Dict[str, str] = {
    "IDEA_STOVE_MATCH": (
        "<b>Идея.</b>\n"
        "Сопоставь значения из строки «{column_label}» с данными печей в таблице."
    ),
}

STEP_TEMPLATES: Dict[str, str] = {
    "STEP_STOVE_MATCH": (
        "<b>Сопоставление:</b>\n"
        "{match_lines}"
    ),
}

TIPS_TEMPLATES: Dict[str, str] = {
    "TIP_STOVE_MATCH": "📌 Ищи точное совпадение значения в таблице.",
}

# ============================================================
# Narrative profiles (источник истины: variables)
# ============================================================

NARRATIVE_PROFILES: Dict[str, Dict[str, Any]] = {
    # -------------------------
    # Q1: stove_match_table
    # -------------------------
    "match_volume": {
        "pattern": "stove_match_table",
        "idea": "IDEA_STOVE_MATCH",
        "step": "STEP_STOVE_MATCH",
        "tip": "TIP_STOVE_MATCH",
    },
    "match_weight": {
        "pattern": "stove_match_table",
        "idea": "IDEA_STOVE_MATCH",
        "step": "STEP_STOVE_MATCH",
        "tip": "TIP_STOVE_MATCH",
    },
    "match_cost": {
        "pattern": "stove_match_table",
        "idea": "IDEA_STOVE_MATCH",
        "step": "STEP_STOVE_MATCH",
        "tip": "TIP_STOVE_MATCH",
    },

    # -------------------------
    # Q2–Q5 добавим позже
    # narratives будут здесь же
    # -------------------------
}


# ============================================================
# Public
# ============================================================

def humanize(solution_core: Dict[str, Any]) -> str:
    """
    Единый humanizer для stoves (вопросы 1–5).
    Humanizer ничего не вычисляет и не анализирует question_text.
    Всё берём из solution_core["variables"].
    """

    pattern = solution_core.get("pattern")
    narrative = solution_core.get("narrative")
    variables = solution_core.get("variables") or {}

    if not pattern or not narrative:
        raise ValueError("HUMANIZER: missing pattern/narrative")

    profile = NARRATIVE_PROFILES.get(narrative)
    if not profile:
        raise ValueError(f"HUMANIZER: unknown narrative: {narrative}")

    # защита: narrative должен соответствовать pattern
    expected_pattern = profile.get("pattern")
    if expected_pattern and expected_pattern != pattern:
        raise ValueError(f"HUMANIZER: narrative {narrative} does not match pattern {pattern}")

    # --------------------------------------------------------
    # Пока реализуем только stove_match_table
    # --------------------------------------------------------
    if pattern == "stove_match_table":
        return _humanize_stove_match(profile, variables)

    # Остальные паттерны добавим позже
    raise ValueError(f"HUMANIZER: unsupported pattern: {pattern}")


# ============================================================
# Internal: Q1 stove_match_table
# ============================================================

def _humanize_stove_match(profile: Dict[str, Any], variables: Dict[str, Any]) -> str:
    """
    variables required (Q1):
      - column_label: str
      - columns: list[int] (в порядке задания)
      - stove_no_to_value_mapping: dict[str,int] (печь -> значение)
      - answer: str (3 цифры)
    """

    column_label = variables["column_label"]
    columns = variables["columns"]
    mapping = variables["stove_no_to_value_mapping"]
    answer = variables["answer"]

    # строки сопоставления
    match_lines = []
    for value in columns:
        found_no = None
        for no, v in mapping.items():
            if v == value:
                found_no = no
                break
        # found_no не должен быть None, если validator/solver корректны
        match_lines.append(f"{value} → печь №{found_no}")

    idea_text = IDEA_TEMPLATES[profile["idea"]].format(column_label=column_label)
    step_text = STEP_TEMPLATES[profile["step"]].format(match_lines="\n".join(match_lines))
    tip_text = TIPS_TEMPLATES[profile["tip"]]

    return (
        f"{idea_text}\n\n"
        f"{step_text}\n\n"
        f"{tip_text}\n"
        f"\n<b>Ответ:</b> {answer}"
    )
