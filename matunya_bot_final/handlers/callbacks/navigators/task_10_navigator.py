import random
from typing import Dict, List, Optional

# =================================================================
# "Мозг": Карта подтипов и их "пулы" для Задания 10
# =================================================================

# 1. Человеческие названия всех 14 подтипов
SUBTYPE_TITLES: Dict[str, str] = {
    # Классические вероятности
    "bernoulli_trials_patterns": "Монеты",
    "dice_outcomes": "Игральные кости",
    "items_colors_selection": "Выбор случайного объекта",
    "participant_order_group": "Задачи на жребий",
    "exam_tickets": "Экзаменационные билеты",
    "item_defect_probability": "Стрельба по мишеням",
    "range_number_property": "Простейшие задачи",
    
    # Статистика и теоремы
    "promotions_prize_in_pack": "Вероятность противоположного события",
    "union_of_topics": "Сложение (несовместные)",
    "time_interval_probability": "Сложение (совместные)",
    "gifts_distribution_child": "Умножение (независимые)",
    "relative_frequency_tasks": "Относительная частота",
    "conference_days_assignment": "Задачи на спортивные матчи",
    "group_transport_batches": "Задачи на круглый стол",
}

# 2. "Пулы" для случайного выбора по темам
POOL_CLASSIC: List[str] = [
    "bernoulli_trials_patterns",
    "dice_outcomes",
    "items_colors_selection",
    "participant_order_group",
    "exam_tickets",
    "item_defect_probability",
    "range_number_property",
]

POOL_STATS: List[str] = [
    "promotions_prize_in_pack",
    "union_of_topics",
    "time_interval_probability",
    "gifts_distribution_child",
    "relative_frequency_tasks",
    "conference_days_assignment",
    "group_transport_batches",
]

# Объединенный пул для выбора абсолютно случайного подтипа
POOL_ALL: List[str] = POOL_CLASSIC + POOL_STATS

# =================================================================
# Публичные функции-утилиты
# =================================================================

def title_for(subtype_key: str) -> str:
    """Возвращает короткое человекочитаемое название подтипа."""
    return SUBTYPE_TITLES.get(subtype_key, subtype_key)

def pick_random_by_theme(theme_key: str) -> Optional[str]:
    """
    Выбирает случайный подтип из нужного "пула" на основе ключа темы.
    theme_key: 'classic' или 'stats'.
    """
    if theme_key == "classic":
        pool = POOL_CLASSIC
    elif theme_key == "stats":
        pool = POOL_STATS
    else:
        pool = POOL_ALL # Если тема не указана, выбираем из всех

    if not pool:
        return None
    return random.choice(pool)

def get_subtypes_by_theme(theme_key: str) -> Dict[str, str]:
    """Возвращает словарь {id: название} для подтипов указанной темы."""
    pool = POOL_CLASSIC if theme_key == "classic" else POOL_STATS
    return {key: SUBTYPE_TITLES[key] for key in pool}