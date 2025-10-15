from __future__ import annotations
from pathlib import Path
lines = Path('task_generators/task_12/task_12_validator.py').read_text(encoding='utf-8').splitlines()
for idx, line in enumerate(lines):
    if 'Вычислите' in line:
        print(idx, line)
