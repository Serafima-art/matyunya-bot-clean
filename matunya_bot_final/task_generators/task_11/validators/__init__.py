"""
__init__.py для пакета validators задания 11
Экспортирует функции валидации для всех подтипов.
"""

from .match_signs_a_c_validator import validate_task_11_match_signs_a_c
from .form_match_mixed_validator import validate_task_11_form_match_mixed
from .match_signs_k_b_validator import validate_task_11_match_signs_k_b  # 👈 новый импорт

__all__ = [
    "validate_task_11_match_signs_a_c",
    "validate_task_11_form_match_mixed",
    "validate_task_11_match_signs_k_b",  # 👈 новый экспорт
]
