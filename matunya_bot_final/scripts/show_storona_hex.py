from __future__ import annotations
from pathlib import Path
lines = Path('task_generators/task_12/task_12_validator.py').read_text(encoding='utf-8').splitlines()
for line in lines:
    if 'сторона b' in line:
        print([hex(ord(ch)) for ch in line])
        break
