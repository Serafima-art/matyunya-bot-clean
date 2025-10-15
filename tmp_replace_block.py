# -*- coding: utf-8 -*-
from pathlib import Path

path = Path('matunya_bot_final/handlers/callbacks/task_handlers/group_1_5/task_1_5_router.py')
text = path.read_text(encoding='utf-8')

start = text.find('TASK_1_5_SUBTYPES =')
if start == -1:
    raise SystemExit('start marker not found')
nav_marker = '\n# =================================================================\n# Обработчик навигации по карусели'
end = text.find(nav_marker, start)
if end == -1:
    raise SystemExit('navigation marker not found')

replacement = '''TASK_1_5_SUBTYPES = ["apartment", "tires", "plot", "bath"]\nSUBTYPES_META = {\n    "apartment": {"name": "🏠 Квартира", "available": False},\n    "tires": {"name": "🚗 Шины", "available": True},\n    "plot": {"name": "🌱 Участок", "available": False},\n    "bath": {"name": "🔥 Печи", "available": False}\n}\n\n\ndef _build_carousel_text(subtype_key: str) -> str:\n    """Формирует текст карусели с учётом доступности подтипа."""\n    text = generate_task_1_5_overview_text(TASK_1_5_SUBTYPES, subtype_key)\n\n    if not SUBTYPES_META.get(subtype_key, {}).get("available", False):\n        text_lines = text.split('\\n')\n        text = '\\n'.join(text_lines[:-2]) + "\\n\\n🚧 Этот подтип находится в разработке.\\nПока доступны подтипы: Шины."\n\n    return text\n\n\n# =================================================================\n# ОБРАБОТЧИК НАВИГАЦИИ ПО КАРУСЕЛИ (БЕЗ ИЗМЕНЕНИЙ)\n# =================================================================\n'''

text = text[:start] + replacement + text[end + len('\n# =================================================================\n# Обработчик навигации по карусели'):]
# we removed same comment, ensure remainder includes proper comment
text = text.replace('# ОБРАБОТЧИК НАВИГАЦИИ ПО КАРУСЕЛИ (БЕЗ ИЗМЕНЕНИЙ)\n# =================================================================\n# Обновленный хендлер навигации\n', '# ОБРАБОТЧИК НАВИГАЦИИ ПО КАРУСЕЛИ (БЕЗ ИЗМЕНЕНИЙ)\n# =================================================================\n# Обновленный хендлер навигации\n', 1)

path.write_text(text, encoding='utf-8')
