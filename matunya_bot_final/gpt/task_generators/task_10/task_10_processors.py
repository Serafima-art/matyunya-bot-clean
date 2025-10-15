import re
import math

# =================================================================
# Вспомогательные функции
# =================================================================
def _normalize_text_for_numbers(text: str) -> str:
    """Преобразует числа, написанные словами, в цифры."""
    replacements = {"один": "1", "два": "2", "три": "3", "четыре": "4", "пять": "5", "шесть": "6", "дважды": "2 раза", "трижды": "3 раза"}
    for word, digit in replacements.items():
        text = re.sub(r'\b' + word + r'\b', digit, text, flags=re.IGNORECASE)
    return text

def _text_to_float(text_answer: str) -> float:
    """Преобразует текстовый ответ "0,25" в число 0.25"""
    return float(text_answer.replace(",", "."))

def _my_float_to_text(num: float) -> str:
    """Преобразует число 0.25 в "0,25", а 0.5 - в "0,5"."""
    return str(num).replace(".", ",")

# =================================================================
# Калькуляторы для подтипов
# =================================================================

def process_bernoulli_task(data: dict) -> dict:
    text = data["text"]
    normalized_text = _normalize_text_for_numbers(text)
    numbers = [int(n) for n in re.findall(r'\d+', normalized_text)]
    if len(numbers) < 2:
        if "ни разу" in normalized_text and len(numbers) == 1: numbers.append(0)
        else: raise ValueError(f"В тексте задачи найдено мало чисел: {numbers}")
    n = max(numbers)
    k = min(numbers)
    if k > n: raise ValueError(f"Число успехов ({k}) не может быть больше числа бросков ({n}).")
    p = 0.5
    combinations = math.factorial(n) // (math.factorial(k) * math.factorial(n - k))
    my_answer_float = combinations * (p ** k) * ((1 - p) ** (n - k))
    return {"text": text, "answer": my_answer_float}

def process_items_colors_task(data: dict) -> dict:
    text = data["text"]
    numbers = [int(n) for n in re.findall(r'\d+', text)]
    if len(numbers) < 2: raise ValueError("В тексте должно быть как минимум два числа (общее и часть).")
    total_items = max(numbers)
    parts = sorted([n for n in numbers if n != total_items])
    favorable_items = 0
    if "остальные" in text or "остальных" in text:
        favorable_items = total_items - sum(parts)
    else:
        if len(parts) == 1: favorable_items = parts[0]
        else: raise ValueError("Калькулятор пока не умеет решать задачи с 3+ компонентами без слова 'остальные'.")
    if total_items == 0: raise ValueError("Общее количество предметов не может быть равно нулю.")
    my_answer_float = favorable_items / total_items
    return {"text": text, "answer": my_answer_float}

def process_dice_task(data: dict) -> dict:
    text = data["text"]
    if "дважды" in text or "две кости" in text or "два кубика" in text:
        total_outcomes = 36
        main_text_part = text.split("В ответ запиши")[0]
        target_sums = [int(n) for n in re.findall(r'\d+', main_text_part)]
        if not target_sums: raise ValueError("Калькулятор 'Кубики' не нашел целевую сумму в тексте.")
        favorable_outcomes = sum(1 for i in range(1, 7) for j in range(1, 7) if (i + j) in target_sums)
        if favorable_outcomes == 0: raise ValueError(f"Суммы {target_sums} невозможны при двух бросках кубика.")
        my_answer_float = favorable_outcomes / total_outcomes
        return {"text": text, "answer": my_answer_float}
    else:
        raise ValueError("Калькулятор 'Кубики' пока умеет работать только с двумя бросками.")

def process_participant_order_task(data: dict) -> dict:
    text = data["text"]
    main_text_part = text.split("Найдите вероятность")[0]
    numbers = [int(n) for n in re.findall(r'\d+', main_text_part)]
    if not numbers: raise ValueError("В задаче про жребий не найдены числа.")
    total_participants = max(numbers)
    parts = sorted([n for n in numbers if n != total_participants])
    favorable_outcomes = 0
    if "остальные" in text or "остальных" in text:
        favorable_outcomes = total_participants - sum(parts)
    else:
        if len(parts) >= 1: favorable_outcomes = parts[0]
        else: raise ValueError("Не удалось определить группу для расчета вероятности.")
    if total_participants == 0: raise ValueError("Общее количество участников не может быть равно нулю.")
    my_answer_float = favorable_outcomes / total_participants
    return {"text": text, "answer": my_answer_float}

def process_exam_tickets_task(data: dict) -> dict:
    text = data["text"]
    numbers = [int(n) for n in re.findall(r'\d+', text.split("Найдите вероятность")[0])]
    if len(numbers) < 2: raise ValueError("В задаче про билеты должно быть 2 числа (всего и часть).")
    total_tickets = max(numbers)
    part = min(numbers)
    favorable_outcomes = 0
    if "не выучил" in text or "невыучен" in text:
        if "выученный" in text: favorable_outcomes = total_tickets - part
        else: favorable_outcomes = part
    else:
        favorable_outcomes = part
    if total_tickets == 0: raise ValueError("Общее количество билетов не может быть равно нулю.")
    my_answer_float = favorable_outcomes / total_tickets
    return {"text": text, "answer": my_answer_float}

