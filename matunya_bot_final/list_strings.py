import re
from pathlib import Path
text = Path('matunya_bot_final/help_core/dispatchers/theory_dispatcher.py').read_text(encoding='utf-8')
pattern = r'([\"\"][^\"\
]*?\ufffd[^\"\
]*?[\"\"])'
strings = re.findall(pattern, text)
print(len(strings))
for s in strings:
    print(s.encode('unicode_escape').decode())
