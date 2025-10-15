import inspect
import ast
import pytest
from typing import Dict, Callable, Tuple

# --- 1. ГЛАВНОЕ ИЗМЕНЕНИЕ: меняем импортируемые модули ---
# Теперь мы смотрим на 'eq_geometry', а не на 'calc_geometry'
from matunya_bot_final.task_generators.task_12.generators import eq_geometry as gen_module
from matunya_bot_final.task_generators.task_12.validators import eq_geometry as val_module


# --- 2. Создаем локальные MAP'ы для конкретного модуля ---
def _create_local_maps() -> Tuple[Dict[str, Callable], Dict[str, Callable]]:
    """
    Создает словари генераторов и валидаторов только для модуля eq_geometry.
    """
    gen_map = {}
    val_map = {}
    
    for name, func in inspect.getmembers(gen_module, inspect.isfunction):
        if name.startswith('_generate_'):
            subtype = name[len('_generate_'):]
            gen_map[subtype] = func
            
    for name, func in inspect.getmembers(val_module, inspect.isfunction):
        if name.startswith('_validate_'):
            subtype = name[len('_validate_'):]
            val_map[subtype] = func
            
    return gen_map, val_map

LOCAL_GENERATOR_MAP, LOCAL_VALIDATOR_MAP = _create_local_maps()


# --- 3. Адаптированные тесты (меняем названия для ясности) ---

def test_generator_vs_validator_eq_geometry():
    """Проверяет совместимость генераторов и валидаторов из eq_geometry."""
    errors = []
    if not LOCAL_GENERATOR_MAP:
        pytest.skip("В модуле eq_geometry нет генераторов для теста.")

    for subtype, generator_func in LOCAL_GENERATOR_MAP.items():
        validator_func = LOCAL_VALIDATOR_MAP.get(subtype)
        if not validator_func:
            continue

        for _ in range(5):
            task = generator_func()
            try:
                if not validator_func(task):
                    errors.append((subtype, task))
            except Exception as e:
                errors.append((subtype, f"Ошибка в валидаторе '{subtype}': {e}"))

    assert not errors, f"Ошибки валидации для eq_geometry:\n{errors}"

def test_subtype_keys_match_eq_geometry():
    """Проверяет, что у каждого генератора в eq_geometry есть свой валидатор."""
    gen_keys = set(LOCAL_GENERATOR_MAP.keys())
    val_keys = set(LOCAL_VALIDATOR_MAP.keys())

    assert gen_keys == val_keys, (
        f"Несоответствие ключей в eq_geometry:\n"
        f"Только в генераторе: {gen_keys - val_keys}\n"
        f"Только в валидаторе: {val_keys - gen_keys}"
    )

def test_constants_usage_eq_geometry():
    """Проверяет использование констант в eq_geometry."""
    source = inspect.getsource(gen_module)
    tree = ast.parse(source)
    
    uses_math_pi = any(
        isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == 'math' and node.attr == "pi"
        for node in ast.walk(tree)
    )
    
    assert not uses_math_pi, f"Модуль {gen_module.__name__} использует math.pi вместо PI из common.py"

# --- 4. Удобный запуск для отладки ---
if __name__ == "__main__":
    pytest.main([__file__])
    print("✅ Все проверки для eq_geometry запущены.")