# task_generators/tasks_1_5/tires/config.py
"""
Конфигурационный модуль для генератора задач "Шины".
Содержит все уникальные пути и правила для этого подтипа.
"""

from pathlib import Path

# --- 1. Пути к данным ---
# Определяем корень проекта, чтобы пути были надежными
# Path(__file__) -> config.py
# .parent -> tires/
# .parent -> tasks_1_5/
# .parent -> task_generators/
# .parent -> matunya_bot_final/ (корень проекта)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

# Путь к папке с данными для "Шин"
TIRES_DATA_ROOT = PROJECT_ROOT / "data" / "tasks_1_5" / "tires"

# Абсолютные пути к файлам и папкам
DATA_PATHS = {
    "intros": TIRES_DATA_ROOT / "texts" / "intros.json",
    "conditions": TIRES_DATA_ROOT / "texts" / "conditions.json",
    "questions": TIRES_DATA_ROOT / "texts" / "questions.json",
    "lexemes": TIRES_DATA_ROOT / "texts" / "lexemes.json",
    "plots_dir": TIRES_DATA_ROOT / "plots"
}

# ⚡ ИСПРАВЛЕНИЕ: Добавляем ожидаемые генератором атрибуты
TEXT_FILES = {
    "intros": TIRES_DATA_ROOT / "texts" / "intros.json",
    "conditions": TIRES_DATA_ROOT / "texts" / "conditions.json",
    "questions": TIRES_DATA_ROOT / "texts" / "questions.json",
    "lexemes": TIRES_DATA_ROOT / "texts" / "lexemes.json"
}

# Путь к папке с плотами (ожидается генератором)
PLOTS_DIR = TIRES_DATA_ROOT / "plots"

# --- 2. Правила Сборки ---
# Последовательность и варианты для сборки набора из 5 вопросов
ASSEMBLY_RULES = {
    "sequence": ["q1", "q2", "q3", "q4", ("q5", "q6")]
}

# --- 3. Статические Ассеты ---
# Список статичных изображений для "display_scenario"
# Пути указываются относительно корня проекта, чтобы хендлер их нашел
STATIC_IMAGES = [
    {
        "type": "image",
        "path": str(TIRES_DATA_ROOT / "assets" / "tire_cross_section.png"),
        "caption": "Рис. 1: Маркировка"
    },
    {
        "type": "image",
        "path": str(TIRES_DATA_ROOT / "assets" / "tire_technical_scheme.png"),
        "caption": "Рис. 2: Схема шины"
    }
]

# ⚡ ИСПРАВЛЕНИЕ: Переименовываем для совместимости с генератором
IMAGES = STATIC_IMAGES

# --- 4. Связь со "Специалистами" ---
# Пути для динамического импорта модулей-помощников
SPECIALISTS = {
    "calculator_path": "matunya_bot_final.task_generators.tasks_1_5.tires.calculator.TiresCalculator",
    "renderer_path": "matunya_bot_final.task_generators.tasks_1_5.tires.render_table"
}

# ⚡ ИСПРАВЛЕНИЕ: Добавляем недостающие атрибуты для генератора
QUESTION_KEYS = ["q1", "q2", "q3", "q4"]
Q5_ALTERNATIVES = ["q5", "q6"]

DEFAULT_METADATA = {
    "version": "1.0",
    "subtype": "tires",
    "category": "tasks_1_5",
    "description": "Задачи на автомобильные шины"
}

# --- Проверка существования файлов (опционально) ---
def validate_files():
    """Проверяет существование всех необходимых файлов"""
    missing_files = []

    for file_type, file_path in TEXT_FILES.items():
        if not file_path.exists():
            missing_files.append(f"{file_type}: {file_path}")

    if not PLOTS_DIR.exists():
        missing_files.append(f"plots directory: {PLOTS_DIR}")

    if missing_files:
        print("⚠️  Отсутствующие файлы:")
        for file in missing_files:
            print(f"   - {file}")
        return False

    return True

# Автоматическая проверка при импорте (можно закомментировать)
# validate_files()
