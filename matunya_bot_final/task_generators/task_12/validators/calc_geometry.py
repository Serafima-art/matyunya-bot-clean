import re
import math
from ..common import NUM, to_float, PI, format_answer
from ..common import to_float, grab_labeled_number

# 1) area_triangle_ah: S = 1/2 · a · h
def _validate_area_triangle_ah(task: dict) -> bool:
    """Валидирует S = ½ah, используя стандартные утилиты."""
    text, answer_str = task.get("text"), task.get("answer")
    if not text or answer_str is None: return False

    # Используем стандартные NUM и _to_float
    numbers_str = re.findall(NUM, text)
    if len(numbers_str) != 2: return False
    
    val1, val2 = to_float(numbers_str[0]), to_float(numbers_str[1])
    
    # Логика определения и вычисления остается той же, но с _to_float
    correct_answer = 0.0
    if "найдите площадь S" in text:
        correct_answer = 0.5 * val1 * val2
    elif "найдите сторону a" in text:
        S, h = val1, val2
        if h == 0: return False
        correct_answer = (2 * S) / h
    elif "найдите высоту h" in text:
        S, a = val1, val2
        if a == 0: return False
        correct_answer = (2 * S) / a
    else:
        return False

    return abs(to_float(answer_str) - correct_answer) < 1e-9

# 2) area_triangle_sides_sin: S = 1/2 · b · c · sinα
def _validate_area_triangle_sides_sin(data: dict) -> bool:
    text = data["text"]

    # b и c — целые
    mb = re.search(r"\bb\s*=\s*(\d+)", text)
    mc = re.search(r"\bc\s*=\s*(\d+)", text)
    # sinα или sina: десятичное число с запятой ИЛИ точкой; не захватываем завершающую пунктуацию
    msin = re.search(r"sin[αa]?\s*=\s*([0-9]+(?:[.,][0-9]+)?)\b", text)

    if not (mb and mc and msin):
        raise ValueError("Не удалось распарсить параметры b, c или sinα в тексте задачи")

    b = int(mb.group(1))
    c = int(mc.group(1))
    sin_alpha = float(msin.group(1).replace(",", "."))

    S = 0.5 * b * c * sin_alpha
    return data["answer"] == format_answer(S)

# 3) area_triangle_inscribed_circle: S = (a+b+c)·r/2
def _validate_area_triangle_inscribed_circle(task: dict) -> bool:
    """Валидирует задачу S = (a+b+c)·r/2, используя grab_labeled_number."""
    text, answer_str = task.get("text"), task.get("answer")
    if not text or answer_str is None: return False

    S = grab_labeled_number(text, labels=['S'])
    a = grab_labeled_number(text, labels=['a'])
    b = grab_labeled_number(text, labels=['b'])
    c = grab_labeled_number(text, labels=['c'])
    r = grab_labeled_number(text, labels=['r'])
    
    correct_answer = 0.0
    
    # --- ИСПРАВЛЕНИЕ ЗДЕСЬ ---
    # Добавлена логика для поиска 'a' и исправлены другие проверки
    if a is None and all(x is not None for x in [S, b, c, r]):
        if r == 0: return False
        correct_answer = (2 * S) / r - b - c
    elif b is None and all(x is not None for x in [S, a, c, r]):
        if r == 0: return False
        correct_answer = (2 * S) / r - a - c
    elif c is None and all(x is not None for x in [S, a, b, r]):
        if r == 0: return False
        correct_answer = (2 * S) / r - a - b
    # (можно будет так же добавить поиск S и r, если генератор научится их генерировать)
    else:
        # Если не нашли ровно одну недостающую переменную, считаем формат неверным
        return False

    return abs(to_float(answer_str) - correct_answer) < 1e-9

