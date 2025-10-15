from __future__ import annotations
from pathlib import Path
line = Path('task_generators/task_12/task_12_validator.py').read_text(encoding='utf-8').splitlines()[133]
print([hex(ord(ch)) for ch in line])
