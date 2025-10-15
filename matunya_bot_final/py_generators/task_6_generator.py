# gpt/task_templates/task_6/task_6_generator.py

import random
from fractions import Fraction
from typing import Optional, Dict, Any, Callable, Tuple

# Тип для наших "маленьких" генераторов
GeneratorFunc = Callable[[], Tuple[str, str, str]]

# =================================================================
#  вспомогательные функции
# =================================================================

def create_task_object(task_id: str, subtype: str, text: str, answer: str) -> Dict[str, Any]:
    """Собирает финальный JSON-объект для одного задания."""
    return {
        "id": task_id,
        "task_type": "6",
        "subtype": subtype,
        "text": text,
        "answer": str(answer)
    }

def to_mixed_number(f: Fraction) -> str:
    """Преобразует объект Fraction в строку со смешанным числом, если нужно."""
    if f.numerator == 0:
        return "0"
    sign = "-" if f.numerator < 0 else ""
    f = abs(f)
    if f.numerator < f.denominator:
        return f"{sign}{f.numerator}/{f.denominator}"
    else:
        whole = f.numerator // f.denominator
        new_num = f.numerator % f.denominator
        if new_num == 0:
            return f"{sign}{whole}"
        return f"{sign}{whole} {new_num}/{f.denominator}"

# =================================================================
# 14 "маленьких" функций-генераторов
# =================================================================

def _generate_obychnye_drobi() -> Tuple[str, str, str]:
    subtype_key = "обычные_дроби_с_преобразованием"
    n1, d1 = random.randint(1, 10), random.randint(11, 20)
    n2, d2 = random.randint(1, 10), random.randint(11, 20)
    op = random.choice(['+', '-'])
    multiplier = random.randint(2, 10)
    
    f1 = Fraction(n1, d1)
    f2 = Fraction(n2, d2)
    
    text = f"Найдите значение выражения ({n1}/{d1} {op} {n2}/{d2}) · {multiplier}"
    
    if op == '+':
        answer = (f1 + f2) * multiplier
    else:
        answer = (f1 - f2) * multiplier
        
    return subtype_key, text, to_mixed_number(answer)

def _generate_desyatichnye_drobi_v_drobi() -> Tuple[str, str, str]:
    subtype_key = "десятичные_дроби_в_дроби"
    a = round(random.uniform(1, 10), 1)
    b = round(random.uniform(1, 10), 1)
    c = round(random.uniform(1, 10), 1)
    op = random.choice(['+', '-'])
    
    text = f"Найдите значение выражения ({a} {op} {b}) / {c}"
    
    if op == '+':
        answer = (a + b) / c
    else:
        answer = (a - b) / c
        
    return subtype_key, text, str(round(answer, 2))

def _generate_chislitel_nesokratimoy() -> Tuple[str, str, str]:
    subtype_key = "числитель_несократимой_дроби"
    d1, d2 = random.sample(range(5, 25), 2)
    n1, n2 = random.randint(1, d1 - 1), random.randint(1, d2 - 1)
    
    f1 = Fraction(n1, d1)
    f2 = Fraction(n2, d2)
    answer_fraction = f1 + f2
    
    text = (f"Найдите значение выражения {n1}/{d1} + {n2}/{d2}. "
            "Представьте результат в виде несократимой обыкновенной дроби. "
            "В ответ запишите числитель этой дроби.")
            
    return subtype_key, text, str(answer_fraction.numerator)

def _generate_otricatelnye_osnovaniya() -> Tuple[str, str, str]:
    subtype_key = "отрицательные_основания_в_степени"
    c1 = round(random.uniform(0.1, 0.9), 1)
    c2 = random.randint(2, 9)
    p1 = random.randint(2, 4)
    p2 = random.randint(2, 3)
    extra = random.randint(20, 100)
    
    superscript = {'2': '²', '3': '³', '4': '⁴'}
    
    text = f"Найдите значение выражения {c1} · (-10){superscript[str(p1)]} + {c2} · (-10){superscript[str(p2)]} + {extra}"
    answer = c1 * ((-10)**p1) + c2 * ((-10)**p2) + extra
    
    return subtype_key, text, str(answer)

