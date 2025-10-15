import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional

from .subtype_templates import generate_help_steps

# 📌 Путь к корню проекта
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Кэш для хранения загруженных данных
_DATA_CACHE: Dict[str, List[Dict[str, Any]]] = {}

def _load_json(path: Path) -> List[Dict[str, Any]]:
    """Загружает и валидирует JSON файл с заданиями."""
    if not path.exists():
        raise FileNotFoundError(f"Файл с заданиями не найден: {path}")
    
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Ошибка в формате JSON: {e}")
    
    if not isinstance(data, list):
        raise ValueError("Файл должен содержать список заданий")
    
    return data

def _ensure_schema_task6(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Приводит задания к единой структуре и генерирует help_steps."""
    normalized = []
    
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        
        # Базовые поля
        task = {
            "id": item.get("id") or f"t6_{idx+1}",
            "text": str(item.get("text") or "").strip(),
            "answer": str(item.get("answer") or "").strip(),
            "subtype": item.get("subtype"),
            "help_steps": item.get("help_steps", [])
        }
        
        # Автогенерация help_steps если есть подтип
        if task["subtype"] and not task["help_steps"]:
            task["help_steps"] = generate_help_steps(task)
        
        normalized.append(task)
    
    if not normalized:
        raise ValueError("Не найдено валидных заданий")
    
    return normalized

def _get_dataset(name: str, loader) -> List[Dict[str, Any]]:
    """Возвращает кэшированные данные или загружает новые."""
    if name not in _DATA_CACHE:
        _DATA_CACHE[name] = loader()
    return _DATA_CACHE[name]

def load_task_6() -> List[Dict[str, Any]]:
    """Основная функция загрузки заданий №6."""
    file_path = DATA_DIR / "tasks_6.json"
    raw_data = _load_json(file_path)
    return _ensure_schema_task6(raw_data)

# Инициализация кэша
task_6_data: List[Dict[str, Any]] = _get_dataset("task_6", load_task_6)

def get_random_task_6(subtype: Optional[str] = None) -> Dict[str, Any]:
    """Возвращает случайное задание с фильтром по подтипу."""
    pool = task_6_data
    if subtype:
        pool = [t for t in pool if t.get("subtype") == subtype]
        if not pool:
            raise ValueError(f"Задания с подтипом '{subtype}' не найдены")
    
    task = random.choice(pool)
    
    # Догенерация help_steps на случай прямого обращения
    if not task.get("help_steps") and task.get("subtype"):
        task["help_steps"] = generate_help_steps(task)
    
    return task

def get_task6_by_id(task_id: str) -> Optional[Dict[str, Any]]:
    """Возвращает задание по ID."""
    task = next((t for t in task_6_data if t["id"] == task_id), None)
    if task and not task.get("help_steps") and task.get("subtype"):
        task["help_steps"] = generate_help_steps(task)
    return task

def load_task_7() -> List[Dict[str, Any]]:
    """Основная функция загрузки заданий №7."""
    file_path = DATA_DIR / "tasks_7.json"
    return _load_json(file_path)

# Инициализация кэша для заданий 7
task_7_data: List[Dict[str, Any]] = _get_dataset("task_7", load_task_7)

def get_random_task_7() -> Dict[str, Any]:
    """Возвращает случайное задание №7."""
    return random.choice(task_7_data)