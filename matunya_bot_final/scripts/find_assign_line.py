from __future__ import annotations
from pathlib import Path
lines = Path('task_generators/task_12/task_12_validator.py').read_text(encoding='utf-8').splitlines()
for line in lines:
    if '({self._number_pattern})\\s*м' in line:
        print(repr(line))
