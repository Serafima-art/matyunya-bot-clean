import pytest
import shutil
from pathlib import Path

from matunya_bot_final.task_generators.task_11.generators.form_match_mixed_generator import (
    generate_task_11_form_match_mixed,
)
from matunya_bot_final.task_generators.task_11.validators.form_match_mixed_validator import (
    validate_task_11_form_match_mixed,
)

TEMP_DIR = Path("matunya_bot_final/temp/task_11/form_match_mixed")


@pytest.mark.asyncio
async def test_form_match_mixed_generator_validator_and_images():
    """
    Тест 1: Базовая проверка генерации, валидации и структуры задачи.
    """
    # --- 0. Чистим temp перед запуском ---
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    # --- 1. Генерация задачи ---
    task = generate_task_11_form_match_mixed()

    # --- 2. Проверка валидатором (НОВЫЙ СТАНДАРТ) ---
    is_valid, errors = validate_task_11_form_match_mixed(task)
    assert is_valid, f"Ошибки валидации: {errors}\nЗадача: {task}"

    # --- 3. Проверка изображений ---
    graphs = task["source_plot"]["params"]["graphs"]
    assert len(graphs) == 3, "Должно быть 3 графика"
    for path in graphs:
        file_path = Path(path)
        assert file_path.exists(), f"Файл графика отсутствует: {file_path}"

    # --- 4. Проверка options ---
    options = task["source_plot"]["params"]["options"]
    assert len(options) == 3, f"Ожидалось 3 опции, найдено {len(options)}"
    assert set(options.keys()) == {"1", "2", "3"}, "Ключи options должны быть '1','2','3'"

    # --- 5. Проверка answer ---
    answer = task["answer"]
    assert isinstance(answer, list) and len(answer) == 3, "Answer должен быть списком из 3 элементов"
    for a in answer:
        assert a in {"1", "2", "3"}, f"Некорректный ответ: {a}"


def test_all_images_are_generated():
    """
    НОВЫЙ Тест 2: НЕПРОБИВАЕМАЯ ПРОВЕРКА - Все файлы должны быть физически созданы.
    Проверяет, что после 10 генераций создано ровно 30 уникальных файлов.
    """
    print("--- Тест: Все изображения физически существуют ---")
    
    # Чистим временную папку перед запуском
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Запускаем генератор 10 раз
    all_graph_paths = []
    for i in range(10):
        task = generate_task_11_form_match_mixed()
        graphs = task['source_plot']['params']['graphs']
        all_graph_paths.extend(graphs)
        print(f"  Генерация {i+1}/10: создано {len(graphs)} графиков")
    
    # ПРОВЕРКА 1: Должно быть создано ровно 30 путей (10 задач × 3 графика)
    assert len(all_graph_paths) == 30, f"Ожидалось 30 путей, получено {len(all_graph_paths)}"
    
    # ПРОВЕРКА 2: Все пути должны быть уникальны
    unique_paths = set(all_graph_paths)
    assert len(unique_paths) == len(all_graph_paths), \
        f"Найдены дубликаты имен файлов! Уникальных: {len(unique_paths)}, всего: {len(all_graph_paths)}"
    
    # ПРОВЕРКА 3: Каждый файл ФИЗИЧЕСКИ СУЩЕСТВУЕТ на диске
    missing_files = []
    for path in all_graph_paths:
        if not Path(path).exists():
            missing_files.append(path)
    
    assert len(missing_files) == 0, \
        f"Следующие файлы не были созданы ({len(missing_files)} шт.):\n" + "\n".join(missing_files[:5])
    
    # ПРОВЕРКА 4: Все файлы имеют ненулевой размер
    empty_files = []
    for path in all_graph_paths:
        file_path = Path(path)
        if file_path.stat().st_size == 0:
            empty_files.append(path)
    
    assert len(empty_files) == 0, \
        f"Следующие файлы пустые ({len(empty_files)} шт.):\n" + "\n".join(empty_files[:5])
    
    print(f"✅ Все проверки пройдены: {len(all_graph_paths)} файлов созданы и уникальны")