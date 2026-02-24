Практико-ориентированные задания 1–5
Тема: Форматы бумаги A0–A7
1. Общая концепция

Данный модуль реализует практико-ориентированное задание 1–5 по теме форматов бумаги серии A (A0–A7).

Реализация строго следует архитектуре:

.txt / json → validator → solver (facts only) → solution_core → humanizer


⚠️ Никаких legacy-контрактов.
⚠️ Никакой логики в humanizer.
⚠️ Источник истины — validator.

2. Архитектура
2.1 Общая схема
tasks_1_5_paper.json
        ↓
validator (non_generators)
        ↓
solver (facts-only)
        ↓
solution_core (канон)
        ↓
humanizer (шаблоны + форматирование)

2.2 Validator
🎯 Роль

Полный источник истины

Проверка входных данных

Вычисление всех числовых значений

Формирование solution_data

📌 В validator обязательно:

расчёт index_difference

построение transition_chain

вычисление rounded_value

вычисление lower_value / upper_value

вычисление is_middle

вычисление exact_multiple

расчёт площадей

расчёт массы

расчёт коэффициентов √2

округления по школьному правилу (0.5 вверх)

Validator ничего не форматирует.

2.3 Solver (facts only)
🎯 Роль

Не делает вычислений

Не анализирует текст

Не округляет

Не форматирует числа

Не генерирует текст

Solver просто передаёт:

solution_core = {
    "pattern": ...,
    "narrative": ...,
    "final_answer": ...,
    "variables": {...}  # факты из validator
}

2.4 Humanizer
🎯 Роль

Только форматирование

Только шаблоны

Только отображение

Никаких вычислений

Порядок внутри humanize():

builder формирует context

numeric formatter форматирует числа

выбирается STEP

рендерятся IDEA / STEPS / ANSWER / TIPS

3. Реализованные нарративы
3.1 match_formats_to_rows

Определение соответствия форматов строкам таблицы.

Ключевые поля:

row_to_format_mapping

answer_sequence

3.2 count_subformats

Количество листов при переходе между форматами.

Формула:

2^(разница индексов)


Обязательные поля:

from_format

to_format

from_index

to_index

index_difference

transition_chain

3.3 find_with_rounding

Определение стороны с округлением до кратного числа.

Обязательные поля:

original_value

round_base

lower_value

upper_value

rounded_value

exact_multiple (bool)

is_middle (bool)

⚠️ exact_multiple и is_middle должны быть bool, не строки.

3.4 area_with_rounding_5 / area_with_rounding_10

Площадь листа:

S = длина × ширина


Перевод:

мм → см (делим на 10)


Округление:

к 5

к 10

3.5 pack_weight

Масса пачки бумаги.

База:

A0 = 1 м²


Количество листов:

2^index_difference


Масса одного листа:

density : количество листов


Масса пачки:

масса одного листа × sheet_count


⚠️ Числа подбираются так, чтобы:

масса одного листа была целой

либо десятичной с максимум 1 знаком

либо красивой (например 62,5)

3.6 font_scaling

Масштабирование шрифта при переходе форматов.

База:

коэффициент = (√2)^n


Упрощения:

(√2)^2 = 2
(√2)^3 = 2√2


Округление — только в конце.

4. Числовая политика

В заданиях 1–5:

избегать длинных дробей

избегать 3+ знаков после запятой

избегать 3,906 и подобных чисел

использовать плотности типа:

125

192

250

256

320

500

5. Правила округления

Используется школьное округление:

0.5 → вверх


Реализация:

math.floor(value/multiple + 0.5) * multiple

6. Контекст-билдеры

В _CONTEXT_BUILDERS:

find_with_rounding → _rounding_context_builder
font_scaling → _font_scaling_context_builder
pack_weight → _pack_weight_context_builder


Никаких лишних ключей.

7. Принцип масштабирования на другие темы

Любая новая практико-ориентированная тема 1–5 должна:

Использовать non_generators

Иметь свой json

Иметь validator как источник истины

Использовать solver facts-only

Использовать humanizer без вычислений

Не смешивать слои

8. Команды запуска
Пересборка БД
python -m matunya_bot_final.non_generators.task_1_5.paper.build

Debug solver
python -m matunya_bot_final.help_core.solvers.task_1_5.paper._debug_solver --to-file

9. Статус модуля

✔ Архитектура стабильна
✔ Округления исправлены
✔ Bool-баг устранён
✔ Школьная логика подтверждена
✔ Массы пачек приведены к «красивым» числам

Модуль можно считать эталонным для практико-ориентированных 1–5.

📄 runtime.py — Paper (задания 1–5)
Назначение файла

runtime.py отвечает за загрузку и подготовку данных варианта "Форматы бумаги A0–A7" для показа пользователю в Telegram-боте.

Он является runtime-слоем non_generators, связывающим:

JSON-базу → FSM → register_task → UI (overview + вопросы)
🎯 Зачем он нужен

В архитектуре заданий 1–5 используется единая механика:

DB → task_1_5_data → register_task → общая логика отображения

Блок «Бумага» должен быть встроен в эту механику,
а не создавать свою собственную.

runtime.py выполняет три задачи:

1️⃣ Загружает БД

Читает файл:

data/tasks_1_5/paper/tasks_1_5_paper.json
2️⃣ Управляет порядком вариантов

Через FSM хранит:

paper_variant_index

Это позволяет:

выдавать варианты по очереди

не повторять один и тот же вариант

не зависеть от рандома

3️⃣ Приводит JSON к формату task_1_5_data

JSON содержит:

variant
 ├── table_context
 └── questions[]

Но общая механика 1–5 работает с полем:

tasks[]

Поэтому runtime:

берёт questions

преобразует их в tasks

добавляет skill_source_id

формирует универсальный контейнер

📦 Что возвращает
{
    "subtype": "paper",
    "id": "...",
    "image_file": "...",
    "table_context": {...},
    "tasks": [
        {
            "skill_source_id": "paper_q1",
            "text": "...",
            "answer": "..."
        },
        ...
    ]
}

Именно этот формат ожидает:

register_task

система трекинга навыков

общий UI заданий 1–5

🧠 Архитектурный принцип

Paper реализован по схеме:

definitions → validator → build.py → JSON DB → runtime.py → UI

build.py собирает БД

runtime.py работает во время исполнения бота

никакой генерации на лету

полная совместимость с общей механикой 1–5

💡 Почему это важно

Без runtime.py:

register_task не получит skill_source_id

overview не отобразится корректно

механика навыков не будет работать

Paper выпадет из общей архитектуры

С runtime.py блок «Бумага» встроен в систему так же,
как и «Шины».
