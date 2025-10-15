from aiogram.filters.callback_data import CallbackData
from typing import Optional

class TaskCallback(CallbackData, prefix="task"):
    """
    УНИВЕРСАЛЬНЫЙ CallbackData для всех действий, связанных с задачами.
    Версия 2.1: Добавлено поле level для системы помощи.

    Атрибуты:
        action: Тип действия (e.g., "carousel_nav", "select_subtype", "focus_question", "get_help", "select_help_level").
                Заменили 'type', чтобы не конфликтовать со встроенными именами.
        
        subtype_key: Ключ подтипа задания ("tires", "ovens", "match_signs_a_c"...), если применимо.

        task_type: Номер задания (6, 7, 11, 20...), если применимо.

        question_num: Номер вопроса в блоке (1-5), если применимо.

        task_id: ID конкретной задачи из БД, если нужно сослаться на нее.
        
        level: Уровень помощи для системы подсказок ("hint", "partial", "step", "solution"), если применимо.
    """
    action: str
    subtype_key: Optional[str] = None
    task_type: Optional[int] = None
    question_num: Optional[int] = None
    task_id: Optional[int] = None
    level: Optional[str] = None
