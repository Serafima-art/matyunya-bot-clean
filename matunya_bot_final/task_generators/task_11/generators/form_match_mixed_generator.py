"""
form_match_mixed_generator.py
Генератор подтипа form_match_mixed для задания 11 ОГЭ.
"""

import random
import string
from pathlib import Path
from typing import Dict, Any

from ..formula_generators import generate_formula, get_color
from matunya_bot_final.utils.visuals.plot_generator import create_graph


def generate_task_11_form_match_mixed() -> Dict[str, Any]:
    """
    Генератор подтипа form_match_mixed.
    Создаёт задание с 3 графиками разных типов функций.
    Картинки сохраняются в temp/task_11/form_match_mixed.
    """

    # Возможные сценарии (3 разных типа из 4)
    scenarios = [
        ("linear", "parabola", "hyperbola"),  # Л+П+Г
        ("linear", "parabola", "sqrt"),       # Л+П+К
        ("linear", "hyperbola", "sqrt"),      # Л+Г+К
        ("parabola", "hyperbola", "sqrt")     # П+Г+К
    ]
    chosen_scenario = random.choice(scenarios)

    # Генерация формул для выбранного сценария
    formulas_data = [generate_formula(ftype) for ftype in chosen_scenario]

    # В ОГЭ всегда 3 варианта — оставляем только 3 формулы
    all_options = formulas_data
    random.shuffle(all_options)

    options = {str(i + 1): opt["formula_str"] for i, opt in enumerate(all_options)}

    # Определяем правильные ответы (номера из options)
    answers = []
    for f in formulas_data:
        for k, v in options.items():
            if v == f["formula_str"]:
                answers.append(k)
                break

    # Подготовка func_data и путей к графикам
    labels = ["A", "Б", "В"]
    func_data_list = []
    graph_paths = []

    # Папка для сохранения картинок
    save_dir = Path("matunya_bot_final/temp/task_11/form_match_mixed")
    save_dir.mkdir(parents=True, exist_ok=True)

    # Уникальный ID
    unique_id = f"11_form_match_mixed_{''.join(random.choices(string.ascii_lowercase + string.digits, k=6))}"

    for i, f in enumerate(formulas_data):
        path = save_dir / f"{unique_id}_{labels[i]}.png"
        func_data_list.append({
            "func": f["func"],
            "label": f["formula_str"],
            "color": get_color(i)
        })
        graph_paths.append(str(path))

        # 🖼 Вызов художника для отрисовки
        create_graph(
            func_data={
                "func": f["func"],
                "label": labels[i],
                "color": get_color(i)
            },
            output_filename=str(path),
            x_lim=(-6, 6),
            y_lim=(-6, 6),
        )

    return {
        "id": unique_id,
        "task_id": "11_10",
        "task_type": 11,
        "subtype": "form_match_mixed",
        "topic": "transformations",
        "category": "matching",
        "subcategory": "formulas",
        "text": (
            "На рисунках изображены графики функций. "
            "Установи соответствие между графиками и формулами. "
            "Ответ запиши в виде: А ___   Б ___   В ___"
        ),
        "answer": answers,
        "func_data": func_data_list,
        "x_lim": [-6, 6],
        "y_lim": [-6, 6],
        "source_plot": {
            "plot_id": "form_match_mixed",
            "params": {
                "labels": labels,
                "graphs": graph_paths,
                "options": options
            }
        }
    }
