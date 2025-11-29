import logging
import re
import random
from typing import Any, Sequence

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from matunya_bot_final.keyboards.inline_keyboards.after_task_keyboard import (
    get_after_task_keyboard,
    get_task_completed_keyboard,
)
from matunya_bot_final.states.states import TaskState
from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback
from matunya_bot_final.utils.answer_utils import answers_equal
from matunya_bot_final.utils.message_manager import (
    cleanup_messages_by_category,
    get_message_id_by_tag,
    send_tracked_message,
)
from matunya_bot_final.utils.text_formatters import escape_for_telegram, format_task
from matunya_bot_final.gpt.phrases.tasks.correct_answer_feedback import get_random_feedback
from matunya_bot_final.gpt.phrases.tasks.incorrect_answer_feedback import INCORRECT_FEEDBACK_PHRASES


logger = logging.getLogger(__name__)
router = Router()

_ANSWER_TAG = "task_11_main_text"
_ANSWER_LINE_PATTERN = re.compile(r"^Ответ:.*$", flags=re.MULTILINE)


@router.message(TaskState.waiting_for_answer_11, F.text)
async def handle_task_11_answer(message: Message, state: FSMContext) -> None:
    """Обрабатывает текстовый ответ пользователя для задания 11."""
    user_answer_raw = (message.text or "").strip()
    user_id = message.from_user.id
    logger.info(
        "Task 11: получен ответ от пользователя %s: '%s'",
        user_id,
        user_answer_raw,
    )

    try:
        await message.delete()
        logger.info("Task 11: сообщение пользователя %s удалено.", user_id)
    except Exception as exc:  # pragma: no cover - Telegram может вернуть ошибку из-за гонки
        logger.error(
            "Task 11: не удалось удалить сообщение пользователя %s: %s",
            user_id,
            exc,
        )

    await cleanup_messages_by_category(
        bot=message.bot,
        state=state,
        chat_id=message.chat.id,
        category="dialog_messages",
    )

    data = await state.get_data()
    task_data = data.get("task_11_data")
    if not isinstance(task_data, dict):
        logger.error("Task 11: данные задания не найдены в FSM.")
        return

    formatted_text = data.get("task_11_formatted_text")
    base_text = formatted_text or _build_base_text(task_data)

    correct_answer = task_data.get("answer")
    if correct_answer is None:
        logger.error("Task 11: эталонный ответ отсутствует в task_data.")
        return

    params = task_data.get("source_plot", {}).get("params", {})
    labels = params.get("labels", ["А", "Б", "В"])

    task_message_id = await get_message_id_by_tag(state, _ANSWER_TAG)
    if task_message_id is None:
        logger.error(
            "Task 11: не удалось получить message_id по тегу '%s'.",
            _ANSWER_TAG,
        )
        return

    feedback_string, is_fully_correct = _build_detailed_feedback(
        user_answer_raw,
        correct_answer,
        labels,
    )
    logger.info(
        "Task 11: детальная проверка завершена. Статус — %s.",
        "все элементы совпали" if is_fully_correct else "есть несовпадения",
    )

    answer_line = f"Ответ: {feedback_string}"
    updated_text = _merge_answer_line(base_text, answer_line)

    raw_task_type = task_data.get("task_type")
    try:
        task_number = int(raw_task_type)
    except (TypeError, ValueError):
        task_number = 11

    task_subtype = task_data.get("subtype") or "match_signs_a_c"

    keyboard = (
        get_task_completed_keyboard(task_number=task_number, task_subtype=task_subtype)
        if is_fully_correct
        else get_after_task_keyboard(
            task_number=task_number,
            task_subtype=task_subtype,
        )
    )

    try:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=task_message_id,
            text=updated_text,
            reply_markup=keyboard,
            parse_mode="HTML",
        )
        logger.info(
            "Task 11: обновлено сообщение задания (message_id=%s).",
            task_message_id,
        )
    except Exception as exc:
        logger.error(
            "Task 11: ошибка при обновлении сообщения: %s",
            exc,
        )
        return

    if is_fully_correct:
        student_name = data.get("student_name")
        gender = data.get("gender")
        feedback_text = get_random_feedback(name=student_name, gender=gender)

        await send_tracked_message(
            bot=message.bot,
            chat_id=message.chat.id,
            state=state,
            text=feedback_text,
            message_tag="task_11_success_feedback",
            category="dialog_messages",
        )

        updated_state = await state.get_data()
        await _finalize_success(state, updated_state)
    else:
        task_type_value = task_data.get("task_type")
        try:
            question_num = int(task_type_value) if task_type_value is not None else None
        except (TypeError, ValueError):
            question_num = None

        help_callback = TaskCallback(
            action="11_get_help",
            subtype_key=task_data.get("subtype"),
            question_num=question_num,
        ).pack()
        help_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🆘 Помощь",
                        callback_data=help_callback,
                    )
                ]
            ]
        )

        text = random.choice(INCORRECT_FEEDBACK_PHRASES)

        await send_tracked_message(
            bot=message.bot,
            chat_id=message.chat.id,
            state=state,
            text=text,
            message_tag="task_11_incorrect_answer_prompt",
            category="dialog_messages",
        )

        await state.update_data(task_11_last_attempt=user_answer_raw)


