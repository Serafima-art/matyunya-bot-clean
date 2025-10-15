import re
from pathlib import Path
text = Path('matunya_bot_final/help_core/dispatchers/theory_dispatcher.py').read_text(encoding='utf-8')
pattern = r'([\"\"][^\"\
]*?\ufffd[^\"\
]*?[\"\"])'
strings = re.findall(pattern, text)
Path('matunya_bot_final/strings_dump.txt').write_text('\n'.join(s.encode('unicode_escape').decode() for s in strings), encoding='utf-8')
print(len(strings))
