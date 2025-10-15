# tests/validators/test_task12_db.py
import json
from pathlib import Path

DB_PATH = Path("data/tasks_12/tasks_12.json")


def load_tasks():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_ids_are_unique():
    tasks = load_tasks()
    ids = [t["id"] for t in tasks]
    assert len(ids) == len(set(ids)), "Есть дубликаты id!"


def test_required_fields_exist_and_not_empty():
    tasks = load_tasks()
    required_fields = [
        "id",
        "task_type",
        "subtype",
        "question_type",
        "difficulty",
        "text",
        "answer",
        "source_plot",
    ]
    for task in tasks:
        for field in required_fields:
            assert field in task, f"Поле {field} отсутствует в задаче {task.get('id')}"
            assert task[field] not in (None, ""), f"Поле {field} пустое в задаче {task['id']}"


def test_task_type_is_12():
    tasks = load_tasks()
    for task in tasks:
        assert task["task_type"] == 12, f"task_type неверный в {task['id']}"


def test_source_plot_structure():
    tasks = load_tasks()
    for task in tasks:
        sp = task["source_plot"]

        # обязательные ключи
        for key in ["plot_id", "params", "hidden_params", "constants"]:
            assert key in sp, f"Нет {key} в source_plot задачи {task['id']}"

        # None быть не должно
        for key in ["params", "hidden_params", "constants"]:
            assert sp[key] is not None, f"{key} = None в {task['id']}"

        # должны быть dict-и (или хотя бы пустые словари)
        for key in ["params", "hidden_params", "constants"]:
            assert isinstance(sp[key], dict), f"{key} не dict в {task['id']}"


def test_text_and_answer_are_valid():
    tasks = load_tasks()
    for task in tasks:
        # текст должен содержать хотя бы одну цифру
        assert any(ch.isdigit() for ch in task["text"]), f"В тексте нет чисел ({task['id']})"
        # ответ не пустой
        assert str(task["answer"]).strip() != "", f"Пустой answer в {task['id']}"