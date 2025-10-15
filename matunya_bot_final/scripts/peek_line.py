from __future__ import annotations

from pathlib import Path
text = Path('task_generators/task_12/task_12_validator.py').read_text(encoding='utf-8')
start = text.index('                re.compile')
for _ in range(4):
    line_end = text.index('\n', start)
    print(repr(text[start:line_end]))
    start = line_end + 1
