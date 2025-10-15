import logging
import re
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

logger = logging.getLogger(__name__)
router = Router()

_ANSWER_TAG = "task_11_main_text"
_ANSWER_LINE_PATTERN = re.compile(r"^\u041e\u0442\u0432\u0435\u0442:.*$", flags=re.MULTILINE)


@router.message(TaskState.waiting_for_answer_11, F.text)
async def handle_task_11_answer(message: Message, state: FSMContext) -> None:
    """\u041e\u0431\u0440\u0430\u0431\u0430\u0442\u044b\u0432\u0430\u0435\u0442 \u0442\u0435\u043a\u0441\u0442\u043e\u0432\u044b\u0439 \u043e\u0442\u0432\u0435\u0442 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f \u0434\u043b\u044f \u0437\u0430\u0434\u0430\u043d\u0438\u044f 11."""
    user_answer_raw = (message.text or "").strip()
    user_id = message.from_user.id
    logger.info("Task 11: \u043f\u043e\u043b\u0443\u0447\u0435\u043d \u043e\u0442\u0432\u0435\u0442 \u043e\u0442 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f %s: '%s'", user_id, user_answer_raw)

    try:
        await message.delete()
        logger.info("Task 11: сообщение пользователя %s удалено.", user_id)
    except Exception as exc:  # pragma: no cover - Telegram может вернуть ошибку из-за гонки
        logger.error("Task 11: не удалось удалить сообщение пользователя %s: %s", user_id, exc)

    await cleanup_messages_by_category(
        bot=message.bot,
        state=state,
        chat_id=message.chat.id,
        category="dialog_messages",
    )

    data = await state.get_data()
    task_data = data.get("task_11_data")
    if not isinstance(task_data, dict):
        logger.error("Task 11: \u0434\u0430\u043d\u043d\u044b\u0435 \u0437\u0430\u0434\u0430\u043d\u0438\u044f \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u044b \u0432 FSM.")
        return

    formatted_text = data.get("task_11_formatted_text")
    base_text = formatted_text or _build_base_text(task_data)

    correct_answer = task_data.get("answer")
    if correct_answer is None:
        logger.error("Task 11: \u044d\u0442\u0430\u043b\u043e\u043d\u043d\u044b\u0439 \u043e\u0442\u0432\u0435\u0442 \u043e\u0442\u0441\u0443\u0442\u0441\u0442\u0432\u0443\u0435\u0442 \u0432 task_data.")
        return

    params = task_data.get("source_plot", {}).get("params", {})
    labels = params.get("labels", ["\u0410", "\u0411", "\u0412"])

    task_message_id = await get_message_id_by_tag(state, _ANSWER_TAG)
    if task_message_id is None:
        logger.error("Task 11: \u043d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u043f\u043e\u043b\u0443\u0447\u0438\u0442\u044c message_id \u043f\u043e \u0442\u0435\u0433\u0443 '%s'.", _ANSWER_TAG)
        return

    feedback_string, is_fully_correct = _build_detailed_feedback(
        user_answer_raw,
        correct_answer,
        labels,
    )
    logger.info(
        "Task 11: \u0434\u0435\u0442\u0430\u043b\u044c\u043d\u0430\u044f \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0430 \u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u0430. \u0421\u0442\u0430\u0442\u0443\u0441 \u2014 %s.",
        "\u0432\u0441\u0435 \u044d\u043b\u0435\u043c\u0435\u043d\u0442\u044b \u0441\u043e\u0432\u043f\u0430\u043b\u0438" if is_fully_correct else "\u0435\u0441\u0442\u044c \u043d\u0435\u0441\u043e\u0432\u043f\u0430\u0434\u0435\u043d\u0438\u044f",
    )

    answer_line = f"\u041e\u0442\u0432\u0435\u0442: {feedback_string}"
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
        logger.info("Task 11: \u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u043e \u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u0435 \u0437\u0430\u0434\u0430\u043d\u0438\u044f (message_id=%s).", task_message_id)
    except Exception as exc:
        logger.error("Task 11: \u043e\u0448\u0438\u0431\u043a\u0430 \u043f\u0440\u0438 \u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u0438 \u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u044f: %s", exc)
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
            inline_keyboard=[[InlineKeyboardButton(text="🆘 Помощь", callback_data=help_callback)]]
        )

        await send_tracked_message(
            bot=message.bot,
            chat_id=message.chat.id,
            state=state,
            text="❌ Не совсем так. Попробуй еще раз или воспользуйся подсказкой!",
            reply_markup=help_keyboard,
            message_tag="task_11_incorrect_answer_prompt",
            category="dialog_messages",
        )

        await state.update_data(task_11_last_attempt=user_answer_raw)


def _extract_answer_tokens(value: str, expected_len: int) -> list[str]:
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
    """\u0413\u043e\u0442\u043e\u0432\u0438\u0442 \u0434\u0435\u0442\u0430\u043b\u044c\u043d\u0443\u044e \u0441\u0442\u0440\u043e\u043a\u0443 \u043e\u0431\u0440\u0430\u0442\u043d\u043e\u0439 \u0441\u0432\u044f\u0437\u0438 \u0438 \u043f\u0440\u0438\u0437\u043d\u0430\u043a \u043f\u043e\u043b\u043d\u043e\u0439 \u043a\u043e\u0440\u0440\u0435\u043a\u0442\u043d\u043e\u0441\u0442\u0438."""
    normalized_labels = list(labels) if labels else ["\u0410", "\u0411", "\u0412"]

    if isinstance(correct_answer, Sequence) and not isinstance(correct_answer, (str, bytes)):
        expected_tokens = [str(item).strip() for item in correct_answer]
    else:
        correct_str = str(correct_answer or "").strip()
        expected_tokens = _extract_answer_tokens(correct_str, len(normalized_labels))
        if not expected_tokens and correct_str:
            expected_tokens = list(correct_str)

    expected_len = len(expected_tokens)
    if expected_len == 0:
        safe_user_answer = escape_for_telegram(user_answer) if user_answer else "\u2014"
        return f"\u274c <b>{safe_user_answer}</b>", False

    user_tokens = _extract_answer_tokens(user_answer, expected_len)
    if len(user_tokens) != expected_len:
        safe_user_answer = escape_for_telegram(user_answer) if user_answer else "\u2014"
        return f"\u274c <b>{safe_user_answer}</b>", False

    feedback_parts: list[str] = []
    all_correct = True
    for idx, expected in enumerate(expected_tokens):
        token = user_tokens[idx] if idx < len(user_tokens) else ""
        is_match = answers_equal(token, expected)
        if not is_match:
            all_correct = False
        label = normalized_labels[idx] if idx < len(normalized_labels) else f"\u2116{idx + 1}"
        safe_token = escape_for_telegram(token) if token else "\u2014"
        mark = "\u2705" if is_match else "\u274c"
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
        final_text = f"{main_text}\n\n<b>\u0412\u0430\u0440\u0438\u0430\u043d\u0442\u044b:</b>\n{variants_text}"

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

    logger.info("Task 11: \u0441\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u0435 \u043e\u0447\u0438\u0449\u0435\u043d\u043e, \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c \u0437\u0430\u0432\u0435\u0440\u0448\u0438\u043b \u0437\u0430\u0434\u0430\u0447\u0443.")




