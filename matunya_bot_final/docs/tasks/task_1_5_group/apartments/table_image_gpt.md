📋 Короткая инструкция: как сейчас передаются таблицы в GPT

Это можно использовать и для Квартиры, потому что механизм уже универсальный.

1️⃣ Таблица хранится в task_data

В данных задания (validator/build) таблица записывается так:

task_data["table_context"] = {
    "table_text": "... текст таблицы ..."
}

То есть таблица хранится как текст, который видел ученик.

Пример:

Помещение | Площадь
1 | 12
2 | 16
3 | 8
2️⃣ task_1_5_context.py забирает таблицу

В файле:

help_core/dialog_contexts/task_1_5_context.py

мы читаем её так:

table_context = (
    task_data.get("table_context", {}).get("table_text", "")
)
3️⃣ Таблица передаётся в prompt

Дальше она передаётся в prompt builder:

get_task_1_5_dialog_prompt(
    ...
    table_context=table_context,
)
4️⃣ В prompt таблица вставляется как отдельный блок

В task_1_5_dialog_prompts.py:

### ТАБЛИЦА ДАННЫХ (если была в задаче)

{table_block}
5️⃣ Что видит GPT

GPT получает буквально ту же таблицу, что видел ученик.

Поэтому он может:

читать данные

сравнивать значения

использовать их в объяснении

📦 Итоговая цепочка
validator / build
        ↓
task_data["table_context"]
        ↓
task_1_5_context.py
        ↓
table_context
        ↓
prompt
        ↓
GPT видит таблицу
👍 Что важно для подтипа Квартира

Для квартир таблицы будут, например:

Q1

таблица помещений

Q5

таблица стоимости материалов

Обе таблицы можно передавать точно тем же механизмом.

🧠 Маленькая рекомендация

Когда будешь делать Квартиру, лучше сразу придерживаться формата:

table_context = {
    "table_text": "..."
}

Даже если таблица одна строка — это сохранит единый контракт для всех подтипов.


📋 Инструкция: как передаются картинки в GPT (задания 1–5)

Картинки (планировки, схемы и т.д.) передаются в GPT через объект help_image.

1️⃣ Картинка формируется в solver подтипа

В solver (например paper_solver.py, stoves_solver.py, позже apartment_solver.py) создаётся объект:

help_image = {
    "file": "... путь к картинке ...",
    "schema": "... тип схемы ...",
    "params": {... параметры ...},
    "description_for_gpt": "... текстовое описание изображения ..."
}

Пример:

help_image = {
    "file": "matunya_bot_final/non_generators/task_1_5/apartment/assets/task_apartment_plan_01.png",
    "schema": "apartment_plan",
    "params": {
        "scale": "0.4 m",
        "rooms": 8
    },
    "description_for_gpt": (
        "На изображении показан план квартиры, разбитый на клетки. "
        "Каждая клетка соответствует 0,4 м. "
        "Помещения обозначены номерами. "
        "Стены показаны толстыми линиями, двери — разрывами в стенах."
    )
}
2️⃣ Solver возвращает help_image

Solver возвращает:

return {
    "solution_core": solution_core,
    "help_image": help_image
}
3️⃣ help_image сохраняется в state

В обработчике помощи (help_handler_1_5.py) изображение кладётся в FSM:

await state.update_data(
    task_1_5_help_image=help_image
)
4️⃣ task_1_5_context.py забирает описание картинки

В контексте диалога:

help_image = data.get("help_image")
image_context = ""

if isinstance(help_image, dict):
    image_context = help_image.get("description_for_gpt", "")
5️⃣ Описание картинки передаётся в prompt

Далее оно передаётся в prompt builder:

get_task_1_5_dialog_prompt(
    ...
    image_context=image_context,
)
6️⃣ В prompt есть специальный блок

В task_1_5_dialog_prompts.py:

### ОПИСАНИЕ ИЗОБРАЖЕНИЯ (если была картинка)

{image_block}
7️⃣ Что получает GPT

GPT не видит саму картинку, но получает её текстовое описание:

На изображении показан план квартиры.
Каждая клетка равна 0,4 м.
Помещения обозначены номерами.

Поэтому GPT может:

объяснять планировку

ссылаться на комнаты

использовать масштаб

📦 Итоговая цепочка
solver (подтип)
        ↓
help_image
        ↓
state
        ↓
task_1_5_context.py
        ↓
image_context
        ↓
prompt
        ↓
GPT понимает изображение
⚠️ Архитектурное правило проекта

Описание картинки не хранится в task_1_5_context.py,
а остаётся в solver конкретного подтипа.

paper_solver
stoves_solver
apartment_solver

Это сохраняет модульность системы.

🧠 Для подтипа Квартира

В apartment_solver лучше использовать schema:

apartment_plan

и описание примерно такого типа:

План квартиры показан на сетке.
Размер клетки — 0,4 м.
Помещения обозначены номерами.
Двери и окна отмечены условными обозначениями.

Этого достаточно, чтобы GPT корректно ориентировался в планировке.
