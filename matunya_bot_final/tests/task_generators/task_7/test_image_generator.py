import asyncio
import sys
import os
import json

# --- Настройка путей ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Импорт ---
from matunya_bot_final.gpt.task_templates.task_7.task_7_generator import generate_task_7

async def run_generation_test():
    """Запускает полную цепочку генерации Задания 7 и печатает результат."""
    print("▶️  Начинаю тест полной генерации Задания 7...")
    generated_task = await generate_task_7()
    
    print("-" * 40)
    if generated_task:
        print("✅ Успешно сгенерировано и обработано финальное задание:")
        print(json.dumps(generated_task, ensure_ascii=False, indent=2))
    else:
        print("❌ Ошибка: не удалось сгенерировать задание.")
    print("-" * 40)
    print("📊 Тест завершен.")

if __name__ == "__main__":
    asyncio.run(run_generation_test())