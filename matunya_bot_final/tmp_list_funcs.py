import ast
from pathlib import Path
path = Path('matunya_bot_final/help_core/dispatchers/theory_dispatcher.py')
text = path.read_text(encoding='utf-8').lstrip('\ufeff').replace('parse_mode=\\"HTML\\"', 'parse_mode="HTML"')
mod = ast.parse(text)
for node in mod.body:
    if isinstance(node, ast.FunctionDef):
        print(node.name)
