# AGENTS.md — Project contract for GPT-5-Codex
**Owner:** Оленька  ·  **Goal:** safe, async, readable code for Matyunya bot

## 1) Tech & Stack (фактический)
- **Python:** 3.11+
- **Bot:** `aiogram` 3.x (современный синтаксис; явный `Bot`, `Router`, `CallbackQuery`, FSM v3)
- **DB:** SQLite через `SQLAlchemy 2.x` (Core & ORM) + драйвер `aiosqlite`
- **LLM:** `openai` (чтение ключей только из env)
- **Images:** `Pillow` (PIL)
- **Config:** `.env` через `python-dotenv`
- **Прочие директории:** `handlers/`, `utils/`, `gpt/`, `states/`, `keyboards/`, `task_generators/`, `tests/`, `alembic/`, `docs/`, `scripts/`

> Примечание: dev-инструменты (ruff/black/isort/mypy/pytest) не обязательны. Если они появятся, соблюдать их правила.

## 2) Security & Secrets Policy (СТРОГО)
**Никогда не читать, не открывать, не печатать и не включать в ответы/диффы:**
- `/.env`, `/.env.*`, `/.env.local`, `/.env.production`, `/.env.test`
- `secrets.*`, `*.pem`, `id_rsa*`, `.ssh/`, `.aws/`, `.kube/`, `*.pfx`, `*.p12`
- любые файлы/пути с названием `secret`, `token`, `credentials`, `key`, `cert`

**Команды и действия ЗАПРЕЩЕНЫ:**
- `cat .env`, `printenv`, `set`, `env`, дампы конфигов/переменных окружения
- любое логирование реальных значений токенов/паролей
- отправка содержимого конфигов/секретов в описание изменений, комментарии или в тесты

**Как работать с секретами правильно:**
- Доступ к секретам — только через `os.getenv(...)` **в одном месте** (например, `utils/config.py`), а дальше передавать **значения параметрами** (dependency injection).
- В логах и сообщениях — только **редакция** (первые 4 символа + `…`) или `None`.
- Для задач, где код требует секреты, использовать **моки/заглушки** (см. чек-лист ниже).
- Если включён Auto-context — **не держать** открытыми файлы из списка выше.

**Контекст Codex:**
- Если задача затрагивает конфиг/секреты — сначала запросить подтверждение и предложить мок-вариант.
- Любые попытки прочитать секреты — **отклонять** и объяснять причину.

## 3) Код-гайд (минимально необходимый)
- Асинхронный стиль (`async/await`) везде, где есть I/O (aiogram, БД, сети).
- SQLAlchemy 2.0 (новый стиль запросов). Без новых зависимостей без просьбы.
- Внешние эффекты (I/O, сеть) — изолировать; логика — чистые функции.
- Типизация где возможно (`-> None` тоже указывать).
- Перед применением изменений — **всегда показать diff** и краткое резюме.

## 4) Разрешено / Нельзя
**Можно:**
- Локальные правки и рефакторинг модулей с показом diff.
- Добавление небольших юнит-тестов (если тестовый фреймворк уже есть).
- Генерация заглушек конфигов (`.env.example`) и тестовых фикстур.

**Нельзя:**
- Перемещать/удалять конфиги, менять git-историю, ходить в сеть, менять CI.
- Печатать/логировать секреты, предлагать команды чтения `.env`.

## 5) Рекомендованные промпты (учитывают политику секретов)
- **Fix/refactor (без секретов):**  
  “Refactor `utils/db_manager.py::log_ai_interaction` for clarity and typing. Keep behavior. Show diff. No new deps.”
- **Тест с моками:**  
  “Create a minimal unit test that sets env via in-memory patch for `OPENAI_API_KEY` (no real secrets). Do not read `.env`.”

## 6) Мини-API для конфигов (безопасный доступ к env)
Создай `utils/config.py` (или обнови) с *единой* точкой входа для переменных окружения:

