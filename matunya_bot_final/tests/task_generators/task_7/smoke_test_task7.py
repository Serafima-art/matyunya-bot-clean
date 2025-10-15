import asyncio
from pathlib import Path
import sys

# 🔹 Добавляем корень проекта в sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from matunya_bot_final.gpt.task_templates.task_7 import list_task7_subtypes, build_task7_prompt, generate_task_7

async def main():
    print(f"Подтипов №7: {len(list_task7_subtypes())}")
    print("Первые 5:", list_task7_subtypes()[:5])

    # Берём случайный подтип
    prompt_text = build_task7_prompt()
    print("\nФрагмент промпта:\n")
    print(prompt_text[:400])  # первые 400 символов

    print("\nЗапускаю generate_task_7() ...\n")
    task_text = await generate_task_7()
    print(task_text)

if __name__ == "__main__":
    asyncio.run(main())