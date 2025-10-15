from __future__ import annotations

from pathlib import Path
import re

text = Path('task_generators/task_12/task_12_validator.py').read_text(encoding='utf-8')
pattern = r're\.compile\(rf"\(\?i\)\\ba\\s\*=\\s\*\({self._number_pattern}\)\(\?:\\s\*м\)\?"\)'
print(bool(re.search(pattern, text)))
