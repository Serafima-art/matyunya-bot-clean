import random
import math
from typing import Optional, Dict, Any, Callable, Tuple

from ..common import format_answer

def _generate_area_triangle_find_sin_alpha() -> dict:
    """
    Генерирует задачу на поиск sinα по формуле S = ½bcsinα.
    """
    # 1. Генерируем "красивый" ответ (sinα) и исходные данные
    sin_alpha = random.choice([0.2, 0.25, 0.4, 0.5, 0.75, 0.8, 1.0])
    
    # Подбираем b и c так, чтобы S было "красивым"
    while True:
        b = random.randint(4, 15)
        c = random.randint(4, 15)
        S = 0.5 * b * c * sin_alpha
        # Проверяем, что S - целое или с ".5"
        if (S * 2).is_integer():
            break

    # 2. Собираем текст задачи из наших уникализированных шаблонов
    intro_templates = [
        "Площадь треугольника (S) вычисляется по формуле S = ½bcsinα, где b и c — две стороны треугольника, а α — угол между ними.",
        "Для нахождения площади треугольника используется формула S = ½bcsinα, в которой b и c — это длины двух сторон, а α — угол между ними."
    ]
    
    known_text = f"b = {b}, c = {c} и S = {format_answer(S)}"
    
    task_templates = [
        f"Используя эту формулу, найди значение sinα, если {known_text}.",
        f"Вычисли, чему равно значение sinα, при условии, что {known_text}."
    ]
    
    intro_text = random.choice(intro_templates)
    task_text = random.choice(task_templates)
    
    final_text = f"{intro_text}\n{task_text}\n\nОтвет: __________"

    return {
        "subtype": "area_triangle_find_sin_alpha",
        "plot_id": "area_triangle_find_sin_alpha",
        "text": final_text,
        "answer": format_answer(sin_alpha),
        "params": {"S": S, "b": b, "c": c, "_find": "sin_alpha"},
        "hidden_params": {"_hidden_answer": sin_alpha},
        "constants": None
    }