# 4) area_parallelogram_ah: S = a · h
def _validate_area_parallelogram_ah(task: dict) -> bool:
    """Валидирует S = a·h для прямой и обратной задачи."""
    text, answer_str = task.get("text"), task.get("answer")
    if not text or answer_str is None: return False

    numbers_str = re.findall(NUM, text)
    if len(numbers_str) != 2: return False
    
    val1 = to_float(numbers_str[0])
    val2 = to_float(numbers_str[1])
    
    # --- ИСПРАВЛЕНИЕ ЗДЕСЬ ---
    # Ищем ключевые слова "площадь", "сторону", "высоту" без привязки к "найдите/вычислите"
    text_lower = text.lower()
    
    correct_answer = 0.0
    if "площадь s" in text_lower:
        correct_answer = val1 * val2
    elif "сторону a" in text_lower:
        S, h = val1, val2
        if h == 0: return False
        correct_answer = S / h
    elif "высоту h" in text_lower:
        S, a = val1, val2
        if a == 0: return False
        correct_answer = S / a
    else:
        return False

    return abs(to_float(answer_str) - correct_answer) < 1e-9

# 5) area_parallelogram_ab_sin: S = a · b · sin α
def _validate_area_parallelogram_ab_sin(task: dict) -> bool:
    """Валидирует S = a·b·sin α."""
    text, answer_str = task.get("text"), task.get("answer")
    if not text or answer_str is None: return False

    # В тексте всегда ровно три числа: две стороны и синус.
    numbers_str = re.findall(NUM, text)
    if len(numbers_str) != 3: return False
    
    try:
        a = to_float(numbers_str[0])
        b = to_float(numbers_str[1])
        sin_alpha = to_float(numbers_str[2])
    except (ValueError, IndexError):
        return False

    correct_answer = a * b * sin_alpha
    return abs(to_float(answer_str) - correct_answer) < 1e-9

# 6) area_rhombus_d1d2: S = ½·d₁·d₂
def _validate_area_rhombus_d1d2(task: dict) -> bool:
    text, answer_str = task.get("text"), task.get("answer")
    if not text or answer_str is None: return False

    # --- ИСПРАВЛЕНИЕ ЗДЕСЬ ---
    # Добавляем в метки варианты с HTML-тегами
    S = grab_labeled_number(text, labels=['S', 'площадь ромба'])
    d1 = grab_labeled_number(text, labels=['d<sub>1</sub>', 'd₁', 'd1'])
    d2 = grab_labeled_number(text, labels=['d<sub>2</sub>', 'd₂', 'd2'])
    
    correct_answer = 0.0
    
    if S is None and d1 is not None and d2 is not None:
        correct_answer = 0.5 * d1 * d2
    elif d1 is None and S is not None and d2 is not None:
        if d2 == 0: return False
        correct_answer = (2 * S) / d2
    elif d2 is None and S is not None and d1 is not None:
        if d1 == 0: return False
        correct_answer = (2 * S) / d1
    else:
        return False

    return abs(to_float(answer_str) - correct_answer) < 1e-9

# 7) area_trapezoid_bases_h: S = (a+b)h/2
def _validate_area_trapezoid_bases_h(task: dict) -> bool:
    """Валидирует S = (a+b)h/2 для прямой и обратных задач."""
    text, answer_str = task.get("text"), task.get("answer")
    if not text or answer_str is None: return False

    text_lower = text.lower()
    
    # --- ИСПРАВЛЕНИЕ ЗДЕСЬ ---
    # Добавляем скобки вокруг NUM, чтобы "захватить" только число, а не единицы измерения
    nums_str = re.findall(f"({NUM})" + r'\s*(?:м²|м)', text)
    if len(nums_str) != 3: return False

    nums = [to_float(s) for s in nums_str]
    
    correct_answer = 0.0
    
    # ... (вся остальная логика остается без изменений) ...
    if "найди площадь" in text_lower:
        a, b, h = nums[0], nums[1], nums[2]
        correct_answer = (a + b) * h / 2
    elif "найди высоту" in text_lower:
        a, b, S = nums[0], nums[1], nums[2]
        if (a + b) == 0: return False
        correct_answer = (2 * S) / (a + b)
    elif "найди основание a" in text_lower:
        b, h, S = nums[0], nums[1], nums[2]
        if h == 0: return False
        correct_answer = (2 * S) / h - b
    else:
        return False

    return abs(to_float(answer_str) - correct_answer) < 1e-9

