✅ Единый solution_core (Задание 8, Паттерны 1.1 / 1.2 / 1.3)
solution_core = {
    "question_id": str,            # напр. "task8_1_1", "task8_1_2", "task8_1_3"
    "question_group": "task_8",
    "explanation_idea": str,       # 1–2 предложения «ключевой идеи» (как в методичке)

    "calculation_steps": [
        {
            "step_number": int,

            # Описание действия — ровно как в методичке ФИПИ
            "description": str,

            # Общая формула (если применяется свойство)
            "formula_general": Optional[str],

            # Формула с подставленными степенями
            "formula_calculation": Optional[str],

            # Чему равно выражение ПОСЛЕ этого шага
            "expression_after_step": str,

            # Если есть числовой результат в конце шага (например, подставили a=5)
            "calculation_result": Optional[str],
        }
    ],

    "final_answer": {
        "value_machine": Union[int, str],  # для валидации
        "value_display": str,              # как показываем ученику
        "unit": None
    },

    "hints": List[str],  # 3–6 образовательных подсказок
}
