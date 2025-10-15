"""
__init__.py для task_11
Хранит карту генераторов и универсальную точку входа.
"""

from typing import Dict, Callable

# Импорты подтипов
from matunya_bot_final.task_generators.task_11.generators.match_signs_a_c_generator import generate_task_11_match_signs_a_c
from matunya_bot_final.task_generators.task_11.generators.form_match_mixed_generator import generate_task_11_form_match_mixed
from matunya_bot_final.task_generators.task_11.generators.match_signs_k_b_generator import generate_task_11_match_signs_k_b  # 👈 новый импорт


# ==============================
# Маппинг генераторов
# ==============================
GENERATOR_MAP: Dict[str, Callable] = {
    "match_signs_a_c": generate_task_11_match_signs_a_c,
    "form_match_mixed": generate_task_11_form_match_mixed,
    "match_signs_k_b": generate_task_11_match_signs_k_b,  # 👈 регистрация нового подтипа
}


# ==============================
# Универсальный вызов
# ==============================
def generate_task_11_by_subtype(subtype: str) -> dict:
    """Универсальная точка входа для генерации задания №11 по подтипу."""
    if subtype not in GENERATOR_MAP:
        raise ValueError(f"Неизвестный подтип задания 11: {subtype}")
    return GENERATOR_MAP[subtype]()