# 8) area_quadrilateral_d1d2_sin_S: S = ½d₁d₂sinα
def _validate_area_quadrilateral_d1d2_sin_S(task: dict) -> bool:
    """Валидирует S = ½d₁d₂sinα для прямой и обратных задач."""
    text, answer_str = task.get("text"), task.get("answer")
    if not text or answer_str is None: return False

    S = grab_labeled_number(text, labels=['S'])
    d1 = grab_labeled_number(text, labels=['d<sub>1</sub>', 'd₁', 'd1'])
    d2 = grab_labeled_number(text, labels=['d<sub>2</sub>', 'd₂', 'd2'])
    
    # sin α может быть без метки 'sin α =', ищем его как простое число, если нужно
    sin_alpha = grab_labeled_number(text, labels=['sin α'])
    if sin_alpha is None:
        # Если не нашли по метке, ищем как последнее число в тексте
        all_nums = re.findall(NUM, text)
        if all_nums:
            possible_sin = to_float(all_nums[-1])
            if possible_sin in [0.5, 1.0]:
                sin_alpha = possible_sin
    
    correct_answer = 0.0
    
    if S is None and all(x is not None for x in [d1, d2, sin_alpha]):
        correct_answer = 0.5 * d1 * d2 * sin_alpha
    elif d1 is None and all(x is not None for x in [S, d2, sin_alpha]):
        if d2 * sin_alpha == 0: return False
        correct_answer = (2 * S) / (d2 * sin_alpha)
    elif d2 is None and all(x is not None for x in [S, d1, sin_alpha]):
        if d1 * sin_alpha == 0: return False
        correct_answer = (2 * S) / (d1 * sin_alpha)
    else:
        return False

    return abs(to_float(answer_str) - correct_answer) < 1e-9

# 9) bisector_length_equal_legs: l_a = √(b² - (a/2)²)
def _validate_bisector_length_equal_legs(task: dict) -> bool:
    """
    Валидирует биссектрису в равнобедренном треугольнике по теореме Пифагора.
    """
    text, answer_str = task.get("text"), task.get("answer")
    if not text or answer_str is None: return False

    # В тексте всегда два числа. Простой поиск здесь надежен.
    numbers_str = re.findall(NUM, text)
    if len(numbers_str) != 2: return False
    
    val1, val2 = to_float(numbers_str[0]), to_float(numbers_str[1])

    # Определяем, что есть что. Боковая сторона 'b' всегда больше половины
    # основания 'a', поэтому 'b' будет больше, чем 'a'.
    # Но для надежности лучше найти их по ключевым словам.
    
    # Ищем число после фразы "боковая сторона"
    b_match = re.search(r"боковая сторона(?:.+?)\s*(" + NUM + r")", text)
    # Ищем число после фразы "основание"
    a_match = re.search(r"основание(?:.+?)\s*(" + NUM + r")", text)

    if not b_match or not a_match:
        # Если не нашли по словам, попробуем по размеру (боковая > основания)
        if val1 > val2:
            b, a = val1, val2
        else:
            a, b = val1, val2
    else:
        b = to_float(b_match.group(1))
        a = to_float(a_match.group(1))
        
    # Проверка на корректность треугольника
    if b <= a / 2: return False

    # Вычисляем ответ по теореме Пифагора
    correct_answer = math.sqrt(b**2 - (a / 2)**2)
    
    return abs(to_float(answer_str) - correct_answer) < 1e-9

# 10) bisector_length_general: l_a = (2/(b+c))√(bcp(p-a))
def _validate_bisector_length_general(task: dict) -> bool:
    text, answer_str = task.get("text"), task.get("answer")
    if not text or answer_str is None: return False

    a = grab_labeled_number(text, labels=['a'])
    b = grab_labeled_number(text, labels=['b'])
    c = grab_labeled_number(text, labels=['c'])
    if a is None or b is None or c is None: return False
    
    if (b + c) == 0: return False

    # Считаем квадрат биссектрисы
    la_squared = b*c - (a**2 * b * c) / ((b+c)**2)
    if la_squared < 0: return False
    
    correct_answer = math.sqrt(la_squared)
    
    return abs(to_float(answer_str) - correct_answer) < 1e-9