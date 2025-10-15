import sys
from pathlib import Path

# Автоматически ищем каталог проекта "matunya_bot_final"
current = Path(__file__).resolve()
for parent in current.parents:
    if parent.name == "matunya_bot_final":
        PROJECT_ROOT = parent
        break
else:
    raise RuntimeError("Каталог matunya_bot_final не найден в пути")

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

print("[DEBUG] PROJECT_ROOT autodetected:", PROJECT_ROOT)