# matunya_bot_final/non_generators/task_6/validators/test_mixed_fractions_validator.py
"""
Мини-тест для проверки валидатора mixed_fractions.
Запуск:
    python -m matunya_bot_final.non_generators.task_6.validators.test_mixed_fractions_validator
"""

from pprint import pprint
from matunya_bot_final.non_generators.task_6.validators.mixed_fractions_validator import validate_mixed_fraction

def run_test():
    print("\n[TEST] Проверяем mixed_fractions_validator\n")
    line = "mixed_types_operations | 8.4 : (1 1/5 + 0.2)"
    result = validate_mixed_fraction(line)

    if not result:
        print("❌ Валидатор вернул None — ошибка при обработке строки.")
        return

    print("✅ Валидатор успешно отработал.")
    print("\n[Вопрос]:")
    print(result["question_text"])
    print("\n[Ответ]:", result["answer"], "(тип:", result["answer_type"], ")")

    print("\n[Дерево выражения]:")
    pprint(result["expression_tree"], width=100, sort_dicts=False)

    # Контрольное условие — mixed должен присутствовать
    def contains_mixed(node):
        if isinstance(node, dict):
            if node.get("type") == "mixed":
                return True
            return any(contains_mixed(v) for v in node.values())
        elif isinstance(node, list):
            return any(contains_mixed(v) for v in node)
        return False

    if contains_mixed(result["expression_tree"]):
        print("\n✅ Найден type: 'mixed' — дерево корректно сохраняет смешанные дроби.")
    else:
        print("\n⚠️ В дереве нет узлов type:'mixed' — проверь _sympy_to_json_tree().")


if __name__ == "__main__":
    run_test()
