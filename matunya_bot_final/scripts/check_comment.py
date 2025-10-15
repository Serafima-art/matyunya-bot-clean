from __future__ import annotations
from pathlib import Path
text = Path('task_generators/task_12/task_12_validator.py').read_text(encoding='utf-8')
needle = '# Allow both "Найдите" and "Определите" commands by normalising to the template wording.'
print(needle in text)
