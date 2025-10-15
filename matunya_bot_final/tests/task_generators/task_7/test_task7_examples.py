# tests/test_task7_examples.py (ГИБРИДНАЯ ВЕРСИЯ)

import asyncio
import re
import json
from typing import Dict, Any, Optional, List

# --- Абсолютные импорты ---
from matunya_bot_final.gpt.task_templates.task_7.task_7_prompts import SUBTYPES
from matunya_bot_final.gpt.task_templates.task_7.task_7_processor import process_generated_task

# Просто перечисляем подтипы, которым нужна картинка.
REQUIRES_IMAGE = {
    "point_to_root", "point_to_fraction", "point_to_fraction_decimal",
    "root_to_point", "decimal_to_point", "variable_on_line",
    "difference_analysis_on_line", "expression_analysis_on_line",
}

def lint_rules(subtype: str, payload: Dict[str, Any]) -> List[str]:
    """ТВОЙ ЛИНТЕР, адаптированный для работы с JSON-payload."""
    errs = []
    text = payload.get("text", "")
    opts = payload.get("options", [])
    
    # Твои проверки стиля (я их сохранил!)
    if re.search(r"\d+\.\d+", text):
        errs.append("десятичные в тексте с точкой, должно быть с запятой")
    if len(opts) != 4:
        errs.append("в options должно быть ровно 4 варианта")
        
    # Твои спец-проверки по подтипам
    if subtype == "point_to_fraction":
        if not re.search(r"\bчисло\s+-?\d+\s*/\s*\d+\b", text):
            errs.append("нет единственной дроби p/q в тексте")
    if subtype == "variable_on_line":
        if not re.search(r"\bчисло\s+[a-z]\b", text):
            errs.append("в тексте должна быть формулировка про число [a-z]")
    # ... сюда можно добавить остальные твои линтеры ...
    
    return errs

async def verify_example(subtype: str, example_json_str: str) -> bool:
    """Проводит ПОЛНУЮ проверку примера из JSON-строки."""
    try:
        # 1. Парсим JSON из примера
        payload = json.loads(example_json_str)
    except json.JSONDecodeError:
        print(f"   ❌ FAIL {subtype}: не удалось прочитать JSON из примера.")
        return False

    # 2. Проверяем стилистику текста (ЛИНТУЕМ)
    lint_errs = lint_rules(subtype, payload)
    if lint_errs:
        print(f"   ⚠ LINT {subtype}: " + "; ".join(lint_errs))
        # Можно сделать return False, если линтер должен быть строгим
        
    # 3. Запускаем наш процессор на данных из примера
    res = await process_generated_task(payload, subtype)
    
    # 4. Проверяем результат работы процессора
    if res is None:
        print(f"   ❌ FAIL {subtype}: процессор забраковал пример.")
        return False
    if subtype in REQUIRES_IMAGE and "image_params" not in res:
        print(f"   ❌ FAIL {subtype}: процессор не сгенерировал обязательные image_params.")
        return False
    if res.get("answer") != payload.get("correct_answer_value"):
        print(f"   ❌ FAIL {subtype}: ответ процессора ({res.get('answer')}) не совпал с эталоном ({payload.get('correct_answer_value')}).")
        return False

    print(f"   ✅ OK {subtype}: пример полностью прошел проверку.")
    return True

async def main():
    # ... (эта функция остается без изменений) ...
    total, ok = 0, 0
    for subtype, info in SUBTYPES.items():
        print(f"\n▶️  Проверка примеров подтипа: {subtype}")
        examples = info.get("examples", [])
        if not examples: continue
        for i, ex in enumerate(examples, 1):
            total += 1
            print(f" — пример #{i}")
            ok += int(await verify_example(subtype, ex))
    print("\n----------------------------------------")
    print(f"📊 ИТОГ: {ok}/{total} примеров прошли проверку")

if __name__ == "__main__":
    asyncio.run(main())