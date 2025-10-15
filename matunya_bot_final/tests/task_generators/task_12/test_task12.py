import asyncio
import inspect
import ast
import pytest
import re
from matunya_bot_final.task_generators.task_12.task_12_generator import generate_task_12_by_subtype, GENERATOR_MAP
from matunya_bot_final.task_generators.task_12.task_12_validator import validator_map, validate_task

# ─────────────────────────────────────────────────────────────
# 1. Проверка совпадения результатов генератора и валидатора
# ─────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_generator_vs_validator():
    errors = []
    for subtype in GENERATOR_MAP.keys():
        for _ in range(5):  # 5 задач на подтип
            task = await generate_task_12_by_subtype(subtype)
            try:
                if not validate_task(task):
                    errors.append((subtype, task))
            except Exception as e:
                errors.append((subtype, f"Ошибка в валидаторе: {e}"))

    assert not errors, f"Ошибки валидации:\n{errors}"

# ─────────────────────────────────────────────────────────────
# 2. Проверка совпадения ключей генератора и валидатора
# ─────────────────────────────────────────────────────────────
def test_subtype_keys_match():
    gen_keys = set(GENERATOR_MAP.keys())
    val_keys = set(validator_map.keys())

    only_in_gen = gen_keys - val_keys
    only_in_val = val_keys - gen_keys

    assert not only_in_gen, f"Ключи есть в генераторе, но нет в валидаторе: {only_in_gen}"
    assert not only_in_val, f"Ключи есть в валидаторе, но нет в генераторе: {only_in_val}"

# ─────────────────────────────────────────────────────────────
# 3. Проверка использования школьных констант (PI, G и т. д.)
# ─────────────────────────────────────────────────────────────
def extract_constants_from_source(module):
    source = inspect.getsource(module)
    tree = ast.parse(source)

    used = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "pi":
            used.add("math.pi")
        if isinstance(node, ast.Name) and node.id in {"pi", "PI", "G", "R_UNIV", "G_CONST", "K_CONST"}:
            used.add(node.id)

    return used

def test_constants_usage():
    import matunya_bot_final.task_generators.task_12.task_12_generator as gen
    import matunya_bot_final.task_generators.task_12.task_12_validator as val

    gen_consts = extract_constants_from_source(gen)
    val_consts = extract_constants_from_source(val)

    # В генераторе и валидаторе не должно быть math.pi
    assert "math.pi" not in gen_consts, "Генератор использует math.pi вместо PI=3.14"
    assert "math.pi" not in val_consts, "Валидатор использует math.pi вместо PI=3.14"

    # Проверка, что хотя бы PI и G упомянуты
    assert "PI" in gen_consts or "PI" in val_consts, "Нет использования PI в коде"
    assert "G" in gen_consts or "G" in val_consts, "Нет использования G в коде"

# ─────────────────────────────────────────────────────────────
# 4. Удобный запуск для отладки
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    asyncio.run(test_generator_vs_validator())
    test_subtype_keys_match()
    test_constants_usage()
    print("✅ Все проверки пройдены успешно!")