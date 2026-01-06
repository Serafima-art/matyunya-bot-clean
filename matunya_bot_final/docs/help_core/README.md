# Архитектура `help_core`

Документ описывает актуальную архитектуру подсистемы «Помощь» и GPT-диалогов.

---
## 1. Структура модуля

```
help_core/
├─ dispatchers/          # Диспетчеры заданий (task_1_5, task_11, task_20, ...)
│   ├─ common.py         # Общая логика: call_dynamic_solver, send_solution_result и др.
│   └─ task_X/...        # Специализированные обработчики help_handler_X.py
├─ dialog_contexts/      # Контексты GPT-диалогов, регистрируются декоратором @register_context
├─ humanizers/           # Преобразование solution_core в дружелюбный вид
├─ knowledge/            # Golden-наборы подсказок и источники знаний
├─ prompts/              # Генерация системных промптов для GPT
└─ solvers/              # Решатели задач (solution_core)
```

Каждый диспетчер отвечает за подготовку `solution_core`, сохранение его в FSM и передачу результата.

---
## 2. Новая архитектура GPT-помощи

- `handlers/callbacks/dialogs/gpt_dialog_control_handler.py` содержит реестр `DIALOG_CONTEXT_HANDLERS` и автоматически подгружает все модули из `help_core/dialog_contexts` через `pkgutil.iter_modules`.
- Контекст задаётся функцией вида `@register_context("task_X") async def handle_task_X_dialog(...): ...`. При импорте модуль автоматически регистрируется в реестре, в логах появляется запись `INFO Registered dialog context: task_X`.
- Общий пайплайн диалога:
  1. Пользователь нажимает кнопку «❓ Задать вопрос». Универсальный хендлер `handle_ask_question` определяет контекст (`task_1_5`, `task_11`, `task_20`, ...), переводит FSM в состояние `GPState.in_dialog` и отправляет приветственное сообщение.
  2. `handle_gpt_dialog_message` получает сообщение ученика, находит обработчик в `DIALOG_CONTEXT_HANDLERS` и получает системный промпт.
  3. GPT вызывается через `ask_gpt_with_history(...)`.
  4. Ответ проходит через `sanitize_gpt_response(...)` (см. `utils/text_formatters.py`) и отправляется с помощью `send_tracked_message(...)`.
  5. Диалог завершается кнопкой «✅ Всё понятно, спасибо!» (`handle_end_gpt_dialog`).

---
## 3. Жизненный цикл кнопок

| Действие пользователя            | Обработчик                                                        | Результат |
|----------------------------------|--------------------------------------------------------------------|-----------|
| «🆘 Помощь»                      | help_core/dispatchers/task_X/help_handler_X.py                     | Генерация `solution_core`, сохранение его в FSM, отправка решения |
| «❓ Задать вопрос»               | `handle_ask_question` (gpt_dialog_control_handler.py)              | FSM → `GPState.in_dialog`, диалоговый контекст запускается        |
| Сообщение пользователю          | `handle_gpt_dialog_message` + `task_X_context.py`                  | Формирование системного промпта и ответ GPT                       |
| «✅ Всё понятно, спасибо!»       | `handle_end_gpt_dialog`                                           | Очистка диалоговых сообщений и возврат в исходное состояние       |

Все тексты из GPT проходят через `sanitize_gpt_response`, что гарантирует безопасный HTML, единое форматирование и стилистику Матюни.

---
## 4. Состояния FSM

- Диспетчеры сохраняют решения в FSM:
  - `task_1_5_solution_core`
  - `task_11_solution_core`
  - `task_20_solution_core`
- Контексты берут значение из FSM и строят промпт через `get_help_dialog_prompt(...)` или специализированные шаблоны.

Пример (фрагмент `task_1_5_context.py`):
```python
@register_context("task_1_5")
async def handle_task_1_5_dialog(data, history):
    task_data = data.get("task_1_5_data")
    solution_core = data.get("task_1_5_solution_core")
    if not isinstance(task_data, dict) or solution_core is None:
        return None

    subtype = task_data.get("subtype") or data.get("current_subtype") or ""
    golden_set = await get_golden_set(subtype, task_type=task_data.get("task_type"))

    return get_help_dialog_prompt(
        task_1_5_data=task_data,
        solution_core=solution_core,
        dialog_history=history,
        student_name=data.get("student_name"),
        gender=data.get("gender"),
        golden_set=golden_set,
    )
```

