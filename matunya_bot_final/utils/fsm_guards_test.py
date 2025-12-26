# matunya_bot_final/utils/fsm_guards_test.py

import pytest
from matunya_bot_final.utils.fsm_guards import ensure_task_index


class FakeFSMContext:
    """
    Минимальный mock FSMContext для unit-тестов FSM-инвариантов.
    """
    def __init__(self, data: dict):
        self._data = dict(data)

    async def get_data(self):
        return self._data

    async def update_data(self, **kwargs):
        self._data.update(kwargs)


@pytest.mark.asyncio
async def test_index_already_exists():
    """
    🧪 index уже есть — возвращаем его, ничего не меняем
    """
    state = FakeFSMContext({"index": 2})

    result = await ensure_task_index(state)

    assert result == 2
    assert state._data["index"] == 2


@pytest.mark.asyncio
async def test_restore_from_current_task_index():
    """
    🧪 index восстанавливается из current_task_index
    """
    state = FakeFSMContext({"current_task_index": 1})

    result = await ensure_task_index(state)

    assert result == 1
    assert state._data["index"] == 1


@pytest.mark.asyncio
async def test_restore_from_question_num():
    """
    🧪 index восстанавливается из question_num (1-based → 0-based)
    """
    state = FakeFSMContext({"question_num": 3})

    result = await ensure_task_index(state)

    assert result == 2
    assert state._data["index"] == 2


@pytest.mark.asyncio
async def test_index_has_priority_over_fallbacks():
    """
    🧪 если index уже есть — fallback-источники игнорируются
    """
    state = FakeFSMContext({
        "index": 0,
        "current_task_index": 5,
        "question_num": 10,
    })

    result = await ensure_task_index(state)

    assert result == 0
    assert state._data["index"] == 0


@pytest.mark.asyncio
async def test_contract_broken_returns_none():
    """
    🧪 контракт сломан — вернуть None
    """
    state = FakeFSMContext({"foo": "bar"})

    result = await ensure_task_index(state)

    assert result is None
    assert "index" not in state._data
