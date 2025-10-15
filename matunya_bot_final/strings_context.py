import re
from pathlib import Path
path = Path('matunya_bot_final/help_core/dispatchers/theory_dispatcher.py')
text = path.read_text(encoding='utf-8')
pattern = r'([\"\"][^\"\
]*?\ufffd[^\"\
]*?[\"\"])'
results = []
for match in re.finditer(pattern, text):
    s = match.group(1)
    line_no = text.count('\n', 0, match.start()) + 1
    snippet = text[match.start()-40:match.end()+40]
    results.append((line_no, s, snippet))

with Path('matunya_bot_final/strings_with_context.txt').open('w', encoding='utf-8') as fh:
    for line_no, s, snippet in results:
        fh.write(f'Line {line_no}: {s.encode("unicode_escape").decode()}\n')
        fh.write(snippet.replace('\n', '\\n') + '\n')
        fh.write('-'*60 + '\n')
print(len(results))
