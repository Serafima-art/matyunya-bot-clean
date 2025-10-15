import asyncio
from pathlib import Path
import sys
import time
import json
from typing import Dict, Any
from colorama import init, Fore, Style

# 🔹 Добавляем корень проекта в sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from matunya_bot_final.gpt.task_templates.task_7 import list_task7_subtypes, generate_task_7

# === НАСТРОЙКИ ===
SAVE = True  # ← включи или выключи сохранение

# === ИНИЦИАЛИЗАЦИЯ ===
init(autoreset=True)
OUTPUT_DIR = Path(__file__).parent / "valid_tasks"

def save_task(subtype: str, task_data: Dict[str, Any], index: int):
    """Сохраняет задание в JSON-файл."""
    dir_path = OUTPUT_DIR / subtype
    dir_path.mkdir(parents=True, exist_ok=True)
    file_path = dir_path / f"{subtype}_{index}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(task_data, f, ensure_ascii=False, indent=2)
    print(f"{Fore.BLUE}[💾 Сохранено в: {file_path}]{Style.RESET_ALL}")

async def main():
    subtypes = ["point_to_root", "point_to_fraction_decimal", "root_to_point", "point_to_fraction", "decimal_to_point", "variable_on_line", "root_in_integer_interval", "fraction_in_decimal_interval", "decimal_between_fractions", "integer_between_roots", "expression_analysis_on_line", "number_in_set", "difference_analysis_on_line"]
    success = []
    failed = []
    counters = {s: 0 for s in subtypes}  # для нумерации файлов

    print(f"\n🔍 Всего подтипов: {len(subtypes)}\n")

    for subtype in subtypes:
        print(f"⏳ Тест подтипа: {subtype} ... ", end="", flush=True)
        start_time = time.time()

        task = await generate_task_7(subtype_key=subtype, max_attempts=5)

        if task:
            elapsed = round(time.time() - start_time, 2)
            print(f"{Fore.GREEN}[✅ OK]{Style.RESET_ALL} за {elapsed} сек")

            success.append(subtype)
            counters[subtype] += 1

            if SAVE:
                save_task(subtype, task, counters[subtype])
        else:
            print(f"{Fore.RED}[❌ FAIL]{Style.RESET_ALL}")
            failed.append(subtype)

    # 📊 Результаты
    print("\n📊 РЕЗУЛЬТАТЫ\n" + "-"*30)
    print(f"{Fore.GREEN}✅ Успешно: {len(success)}{Style.RESET_ALL}")
    for s in success:
        print(f"   ✔ {s}")
    print(f"{Fore.RED}❌ Не удалось: {len(failed)}{Style.RESET_ALL}")
    for s in failed:
        print(f"   ✖ {s}")

if __name__ == "__main__":
    asyncio.run(main())