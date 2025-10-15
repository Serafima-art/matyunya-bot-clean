import pkgutil
import importlib
import inspect
import random
from typing import Optional, Dict, Any, Callable 

# --- Главные словари, которые будет использовать весь остальной проект ---
GENERATOR_MAP = {}
VALIDATOR_MAP = {}

# --- Пути к нашим новым папкам с модулями ---
GENERATORS_PACKAGE = '.generators'
VALIDATORS_PACKAGE = '.validators'


def _populate_map_from_package(package_name: str, prefix: str, target_map: dict):
    """
    Автоматически находит все функции в пакете по префиксу и добавляет их в словарь.

    Например, находит функцию `_generate_some_task` в пакете `.generators`
    и добавляет её в `GENERATOR_MAP` под ключом `some_task`.
    """
    try:
        # Динамически импортируем пакет (например, task_12.generators)
        package = importlib.import_module(package_name, package=__name__)

        # Проходим по всем файлам (модулям) внутри этого пакета
        for _, module_name, _ in pkgutil.iter_modules(package.__path__):
            # Динамически импортируем каждый модуль (например, task_12.generators.calc)
            module = importlib.import_module(f"{package_name}.{module_name}", package=__name__)

            # Ищем внутри модуля все функции, которые начинаются с нужного префикса
            for func_name, func_obj in inspect.getmembers(module, inspect.isfunction):
                if func_name.startswith(prefix):
                    # Создаем ключ для словаря, убирая префикс
                    # "_generate_area_triangle" -> "area_triangle"
                    map_key = func_name[len(prefix):]
                    target_map[map_key] = func_obj

    except (ImportError, ModuleNotFoundError) as e:
        # Это может случиться, если папки еще не созданы. Просто выводим предупреждение.
        print(f"Предупреждение: не удалось загрузить модули из пакета '{package_name}'. Ошибка: {e}")


# --- Запускаем процесс сборки ---
_populate_map_from_package(GENERATORS_PACKAGE, '_generate_', GENERATOR_MAP)
_populate_map_from_package(VALIDATORS_PACKAGE, '_validate_', VALIDATOR_MAP)


# ─────────────────────────────────────────────────────────────────────────────
# Главная функция-дирижёр
# ─────────────────────────────────────────────────────────────────────────────
def generate_task_12_by_subtype(
    subtype_key: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Выбирает и запускает генератор задач №12 по его ключу (subtype).
    Если ключ не указан, выбирает случайный.
    """
    if subtype_key is None:
        subtype_key = random.choice(list(GENERATOR_MAP.keys()))
    
    generator_func = GENERATOR_MAP.get(subtype_key)
    if not generator_func:
        return None

    # Просто вызываем функцию-генератор
    task_data = generator_func()

    # Проверяем, что результат - это словарь с обязательными полями
    if not isinstance(task_data, dict):
         raise ValueError(f"Генератор '{subtype_key}' вернул не словарь, а {type(task_data)}")
    
    for key in ("subtype", "text", "answer"):
        if key not in task_data:
            raise ValueError(f"Генератор '{subtype_key}' вернул словарь без обязательного поля '{key}'")
    
    return task_data

# --- Добавляем "дирижёра" в список экспорта ---
__all__ = [
    'GENERATOR_MAP',
    'VALIDATOR_MAP',
    'generate_task_12_by_subtype' # <-- Теперь его можно будет импортировать из task_12
]