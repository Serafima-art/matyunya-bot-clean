# handlers/callbacks/task_handlers/group_1_5/theory_handler.py
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
import logging

# Импортируем наш "умный" колбэк
from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback
# Импортируем GPT-утилиты
from matunya_bot_final.gpt.gpt_utils import ask_gpt_with_history

logger = logging.getLogger(__name__)
router = Router(name="theory_handler_1_5")

# --- НОВЫЙ "УМНЫЙ" ХЕНДЛЕР ---
@router.callback_query(TaskCallback.filter(F.action == "get_theory"))
async def handle_show_theory(callback: CallbackQuery, callback_data: TaskCallback, state: FSMContext):
    """
    Отправляет запрос к GPT для получения теории по конкретному вопросу.
    Работает с новой архитектурой task_1_5_data.
    """
    await callback.answer("📚 Ищу теорию по этому вопросу...")

    try:
        question_num = callback_data.question_num
        if not question_num:
            await callback.message.answer("⚠️ Не удалось определить номер задания.")
            return

        user_data = await state.get_data()
        task_1_5_data = user_data.get("task_1_5_data", {})
        tasks = task_1_5_data.get("tasks", [])

        # Извлекаем текст конкретного, нужного нам задания
        if 0 < question_num <= len(tasks):
            task_text = tasks[question_num - 1].get("text")
        else:
            await callback.message.answer(f"⚠️ Задание №{question_num} не найдено.")
            return

        if not task_text:
            await callback.message.answer("⚠️ Текст задания пуст.")
            return

        # Промпт для GPT
        theory_prompt = (
            f"Вот задание из ОГЭ по математике:\n\n{task_text}\n\n"
            "Объясни кратко (в 2-3 абзацах), какая основная теория нужна для его решения. "
            "Объясни как добрый репетитор для ученика 9 класса, простыми словами. "
            "Не используй сложные формулы. Твоя задача — напомнить тему и ключевую идею, а не решать задачу."
        )

        # Вызываем GPT
        theory_text, _ = await ask_gpt_with_history(
            user_prompt=theory_prompt,
            dialog_history=[] # Теорию всегда спрашиваем с чистого листа
        )

        await callback.message.answer(f"📘 <b>Теория к Заданию №{question_num}:</b>\n\n{theory_text}")

    except Exception as e:
        logger.error(f"Ошибка при получении теории для Задания {callback_data.question_num}: {e}")
        await callback.message.answer("❌ Ой, что-то пошло не так при поиске теории. Попробуй еще раз!")