import re
import math
import random

from ..common import to_float, grab_labeled_number, format_answer

def _generate_joule_lenz_find_t() -> dict:
    """
    Генерирует задачу на поиск времени t по закону Джоуля-Ленца (Q = I²Rt).
    Использует уникализированные формулировки.
    """
    # 1. Генерация чисел (остается без изменений)
    t = random.randint(5, 25) 
    I = random.randint(2, 9) + 0.5
    R = random.randint(2, 5)
    Q = I**2 * R * t
    
    # 2. Собираем текст задачи из наших собственных шаблонов
    
    # --- БАНК ФОРМУЛИРОВОК ---
    intro_templates = [
        "Количество теплоты Q (в джоулях), выделяемое проводником, можно рассчитать по закону Джоуля — Ленца: Q = I²Rt. В этой формуле I — сила тока (в амперах), R — сопротивление (в омах), а t — время прохождения тока (в секундах).",
        "Для расчёта количества теплоты Q (в джоулях) применяется формула Q = I²Rt (закон Джоуля — Ленца), где R — сопротивление цепи (в омах), I — сила тока (в амперах), а t — продолжительность протекания тока (в секундах)."
    ]
    
    known_text = f"Q = {format_answer(Q)} Дж, I = {format_answer(I)} А и R = {R} Ом"
    
    task_templates = [
        f"Используя данную формулу, определи время t (в секундах), если известно, что {known_text}.",
        f"Вычисли время t (в секундах) для цепи, в которой {known_text}, пользуясь указанной формулой."
    ]
    # --- КОНЕЦ БАНКА ---

    # Случайным образом выбираем шаблоны и собираем текст
    intro_text = random.choice(intro_templates)
    task_text = random.choice(task_templates)
    
    # Добавляем обязательное поле для ответа
    final_text = f"{intro_text}\n{task_text}\n\nОтвет: __________"

    return {
        "subtype": "joule_lenz_find_t",
        "plot_id": "joule_lenz_find_t",
        "text": final_text,
        "answer": format_answer(t),
        "params": {"Q": Q, "I": I, "R": R, "_find": "t"},
        "hidden_params": {"_hidden_answer": t},
        "constants": None
    }