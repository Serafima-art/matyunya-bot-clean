import pytest
import shutil
from pathlib import Path

# --- Импортируем наши модули по новому, абсолютному стандарту ---
from matunya_bot_final.task_generators.task_11.generators.match_signs_a_c_generator import generate_task_11_match_signs_a_c
from matunya_bot_final.task_generators.task_11.validators.match_signs_a_c_validator import validate_task_11_match_signs_a_c
from matunya_bot_final.utils.visuals.plot_generator import create_graph


TEMP_DIR = Path("matunya_bot_final/temp/task_11/match_signs_a_c")


def test_generator_structure_and_validity():
    """
    Тест 1: Проверяет, что генератор создает корректную структуру 
    и что она проходит собственную валидацию.
    """
    print("--- Тест: Структура и базовая валидность ---")
    
    # Генерируем задачу
    task = generate_task_11_match_signs_a_c()
    
    # Проверяем, что валидатор считает ее корректной
    is_valid, errors = validate_task_11_match_signs_a_c(task)
    
    assert is_valid, f"Свежесгенерированная задача не прошла валидацию! Ошибки: {'; '.join(errors)}"
    
    # Проверяем ключевые поля
    assert task["task_type"] == 11
    assert task["subtype"] == "match_signs_a_c"
    assert isinstance(task["answer"], list) and len(task["answer"]) == 3
    
    # Проверяем, что нет "сырых" функций
    for func_data in task.get("func_data", []):
        assert "func" not in func_data, "В func_data не должно быть 'сырых' функций"
        assert "coeffs" in func_data, "В func_data должны быть коэффициенты 'coeffs'"


def test_validator_detects_wrong_answer():
    """
    Тест 2: Проверяет, что валидатор правильно определяет неверный ответ.
    """
    print("--- Тест: Валидатор ловит неверный ответ ---")
    
    task = generate_task_11_match_signs_a_c()
    
    # Создаем заведомо неверный ответ
    wrong_answer = ["9", "9", "9"]
    task_with_wrong_answer = task.copy()
    task_with_wrong_answer["answer"] = wrong_answer
    
    is_valid, errors = validate_task_11_match_signs_a_c(task_with_wrong_answer)
    
    assert not is_valid, "Валидатор не смог определить неверный ответ!"
    assert len(errors) > 0, "Список ошибок не должен быть пустым при неверном ответе."
    print(f"✅ Валидатор успешно определил ошибку: {errors[0]}")


@pytest.mark.asyncio
async def test_plot_generator_compatibility(tmp_path: Path):
    """
    Тест 3: Проверяет, что данные из генератора совместимы с "Художником" (plot_generator).
    """
    print("--- Тест: Совместимость с plot_generator ---")
    
    task = generate_task_11_match_signs_a_c()
    
    # Берем данные для первого графика
    first_graph_data = task["func_data"][0]
    
    # Формируем данные для "Художника"
    plot_data = {
        "coeffs": first_graph_data["coeffs"],  # Передаем коэффициенты
        "color": "purple"
    }
    
    output_filename = tmp_path / "test_graph.png"

    try:
        # Пытаемся нарисовать график
        create_graph(
            func_data=plot_data,
            output_filename=str(output_filename)
        )
    except Exception as e:
        pytest.fail(f"create_graph упал с ошибкой при работе с coeffs: {e}")

    assert output_filename.exists(), "Художник не смог создать файл графика по коэффициентам."
    print("✅ plot_generator успешно создал график по коэффициентам.")


def test_all_images_are_generated():
    """
    НОВЫЙ Тест 4: НЕПРОБИВАЕМАЯ ПРОВЕРКА - Все файлы должны быть физически созданы.
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
        task = generate_task_11_match_signs_a_c()
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