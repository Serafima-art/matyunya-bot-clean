import json
import random
from typing import Dict, Any, Optional
import re, math

from matunya_bot_final.config import TASK_GENERATION_MODEL
from matunya_bot_final.gpt.gpt_utils import ask_gpt_with_history
from matunya_bot_final.gpt.task_templates.task_7.task_7_prompts import MAIN_PROMPT, SUBTYPES
from matunya_bot_final.gpt.task_templates.task_7.task_7_processor import process_generated_task

def _sqrt_floors_unique(options) -> bool:
    """True, если у четырёх вариантов √n попарно разные floor(√n). Допускаем формат '1) √(17) ' и пробелы."""
    if not isinstance(options, list) or len(options) != 4:
        return False
    floors = []
    for opt in options:
        s = str(opt).strip()
        s = re.sub(r'^\s*\d+[\)\.\:]\s*', '', s)   # срезаем нумерацию: '1) ', '2. ', '3: '
        s = s.replace(' ', '')
        s = re.sub(r'^√\((\d+)\)$', r'√\1', s)     # √(17) → √17
        m = re.match(r'^√(\d+)$', s)
        if not m:
            return False
        n = int(m.group(1))
        if n <= 1 or int(math.isqrt(n))**2 == n:   # запрещаем идеальные квадраты
            return False
        floors.append(int(math.floor(math.sqrt(n))))
    return len(set(floors)) == 4

def _build_user_prompt(subtype_key: str, examples: list) -> str:
    """Собирает финальный промпт для GPT: каркас + примеры + инварианты подтипа + строгая схема JSON."""
    info = SUBTYPES[subtype_key]
    examples_block = "\n\n".join(json.dumps(ex, ensure_ascii=False, indent=2) for ex in examples)
    rules_block = info.get("rules", "").strip()

    # какие подтипы требуют рисунок (image_params)
    REQUIRES_IMAGE = {
        "point_to_root",
        "root_to_point",
        "point_to_fraction",
        "point_to_fraction_decimal",
        "variable_on_line",
        "decimal_to_point",
        "difference_analysis_on_line",
        "expression_analysis_on_line",
        "compare_fractions_on_line",
        "true_statement_about_line",
    }
    requires_image = subtype_key in REQUIRES_IMAGE

    schema_with_image = """
ТЫ ОБЯЗАН вернуть ТОЛЬКО один объект JSON без пояснений, РОВНО по схеме:
{
  "text": string,                                  // весь текст условия; десятичные дроби с ЗАПЯТОЙ (напр., 0,25)
  "options": [string, string, string, string],     // ровно 4 разных варианта
  "correct_answer_index": 0|1|2|3,
  "correct_answer_value": string,                  // БУКВАЛЬНО options[correct_answer_index]
  "image_params": {
    "min_val": integer,                            // целые; min_val < max_val
    "max_val": integer,
    "points": [                                    // метки только латиницей A,B,C,D,...
      {"label": string, "pos": number},            // pos — число (тип number), не строка
      {"label": string, "pos": number},
      {"label": string, "pos": number},
      {"label": string, "pos": number}
    ]
  }
}
"""

    schema_without_image = """
ТЫ ОБЯЗАН вернуть ТОЛЬКО один объект JSON без пояснений, РОВНО по схеме:
{
  "text": string,                                  // весь текст условия; десятичные дроби с ЗАПЯТОЙ (напр., 0,25)
  "options": [string, string, string, string],     // ровно 4 разных варианта
  "correct_answer_index": 0|1|2|3,
  "correct_answer_value": string                   // БУКВАЛЬНО options[correct_answer_index]
}
"""

    consistency_rules = f"""
# Единые правила согласованности для всех подтипов
• Лейблы точек — только латиницей (A, B, C, D); кириллицу не использовать.
• "correct_answer_value" обязан совпадать БУКВАЛЬНО с options[correct_answer_index].
• Вне JSON — ничего.
• Если подтип требует рисунок: укажи "image_params"; все points строго внутри (min_val; max_val); label уникальны.
• Соблюдай Блок 6 оформления записи: десятичные дроби в ТЕКСТЕ — с запятой (0,25); корни через символ √; дроби a/b; знаки и скобки как в правилах.
"""

    prompt = (
        f"{MAIN_PROMPT}\n"
        f"\nПодтип: {subtype_key}\n"
        f"Описание подтипа: {info.get('description','')}\n"
        f"\nПримеры по этому подтипу (не копируй числа, это только стиль):\n{examples_block}\n"
        f"\nИнварианты выбранного подтипа (обязательно соблюдай):\n{rules_block if rules_block else '—'}\n"
        f"\nСтрогая схема ответа:\n{schema_with_image if requires_image else schema_without_image}\n"
        f"{consistency_rules}\n"
        f"\nСгенерируй СТРОГО ОДНО новое задание №7 по подтипу «{subtype_key}». "
        f"Верни только JSON по схеме выше."
    )
    return prompt

async def _generate_task_7_ideas(user_prompt: str) -> Optional[Dict[str, Any]]:
    """Запрашивает 'идеи' у GPT и надёжно вытаскивает верхний JSON."""
    def _extract_json_block(s: str) -> Dict[str, Any]:
        import json
        start, end = s.find("{"), s.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("В ответе нет JSON-блока.")
        return json.loads(s[start:end+1])

    for attempt in range(1, 4):  # до 3 попыток получить валидный JSON от модели
        try:
            raw_response = await ask_gpt_with_history(
                system_prompt="",  # системный уже в MAIN_PROMPT
                user_prompt=user_prompt,
                model=TASK_GENERATION_MODEL
            )
            ideas = _extract_json_block(raw_response)
            if all(k in ideas for k in ("text", "options", "correct_answer_index", "correct_answer_value")):
                return ideas
            print(f"[DEBUG][ideas] попытка {attempt}: не хватает ключей в JSON")
        except Exception as e:
            print(f"[DEBUG][ideas] попытка {attempt}: ошибка парсинга JSON: {e}")
    return None

async def generate_task_7(subtype_key: Optional[str] = None, max_attempts: int = 5) -> Optional[Dict[str, Any]]:
    """Полный цикл генерации Задания 7 с автопроверкой и перегенерацией."""
    if subtype_key is None:
        subtype_key = "variable_on_line"
    if subtype_key not in SUBTYPES:
        return None

    examples = SUBTYPES[subtype_key].get("examples", [])
    # берём до 2 примеров для стиля
    user_prompt = _build_user_prompt(subtype_key, random.sample(examples, min(len(examples), 2)))

    for attempt in range(1, max_attempts + 1):
        gpt_response = await _generate_task_7_ideas(user_prompt)
        if not gpt_response:
            print(f"[DEBUG][{subtype_key}] попытка {attempt}: GPT вернул невалидные идеи → ретрай")
            continue

        # 🔒 Предфильтр только для point_to_root: требуем уникальные floor(√n)
        if subtype_key == "point_to_root" and not _sqrt_floors_unique(gpt_response.get("options", [])):
            print(f"[DEBUG][{subtype_key}] попытка {attempt}: floors(√n) не уникальны → ретрай")
            continue

        final_task = await process_generated_task(gpt_response, subtype_key)
        if final_task is not None:
            print(f"[OK][{subtype_key}] с {attempt}-й попытки сгенерировано корректное задание")
            return final_task

        print(f"[DEBUG][{subtype_key}] попытка {attempt}: процессор забраковал задание → ретрай")

    print(f"[FAIL][{subtype_key}] после {max_attempts} попыток корректное задание не получено")
    return None