# scripts/smoke_test_task6.py
import asyncio

async def main():
    # 1) Импорт: падает ли?
    from matunya_bot_final.gpt.task_templates.task_6 import list_task6_subtypes, build_task6_prompt, generate_task_6

    # 2) Есть ли подтипы?
    subtypes = list_task6_subtypes()
    print("Подтипов №6:", len(subtypes))
    print("Первые 5:", subtypes[:5])

    # 3) Сборка промпта (без GPT-запроса)
    prompt, used = build_task6_prompt(subtype_key=None)  # случайный
    print("\nСлучайный подтип:", used)
    print("Фрагмент промпта:\n", prompt[:400], "...\n")

    # 4) Полная генерация (c GPT)
    print("Запускаю generate_task_6() ...")
    text, used2 = await generate_task_6()
    print("\nИспользованный подтип:", used2)
    print("Сгенерированный текст:\n", text)

if __name__ == "__main__":
    asyncio.run(main())