from .task_7_generator import generate_task_7
from .task_7_prompts import SUBTYPES

def list_task7_subtypes():
    return [k.split(" ", 1)[1] if " " in k else k for k in SUBTYPES.keys()]