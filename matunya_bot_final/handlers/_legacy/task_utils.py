import asyncio
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

# Конфиги и утилиты
from matunya_bot_final.config import USE_GPT_FOR_TASK6
from matunya_bot_final.handlers._legacy.task_loader import get_random_task_6
from matunya_bot_final.handlers._legacy.bot_messages import build_instruction

# Состояния
from matunya_bot_final.states.states import TaskState

# Клавиатуры
from matunya_bot_final.keyboards.inline_keyboards.after_task_keyboard import get_after_task_keyboard

# Генераторы заданий
#from gpt.gpt_utils import generate_task
from matunya_bot_final.gpt.task_templates.task_6 import generate_task_6
from matunya_bot_final.gpt.task_templates.task_7.task_7_generator import generate_task_7
# ВАЖНО: Мы пока оставляем старый импорт generate_task_8_by_subtype,
# так как функция gen_by_type все еще его использует. Позже мы это улучшим.
from matunya_bot_final.py_generators.task_8_generator import generate_task_8_by_subtype

# ──────────────────────────────────────────────────────────────────────────────
# Безопасная генерация задания с таймаутом и 1 повтором
# ──────────────────────────────────────────────────────────────────────────────
async def safe_gen(task_type: str, state: FSMContext, timeout: int = 20) -> tuple[str, list[str]]:
    """
    Генерация задания с таймаутом и повторной попыткой.
    Возвращает (task_text, correct_answers).
    """
    for attempt in range(2):
        try:
            return await asyncio.wait_for(gen_by_type(task_type, state), timeout=timeout)
        except asyncio.TimeoutError:
            if attempt == 0:
                print(f"[WARN] Первая попытка генерации задания {task_type} превысила {timeout} сек. Повтор...")
            else:
                raise


# ──────────────────────────────────────────────────────────────────────────────
# Единая точка генерации по типу задания
# Возвращает: (text: str, correct_answers: list[str])
# ВАЖНО: Всегда проставляем task_source в FSM для корректной работы «Помощи».
# ──────────────────────────────────────────────────────────────────────────────
async def gen_by_type(task_type: str, state: FSMContext) -> tuple[str, list[str]]:
    if task_type == "6":
        if USE_GPT_FOR_TASK6:
            text, answer = await generate_task_6()
            await state.update_data(task_source="gpt", task_id=None)
            return text, [str(answer)]
        else:
            task = get_random_task_6()
            await state.update_data(task6_id=task["id"], task_source="db")
            return task["text"], [task["answer"]]

    if task_type == "7":
        text, answer = await generate_task_7()
        await state.update_data(task_source="gpt", task_id=None)
        return text, [str(answer)]

    if task_type == "8":
        text, answer = await generate_task_8_by_subtype()
        await state.update_data(task_source="gpt", task_id=None)
        return text, [str(answer)]
        


# ──────────────────────────────────────────────────────────────────────────────
# Универсальный обработчик выдачи задания
# ──────────────────────────────────────────────────────────────────────────────
async def handle_task(callback: CallbackQuery, state: FSMContext, task_type: str, task_label: str):
    print(f"🕵️‍♂️ [ШПИОН] Сработал handle_task для task_type={task_type}!")
    """Единая логика для кнопок task_X."""
    await callback.answer()

    # 1) Сообщение ожидания
    waiting_text = f"⏳ Подбираю задание {task_label}..."
    try:
        await callback.message.edit_text(waiting_text)
    except Exception:
    # если не получилось отредактировать (например, старое сообщение), просто отправим новое
        await callback.message.answer(waiting_text)

    # 2) Генерация/выбор задания
    try:
        task_text, correct_answers = await safe_gen(task_type, state, timeout=20)
    except asyncio.TimeoutError:
        await callback.message.answer(
            "⚠️ Кажется, сеть задумалась и не отвечает. Попробуй ещё раз или выбери другое задание 🙏"
        )
        return

    # 3) Источник для подписи и для FSM
    data_after_gen = await state.get_data()
    task_source_value = data_after_gen.get("task_source", "gpt")
    source_human = "от GPT" if task_source_value == "gpt" else "из базы"

    # 4) Печатаем задание
    await callback.message.answer(f"📘 <b>Задание {task_label}</b>:\n\n{task_text}")

    # 5) Сохраняем всё необходимое для «Помощи»/проверки
    await state.update_data(
        task_type=task_type,
        task_text=task_text,
        correct_answers=correct_answers,
        source=task_source_value,  # ключ, который читает handlers/help.py
        dialog_history=[{"role": "system", "content": f"Вот текущее задание:\n\n{task_text}"}]
    )
    await state.update_data(current_task_text=task_text)

    # 🔒 Предохранитель FSM: убеждаемся, что поля на месте
    data_chk = await state.get_data()
    required_ok = all([
        bool(data_chk.get("task_text")),
        isinstance(data_chk.get("correct_answers"), list),
        data_chk.get("source") in {"db", "gpt"},
        isinstance(data_chk.get("dialog_history"), list),
    ])
    if not required_ok:
        await state.update_data(
            task_text=task_text,
            correct_answers=correct_answers or [],
            source=task_source_value,
            dialog_history=data_chk.get("dialog_history") or []
        )
        await state.update_data(current_task_text=task_text)

    # 6) Инструкция + клавиатура (ВНИМАНИЕ: after_task_keyboard — это ФУНКЦИЯ)
    gender = data_after_gen.get("gender", "неизвестно")
    instruction_text = build_instruction(gender, task_type)
    try:
        try:
            task_number = int(task_type)
        except (TypeError, ValueError):
            task_number = 0
        task_subtype = (
            data_after_gen.get("task_subtype")
            or data_after_gen.get("subtype")
            or "generic"
        )
        await callback.message.answer(
            instruction_text,
            reply_markup=get_after_task_keyboard(
                task_number=task_number,
                task_subtype=task_subtype,
                show_help=False,
            ),
        )
    except Exception as e:
        # не валим поток, хотя бы текст покажем
        await callback.message.answer(instruction_text)
        print(f"[WARN] after_task_keyboard не отправилась: {e}")

    # 7) Для №6 переходим в режим ожидания ответа
    if task_type == "6":
        await state.set_state(TaskState.waiting_for_answer)
