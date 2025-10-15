import os
from pathlib import Path

# --- ШАБЛОНЫ КОДА ДЛЯ НОВЫХ ФАЙЛОВ ---

CONFIG_TEMPLATE = """# task_generators/tasks_1_5/{subtype_name}/config.py
from pathlib import Path

# Определяем базовую директорию для этого подтипа
BASE_DIR = Path(__file__).parent.parent / "{subtype_name}"
DATA_DIR = Path("data/tasks_1_5/{subtype_name}")

# --- Пути к файлам с данными ---
TEXT_FILES = {{
    "intros": DATA_DIR / "texts" / "intros.json",
    "conditions": DATA_DIR / "texts" / "conditions.json",
    "questions": DATA_DIR / "texts" / "questions.json",
    "lexemes": DATA_DIR / "texts" / "lexemes.json",
}}

PLOTS_DIR = DATA_DIR / "plots"

# --- Пути к файлам со статикой ---
ASSETS_DIR = DATA_DIR / "assets"
IMAGES = [
    # {{"type": "image", "path": str(ASSETS_DIR / "image1.png")}},
]

# --- Подключение "Специалистов" ---
SPECIALISTS = {{
    "calculator_path": "task_generators.tasks_1_5.{subtype_name}.calculator.{capitalized_name}Calculator",
    "renderer_path": "task_generators.tasks_1_5.{subtype_name}.render_table",
}}

# --- Правила сборки ---
QUESTION_KEYS = ["q1", "q2", "q3", "q4"]
Q5_ALTERNATIVES = ["q5", "q6"]

# --- Метаданные для отображения ---
DEFAULT_METADATA = {{
    "name": "📝 {capitalized_name}",
    "success_emoji": "🎉",
}}
"""

CALCULATOR_TEMPLATE = """# task_generators/tasks_1_5/{subtype_name}/calculator.py
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class {capitalized_name}Calculator:
    \"\"\"
    Производит все математические расчеты для подтипа '{subtype_name}'.
    \"\"\"
    def calculate_all_tasks(self, plot_data: Dict[str, Any]) -> Dict[str, Any]:
        answers = {{}}
        try:
            # Здесь будет логика для расчета всех 5-6 задач
            # answers["task_1_answer"] = self._solve_task_1(plot_data)
            # answers["task_2_answer"] = self._solve_task_2(plot_data)
            # ...
            logger.info("Все задачи для '{subtype_name}' успешно рассчитаны.")
            
        except Exception as e:
            logger.error(f"Ошибка при расчете задач для '{subtype_name}': {{e}}")

        return answers

    # --- Приватные методы для решения каждой задачи ---
    # def _solve_task_1(self, plot_data):
    #     # ...
    #     return 42
"""

RENDERER_TEMPLATE = """# task_generators/tasks_1_5/{subtype_name}/render_table.py
from typing import Dict, Any

def render_custom_table(data: Dict[str, Any]) -> str:
    \"\"\"
    Генерирует кастомную HTML-таблицу для подтипа '{subtype_name}'.
    
    Returns:
        Строка с готовой HTML-разметкой.
    \"\"\"
    html = "<b>Таблица для {subtype_name}</b><br>"
    # ... здесь будет логика генерации таблицы ...
    return html
"""

def main():
    """Главная функция скрипта-строителя."""
    subtype_name = input("Введите имя нового подтипа (например, ovens, apartment): ").strip().lower()

    if not subtype_name or not subtype_name.isidentifier():
        print("❌ Ошибка: Имя подтипа должно быть одним словом на латинице.")
        return

    print(f"\n🚀 Создаю структуру для подтипа '{subtype_name}'...")

    # Определяем пути
    base_dir = Path("task_generators/tasks_1_5") / subtype_name
    data_dir = Path("data/tasks_1_5") / subtype_name

    # Список папок для создания
    dirs_to_create = [
        base_dir,
        data_dir,
        data_dir / "plots",
        data_dir / "texts",
        data_dir / "assets",
    ]

    for d in dirs_to_create:
        d.mkdir(parents=True, exist_ok=True)
        print(f"✅ Папка '{d}' создана.")

    # Список файлов для создания с их шаблонами
    capitalized_name = subtype_name.capitalize()
    files_to_create = {
        base_dir / "__init__.py": "",
        base_dir / "config.py": CONFIG_TEMPLATE.format(subtype_name=subtype_name, capitalized_name=capitalized_name),
        base_dir / "calculator.py": CALCULATOR_TEMPLATE.format(subtype_name=subtype_name, capitalized_name=capitalized_name),
        base_dir / "render_table.py": RENDERER_TEMPLATE.format(subtype_name=subtype_name),
        data_dir / "texts" / "intros.json": "[]",
        data_dir / "texts" / "conditions.json": "[]",
        data_dir / "texts" / "questions.json": "{}",
        data_dir / "texts" / "lexemes.json": "{}",
        data_dir / "plots" / f"{subtype_name}_plot_01.json": "{}",
    }

    for file_path, content in files_to_create.items():
        if not file_path.exists():
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ Файл '{file_path}' создан.")
        else:
            print(f"🟡 Файл '{file_path}' уже существует, пропускаю.")

    print(f"\n🎉 Готово! Фундамент для подтипа '{subtype_name}' заложен.")
    print("Не забудьте добавить новый подтип в конфигурацию роутеров и метаданные.")

if __name__ == "__main__":
    main()