---
## 5. Добавление нового задания

1. Создать диспетчер `help_core/dispatchers/task_X/help_handler_X.py`, который:
   - достаёт данные из FSM,
   - вызывает `call_dynamic_solver(...)`,
   - сохраняет `task_X_solution_core` в FSM,
   - отправляет решение через `send_solution_result(...)`.
2. Добавить контекст `help_core/dialog_contexts/task_X_context.py`:
```python
from matunya_bot_final.handlers.callbacks.dialogs.gpt_dialog_control_handler import register_context

@register_context("task_X")
async def handle_task_X_dialog(data, history):
    task_data = data.get("task_X_data")
    solution_core = data.get("task_X_solution_core")
    if not isinstance(task_data, dict) or solution_core is None:
        return None

    # Вернуть системный промпт (пример через get_help_dialog_prompt)
    ...
```
3. При необходимости расширить prompt/knowledge (директории `prompts/`, `knowledge/`).
4. Убедиться, что новая пара «диспетчер + контекст» проходит автотесты (см. ниже).

Автоподключение сработает автоматически — декоратор `@register_context` добавит запись в реестр, а `pkgutil.iter_modules` загрузит модуль при старте бота.

---
## 6. Тестирование

- `tests/test_gpt_dialog_integrity.py` — проверяет, что:
  - все обязательные контексты зарегистрированы в `DIALOG_CONTEXT_HANDLERS`;
  - контекстные функции возвращают корректный тип (строка или None);
  - `sanitize_gpt_response` убирает markdown и оставляет допустимый HTML.

Дополнительно рекомендуется запускать интеграционные проверки (ручной прогон заданий 1–5, 11, 20) после добавления новых заданий.

---
## 7. Устаревшие компоненты

- Legacy-хендлер `handlers/callbacks/task_handlers/task_11/help_handler.py` удалён.
- Все задания используют новую архитектуру `help_core/dispatchers/task_X/help_handler_X.py` + `dialog_contexts/task_X_context.py`.
- Кнопки `11_get_help`/`11_ask_gpt` больше не регистрируются, вместо них работает универсальный поток `request_help` → `ask_question`.

---
## 8. Чеклист для разработчика

- [ ] Диспетчер сохраняет `solution_core` в FSM.
- [ ] Контекст возвращает системный промпт и зарегистрирован декоратором `@register_context`.
- [ ] При запуске бота в логах есть строки `INFO Registered dialog context: ...` для всех задач.
- [ ] `sanitize_gpt_response` используется для всех ответов GPT.
- [ ] Тест `tests/test_gpt_dialog_integrity.py` проходит.

Система полностью готова к масштабированию: для добавления нового задания достаточно создать диспетчер и контекст, остальная инфраструктура (реестр, автоподключение, форматирование) работает «из коробки».





"Хостес" (help_handler.py): Он просто передает управление. Маловероятно, что он виноват.
"Официант" (help_handler_6.py): Он берет task_data, вызывает call_dynamic_solver. Он не меняет математику. Маловероятно.
"Инструмент" (common.py): call_dynamic_solver находит решатель по подтипу. Для mixed_fractions он должен был найти mixed_fractions_solver.py. Он мог ошибиться?
"Повар" (mixed_fractions_solver.py): ГЛАВНЫЙ ПОДОЗРЕВАЕМЫЙ. Именно он получает expression_tree с операцией "divide" и должен ее выполнить. Если он вместо деления выполняет умножение — это его вина.
(диалог с Gemini задание 6)


⚠️ Задание 15 — временный legacy-контракт

Задание 15 (геометрия, треугольники) реализовано не по ГОСТ-2026 solution_core, а по legacy-контракту solver → humanizer, сформировавшемуся исторически в ходе разработки.

Solver возвращает список действий вида {"action": "<pattern>:<narrative>", "data": {...}}

Humanizer работает напрямую с action и data, без solution_core v2.x

Вся логика отображения шагов зашита в humanizer-шаблонах

Solver обязан подготовить полный контекст (data), humanizer не выполняет вычислений

📌 Это осознанный технический долг, зафиксированный для завершения задания 15 в срок (подготовка к ОГЭ).
📌 В будущем задание 15 планируется привести к ГОСТ-2026 единым рефакторингом.
