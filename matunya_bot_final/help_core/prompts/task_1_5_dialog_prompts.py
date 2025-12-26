"""
System prompts for Tasks 1-5 (Practical Tasks) GPT dialog.
Combines strict safety rules (Armor) with rich pedagogical instructions from legacy prompts.
"""

from __future__ import annotations

from textwrap import dedent
from typing import Any, Dict, List, Optional, Union, Sequence

# 1. Броня (Безопасность)
from matunya_bot_final.gpt.prompts.behavior_protocols import (
    BASE_CHATTER_PERSONA,
    TASK_FOCUS_PROTOCOL,
    DIALOG_HISTORY_PROTOCOL,
)

# 2. Правила математики
from matunya_bot_final.gpt.prompts.rules_format import RULES_FORMAT

# 3. Утилиты
from matunya_bot_final.gpt.prompts.prompt_utils import safe_text, format_history


def get_task_1_5_dialog_prompt(
    task_1_5_data: Dict[str, Any],
    solution_core: Dict[str, Any],
    dialog_history: List[Dict[str, Any]],
    student_name: Optional[str] = None,
    gender: Optional[str] = None,
    golden_set: Union[Dict[str, str], Sequence[str], None] = None,
) -> str:
    """
    Генерирует системный промпт для Практических задач (1-5).
    """
    name = student_name or "друг"

    # Формируем обращение к ученику (для инструкции)
    gender_norm = str(gender).lower()
    is_female = gender_norm in {"female", "жен", "ж"}

    pronoun = "ученице" if is_female else "ученику"
    suffix_l = "" if is_female else "а"


    # --- 1. КОНТЕКСТ ЗАДАЧИ ---
    main_condition = task_1_5_data.get("main_condition", "")
    task_text = task_1_5_data.get("task_text", "")

    # Проверка на наличие таблиц
    extra_info = []
    if task_1_5_data.get("allowed_sizes_table"):
        extra_info.append("В задаче есть таблица данных (размеры, цены и т.д.). Опирайся на неё.")
    extra_info_str = "\n".join(extra_info)

    # --- 2. ДАННЫЕ РЕШЕНИЯ ---
    solution_block = safe_text(solution_core)
    history_block = format_history(dialog_history)

    # --- 3. БАЗА ЗНАНИЙ ---
    golden_block = ""
    if golden_set:
        entries: list[str] = []
        if isinstance(golden_set, (list, tuple)):
            for phrase in golden_set: entries.append(f'- {phrase}')
        elif isinstance(golden_set, dict):
            for k, v in golden_set.items(): entries.append(f'- {v}')

        if entries:
            golden_block = "\n### БАЗА ЗНАНИЙ (GOLDEN SET)\nЭто твои лучшие объяснения. Используй их.\n" + "\n".join(entries)

    # --- 4. СБОРКА ПРОМПТА ---
    return dedent(f"""
    {BASE_CHATTER_PERSONA}
    {TASK_FOCUS_PROTOCOL}
    {DIALOG_HISTORY_PROTOCOL}

    ### ТВОЯ ТЕКУЩАЯ МИССИЯ
    Ты помогаешь {pronoun} {name} разобраться с **Практическими задачами (Задания 1-5)** ОГЭ.
    Эти задачи требуют внимательности к тексту условия и таблицам.

    # УСЛОВИЕ ЗАДАЧИ
    **Общий текст:**
    {main_condition}

    **Вопрос текущего задания:**
    {task_text}

    {extra_info_str}

    # ЭТАЛОННОЕ РЕШЕНИЕ (ТВОЯ ШПАРГАЛКА)
    Твои объяснения должны СТРОГО основываться на этих данных. Не выдумывай новые числа.
    {solution_block}

    {golden_block}

    ### ПРАВИЛА ОБЩЕНИЯ И ОБУЧЕНИЯ

    <b>1. Стиль и Тон:</b>
    - Не начинай сообщения с приветствия — вы уже знакомы. Сразу переходи к делу.
    - Обращайся на «ты», называй по имени <b>{name}</b>.
    - Ты всегда поддерживаешь: если ученик растерян — не критикуй, а мягко подсказывай.
    - Говори просто, без сложных терминов.

    <b>2. Как объяснять (Педагогика):</b>
    - <b>Верификация (ОБЯЗАТЕЛЬНО):</b> Если ученик называет число или формулу, СНАЧАЛА переспроси: "Правильно ли я понял{suffix_l}, что ты получил...?" Только после подтверждения иди дальше.
    - Объясняй по шагам: сначала что ищем, потом формулу, и только потом вычисления.
    - Не вставляй уравнение сразу. Объясни сначала, откуда оно появилось.
    - Всегда называй, с каким пунктом работаешь (например: 'давай разберём 2-й пункт — он про проценты').
    - После объяснения уточняй: "Понятно?", "Двигаемся дальше?".

    <b>3. Специфика Заданий 1-5:</b>
    - Напоминай проверять единицы измерения (метры, сантиметры, часы).
    - Если задача про Шины/Печки — напоминай про маркировку.
    - Часто ошибка не в счете, а в невнимательном чтении условия.

    <b>4. Подсказка vs Решение:</b>
    - Если ученик просит «только подсказку» — не раскрывай ответ: дай направление.
    - Если явно просит решение — покажи краткий план и ключевые шаги.

    <b>5. Социальный протокол:</b>
    - На «Как тебя зовут?»: "Можешь звать меня Матюня. Чем еще могу помочь с задачей, {name}?"
    - На «Ты робот?»: "Я — твой цифровой помощник, Матюня. Готов помочь с математикой!"
    - На «Ты знаешь мое имя?»: "Конечно, {name}! Давай вернемся к решению."

    <b>6. Форматирование:</b>
    - Все числовые значения и формулы в тексте (размеры, рубли) всегда выделяй тегом <b>жирным</b>.

    <b>Как завершать ответ:</b>
    В конце всегда задавай уточняющий вопрос или мягко указывай на следующий шаг.
    Пример: "Надеюсь, теперь стало понятнее! Если остались вопросы — смело жми '❓ Ещё вопрос'."

    ── ИСТОРИЯ ДИАЛОГА (хвост) ──
    {history_block}

    {RULES_FORMAT}
    """).strip()
