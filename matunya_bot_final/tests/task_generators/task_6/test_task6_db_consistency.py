import json
import re
import pathlib
from rich import print
from rich.table import Table
from fractions import Fraction

DB_PATH = pathlib.Path("matunya_bot_final/data/tasks_6/tasks_6.json")

# --- более гибкие шаблоны ---
EXPECTED_PATTERNS = {
    "common_fractions": {
        "cf_addition_subtraction":  r"\d+\s*/\s*\d+\s*[+\-−]\s*\d+\s*/\s*\d+",
        "multiplication_division":  r"\d+(\s+\d+/\d+)?\s*[·:×*]\s*\d+(/\d+)?",
        "parentheses_operations":   r"\(.+?\)\s*[·:×*]\s*\d+(/\d+)?",
        "complex_fraction":         r"\(.+?\)\s*[:/÷]\s*\(.+?\)",
    },
    "decimal_fractions": {
        "df_addition_subtraction":  r"-?\d+,\d+\s*[+\-−]\s*-?\d+,\d+",
        # добавлены скобки и пробелы вокруг знаков, допускаем двойные скобки
        "linear_operations":        r"\(?-?\d+\)?\s*[·×*]\s*\(?-?\d+,\d+\)?\s*[+\-−]\s*\(?-?\d+,\d+\)?",
        "fraction_structure":       r"\d+(,\d+)?\s*/\s*\(.+?\)",
    },
    "mixed_fractions": {
        "mixed_types_operations":   r"(\d+\s+\d+/\d+|[0-9]+,[0-9]+)",
    },
    "powers": {
        # разрешаем и +, и − между слагаемыми, допускаем пробелы и ⋅/×
        "p_powers_with_fractions":  r"\d+\s*[·×*]\s*\(\d+/\d+\)\s*[²³]\s*([+\-−]\s*\d+\s*[·×*]\s*\d+/\d+)?",
        # теперь разрешаем пробел после 10 и перед степенью
        "p_powers_of_ten":          r"\(\d+\s*[·×*]\s*10\s*[⁰¹²³⁴⁵⁶⁷⁸⁹⁻]*\)\s*[²³]?\s*[·×*]\s*\(\d+\s*[·×*]\s*10\s*[⁰¹²³⁴⁵⁶⁷⁸⁹⁻]*\)",
    },
}

def check_pattern(pattern_id: str, text: str, subtype: str) -> bool:
    regex = EXPECTED_PATTERNS.get(subtype, {}).get(pattern_id)
    if not regex:
        return True
    cleaned = text.replace(" ", "")
    return bool(re.search(regex, cleaned))

def test_task6_db_consistency():
    problems = []
    data = json.loads(DB_PATH.read_text(encoding="utf-8"))

    for task in data:
        pattern = task.get("pattern")
        subtype = task.get("subtype", "")
        text = task.get("question_text", "")
        if not check_pattern(pattern, text, subtype):
            problems.append({
                "id": task.get("id"),
                "pattern": pattern,
                "subtype": subtype,
                "text": text.splitlines()[1] if "\n" in text else text
            })

    if problems:
        table = Table(title="❌ Найдены несоответствия паттернам ОГЭ", show_lines=True)
        table.add_column("ID", style="cyan")
        table.add_column("Subtype", style="magenta")
        table.add_column("Pattern", style="yellow")
        table.add_column("Expression", style="white")
        for p in problems:
            table.add_row(p["id"], p["subtype"], p["pattern"], p["text"])
        print(table)
        raise AssertionError(f"Найдено {len(problems)} несоответствующих заданий.")
    else:
        print("[green]🌿 Всё чисто: база задания №6 соответствует ГОСТ-2026.[/green]")

def test_cf_addition_subtraction_integrity():
    data = json.loads(DB_PATH.read_text(encoding="utf-8"))
    bad_tasks = []
    for t in data:
        if t.get("pattern") != "cf_addition_subtraction":
            continue
        qtext, answer = t.get("question_text", ""), t.get("answer", "")
        expr_match = re.findall(r"(\d+)\s*/\s*(\d+)", qtext)
        if len(expr_match) != 2:
            bad_tasks.append((t["id"], "❌ не найдены две дроби"))
            continue
        (a1,b1),(a2,b2)=[(int(x),int(y)) for x,y in expr_match]
        if a1==b1 or a2==b2:
            bad_tasks.append((t["id"],f"⚠️ единичная дробь {a1}/{b1} или {a2}/{b2}"))
            continue
        op = "+" if "+" in qtext else "−"
        res = Fraction(a1,b1)+Fraction(a2,b2) if op=="+" else Fraction(a1,b1)-Fraction(a2,b2)
        if res<=0:
            bad_tasks.append((t["id"],f"🚫 отрицательный результат {res}"))
            continue
        simp=res.limit_denominator()
        if simp!=res:
            bad_tasks.append((t["id"],f"🔸 дробь сокращаемая: {res}->{simp}"))
            continue
        if str(simp.numerator)!=answer:
            bad_tasks.append((t["id"],f"❌ answer={answer}, должен быть {simp.numerator}"))
    if bad_tasks:
        table=Table(title="❌ Ошибки cf_addition_subtraction",show_lines=True)
        table.add_column("ID",style="cyan")
        table.add_column("Ошибка",style="red")
        for tid,msg in bad_tasks: table.add_row(tid,msg)
        print(table)
        assert False,f"{len(bad_tasks)} некорректных заданий"
    else:
        print("[green]✅ Все задания cf_addition_subtraction корректны![/green]")
