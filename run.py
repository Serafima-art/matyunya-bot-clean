import os
import sys
import asyncio

# --- ★★★ НАШЕ ЛЕКАРСТВО ★★★ ---

# 1. Добавляем корневую папку проекта в пути поиска Python
# Это решает все проблемы с импортами (аналог PYTHONPATH)
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 2. Устанавливаем кодировку UTF-8 (аналог PYTHONIOENCODING)
# Это решает проблемы с русскими буквами в Windows
# (Проверяем, нужно ли это, чтобы не конфликтовать с другими ОС)
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

# --- КОНЕЦ ЛЕКАРСТВА ---


# Теперь, когда пути настроены, можно безопасно импортировать наш модуль
from matunya_bot_final.main_v2 import main


if __name__ == "__main__":
    print("Матюня запускается...")
    asyncio.run(main())
