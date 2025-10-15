from __future__ import annotations

from typing import Any, Dict, List

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from matunya_bot_final.gpt.gpt_utils import ask_gpt_with_history
from matunya_bot_final.gpt.prompts.chatter_prompt import get_chatter_prompt
from matunya_bot_final.states.states import DialogState

router = Router(name="chatter_handler")

MAX_CHATTER_EXCHANGES = 10


@router.message(DialogState.in_chatter, F.text)
async def handle_chatter(message: Message, state: FSMContext) -> None:
    """Handle small talk while the user is in DialogState.in_chatter."""
    data = await state.get_data()
    student_name = str(data.get("student_name", "") or "")
    gender = str(data.get("gender", "") or "")

    raw_history: Any = data.get("dialog_history", [])
    if not isinstance(raw_history, list):
        raw_history = []
    dialog_history: List[Dict[str, str]] = [
        entry
        for entry in raw_history
        if isinstance(entry, dict) and "role" in entry and "content" in entry
    ]

    if len(dialog_history) > MAX_CHATTER_EXCHANGES * 2:
        dialog_history = dialog_history[-(MAX_CHATTER_EXCHANGES * 2):]

    system_prompt = get_chatter_prompt(
        student_name=student_name,
        gender=gender,
        dialog_history=dialog_history,
    )

    gpt_response, updated_history = await ask_gpt_with_history(
        user_prompt=message.text,
        dialog_history=dialog_history,
        system_prompt=system_prompt,
    )

    # Шаг 1: ПРОВЕРЯЕМ на наличие сигнала в "сыром" ответе
    if "[ALARM_SIGNAL]" in gpt_response:
        print("ALARM SIGNAL DETECTED!")
        # Здесь в будущем можно будет добавить логирование в базу
    
    # Шаг 2: ОЧИЩАЕМ ответ от сигнала, готовим его для пользователя
    final_response = gpt_response.replace("[ALARM_SIGNAL]", "").strip()

    # Шаг 3: СОХРАНЯЕМ историю и ОТПРАВЛЯЕМ чистый ответ
    await state.update_data(dialog_history=updated_history)
    await message.answer(final_response)
    

@router.callback_query(F.data == "menu_talk")
async def enter_chatter_mode(callback: CallbackQuery, state: FSMContext) -> None:
    """Enter chatter mode when the user presses the talk button."""
    await callback.answer()
    await state.set_state(DialogState.in_chatter)
    await state.update_data(dialog_history=[])

    if callback.message is not None:
        await callback.message.answer(
            "Привет! Рад поболтать. О чем хочешь поговорить?"
        )
