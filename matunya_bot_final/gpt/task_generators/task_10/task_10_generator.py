import json
from typing import Dict, Any
import aiofiles
import datetime

from matunya_bot_final.gpt.gpt_utils import ask_gpt_with_history
from matunya_bot_final.config import TASK_GENERATION_MODEL

from matunya_bot_final.gpt.task_generators.task_10.task_10_verifiers import VERIFIER_MAP
from matunya_bot_final.gpt.task_generators.task_10.task_10_processors import PROCESSOR_MAP, _my_float_to_text # Импортируем наш форматер

from matunya_bot_final.gpt.task_templates.task_10.task_10_prompts import build_prompt_with_example

LOG_FILE_PATH = "data/tasks_10.json"

class TaskGenerationError(Exception):
    pass

async def _log_successful_task(task_data: dict, subtype_id: str):
    """Асинхронно записывает успешно сгенерированную задачу в файл."""
    # Преобразуем численный ответ обратно в строку для лога
    task_data_for_log = task_data.copy()
    task_data_for_log['answer'] = _my_float_to_text(task_data['answer'])

    log_entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "subtype_id": subtype_id,
        "task": task_data_for_log
    }
    try:
        async with aiofiles.open(LOG_FILE_PATH, mode='a', encoding='utf-8') as f:
            await f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        print(f"--- УСПЕХ! Задача сгенерирована и ЗАЛОГИРОВАНА в {LOG_FILE_PATH}. ---")
    except Exception as e:
        print(f"!!! ОШИБКА ЛОГИРОВАНИЯ: {e} !!!")

async def _call_gpt_api_and_parse(prompt: str) -> Dict[str, Any]:
    """Отправляет реальный запрос к GPT и извлекает JSON."""
    print("--- Отправляю реальный запрос к GPT... ---")
    raw_response = await ask_gpt_with_history(
        system_prompt="", user_prompt=prompt, model=TASK_GENERATION_MODEL
    )
    try:
        start, end = raw_response.find("{"), raw_response.rfind("}")
        if start == -1 or end == -1: raise ValueError("В ответе GPT нет JSON-объекта.")
        json_str = raw_response[start:end+1]
        return json.loads(json_str)
    except Exception as e:
        raise ValueError(f"GPT вернул невалидный JSON. Ошибка: {e}")

async def generate_task_10(subtype_id: str, max_attempts: int = 5) -> Dict[str, Any]:
    """
    Главная функция-оркестратор.
    Принцип: "GPT предлагает, Python решает и утверждает".
    """
    print(f"\n--- ЗАПУСК ГЕНЕРАЦИИ ДЛЯ ПОДТИПА: {subtype_id} ---")

    if subtype_id not in VERIFIER_MAP or subtype_id not in PROCESSOR_MAP:
        raise TaskGenerationError(f"Для подтипа '{subtype_id}' не реализован верификатор или процессор.")

    prompt = build_prompt_with_example(subtype_id)

    for attempt in range(1, max_attempts + 1):
        print(f"\n[Попытка {attempt}/{max_attempts}]")
        try:
            gpt_response_json = await _call_gpt_api_and_parse(prompt)
            
            verifier = VERIFIER_MAP[subtype_id]
            is_valid_format, format_errors = verifier(gpt_response_json)
            if not is_valid_format:
                print(f"ОШИБКА ФОРМАТА: {format_errors} -> Повторная генерация")
                continue

            processor = PROCESSOR_MAP[subtype_id]
            # --- ГЛАВНОЕ ИЗМЕНЕНИЕ ---
            # Процессор теперь не проверяет, а сам вычисляет финальный ответ
            final_task = processor(gpt_response_json)
            
            # Логируем задачу с 100% правильным ответом
            await _log_successful_task(final_task, subtype_id)
            
            return final_task

        except (ValueError, Exception) as e:
            print(f"ОШИБКА ВАЛИДАЦИИ ИЛИ РАСЧЕТА: {e} -> Повторная генерация")
            continue
    
    raise TaskGenerationError(f"Не удалось сгенерировать корректную задачу для '{subtype_id}' за {max_attempts} попыток.")