def _generate_tri_drobi() -> Tuple[str, str, str]:
    subtype_key = "три_обычные_дроби_без_скобок"
    d1, d2, d3 = random.sample(range(5, 20), 3)
    n1, n2, n3 = random.randint(1, d1-1), random.randint(1, d2-1), random.randint(1, d3-1)
    
    f1, f2, f3 = Fraction(n1, d1), Fraction(n2, d2), Fraction(n3, d3)
    answer = f1 + f2 - f3
    
    text = f"Найдите значение выражения {n1}/{d1} + {n2}/{d2} - {n3}/{d3}"
    return subtype_key, text, to_mixed_number(answer)

def _generate_desyatichnye_s_otricatelnymi() -> Tuple[str, str, str]:
    subtype_key = "десятичные_числа_с_отрицательными_множителями"
    a = round(random.uniform(1, 10), 1)
    b = random.randint(2, 9)
    c = round(random.uniform(-10, -1), 1)
    
    text = f"Найдите значение выражения {a} - {b} · ({c})"
    answer = a - b * c
    return subtype_key, text, str(round(answer, 2))

def _generate_drob_s_zadannym_znamenatelem() -> Tuple[str, str, str]:
    # TODO: Реализовать сложную логику, пока это просто сложение дробей
    subtype_key = "дробь_с_заданным_знаменателем"
    d1, d2 = random.sample(range(10, 30, 5), 2)
    n1, n2 = random.randint(1, d1-1), random.randint(1, d2-1)
    
    f1 = Fraction(n1, d1)
    f2 = Fraction(n2, d2)
    answer_fraction = f1 + f2
    
    text = (f"Найдите значение выражения {n1}/{d1} + {n2}/{d2}. "
            "Представьте результат в виде несократимой обыкновенной дроби. "
            "В ответ запишите числитель этой дроби.")
    return subtype_key, text, str(answer_fraction.numerator)

def _generate_smeshannye_chisla() -> Tuple[str, str, str]:
    subtype_key = "смешанные_числа"
    w1 = random.randint(1, 5)
    n1, d1 = random.randint(1, 5), random.randint(6, 10)
    w2 = random.randint(1, 5)
    n2, d2 = random.randint(1, 5), random.randint(6, 10)
    
    f1 = w1 + Fraction(n1, d1)
    f2 = w2 + Fraction(n2, d2)
    answer = f1 - f2
    
    text = f"Найдите значение выражения {w1} {n1}/{d1} - {w2} {n2}/{d2}"
    return subtype_key, text, to_mixed_number(answer)

def _generate_drob_v_drobi() -> Tuple[str, str, str]:
    subtype_key = "дробь_в_дроби"
    d1, d2 = random.sample(range(10, 40, 5), 2)
    n = random.randint(1, 5)
    
    f1 = Fraction(1, d1)
    f2 = Fraction(1, d2)
    answer = n / (f1 + f2)
    
    text = f"Найдите значение выражения {n} / (1/{d1} + 1/{d2})"
    return subtype_key, text, to_mixed_number(answer)

def _generate_drob_v_stepeni() -> Tuple[str, str, str]:
    subtype_key = "дробь_в_степени"
    n1, d1 = random.randint(1, 5), random.randint(6, 10)
    n2, d2 = random.randint(1, 5), random.randint(6, 10)
    
    f1 = Fraction(n1, d1)
    f2 = Fraction(n2, d2)
    answer = f1**2 - f2
    
    text = f"Найдите значение выражения ({n1}/{d1})² - {n2}/{d2}"
    return subtype_key, text, to_mixed_number(answer)

