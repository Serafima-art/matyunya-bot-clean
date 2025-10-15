"""
Скрипт для проверки соответствия генератора и валидатора match_signs_k_b
Запуск: python test_match_signs_k_b.py
"""

import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь
# Из matunya_bot_final/tests/task_generators/task_11/ идём на 4 уровня вверх до matunya/
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from matunya_bot_final.task_generators.task_11.generators.match_signs_k_b_generator import generate_task_11_match_signs_k_b
from matunya_bot_final.task_generators.task_11.validators.match_signs_k_b_validator import validate_task_11_match_signs_k_b
import json


def test_generator_validator_compatibility():
    """Тест совместимости генератора и валидатора"""

    print("🧪 ТЕСТ СООТВЕТСТВИЯ ГЕНЕРАТОРА И ВАЛИДАТОРА\n")
    print("=" * 60)

    # Генерируем несколько задач для проверки
    num_tests = 10
    passed = 0
    failed = 0

    for i in range(1, num_tests + 1):
        print(f"\n📋 Тест #{i}")
        print("-" * 60)

        # Генерируем задачу
        task = generate_task_11_match_signs_k_b()

        # Выводим основную информацию
        print(f"ID: {task['id']}")
        print(f"Ответ: {task['answer']}")
        print(f"Варианты: {list(task['source_plot']['params']['options'].keys())}")

        # Выводим комбинации знаков
        print("\nКомбинации знаков:")
        for j, fd in enumerate(task['func_data']):
            k = fd['coeffs']['k']
            b = fd['coeffs']['b']
            label = task['source_plot']['params']['labels'][j]
            print(f"  {label}: k={k:+2d}, b={b:+2d}  →  {task['answer'][j]}) {task['source_plot']['params']['options'][task['answer'][j]]}")

        # Валидируем
        is_valid, errors = validate_task_11_match_signs_k_b(task)

        if is_valid:
            print("\n✅ Валидация пройдена")
            passed += 1
        else:
            print("\n❌ Валидация провалена:")
            for error in errors:
                print(f"   {error}")
            failed += 1

            # Выводим JSON для отладки
            print("\n📄 JSON задачи:")
            print(json.dumps(task, indent=2, ensure_ascii=False))

    # Итоговая статистика
    print("\n" + "=" * 60)
    print(f"\n📊 ИТОГО:")
    print(f"   ✅ Успешно: {passed}/{num_tests}")
    print(f"   ❌ Провалено: {failed}/{num_tests}")

    if failed == 0:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Генератор и валидатор совместимы.")
        return True
    else:
        print("\n⚠️  ЕСТЬ ПРОБЛЕМЫ! Требуется доработка.")
        return False


def test_edge_cases():
    """Тест граничных случаев"""

    print("\n\n🔬 ТЕСТ ГРАНИЧНЫХ СЛУЧАЕВ\n")
    print("=" * 60)

    # Генерируем 50 задач, чтобы поймать все комбинации
    all_combinations = set()

    for i in range(50):
        task = generate_task_11_match_signs_k_b()

        # Собираем комбинации знаков
        signs = []
        for fd in task['func_data']:
            k = fd['coeffs']['k']
            b = fd['coeffs']['b']
            signs.append((1 if k > 0 else -1, 1 if b > 0 else -1))

        all_combinations.add(tuple(sorted(signs)))

    print(f"Найдено уникальных комбинаций трёх графиков: {len(all_combinations)}")
    print("\nПримеры комбинаций:")
    for combo in list(all_combinations)[:5]:
        print(f"  {combo}")

    print("\n✅ Тест граничных случаев завершён")


if __name__ == "__main__":
    # Запускаем тесты
    success = test_generator_validator_compatibility()
    test_edge_cases()

    # Возвращаем код выхода
    sys.exit(0 if success else 1)
