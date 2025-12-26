# matunya_bot_final/utils/fsm_guards.py

import logging
from typing import Optional
from aiogram.fsm.context import FSMContext

logger = logging.getLogger(__name__)


async def ensure_task_index(state: FSMContext) -> Optional[int]:
    """
    🔐 FSM-инвариант для заданий 1–5.

    Гарантирует, что в state есть корректный `index` (0-based).

    Источники восстановления (по приоритету):
    1) state['index']
    2) state['current_task_index']
    3) state['question_num'] - 1

    Если восстановить нельзя — логируем CRITICAL и возвращаем None.
    """

    data = await state.get_data()

    # 1️⃣ Основной путь — index уже есть
    if isinstance(data.get("index"), int):
        return data["index"]

    # 2️⃣ Запасной вариант — current_task_index
    if isinstance(data.get("current_task_index"), int):
        index = data["current_task_index"]
        await state.update_data(index=index)
        logger.warning(
            "FSM GUARD: восстановили index из current_task_index=%s",
            index
        )
        return index

    # 3️⃣ Последний шанс — question_num (1-based)
    if isinstance(data.get("question_num"), int):
        index = data["question_num"] - 1
        await state.update_data(index=index)
        logger.warning(
            "FSM GUARD: восстановили index из question_num=%s",
            data["question_num"]
        )
        return index

    # ❌ Контракт сломан
    logger.critical(
        "🚨 FSM CONTRACT BROKEN: невозможно восстановить index.\n"
        "state_keys=%s\n"
        "state_data=%s",
        list(data.keys()),
        data,
    )

    return None
