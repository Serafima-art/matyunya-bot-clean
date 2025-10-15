from __future__ import annotations

from pathlib import Path

text = Path('task_generators/task_12/task_12_validator.py').read_text(encoding='utf-8')
start = text.index('        assignment_normalisers: list[tuple[re.Pattern[str], str]] = [')
end = text.index('        for regex, replacement in assignment_normalisers:')
print(text[start:end])
print('---BLOCK-END---')
start_fb = text.index('        fallback_patterns: dict[str, list[re.Pattern[str]]] = {')
end_fb = text.index('        }\n\n        fallback_values', start_fb)
print(text[start_fb:end_fb])
