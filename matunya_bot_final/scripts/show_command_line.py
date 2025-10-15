from __future__ import annotations
from pathlib import Path
lines = Path('task_generators/task_12/task_12_validator.py').read_text(encoding='utf-8').splitlines()
for line in lines:
    if 'command_regex = re.compile' in line:
        print(line)
