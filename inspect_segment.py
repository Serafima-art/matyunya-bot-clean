from pathlib import Path
text = Path('generate_new_theory_dispatcher.py').read_text(encoding='utf-8')
start = text.index('unavailable_text = (')
end = text.index(')\n\n\nasync def delete_message_after_delay', start)
segment = text[start:end]
print(segment.encode('unicode_escape').decode())
