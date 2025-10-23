from __future__ import annotations

import os
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from matunya_bot_final.help_core.dispatchers.task_6 import help_handler_6 as handler_module


class FakeState:
    def __init__(self, data: dict | None = None) -> None:
        self._data = data or {}

    async def get_data(self) -> dict:
        return dict(self._data)

    async def update_data(self, **kwargs) -> None:
        self._data.update(kwargs)


def make_callback(chat_id: int = 123) -> SimpleNamespace:
    message = SimpleNamespace(
        chat=SimpleNamespace(id=chat_id),
    )
    callback = SimpleNamespace(
        answer=AsyncMock(),
        message=message,
    )
    return callback


@pytest.mark.asyncio
async def test_handle_task_6_help_success(monkeypatch):
    task_payload = {"id": "task6_demo", "subtype": "cf_addition_subtraction"}
    state = FakeState({"task_6_data": task_payload})
    callback = make_callback()
    callback_data = SimpleNamespace(subtype_key="cf_addition_subtraction")

    solve_mock = AsyncMock(
        return_value={
            "status": "success",
            "final_block": {
                "summary": "Готово",
                "primary_value": {"display": "3/4"},
            },
        }
    )
    humanize_mock = MagicMock(return_value="<b>solution</b>")
    clean_mock = MagicMock(side_effect=lambda text: text)
    processing_mock = AsyncMock(return_value="processing_msg")
    cleanup_mock = AsyncMock()
    send_result_mock = AsyncMock()
    send_tracked_mock = AsyncMock()
    keyboard_mock = MagicMock(return_value="keyboard")

    monkeypatch.setitem(handler_module.SUBTYPE_SOLVERS, "cf_addition_subtraction", solve_mock)
    monkeypatch.setattr(handler_module, "humanize_task_6_solution", humanize_mock)
    monkeypatch.setattr(handler_module, "clean_html_tags", clean_mock)
    monkeypatch.setattr(handler_module, "send_processing_message", processing_mock)
    monkeypatch.setattr(handler_module, "cleanup_messages_by_category", cleanup_mock)
    monkeypatch.setattr(handler_module, "send_solution_result", send_result_mock)
    monkeypatch.setattr(handler_module, "send_tracked_message", send_tracked_mock)
    monkeypatch.setattr(handler_module, "get_after_task_keyboard", keyboard_mock)

    await handler_module.handle_task_6_help(callback, callback_data, bot=None, state=state)

    solve_mock.assert_awaited_once_with(task_payload)
    humanize_mock.assert_called_once()
    clean_mock.assert_called_once_with("<b>solution</b>")
    cleanup_mock.assert_awaited_once()
    keyboard_mock.assert_called_once()
    send_result_mock.assert_awaited_once()
    send_tracked_mock.assert_not_awaited()
    assert "task_6_solution_core" in state._data


@pytest.mark.asyncio
async def test_handle_task_6_help_error(monkeypatch):
    task_payload = {"id": "task6_demo", "subtype": "cf_addition_subtraction"}
    state = FakeState({"task_6_data": task_payload})
    callback = make_callback()
    callback_data = SimpleNamespace(subtype_key="cf_addition_subtraction")

    solve_mock = AsyncMock(
        return_value={
            "status": "error",
            "final_block": {"summary": "Деление на ноль недопустимо."},
        }
    )
    monkeypatch.setitem(handler_module.SUBTYPE_SOLVERS, "cf_addition_subtraction", solve_mock)
    monkeypatch.setattr(handler_module, "send_processing_message", AsyncMock(return_value="processing"))
    monkeypatch.setattr(handler_module, "cleanup_messages_by_category", AsyncMock())
    send_result_mock = AsyncMock()
    monkeypatch.setattr(handler_module, "send_solution_result", send_result_mock)
    send_tracked_mock = AsyncMock()
    monkeypatch.setattr(handler_module, "send_tracked_message", send_tracked_mock)

    await handler_module.handle_task_6_help(callback, callback_data, bot=None, state=state)

    send_tracked_mock.assert_awaited()
    send_result_mock.assert_not_awaited()
    assert state._data["task_6_solution_core"]["status"] == "error"
