📌 ПАМЯТКА
Кеширование file_id для изображений Telegram (Матюня)
Проблема

При отправке изображения через:

photo = FSInputFile(path)
await bot.send_photo(...)

Telegram каждый раз загружает файл заново:

диск → Python → сеть → Telegram сервер

Это вызывало задержку 10–20 секунд при открытии задания (например Q5 в подтипе Печи).

💡 Решение

Мы реализовали кеш file_id Telegram.

Идея:

1️⃣ Первый раз изображение загружается в Telegram.
2️⃣ Telegram возвращает file_id.
3️⃣ Этот file_id сохраняется в памяти.
4️⃣ При следующих отправках используется file_id, а не файл.

Тогда Telegram берёт изображение из своего CDN.

📦 Реализация

Создан модуль:

matunya_bot_final/utils/telegram_file_cache.py
from aiogram.types import FSInputFile
from pathlib import Path

FILE_CACHE = {}

async def send_cached_photo(bot, chat_id, path: Path):
    key = str(path)

    if key in FILE_CACHE:
        return await bot.send_photo(chat_id, FILE_CACHE[key])

    msg = await bot.send_photo(chat_id, FSInputFile(str(path)))
    FILE_CACHE[key] = msg.photo[-1].file_id

    return msg
⚙️ Использование

В focused.py изображение отправляется так:

msg = await send_cached_photo(bot, chat_id, image_path)

await track_existing_message(
    state=state,
    message_id=msg.message_id,
    message_tag=f"focused_task_image_q{question_num}",
    category="focused_assets",
)
🚀 Результат
До	После
17–20 секунд	~1–2 секунды
каждый раз upload	upload только один раз
высокая задержка	Telegram CDN
ℹ️ Особенность текущего кеша

Кеш хранится в памяти бота:

FILE_CACHE = {}

Поэтому:

при первом показе после запуска происходит upload

дальше используется file_id

Это нормально и не влияет на UX.

📈 Плюсы решения

✔ ускоряет отправку изображений
✔ уменьшает сетевую нагрузку
✔ не требует ручного хранения file_id
✔ работает для всех подтипов 1–5 (Paper, Stoves, Apartment и др.)





⚠️ Особенность текущего кеша

Сейчас кеш хранится только в памяти процесса:

FILE_CACHE = {}

Поэтому:

при перезапуске бота кеш очищается

первый показ картинки снова делает upload

далее снова используется file_id

Это нормально и практически не влияет на UX.

🔧 Возможное улучшение — «вечный кеш»

Можно сделать персистентный кеш file_id, чтобы он сохранялся между перезапусками бота.

Для этого FILE_CACHE сохраняется в файл:

matunya_bot_final/data/telegram_file_cache.json

Алгоритм:

При запуске бота загружается JSON с file_id.

Если картинка уже есть в кеше → используется file_id.

Если нет → происходит upload.

Новый file_id записывается в JSON.

Пример:

import json

CACHE_PATH = Path("matunya_bot_final/data/telegram_file_cache.json")

if CACHE_PATH.exists():
    FILE_CACHE = json.loads(CACHE_PATH.read_text())
else:
    FILE_CACHE = {}

# после загрузки новой картинки
FILE_CACHE[key] = file_id
CACHE_PATH.write_text(json.dumps(FILE_CACHE, indent=2))
📈 Плюсы вечного кеша

upload выполняется только один раз за всю жизнь проекта

изображения всегда отправляются через CDN

бот быстрее запускается после рестарта

меньше сетевой нагрузки

🧠 Когда стоит внедрить

Персистентный кеш имеет смысл если:

бот часто перезапускается

используется много изображений

хочется максимальной скорости UX

Для текущего состояния проекта достаточно in-memory кеша, но архитектура уже позволяет легко добавить вечный кеш при необходимости.


🧠 Памятка (на будущее)

matunya_bot_final/docs/telegram_image_acceleration.md

Ускорение отправки изображений Telegram

В проекте Матюня используются изображения для заданий:

paper
stoves
apartments
geometry

Для ускорения работы бота применяется кеширование file_id.

Текущее решение (реализовано)

Используется in-memory cache:

FILE_CACHE = {}

Алгоритм:

1️⃣ первый показ картинки → upload в Telegram
2️⃣ Telegram возвращает file_id
3️⃣ file_id сохраняется в FILE_CACHE
4️⃣ последующие отправки → через CDN

Результат:

запуск	время
первый	10–15 сек
последующие	1–2 сек
Улучшение №1 (вечный кеш)

Можно сохранить file_id в файл:

matunya_bot_final/data/telegram_file_cache.json

При старте бота:

загружается JSON
file_id сразу известен
upload не требуется

Плюсы:

✔ после перезапуска бота нет задержки
✔ меньше сетевой нагрузки
✔ стабильный UX
Улучшение №2 (CDN warmup)

При старте бота можно предварительно загрузить изображения.

Алгоритм:

bot start
→ отправляет картинки в служебный чат
→ получает file_id
→ CDN уже прогрет

Плюсы:

✔ пользователь никогда не ждёт первый upload
✔ изображения открываются мгновенно
Когда внедрять

Когда в проекте появится много изображений:

10+
20+
30+

Тогда рекомендуется реализовать:

вечный кеш + CDN warmup
