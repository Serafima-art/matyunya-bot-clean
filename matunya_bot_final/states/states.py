"""FSM States for the Matunya bot."""

from aiogram.fsm.state import State, StatesGroup


class NameGenderState(StatesGroup):
    """Collect user name and gender during onboarding."""

    waiting_for_name = State()
    waiting_for_gender = State()


class TaskState(StatesGroup):
    """Track progress while solving training tasks."""

    waiting_for_answer = State()
    waiting_for_answer_6 = State()
    waiting_for_answer_8 = State()
    waiting_for_answer_11 = State()
    waiting_for_answer_15 = State()
    waiting_for_answer_16 = State()
    waiting_for_answer_20 = State()
    task_in_progress = State()
    task_completed = State()


class DialogState(StatesGroup):
    """Legacy chat states (kept for backward compatibility)."""

    in_dialog = State()
    in_chatter = State()


class GPState(StatesGroup):
    """Hybrid GPT dialogue states."""

    in_dialog = State()