def _generate_stepeni_s_desyatichnymi() -> Tuple[str, str, str]:
    subtype_key = "степени_с_десятичными_множителями"
    c1, p1 = random.randint(2, 9), random.randint(2, 4)
    c2, p2 = random.randint(11, 20), random.randint(-5, -2)
    
    text = f"Найдите значение выражения ({c1}·10{chr(178+p1-2)})³ · ({c2}·10{chr(8314+abs(p2))})"
    answer = ((c1 * 10**p1)**3) * (c2 * 10**p2)
    return subtype_key, text, str(answer)

def _generate_smeshannye_drobi_v_vyrazhenii() -> Tuple[str, str, str]:
    subtype_key = "смешанные_дроби_в_выражении"
    n, d = random.choice([(1, 4), (1, 2), (3, 4)])
    dec = round(random.uniform(0.1, 0.9), 2)
    
    f = Fraction(n, d)
    answer = float(f) + dec
    
    text = f"Найдите значение выражения {n}/{d} + {str(dec).replace('.', ',')}"
    return subtype_key, text, str(round(answer, 3)).replace('.', ',')

def _generate_desyatichnye_iz_stepeney() -> Tuple[str, str, str]:
    subtype_key = "десятичные_из_степеней"
    c1, c2, c3 = random.randint(1,9), random.randint(1,9), random.randint(1,9)
    
    text = f"Найдите значение выражения {c1} · 10⁻¹ + {c2} · 10⁻² + {c3} · 10⁻⁴"
    answer = c1 * 10**-1 + c2 * 10**-2 + c3 * 10**-4
    return subtype_key, text, str(answer)

def _generate_stepeni_s_odinak_osnovaniem() -> Tuple[str, str, str]:
    subtype_key = "степени_с_одинаковым_основанием"
    base = random.randint(2, 5)
    p1, p2, p3 = random.sample(range(3, 12), 3)
    
    text = f"Найдите значение выражения ({base}⁸ · {base}⁵) / {base}⁹" # Пример из PDF
    answer = (base**8 * base**5) / base**9
    return subtype_key, text, str(answer)

# =================================================================
# "Карта дирижера"
# =================================================================
GENERATOR_MAP: Dict[str, GeneratorFunc] = {
    "обычные_дроби_с_преобразованием": _generate_obychnye_drobi,
    "десятичные_дроби_в_дроби": _generate_desyatichnye_drobi_v_drobi,
    "числитель_несократимой_дроби": _generate_chislitel_nesokratimoy,
    "отрицательные_основания_в_степени": _generate_otricatelnye_osnovaniya,
    "три_обычные_дроби_без_скобок": _generate_tri_drobi,
    "десятичные_числа_с_отрицательными_множителями": _generate_desyatichnye_s_otricatelnymi,
    "дробь_с_заданным_знаменателем": _generate_drob_s_zadannym_znamenatelem,
    "смешанные_числа": _generate_smeshannye_chisla,
    "дробь_в_дроби": _generate_drob_v_drobi,
    "дробь_в_степени": _generate_drob_v_stepeni,
    "степени_с_десятичными_множителями": _generate_stepeni_s_desyatichnymi,
    "смешанные_дроби_в_выражении": _generate_smeshannye_drobi_v_vyrazhenii,
    "десятичные_из_степеней": _generate_desyatichnye_iz_stepeney,
    "степени_с_одинаковым_основанием": _generate_stepeni_s_odinak_osnovaniem,
}

# =================================================================
# Главная функция-"дирижер"
# =================================================================
async def generate_task_6_by_subtype(subtype_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Выбирает и запускает нужный генератор для Задания 6.
    Если subtype_key не указан, выбирает случайный.
    """
    if subtype_key is None:
        subtype_key = random.choice(list(GENERATOR_MAP.keys()))

    generator_func = GENERATOR_MAP.get(subtype_key)

    if generator_func is None:
        print(f"ОШИБКА: Неизвестный подтип задания 6: {subtype_key}")
        return None

    result = generator_func()

    return {
        "subtype": result[0],
        "text": result[1],
        "answer": result[2]
    }