from pathlib import Path
text = Path('matunya_bot_final/help_core/dispatchers/theory_dispatcher.py').read_text(encoding='utf-8')
needle = '?? <b>'
start = text.index(needle)
substr = text[start:start+20]
print(substr.encode('unicode_escape').decode())
