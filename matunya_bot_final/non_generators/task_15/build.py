# matunya_bot_final/non_generators/task_15/build.py

import os
import json
import sys

# Добавляем корневую директорию проекта в sys.path, чтобы импорты работали корректно
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# Импортируем валидаторы
from matunya_bot_final.non_generators.task_15.validators.angles_validator import AnglesValidator

# --- КОНФИГУРАЦИЯ ПУТЕЙ ---

# Папка, где лежит этот скрипт (task_15)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Папка с сырьем (.txt)
DEFINITIONS_DIR = os.path.join(BASE_DIR, "definitions")

# Папка с картинками (.svg)
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Папка для итогового JSON (data/tasks_15)
# Поднимаемся на 3 уровня вверх от task_15: non_generators -> matunya_bot_final -> root -> data
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "tasks_15")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "tasks_15.json")

# --- КАРТА ВАЛИДАТОРОВ ---
# Связывает имя файла с сырьем и класс валидатора, который его обрабатывает
VALIDATOR_MAPPING = {
    "angles.txt": AnglesValidator,
    # Будущие темы:
    # "right_triangles.txt": RightTrianglesValidator,
    # "isosceles_triangles.txt": IsoscelesTrianglesValidator,
    # "general_triangles.txt": GeneralTrianglesValidator,
}

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def load_svg_content(filename: str) -> str:
    """
    Читает содержимое SVG-файла из папки assets.
    Если файла нет, возвращает пустую строку и пишет предупреждение.
    """
    if not filename:
        return ""

    path = os.path.join(ASSETS_DIR, filename)

    if not os.path.exists(path):
        print(f"⚠️  WARNING: SVG файл не найден: {filename}")
        return ""

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return content
    except Exception as e:
        print(f"❌ ERROR: Не удалось прочитать SVG {filename}: {e}")
        return ""

def build():
    print(f"🏭 ЗАПУСК СБОРОЧНОГО ЦЕХА ЗАДАНИЯ 15...")
    print(f"📍 Директория определений: {DEFINITIONS_DIR}")
    print(f"📍 Директория ассетов: {ASSETS_DIR}")
    print(f"📍 Файл на выходе: {OUTPUT_FILE}")
    print("-" * 50)

    # Создаем папку для вывода, если её нет
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    all_tasks = []
    # Уникальный ID для задания 15 начинается с 1500000
    current_id = 1500000

    # Проходим по всем файлам, указанным в карте
    for filename, ValidatorClass in VALIDATOR_MAPPING.items():
        filepath = os.path.join(DEFINITIONS_DIR, filename)

        if not os.path.exists(filepath):
            print(f"🔸 Пропуск {filename}: файл еще не создан.")
            continue

        print(f"🔨 Обработка {filename}...")

        # Инициализируем валидатор для текущей темы
        try:
            validator = ValidatorClass()
        except Exception as e:
            print(f"❌ CRITICAL: Не удалось инициализировать валидатор для {filename}: {e}")
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        file_tasks_count = 0

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            # Пропускаем пустые строки и комментарии
            if not line or line.startswith("#"):
                continue

            try:
                # 1. Парсинг строки: pattern|text
                if "|" not in line:
                    raise ValueError(f"Неверный формат строки (нет разделителя '|'): {line[:50]}...")

                pattern, text = line.split("|", 1)

                # 2. Валидация и генерация "педагогического JSON"
                raw_data = {
                    "pattern": pattern.strip(),
                    "text": text.strip() # Используем ключ 'text' как в ТЗ для валидатора
                }

                # Здесь валидатор возвращает JSON структуру версии 3.0
                task_data = validator.validate(raw_data)

                # 3. Присвоение системного ID
                current_id += 1
                task_data["id"] = current_id

                # 4. ВНЕДРЕНИЕ КАРТИНКИ (SVG Injection)
                # Берем имя файла, которое определил валидатор
                img_filename = task_data.get("image_file")

                if img_filename:
                    # Читаем код картинки с диска
                    svg_code = load_svg_content(img_filename)
                    # Вставляем код картинки прямо в JSON
                    task_data["image_svg"] = svg_code
                else:
                    task_data["image_svg"] = ""

                # Добавляем готовую задачу в общий список
                all_tasks.append(task_data)
                file_tasks_count += 1

            except Exception as e:
                print(f"❌ Ошибка в файле {filename} на строке {line_num}:")
                print(f"   Текст: {line}")
                print(f"   Причина: {e}")

        print(f"   ✅ Добавлено задач: {file_tasks_count}")

    # Сохраняем итоговый JSON
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(all_tasks, f, ensure_ascii=False, indent=2)
        print("-" * 50)
        print(f"🎉 СБОРКА ЗАВЕРШЕНА УСПЕШНО!")
        print(f"📊 Всего задач в базе: {len(all_tasks)}")
        print(f"💾 Путь к файлу: {OUTPUT_FILE}")
    except Exception as e:
        print(f"❌ FATAL ERROR: Не удалось сохранить итоговый файл: {e}")

if __name__ == "__main__":
    build()
