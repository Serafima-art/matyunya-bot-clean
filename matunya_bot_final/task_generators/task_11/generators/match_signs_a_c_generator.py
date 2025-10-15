"""
Генератор подтипа match_signs_a_c для задания 11.
"""

import uuid
import random
from pathlib import Path
from typing import Dict, Any, List

from matunya_bot_final.utils.visuals.plot_generator import create_graph


def generate_task_11_match_signs_a_c() -> dict:
    ALL_OPTIONS = {
        "1": "a > 0, c > 0",
        "2": "a > 0, c < 0",
        "3": "a < 0, c > 0",
        "4": "a < 0, c < 0"
    }

    # --- Случайные коэффициенты ---
    coef_sets = []
    used_signs = set()
    while len(coef_sets) < 3:
        a = random.choice([-2, -1, 1, 2])
        b = random.randint(-3, 3)
        c = random.choice([-3, -2, -1, 1, 2, 3])
        sign_pair = (1 if a > 0 else -1, 1 if c > 0 else -1)
        if sign_pair not in used_signs:
            used_signs.add(sign_pair)
            coef_sets.append((a, b, c))

    # --- Генерация уникального ID для задачи ---
    unique_id_for_task = f"11_match_signs_a_c_{uuid.uuid4().hex[:6]}"

    save_dir = Path("matunya_bot_final/temp/task_11/match_signs_a_c")
    save_dir.mkdir(parents=True, exist_ok=True)

    labels = ["A", "Б", "В"]
    graphs_data = []
    answer_global = []
    graph_paths = []

    for (a, b, c), label in zip(coef_sets, labels):
        graph_filename = str(save_dir / f"{unique_id_for_task}_{label}.png")
        graph_paths.append(graph_filename)

        create_graph(
            func_data={
                "coeffs": {"a": a, "b": b, "c": c},
                "label": label,
                "color": "orange"
            },
            output_filename=graph_filename,
            x_lim=[-5, 5],
            y_lim=[-5, 5]
        )

        graphs_data.append({
            "coeffs": {"a": a, "b": b, "c": c},
            "color": "orange",
            "label": f"y={a}x²{b:+d}x{c:+d}",
            "graphs": [graph_filename],
            "_debug_coeffs": {"a": a, "b": b, "c": c}
        })

        # Определяем глобальный ответ (1..4)
        if a > 0 and c > 0:
            expected = "1"
        elif a > 0 and c < 0:
            expected = "2"
        elif a < 0 and c > 0:
            expected = "3"
        else:
            expected = "4"
        answer_global.append(expected)

    # --- Перенумеровка в локальные 1,2,3 ---
    unique_answers = sorted(set(answer_global), key=int)   # например ["1","2","4"]
    local_map = {glob: str(i+1) for i, glob in enumerate(unique_answers)}  # {"1":"1","2":"2","4":"3"}
    answer_local = [local_map[a] for a in answer_global]
    displayed_options = {local_map[k]: ALL_OPTIONS[k] for k in unique_answers}

    # --- Текст задания ---
    variants_text = "\n".join([f"{k}) {displayed_options[k]}" for k in displayed_options])
    text = (
        "На рисунках изображены графики квадратичных функций\n"
        "y = ax² + bx + c.\n\n"
        "Установи соответствие между графиками и знаками коэффициентов a и c.\n\n"
        f"{variants_text}\n\n"
        "Ответ:  А ___   Б ___   В ___\n\n"
        "👉 В ответе укажи соответствующий номер\n"
        "(например: 3 2 1)"
    )

    return {
        "id": unique_id_for_task,
        "task_id": f"11_{random.randint(1, 99):02d}",
        "task_type": 11,
        "subtype": "match_signs_a_c",
        "topic": "read_graphs",
        "category": "matching",
        "subcategory": "coefficients",
        "text": text,
        "answer": answer_local,           # ["1","2","3"]
        "func_data": graphs_data,
        "x_lim": [-5, 5],
        "y_lim": [-5, 5],
        "source_plot": {
            "plot_id": "match_signs_a_c",
            "params": {
                "labels": labels,
                "graphs": graph_paths,
                "options": displayed_options   # только 3, перенумерованные
            }
        }
    }
