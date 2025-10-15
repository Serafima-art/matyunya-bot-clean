# utils/help_reset.py
from aiogram.fsm.context import FSMContext

async def reset_help_state(state: FSMContext) -> None:
    """
    Мягкий сброс полей режима помощи.
    Вызывать КАЖДЫЙ РАЗ перед показом нового задания.
    """
    await state.update_data(
        help_on=False,
        help_step=0,
        last_hint_level=0,
        last_user_text="",
        dialog_history=[]  # обнуляем историю помощи в рамках нового задания
    )