```python
# utils/config.py
from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Загружаем только из файла по умолчанию, но не печатаем содержимое
load_dotenv()

@dataclass(frozen=True)
class Settings:
    OPENAI_API_KEY: Optional[str] = None
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    DATABASE_URL: Optional[str] = None  # например, "sqlite+aiosqlite:///matunya.db"

def _redact(value: Optional[str]) -> str:
    if not value:
        return "None"
    return (value[:4] + "…") if len(value) > 4 else "…"

_cached: Optional[Settings] = None

def get_settings(*, refresh: bool = False) -> Settings:
    """Единая точка чтения env (без печати значений)."""
    global _cached
    if _cached is not None and not refresh:
        return _cached
    s = Settings(
        OPENAI_API_KEY=os.getenv("OPENAI_API_KEY"),
        TELEGRAM_BOT_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN"),
        DATABASE_URL=os.getenv("DATABASE_URL"),
    )
    _cached = s
    return s

def debug_settings_redacted() -> str:
    """Безопасная строка для логов (всегда с редактированием)."""
    s = get_settings()
    return (
        f"Settings("
        f"OPENAI_API_KEY={_redact(s.OPENAI_API_KEY)}, "
        f"TELEGRAM_BOT_TOKEN={_redact(s.TELEGRAM_BOT_TOKEN)}, "
        f"DATABASE_URL={_redact(s.DATABASE_URL)})"
    )

# AGENTS.md — Project contract for GPT-5-Codex (owner: Оленька)

## Tech & style
- Language: **Python 3.11+**, async/await.
- Framework: **aiogram v3** (FSMContext, CallbackQuery из aiogram 3).
- DB: **SQLAlchemy 2.0**, Alembic для миграций.
- Tests: **pytest**.
- Formatting: **Black** (line length 88), import sort — **isort**.
- Lint: **ruff** (pep8/pyflakes), Type checking: **mypy (strict-ish)**.
- Docstrings: **Google style**.
- Логирование: стандартный `logging`, уровень по умолчанию INFO.

## Conventions
- Всегда добавляй **type hints**. Не ломай публичные сигнатуры без необходимости.
- При рефакторинге: сохраняй поведение, покрывай изменённый код **pytest** тестами.
- Имена: `snake_case` для функций/переменных, `PascalCase` для классов.
- Обработка ошибок: `try/except` узкой гранулярности, логируй причину, не глуши исключения.
- Не тянуть новые зависимости без согласования.

## Repo map (read-only)
- `handlers/` — хендлеры бота (aiogram v3)
- `utils/` — утилиты (в т.ч. `db_manager.py`)
- `gpt/`, `scripts/`, `states/`, `task_generators/`, `tests/`, `help_core/`, `keyboards/`, `py_generators/`, `docs/`
- `.env` — конфиг окружения; **не изменять**
- Миграции: `alembic/`

## What Codex may do
- Мелкие правки в текущих файлах.
- Рефакторинг модулей с показом **diff**.
- Генерация **pytest**-тестов для изменённого кода.
- Команды (локально или в облаке), которые можно выполнять:
  - `ruff --fix .`, `black .`, `pytest -q`, `mypy .`
  - `alembic revision --autogenerate` (только при явной просьбе)
- **Запрещённые команды:** всё, что удаляет/перемещает файлы, меняет git-историю, взаимодействует с сетью/секретами, запускает произвольные скрипты.

## Guidance for tasks
- Если просишь «исправь баг» — добавь минимальный тест, воспроизводящий проблему.
- Если задача > ~200 строк, работать **в Cloud-режиме**.
- Перед применением ALWAYS показать diff и короткое резюме изменений.

## Style examples
```python
async def log_ai_interaction(... ) -> AIInteractionLog:
    """Short summary.

    Args:
        user_id: ...
    Returns:
        AIInteractionLog: ...
    Raises:
        ValueError: ...
    """

## Operational Safety (must follow)
- Before writing any files: propose a patch (diff) and WAIT for my explicit "apply".
- Before running ANY shell commands: list exact commands and WAIT for my explicit "approve".
- Never auto-stage/commit; never modify git history; do not run external network calls.