def _extract_answer_tokens(value: str, expected_len: int) -> list[str]:
    # Здесь оставляем Unicode-диапазоны как есть, чтобы не нарушить логику.
    tokens = re.findall(r"[A-Za-z\u0410-\u042f\u0430-\u044f\u0401\u04510-9]+", value or "")
    if len(tokens) == expected_len:
        return tokens
    if len(tokens) == 1 and tokens[0].isdigit() and len(tokens[0]) == expected_len:
        return list(tokens[0])
    return tokens


def _build_detailed_feedback(
    user_answer: str,
    correct_answer: Any,
    labels: Sequence[str],
) -> tuple[str, bool]:
    """Готовит детальную строку обратной связи и признак полной корректности."""
    normalized_labels = list(labels) if labels else ["А", "Б", "В"]

    if isinstance(correct_answer, Sequence) and not isinstance(correct_answer, (str, bytes)):
        expected_tokens = [str(item).strip() for item in correct_answer]
    else:
        correct_str = str(correct_answer or "").strip()
        expected_tokens = _extract_answer_tokens(correct_str, len(normalized_labels))
        if not expected_tokens and correct_str:
            expected_tokens = list(correct_str)

    expected_len = len(expected_tokens)
    if expected_len == 0:
        safe_user_answer = escape_for_telegram(user_answer) if user_answer else "—"
        return f"❌ <b>{safe_user_answer}</b>", False

    user_tokens = _extract_answer_tokens(user_answer, expected_len)
    if len(user_tokens) != expected_len:
        safe_user_answer = escape_for_telegram(user_answer) if user_answer else "—"
        return f"❌ <b>{safe_user_answer}</b>", False

    feedback_parts: list[str] = []
    all_correct = True
    for idx, expected in enumerate(expected_tokens):
        token = user_tokens[idx] if idx < len(user_tokens) else ""
        is_match = answers_equal(token, expected)
        if not is_match:
            all_correct = False
        label = normalized_labels[idx] if idx < len(normalized_labels) else f"№{idx + 1}"
        safe_token = escape_for_telegram(token) if token else "—"
        mark = "✅" if is_match else "❌"
        feedback_parts.append(f"{mark} {label} <b>{safe_token}</b>")

    return " ".join(feedback_parts), all_correct


def _merge_answer_line(base_text: str, answer_line: str) -> str:
    if _ANSWER_LINE_PATTERN.search(base_text):
        return _ANSWER_LINE_PATTERN.sub(answer_line, base_text, count=1)

    return f"{base_text}\n{answer_line}"


def _build_base_text(task_data: dict) -> str:
    main_text = task_data.get("text", "")
    source_plot = task_data.get("source_plot", {})
    params = source_plot.get("params", {})
    options = params.get("options", {})

    final_text = main_text
    if options:
        variants_text = "\n".join(
            f"<b>{num})</b> {formula}" for num, formula in options.items()
        )
        final_text = f"{main_text}\n\n<b>Варианты:</b>\n{variants_text}"

    return format_task(str(task_data.get("task_type")), final_text)


async def _finalize_success(state: FSMContext, data: dict) -> None:
    tracked_messages = data.get("tracked_messages")
    message_tags_by_category = data.get("message_tags_by_category")

    await state.clear()

    preserved: dict[str, Any] = {}
    if tracked_messages:
        preserved["tracked_messages"] = tracked_messages
    if message_tags_by_category:
        preserved["message_tags_by_category"] = message_tags_by_category

    if preserved:
        await state.update_data(**preserved)

    logger.info(
        "Task 11: состояние очищено, пользователь завершил задачу.",
    )
