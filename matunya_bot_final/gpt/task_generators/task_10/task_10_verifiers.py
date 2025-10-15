# Это наш "Отдел контроля качества", основанный на твоих наработках.
from typing import Tuple, List, Any
import re

ANSWER_REGEX = re.compile(r"^0,\d{1,2}$")
REQUIRED_PHRASE = "В ответ запиши конечную десятичную дробь от 0 до 1."

def _normalize_spaces(s: str) -> str:
    """Сжимает пробелы, чтобы не зависеть от форматирования GPT."""
    return re.sub(r"\s+", " ", (s or "").strip())

def verify_gpt_response_format(obj: Any) -> Tuple[bool, List[str]]:
    """
    Проверяет JSON-ответ от GPT для Задания 10.
    Эта функция взята из твоего файла task_10_prompts.py.
    """
    errors: List[str] = []
    if not isinstance(obj, dict):
        return False, ["Ответ от GPT - это не JSON-объект."]

    # 1. Проверяем ключи
    allowed = {"text", "answer"}
    extra = set(obj.keys()) - allowed
    missing = allowed - set(obj.keys())
    if extra: errors.append(f"Лишние ключи: {', '.join(sorted(extra))}.")
    if missing: errors.append(f"Отсутствуют ключи: {', '.join(sorted(missing))}.")
    if missing or extra: return False, errors # Дальше нет смысла проверять

    # 2. Проверяем 'text'
    text = obj.get("text")
    if not isinstance(text, str) or len(text.strip()) < 20:
        errors.append("'text' должен быть непустой строкой.")
    else:
        norm_text = _normalize_spaces(text)
        norm_required = _normalize_spaces(REQUIRED_PHRASE)
        if norm_required not in norm_text:
            errors.append(f"В 'text' нет обязательной фразы: «{REQUIRED_PHRASE}»")

    # 3. Проверяем 'answer'
    answer = obj.get("answer")
    if not isinstance(answer, str):
        errors.append("'answer' должен быть строкой '0,dd'.")
    else:
        if "." in answer: errors.append("В 'answer' используется точка. Нужна запятая.")
        if not ANSWER_REGEX.fullmatch(answer): errors.append("Неверный формат 'answer'. Требуется '0,d' или '0,dd'.")
        try:
            val = float(answer.replace(",", "."))
            if not (0.0 < val < 1.0):
                errors.append("Вероятность в 'answer' должна быть строго между 0 и 1.")
        except (ValueError, TypeError):
            errors.append("Не удалось преобразовать 'answer' в число.")
            
    return len(errors) == 0, errors

# "Карта верификаторов". Теперь у нас один верификатор на все подтипы,
# потому что формат JSON у них одинаковый. Но для гибкости сохраним карту.
VERIFIER_MAP = {
    # Поставим заглушки для всех 14 подтипов, чтобы не было ошибок
    "exam_tickets": verify_gpt_response_format,
    "participant_order_group": verify_gpt_response_format,
    "items_colors_selection": verify_gpt_response_format,
    "conference_days_assignment": verify_gpt_response_format,
    "time_interval_probability": verify_gpt_response_format,
    "item_defect_probability": verify_gpt_response_format,
    "group_transport_batches": verify_gpt_response_format,
    "gifts_distribution_child": verify_gpt_response_format,
    "promotions_prize_in_pack": verify_gpt_response_format,
    "range_number_property": verify_gpt_response_format,
    "bernoulli_trials_patterns": verify_gpt_response_format,
    "dice_outcomes": verify_gpt_response_format,
    "union_of_topics": verify_gpt_response_format,
    "relative_frequency_tasks": verify_gpt_response_format,
}