import asyncio
import json
from pathlib import Path
from colorama import init, Fore, Style

from matunya_bot_final.gpt.task_templates.task_7.task_7_prompts import SUBTYPES
from matunya_bot_final.gpt.task_templates.task_7.task_7_processor import process_generated_task

init(autoreset=True)  # для цветного вывода

def extract_key(raw_key: str) -> str:
    """Преобразует '01 point_to_root' → 'point_to_root'."""
    return raw_key.split(" ", 1)[1].strip() if " " in raw_key else raw_key

async def validate_examples():
    total = 0
    passed = 0
    failed_examples = []

    for raw_key, subtype_data in SUBTYPES.items():
        subtype_key = extract_key(raw_key)
        print(f"\n🔍 Подтип: {raw_key} — {subtype_data['description']}")

        for example in subtype_data.get("examples", []):
            total += 1
            ex_id = example.get("id", "???")

            try:
                result = await process_generated_task(example, subtype=subtype_key)
                if result:
                    print(f"{Fore.GREEN}✅ OK{Style.RESET_ALL}: id={ex_id}")
                    passed += 1
                else:
                    print(f"{Fore.RED}❌ FAIL{Style.RESET_ALL}: id={ex_id}")
                    failed_examples.append({"id": ex_id, "subtype": subtype_key})
            except Exception as e:
                print(f"{Fore.MAGENTA}❌ EXCEPTION{Style.RESET_ALL}: id={ex_id} — {e}")
                failed_examples.append({"id": ex_id, "subtype": subtype_key, "error": str(e)})

    # 📁 Сохраняем невалидные примеры (если есть)
    if failed_examples:
        save_path = Path(__file__).parent / "failed_ids.json"
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(failed_examples, f, indent=2, ensure_ascii=False)
        print(f"\n{Fore.YELLOW}⚠️ Сохранены невалидные примеры в: {save_path}{Style.RESET_ALL}")

    # 📊 Статистика
    print("\n📊 РЕЗУЛЬТАТ:")
    print(f"   Прошли:     {Fore.GREEN}{passed}{Style.RESET_ALL}")
    print(f"   Провалены:  {Fore.RED}{len(failed_examples)}{Style.RESET_ALL}")
    print(f"   Всего:      {total}")

def run_validation():
    asyncio.run(validate_examples())

if __name__ == "__main__":
    run_validation()