def process_item_defect_task(data: dict) -> dict:
    text = data["text"]
    main_text_part = text.split("Найдите вероятность")[0]
    numbers = [int(n) for n in re.findall(r'\d+', main_text_part)]
    if len(numbers) < 2: raise ValueError("В задаче про дефекты/мишени должно быть 2 числа (всего и часть).")
    total_items = max(numbers)
    part = min(numbers)
    favorable_outcomes = 0
    if "исправен" in text or "попадет" in text or "пригодн" in text:
        favorable_outcomes = total_items - part
    else:
        favorable_outcomes = part
    if total_items == 0: raise ValueError("Общее количество предметов не может быть равно нулю.")
    my_answer_float = favorable_outcomes / total_items
    return {"text": text, "answer": my_answer_float}

def process_range_number_task(data: dict) -> dict:
    text = data["text"]
    main_text_part = text.split("Найдите вероятность")[0]
    total_count = 0
    if "двузначное число" in main_text_part: total_count = 90
    elif "трёхзначное число" in main_text_part: total_count = 900
    else:
        match = re.search(r'от\s+(\d+)\s+до\s+(\d+)', main_text_part)
        if match:
            start, end = int(match.group(1)), int(match.group(2))
            total_count = end - start + 1
        else: raise ValueError("Не удалось определить диапазон чисел в задаче.")
    favorable_outcomes = 0
    match_ends = re.search(r'оканчивается\s+на\s+(\d+)', main_text_part)
    if match_ends:
        if total_count == 90: favorable_outcomes = 9
    else:
        match_div = re.search(r'делится\s+на\s+(\d+)', main_text_part)
        if match_div:
            divisor = int(match_div.group(1))
            start, end = int(re.search(r'от\s+(\d+)', main_text_part).group(1)), int(re.search(r'до\s+(\d+)', main_text_part).group(1))
            favorable_outcomes = sum(1 for i in range(start, end + 1) if i % divisor == 0)
        else: raise ValueError("Калькулятор пока не умеет определять свойство числа.")
    if total_count == 0: raise ValueError("Диапазон чисел не может быть пустым.")
    my_answer_float = favorable_outcomes / total_count
    return {"text": text, "answer": my_answer_float}

def process_opposite_event_task(data: dict) -> dict:
    text = data["text"]
    main_text_part = text.split("Найдите вероятность")[0]
    match = re.search(r'каждой\s+(\d+)', main_text_part)
    if not match: raise ValueError("Не удалось найти число 'n' в условии задачи.")
    n = int(match.group(1))
    if n == 0: raise ValueError("Число 'n' не может быть равно нулю.")
    p_direct = 1 / n
    my_answer_float = (1 - p_direct) if "не найдёт" in text or "не будет" in text else p_direct
    return {"text": text, "answer": my_answer_float}

def process_union_of_topics_task(data: dict) -> dict:
    text = data["text"]
    main_text_part = text.split("Найдите вероятность")[0]
    probabilities = [float(p.replace(",", ".")) for p in re.findall(r'0,\d+', main_text_part)]
    if len(probabilities) < 2: raise ValueError("В задаче на сложение должно быть как минимум 2 вероятности.")
    my_answer_float = sum(probabilities)
    return {"text": text, "answer": my_answer_float}

def process_time_interval_task(data: dict) -> dict:
    text = data["text"]
    main_text_part = text.split("Найдите вероятность")[0]
    probabilities = [float(p.replace(",", ".")) for p in re.findall(r'0,\d+', main_text_part)]
    if len(probabilities) < 2: raise ValueError("В задаче на интервал должно быть как минимум 2 вероятности.")
    my_answer_float = abs(max(probabilities) - min(probabilities))
    return {"text": text, "answer": my_answer_float}

def process_gifts_distribution_task(data: dict) -> dict:
    return process_participant_order_task(data)

def process_relative_frequency_task(data: dict) -> dict:
    text = data["text"]
    main_text_part = text.split("Найдите")[0]
    numbers = [float(n.replace(",", ".")) for n in re.findall(r'\d+,\d+|\d+', main_text_part)]
    if len(numbers) < 2: raise ValueError("В задаче на частоту должно быть как минимум 2 числа.")
    if "на сколько отличается" in text and len(numbers) >= 3:
        p_given = max([n for n in numbers if n < 1])
        numbers.remove(p_given)
        total_count = max(numbers)
        part = min(numbers)
        p_event = (1 - p_given) if "девочек" in text and p_given > 0.5 else p_given
        frequency = part / total_count
        my_answer_float = abs(p_event - frequency)
    else:
        total_count = max(numbers)
        part = min(numbers)
        my_answer_float = part / total_count
    return {"text": text, "answer": my_answer_float}

def process_conference_days_task(data: dict) -> dict:
    return process_participant_order_task(data)

def process_group_transport_task(data: dict) -> dict:
    return process_participant_order_task(data)

# "Карта калькуляторов" - ФИНАЛЬНАЯ ВЕРСИЯ
PROCESSOR_MAP = {
    "items_colors_selection": process_items_colors_task, "bernoulli_trials_patterns": process_bernoulli_task,
    "dice_outcomes": process_dice_task, "exam_tickets": process_exam_tickets_task,
    "participant_order_group": process_participant_order_task, "item_defect_probability": process_item_defect_task,
    "range_number_property": process_range_number_task, "promotions_prize_in_pack": process_opposite_event_task,
    "union_of_topics": process_union_of_topics_task, "time_interval_probability": process_time_interval_task,
    "gifts_distribution_child": process_gifts_distribution_task, "relative_frequency_tasks": process_relative_frequency_task,
    "conference_days_assignment": process_conference_days_task, "group_transport_batches": process_group_transport_task,
}