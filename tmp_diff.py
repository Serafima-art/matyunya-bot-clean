import difflib
from pathlib import Path

path = Path('matunya_bot_final/handlers/parts_handlers.py')
new = path.read_text(encoding='utf-8').splitlines(True)
orig = new.copy()
for i, line in enumerate(orig):
    if line.strip().startswith('__all__'):
        orig[i] = '__all__ = ("router", "send_parts_choice")\n'
        break
print(''.join(difflib.unified_diff(orig, new, fromfile='a/matunya_bot_final/handlers/parts_handlers.py', tofile='b/matunya_bot_final/handlers/parts_handlers.py')))
