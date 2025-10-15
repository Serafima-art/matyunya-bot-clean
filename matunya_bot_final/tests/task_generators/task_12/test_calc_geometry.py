import asyncio
import inspect
import ast
import pytest
from typing import Dict, Callable, Tuple

# --- 1. Адаптированный импорт под новую архитектуру ---
# Импортируем нужные модули, а не глобальные MAP'ы
from matunya_bot_final.task_generators.task_12.generators import calc_geometry as gen_module
from matunya_bot_final.task_generators.task_12.validators import calc_geometry as val_module


# --- 2. Создаем локальные MAP'ы для конкретного модуля ---
def _create_local_maps() -> Tuple[Dict[str, Callable], Dict[str, Callable]]:
    """
    Создает словари генераторов и валидаторов только для модуля calc_geometry.
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


# --- 3. Адаптированные тесты ---

@pytest.mark.asyncio
async def test_generator_vs_validator_calc_geometry():
    """Проверяет совместимость генераторов и валидаторов из calc_geometry."""
    errors = []
    if not LOCAL_GENERATOR_MAP:
        pytest.skip("В модуле calc_geometry нет генераторов для теста.")

    for subtype, generator_func in LOCAL_GENERATOR_MAP.items():
        validator_func = LOCAL_VALIDATOR_MAP.get(subtype)
        if not validator_func:
            continue # Ошибка отсутствия валидатора поймается в следующем тесте

        for _ in range(5):  # 5 задач на подтип
            # Генератор теперь не асинхронный, вызываем его напрямую
            task = generator_func()
            try:
                # Валидатор тоже не асинхронный
                if not validator_func(task):
                    errors.append((subtype, task))
            except Exception as e:
                errors.append((subtype, f"Ошибка в валидаторе '{subtype}': {e}"))

    assert not errors, f"Ошибки валидации для calc_geometry:\n{errors}"

def test_subtype_keys_match_calc_geometry():
    """Проверяет, что у каждого генератора в calc_geometry есть свой валидатор."""
    gen_keys = set(LOCAL_GENERATOR_MAP.keys())
    val_keys = set(LOCAL_VALIDATOR_MAP.keys())

    assert gen_keys == val_keys, (
        f"Несоответствие ключей в calc_geometry:\n"
        f"Только в генераторе: {gen_keys - val_keys}\n"
        f"Только в валидаторе: {val_keys - val_keys}"
    )

def test_constants_usage_calc_geometry():
    """Проверяет использование PI в calc_geometry и запрет на math.pi."""
    source = inspect.getsource(gen_module)
    tree = ast.parse(source)
    
    uses_math_pi = any(
        isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == 'math' and node.attr == "pi"
        for node in ast.walk(tree)
    )
    
    assert not uses_math_pi, f"Модуль {gen_module.__name__} использует math.pi вместо PI из common.py"


# --- 4. Удобный запуск для отладки (опционально) ---
if __name__ == "__main__":
    # Поскольку тесты больше не асинхронные, убираем asyncio.run
    pytest.main([__file__])
    print("✅ Все проверки для calc_geometry запущены.")