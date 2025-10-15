from .task_6 import MAIN_PROMPT, SUBTYPES
from ._task_6_gpt_legacy import (
    list_task6_subtypes,
    build_task6_prompt,
    generate_task_6,
)

__all__ = [
    "MAIN_PROMPT",
    "SUBTYPES",
    "list_task6_subtypes",
    "build_task6_prompt",
    "generate_task_6",
]