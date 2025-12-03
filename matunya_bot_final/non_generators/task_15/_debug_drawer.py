# matunya_bot_final/non_generators/task_15/_debug_drawer.py
"""
Простой отладочный скрипт для локальной проверки SVGDrawer.
Рендерит все шаблоны T1-T9 и дополнительный тест угловых украшений.
"""

import os
from svg_drawer import SVGDrawer

OUTPUT_DIR = "debug_drawings"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


def run_full_template_test() -> None:
    """Рендер всех базовых шаблонов."""
    print("--- Генерация всех шаблонов SVGDrawer ---")
    drawer = SVGDrawer()

    template_keys = sorted(drawer.templates.keys())
    if not template_keys:
        print("Нет шаблонов для рендера.")
        return

    for template_id in template_keys:
        print(f"  - Рендер шаблона '{template_id}'...")
        drawing_info = {"template_id": template_id}
        svg_output = drawer.draw(drawing_info)
        file_path = os.path.join(OUTPUT_DIR, f"template_{template_id}.svg")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(svg_output)
    print(f"Готово: {len(template_keys)} файлов в '{OUTPUT_DIR}'.")


def run_decorations_test() -> None:
    """Рендер теста дуг и квадратиков в вершинах."""
    print("\n--- Генерация теста дуг/квадратиков ---")
    drawer = SVGDrawer()

    test_case_angles = {
        "name": "test_angles",
        "drawing_info": {
            "template_id": "T1",
            "decorations": [
                {"type": "right_angle_square", "at_vertex": "C"},
                {"type": "angle_arc", "at_vertex": "A", "style": "single"},
                {"type": "angle_arc", "at_vertex": "B", "style": "double"},
            ],
        },
    }

    svg_output = drawer.draw(test_case_angles["drawing_info"])
    file_path = os.path.join(OUTPUT_DIR, f"{test_case_angles['name']}.svg")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(svg_output)
    print(f"Готово: файл {file_path}")


if __name__ == "__main__":
    run_full_template_test()
    run_decorations_test()
