import random

# Импортируем "память" с промптами
from matunya_bot_final.gpt.task_templates.task_10.task_10_prompts import TASK_10_PROMPTS


class TaskGenerationError(Exception):
    """Кастомное исключение для ошибок генерации задач."""
    pass


async def generate_task_10(subtype_id: str) -> dict:
    """
    Главная функция-"Фабрика" для генерации Задания 10.
    """
    print(f"Запущен генератор для подтипа: {subtype_id}")

    # ЭТАП 1: Подготовка промпта
    prompt_template = TASK_10_PROMPTS.get(subtype_id)
    if not prompt_template:
        raise TaskGenerationError(f"Не найден промпт для подтипа {subtype_id}")

    # ЭТАП 2: Обращение к GPT (пока имитация)
    print("Имитируем ответ от GPT...")
    scenario_data = {
        "text": f"Это временный текст задачи для подтипа '{subtype_id}'.",
        "answer_raw": 0.25
    }

    # ЭТАП 3: Валидация и расчеты (пока имитация)
    # Здесь в будущем будет наша математика
    correct_answer = scenario_data["answer_raw"]

    # ЭТАП 4: Сборка финального продукта
    final_task = {
        "text": scenario_data["text"],
        "answer": correct_answer
    }
    
    print(f"Задача успешно сгенерирована: {final_task}")
    return final_task