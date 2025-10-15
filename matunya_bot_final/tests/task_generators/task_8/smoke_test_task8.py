import asyncio
from pathlib import Path
import sys

# Добавляем корень проекта в sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from matunya_bot_final.gpt.task_templates.task_8 import (
    list_task8_subtypes,
    build_task8_prompt,
    generate_task_8,
)

async def main():
    subs = list_task8_subtypes()
    print("Подтипов №8:", len(subs))
    print("Первые 5:", subs[:5])

    prompt_text, used = build_task8_prompt()  # случайный подтип
    print("\nСлучайный подтип:", used)
    print("Фрагмент промпта:\n", prompt_text[:400], "...\n")

    print("Запускаю generate_task_8() ...")
    text, used2 = await generate_task_8()
    print("\nИспользованный подтип:", used2)
    print("Сгенерированный текст:\n", text)

if __name__ == "__main__":
    asyncio.run(main())