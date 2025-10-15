"""
Генератор подтипа match_signs_k_b для задания 11 (линейная функция).
Задача: установить соответствие между графиками и знаками коэффициентов k и b.
"""

import uuid
import random
from pathlib import Path
from typing import Dict, Any, List

from matunya_bot_final.utils.visuals.plot_generator import create_graph


def generate_task_11_match_signs_k_b() -> dict:
    # --- Все возможные комбинации ---
    ALL_OPTIONS = {
        "1": "k > 0, b < 0",
        "2": "k < 0, b > 0",
        "3": "k < 0, b < 0",
        "4": "k > 0, b > 0",
    }

    # --- Генерация коэффициентов ---
    coef_sets: List[tuple[int, int]] = []
    used_signs = set()

    while len(coef_sets) < 3:
        k = random.choice([-3, -2, -1, 1, 2, 3])
        b = random.choice([-5, -4, -3, -2, 2, 3, 4, 5])  # исключаем 0
        sign_pair = (1 if k > 0 else -1, 1 if b > 0 else -1)

        if sign_pair not in used_signs:
            used_signs.add(sign_pair)
            coef_sets.append((k, b))

    # --- ID и директория сохранения ---
    unique_id_for_task = f"11_match_signs_k_b_{uuid.uuid4().hex[:6]}"
    save_dir = Path("matunya_bot_final/temp/task_11/match_signs_k_b")
    save_dir.mkdir(parents=True, exist_ok=True)

    labels = ["A", "Б", "В"]
    graphs_data: List[Dict[str, Any]] = []
    answer_global: List[str] = []
    graph_paths: List[str] = []

    # --- Создаём графики ---
    for (k, b), label in zip(coef_sets, labels):
        graph_filename = str(save_dir / f"{unique_id_for_task}_{label}.png")
        graph_paths.append(graph_filename)

        # ✅ ИСПРАВЛЕНО: создаём готовую lambda-функцию, которую умеет рисовать художник
        create_graph(
            func_data={
                "func": lambda x, k=k, b=b: k * x + b,  # 👈 готовая функция y = kx + b
                "label": label,
                "color": "orange",
            },
            output_filename=graph_filename,
            x_lim=[-5, 5],
            y_lim=[-5, 5],
        )

        graphs_data.append({
            "type": "linear",
            "coeffs": {"k": k, "b": b},
            "color": "orange",
            "label": label,
            "graphs": [graph_filename],
        })

        # Определяем правильный глобальный вариант
        if k > 0 and b < 0:
            expected = "1"
        elif k < 0 and b > 0:
            expected = "2"
        elif k < 0 and b < 0:
            expected = "3"
        else:  # k > 0 and b > 0
            expected = "4"

        answer_global.append(expected)

    # --- Перенумеровка в локальные варианты ---
    unique_answers = sorted(set(answer_global), key=int)
    local_map = {glob: str(i + 1) for i, glob in enumerate(unique_answers)}
    answer_local = [local_map[a] for a in answer_global]
    displayed_options = {local_map[k]: ALL_OPTIONS[k] for k in unique_answers}

    # --- Текст условия (свободная формулировка) ---
    variants_text = "\n".join([f"{k}) {displayed_options[k]}" for k in sorted(displayed_options.keys(), key=int)])
    text = (
        "Перед тобой три графика линейных функций вида y = kx + b.\n\n"
        "Определи, какие знаки имеют коэффициенты k и b для каждого графика.\n\n"
        f"{variants_text}\n\n"
        "Ответ:  А ___   Б ___   В ___\n\n"
        "👉 Запиши номера выбранных вариантов через пробел\n"
        "(например: 3 2 1)"
    )

    return {
        "id": unique_id_for_task,
        "task_id": f"11_{random.randint(1, 99):02d}",
        "task_type": 11,
        "subtype": "match_signs_k_b",
        "topic": "read_graphs",
        "category": "matching",
        "subcategory": "coefficients",
        "text": text,
        "answer": answer_local,
        "func_data": graphs_data,
        "x_lim": [-5, 5],
        "y_lim": [-5, 5],
        "source_plot": {
            "plot_id": "match_signs_k_b",
            "params": {
                "labels": labels,
                "graphs": graph_paths,
                "options": displayed_options,
            },
        },
    }
