import random
import math
from typing import Optional, Dict, Any, Callable, Tuple

# Импортируем нужные утилиты и константы из общего файла
from ..common import format_answer, PI

# ─────────────────────────────────────────────────────────────────────────────
# 1) Площадь треугольника через сторону и высоту: S = 1/2 · a · h
#    Подбираем S и a так, чтобы h было целым.
# ─────────────────────────────────────────────────────────────────────────────
def _generate_area_triangle_ah() -> dict:
    """
    Генерирует задачу на вычисление площади, стороны или высоты треугольника
    по формуле S = ½ah.
    """
    subtype = "area_triangle_ah"
    plot_id = "area_triangle_ah"

    # Случайно выбираем, что будем искать
    target_variable = random.choice(['S', 'a', 'h'])

    if target_variable == 'S':
        # Ищем площадь S. Генерируем a и h.
        # Делаем h четным, чтобы S всегда было целым.
        a = random.randint(5, 25)
        h = random.randint(4, 20) * 2
        S = (a * h) // 2
        
        answer = S
        target_text = "площадь S"
        known_text = f"сторона a равна {a} см, а высота h, проведённая к этой стороне, — {h} см"
        params = {"a": a, "h": h}
        hidden_params = {"_hidden_S": S}

    elif target_variable == 'a':
        # Ищем сторону a. Генерируем S и h.
        # Логика гарантирует, что a = (2*S)/h будет целым.
        while True:
            S = random.randint(20, 150)
            divisors = [d for d in range(5, 41) if (2 * S) % d == 0]
            if divisors:
                break
        
        h = random.choice(divisors)
        a = (2 * S) // h

        answer = a
        target_text = "сторону a"
        known_text = f"площадь треугольника S равна {S} см², а высота h, проведённая к этой стороне, — {h} см"
        params = {"S": S, "h": h}
        hidden_params = {"_hidden_a": a}

    else:  # target_variable == 'h'
        # Ищем высоту h. Генерируем S и a.
        # Логика гарантирует, что h = (2*S)/a будет целым.
        while True:
            S = random.randint(20, 150)
            divisors = [d for d in range(5, 41) if (2 * S) % d == 0]
            if divisors:
                break
        
        a = random.choice(divisors)
        h = (2 * S) // a

        answer = h
        target_text = "высоту h"
        known_text = f"площадь треугольника S равна {S} см², а сторона a — {a} см"
        params = {"S": S, "a": a}
        hidden_params = {"_hidden_h": h}

    # Собираем текст задачи по новому "Золотому Стандарту"
    intro_text = (
        "Площадь треугольника (в см²) можно вычислить по формуле S = ½ah, "
        "где a — сторона треугольника, h — высота, проведённая к этой стороне (в см)."
    )
    text = (
        f"{intro_text}\n"
        f"Пользуясь этой формулой, найдите {target_text}, если известно, "
        f"что {known_text}."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(answer),
        "params": params,
        "hidden_params": hidden_params,
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 2) Площадь треугольника через две стороны и sin угла: S = 1/2 · b · c · sin(α)
#    Чтобы S было целым, берём sin(α) = 1 или 1/2 и подбираем b, c.
# ─────────────────────────────────────────────────────────────────────────────
def _generate_area_triangle_sides_sin() -> dict:
    subtype = "area_triangle_sides_sin"
    plot_id = "area_triangle_sides_sin"

    sin_alpha = random.choice([1, 0.5])   # sin 90° или sin 30°
    if sin_alpha == 1:
        # S = 1/2 * b * c → берём b*c кратно 2
        b = random.choice([8, 10, 12, 14, 16, 18, 20])
        c = random.choice([6, 8, 10, 12, 14, 16])
        S = (b * c) // 2
        sin_text = "1"
    else:
        # S = 1/2 * b * c * 1/2 = b*c/4 → b*c кратно 4
        b = random.choice([8, 12, 16, 20, 24, 28])
        c = random.choice([8, 12, 16, 20, 24, 28])
        S = (b * c) // 4
        sin_text = "0,5"

    text = (
        "Площадь треугольника вычисляется по формуле S = ½·b·c·sinα. "
        f"Найди площадь S, если b = {b} см, c = {c} см, а sinα = {sin_text}."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(S),
        "params": {"b": b, "c": c, "sinα": sin_text},
        "hidden_params": {"_hidden_S": S},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 3) Площадь треугольника через радиус вписанной окружности: S = (a+b+c)·r/2
#    Берём p и r так, чтобы S было целым.
# ─────────────────────────────────────────────────────────────────────────────
def _generate_area_triangle_inscribed_circle() -> dict:
    """
    Генерирует задачу на поиск стороны треугольника по формуле S = (a+b+c)·r/2.
    """
    # 1. Генерируем "красивый" треугольник со сторонами a, b, c
    while True:
        a = random.randint(5, 15)
        b = random.randint(a + 1, 20) # b > a для разнообразия
        # Генерируем c так, чтобы оно было целым и удовлетворяло нер-ву треугольника
        c_min = b - a + 1
        c_max = a + b - 1
        if c_min >= c_max: continue
        c = random.randint(c_min, c_max)
        break
    
    # 2. Находим полупериметр и подбираем "красивый" радиус
    p = (a + b + c) / 2
    r_variants = [r for r in range(2, 6) if (p * r).is_integer()]
    if not r_variants: r_variants = [2] # Запасной вариант
    r = random.choice(r_variants)
    
    # 3. Считаем площадь
    S = p * r

    # 4. Случайно выбираем, какую сторону будем искать (a, b или c)
    target_side_label = random.choice(['a', 'b', 'c'])
    
    if target_side_label == 'a':
        answer = a
        known_vars = f"S = {format_answer(S)}, b = {b}, c = {c}, r = {r}"
    elif target_side_label == 'b':
        answer = b
        known_vars = f"S = {format_answer(S)}, a = {a}, c = {c}, r = {r}"
    else: # target_side_label == 'c'
        answer = c
        known_vars = f"S = {format_answer(S)}, a = {a}, b = {b}, r = {r}"

    intro_text = (
        "Площадь треугольника можно вычислить по формуле S = (a+b+c)·r/2, "
        "где a, b, c — длины сторон треугольника, r — радиус вписанной окружности."
    )
    text = (
        f"{intro_text}\n"
        f"Вычислите длину стороны {target_side_label}, если {known_vars}."
    )

    return {
        "subtype": "area_triangle_inscribed_circle",
        "plot_id": "area_triangle_inscribed_circle",
        "text": text,
        "answer": format_answer(answer),
        "params": {"S": S, "a": a, "b": b, "c": c, "r": r, "_find": target_side_label},
        "hidden_params": {"_hidden_answer": answer},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 4) Площадь параллелограмма через сторону и высоту: S = a · h
# ─────────────────────────────────────────────────────────────────────────────
def _generate_area_parallelogram_ah() -> dict:
    """
    Генерирует задачу на S = a·h (поиск S, a или h) с целыми и десятичными числами.
    """
    # 1. Случайно выбираем, что будем искать
    target_var = random.choice(['S', 'a', 'h'])
    
    # 2. Генерируем "красивые" числа, включая десятичные
    def _get_nice_number(is_side=True):
        """Генерирует целое или десятичное число (с .5)"""
        if is_side: # Стороны и высоты делаем поменьше
            return random.randint(3, 20) + random.choice([0, 0.5])
        else: # Площадь делаем побольше
            return random.randint(20, 200) + random.choice([0, 0.5])

    # 3. Генерируем параметры в зависимости от того, что ищем
    if target_var == 'S':
        a = _get_nice_number()
        h = _get_nice_number()
        S = a * h
        answer = S
        target_text = "площадь S"
        known_text = f"сторона a равна {format_answer(a)} м, а высота h, проведённая к этой стороне, — {format_answer(h)} м"
        
    else: # Ищем 'a' или 'h' (обратная задача)
        # Генерируем ответ и одну из сторон, чтобы получить "красивую" площадь
        known_side = _get_nice_number()
        answer = _get_nice_number()
        S = known_side * answer
        
        if target_var == 'a':
            a, h = answer, known_side
            target_text = "сторону a"
            known_text = f"площадь параллелограмма S равна {format_answer(S)} м², а высота h, проведённая к этой стороне, — {format_answer(h)} м"
        else: # target_var == 'h'
            a, h = known_side, answer
            target_text = "высоту h"
            known_text = f"площадь параллелограмма S равна {format_answer(S)} м², а сторона a — {format_answer(a)} м"
            
    # 4. Собираем текст задачи из шаблонов
    intro_templates = [
        "Площадь параллелограмма (в м²) можно вычислить по формуле S = a·h, где a — сторона параллелограмма, h — высота, проведенная к этой стороне (в метрах).",
        "Формула S = a·h позволяет найти площадь параллелограмма (в м²), если известны его сторона a и проведённая к ней высота h (в метрах)."
    ]
    task_templates = [
        f"Пользуясь этой формулой, найдите {target_text}, если {known_text}.",
        f"Вычислите {target_text}, если известно, что {known_text}."
    ]

    text = f"{random.choice(intro_templates)}\n{random.choice(task_templates)}"

    return {
        "subtype": "area_parallelogram_ah",
        "plot_id": "area_parallelogram_ah",
        "text": text,
        "answer": format_answer(answer),
        "params": {"S": S, "a": a, "h": h, "_find": target_var},
        "hidden_params": {"_hidden_answer": answer},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 5) Площадь параллелограмма через стороны и угол: S = a · b · sin(α)
#    Для «красивого» S берём sin(α) = 1 или 1/2.
# ─────────────────────────────────────────────────────────────────────────────
def _generate_area_parallelogram_ab_sin() -> dict:
    """
    Генерирует задачу на S = a·b·sin α.
    Использует стандартные формулировки ОГЭ и разнообразные числа.
    """
    sin_alpha = random.choice([0.5, 1.0])
    
    # Генерируем "красивые" стороны, возможно, с .5
    a = random.randint(5, 20) + random.choice([0, 0.5])
    b = random.randint(5, 20) + random.choice([0, 0.5])

    # Если sin_alpha = 0.5, нужно, чтобы произведение a*b было целым,
    # чтобы избежать сложных дробей типа .25 или .75 в ответе.
    if sin_alpha == 0.5:
        if not (a * b).is_integer():
            # Если оба числа с .5 (например 5.5 * 6.5), делаем одно из них целым
            a = int(a)

    S = a * b * sin_alpha

    # Банк уникализированных формулировок
    intro_templates = [
        "Площадь параллелограмма можно определить по формуле S = a·b·sin α, где a и b — смежные стороны параллелограмма (в метрах).",
        "Для вычисления площади параллелограмма (в м²) применяется формула S = a·b·sin α, где a, b — длины его сторон (в метрах)."
    ]
    
    known_text = f"его стороны равны {format_answer(a)} м и {format_answer(b)} м, а синус угла (sin α) между ними равен {format_answer(sin_alpha)}"
    
    task_templates = [
        f"Используя эту формулу, найди площадь параллелограмма, если {known_text}.",
        f"Вычисли, чему равна площадь параллелограмма (в м²), при условии, что {known_text}."
    ]

    text = f"{random.choice(intro_templates)}\n{random.choice(task_templates)}"

    return {
        "subtype": "area_parallelogram_ab_sin",
        "plot_id": "area_parallelogram_ab_sin",
        "text": text,
        "answer": format_answer(S),
        "params": {"a": a, "b": b, "sin_alpha": sin_alpha},
        "hidden_params": {"_hidden_S": S},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 6) Площадь ромба по диагоналям: S = 1/2 · d1 · d2
# ─────────────────────────────────────────────────────────────────────────────

def _generate_area_rhombus_d1d2() -> dict:
    """
    Генерирует задачу на S = ½d₁d₂ (поиск S, d₁ или d₂) с HTML-индексами.
    """
    # 1. Случайно выбираем, что будем искать
    target_var = random.choice(['S', 'd1', 'd2'])

    # 2. Генерируем "красивые" целочисленные параметры
    if target_var == 'S':
        d1 = random.randint(5, 25)
        d2 = random.randint(4, 20)
        # Гарантируем, что площадь будет целой
        if (d1 * d2) % 2 != 0:
            d2 += 1
        S = (d1 * d2) // 2
        answer = S
    else: # Ищем одну из диагоналей (обратная задача)
        answer = random.randint(5, 25)
        known_diag = random.randint(4, 20)
        # Гарантируем, что площадь будет целой
        if (answer * known_diag) % 2 != 0:
            known_diag += 1
        S = (answer * known_diag) // 2
        
        if target_var == 'd1':
            d1, d2 = answer, known_diag
        else: # target_var == 'd2'
            d1, d2 = known_diag, answer
            
    # 3. Собираем текст задачи с использованием HTML-тегов <sub> для индексов
    d1_html = "d<sub>1</sub>"
    d2_html = "d<sub>2</sub>"
    
    if target_var == 'S':
        target_text = "площадь S"
        known_text = f"диагонали равны {d1_html} = {d1} м и {d2_html} = {d2} м"
    elif target_var == 'd1':
        target_text = f"диагональ {d1_html}"
        # --- ИСПРАВЛЕНО ЗДЕСЬ ---
        known_text = f"диагональ {d2_html} равна {d2} м, а площадь ромба S = {S} м²"
    else: # target_var == 'd2'
        target_text = f"диагональ {d2_html}"
        # --- И ИСПРАВЛЕНО ЗДЕСЬ ---
        known_text = f"диагональ {d1_html} равна {d1} м, а площадь ромба S = {S} м²"

    # Банк уникализированных формулировок
    intro_templates = [
        f"Площадь ромба (в м²) можно вычислить по формуле S = ½{d1_html}{d2_html}, где {d1_html}, {d2_html} — диагонали ромба (в метрах).",
        f"Формула S = ½{d1_html}{d2_html} используется для нахождения площади ромба (в м²), где {d1_html} и {d2_html} — его диагонали (в метрах)."
    ]
    task_templates = [
        f"Пользуясь этой формулой, найди {target_text}, если {known_text}.",
        f"Вычисли, чему равна {target_text}, если известно, что {known_text}."
    ]

    text = f"{random.choice(intro_templates)}\n{random.choice(task_templates)}"
    
    return {
        "subtype": "area_rhombus_d1d2",
        "plot_id": "area_rhombus_d1d2",
        "text": text,
        "answer": format_answer(answer),
        "params": {"S": S, "d1": d1, "d2": d2, "_find": target_var},
        "hidden_params": {"_hidden_answer": answer},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 7) Площадь трапеции: S = (a + b) · h / 2
#    Подбираем (a + b)·h чётным → S целое.
# ─────────────────────────────────────────────────────────────────────────────
def _generate_area_trapezoid_bases_h() -> dict:
    """
    Генерирует задачу на S = (a+b)h/2 (поиск S, h, a или b).
    """
    # 1. Случайно выбираем, что будем искать
    target_var = random.choice(['S', 'h', 'a']) # 'b' эквивалентно 'a'

    # 2. Генерируем "красивые" целочисленные параметры
    if target_var == 'S':
        a = random.randint(4, 20)
        b = random.randint(4, 20)
        h = random.randint(3, 15)
        # Гарантируем, что S будет целым
        if ((a + b) * h) % 2 != 0:
            h += 1
        S = ((a + b) * h) // 2
        answer = S
    else: # Обратная задача
        # Генерируем "ответ" и остальные параметры
        if target_var == 'h':
            a = random.randint(4, 20)
            b = random.randint(4, 20)
            answer = random.randint(3, 15) # это будет h
            h = answer
            if ((a + b) * h) % 2 != 0:
                # Корректируем одно из оснований, чтобы S было целым
                b += 1
            S = ((a + b) * h) // 2
        else: # Ищем 'a'
            b = random.randint(5, 20)
            h = random.randint(3, 15)
            answer = random.randint(4, b - 1) # a < b для разнообразия
            a = answer
            if ((a + b) * h) % 2 != 0:
                h += 1
            S = ((a + b) * h) // 2
            
    # 3. Собираем текст задачи
    if target_var == 'S':
        target_text = "площадь S"
        known_text = f"основания трапеции равны {a} м и {b} м, а её высота {h} м"
    elif target_var == 'h':
        target_text = "высоту h"
        known_text = f"основания трапеции равны {a} м и {b} м, а её площадь {S} м²"
    else: # target_var == 'a'
        target_text = "основание a"
        known_text = f"другое основание b равно {b} м, высота h равна {h} м, а площадь S = {S} м²"

    intro_text = "Площадь трапеции (в м²) можно вычислить по формуле S = (a+b)h/2, где a, b — основания трапеции, h — высота (в метрах)."
    task_text = f"Пользуясь этой формулой, найди {target_text}, если {known_text}."

    return {
        "subtype": "area_trapezoid_bases_h",
        "plot_id": "area_trapezoid_bases_h",
        "text": f"{intro_text}\n{task_text}",
        "answer": format_answer(answer),
        "params": {"S": S, "a": a, "b": b, "h": h, "_find": target_var},
        "hidden_params": {"_hidden_answer": answer},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 8) Площадь выпуклого четырёхугольника: S = 1/2 · d1 · d2 · sin(α)
#    Берём sin(α) = 1 или 1/2; подбираем d1, d2 для целого S.
# ─────────────────────────────────────────────────────────────────────────────
def _generate_area_quadrilateral_d1d2_sin_S() -> dict:
    """
    Генерирует задачу на S = ½d₁d₂sinα (поиск S, d₁ или d₂).
    """
    target_var = random.choice(['S', 'd1', 'd2'])
    sin_alpha = random.choice([0.5, 1.0])

    def _get_nice_diag():
        return random.randint(5, 25) + random.choice([0, 0.5])

    if target_var == 'S':
        d1 = _get_nice_diag()
        d2 = _get_nice_diag()
        if not (d1 * d2 * sin_alpha).is_integer():
             d1 = int(d1)
        S = 0.5 * d1 * d2 * sin_alpha
        answer = S
    else: # Обратная задача
        answer = _get_nice_diag()
        known_diag = _get_nice_diag()
        
        # Гарантируем "красивую" площадь
        temp_S = 0.5 * answer * known_diag * sin_alpha
        if not temp_S.is_integer():
             known_diag = int(known_diag)
        S = 0.5 * answer * known_diag * sin_alpha

        if target_var == 'd1':
            d1, d2 = answer, known_diag
        else: # target_var == 'd2'
            d1, d2 = known_diag, answer
            
    # Собираем текст с HTML
    d1_html = "d<sub>1</sub>"
    d2_html = "d<sub>2</sub>"
    
    if target_var == 'S':
        target_text = "площадь S"
        known_text = f"{d1_html} = {format_answer(d1)}, {d2_html} = {format_answer(d2)}, а sin α = {format_answer(sin_alpha)}"
    elif target_var == 'd1':
        target_text = f"длину диагонали {d1_html}"
        known_text = f"{d2_html} = {format_answer(d2)}, S = {format_answer(S)}, а sin α = {format_answer(sin_alpha)}"
    else: # target_var == 'd2'
        target_text = f"длину диагонали {d2_html}"
        known_text = f"{d1_html} = {format_answer(d1)}, S = {format_answer(S)}, а sin α = {format_answer(sin_alpha)}"

    intro_text = f"Площадь четырёхугольника можно вычислить по формуле S = ½{d1_html}{d2_html} sin α, где {d1_html} и {d2_html} — длины диагоналей, α — угол между ними."
    task_text = f"Пользуясь этой формулой, найди {target_text}, если {known_text}."

    return {
        "subtype": "area_quadrilateral_d1d2_sin_S",
        "plot_id": "area_quadrilateral_d1d2_sin_S",
        "text": f"{intro_text}\n{task_text}",
        "answer": format_answer(answer),
        "params": {"S": S, "d1": d1, "d2": d2, "sin_alpha": sin_alpha, "_find": target_var},
        "hidden_params": {"_hidden_answer": answer},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 9) Задача на поиск длины биссектрисы, проведённой к основанию
#    в равнобедренном треугольнике.
#    В равнобедренном треугольнике эта биссектриса является также высотой,
#    поэтому её длина вычисляется по теореме Пифагора.
#    Генератор использует "пифагоровы тройки", чтобы гарантировать
#    целочисленные значения для сторон и ответа. lₐ = √(b² - (a/2)²)
# ─────────────────────────────────────────────────────────────────────────────
def _generate_bisector_length_equal_legs() -> dict:
    """
    Генерирует задачу на поиск биссектрисы к основанию в равнобедренном треугольнике.
    Использует простую и понятную формулировку.
    """
    # Используем "пифагоровы тройки" (b, k, m)
    # b - боковая сторона, k - половина основания, m - биссектриса (она же высота)
    triples = [(5, 3, 4), (13, 5, 12), (10, 6, 8), (25, 7, 24), (15, 9, 12)]
    b, k, m = random.choice(triples)
    
    a = 2 * k  # Основание
    l_a = m    # Ответ - длина биссектрисы

    # Банк уникализированных формулировок
    task_templates = [
        f"В равнобедренном треугольнике боковая сторона равна {b} см, а основание — {a} см. Найди длину биссектрисы, проведённой к основанию (в см).",
        f"К основанию равнобедренного треугольника проведена биссектриса. Вычисли её длину (в см), если основание равно {a} см, а боковая сторона — {b} см."
    ]
    
    return {
        "subtype": "bisector_length_equal_legs",
        "plot_id": "bisector_length_equal_legs",
        "text": random.choice(task_templates),
        "answer": format_answer(l_a),
        "params": {"a": a, "b": b},
        "hidden_params": {"_hidden_l_a": l_a},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 10) Задача на поиск длины биссектрисы в разностороннем треугольнике
#    по общей формуле lₐ = (2bc√(p(p-a)))/(b+c).
#    Так как генерировать случайные стороны с "красивым" целочисленным
#    ответом для этой сложной формулы математически трудно, генератор
#    использует заранее просчитанный список треугольников, для которых
#    ответ гарантированно является целым числом.
#    В тексте задачи ученику предоставляется полная формула и все
#    необходимые данные (a, b, c, p) для прямого вычисления.
# ─────────────────────────────────────────────────────────────────────────────
def _generate_bisector_length_general() -> dict:
    subtype = "bisector_length_general"
    plot_id = "bisector_length_general"

    # Генерируем стороны так, чтобы биссектриса была целой
    while True:
        b = random.randint(4, 12)
        c = random.randint(4, 12)
        # Подбираем 'a' так, чтобы l_a было целым
        # l_a^2 = bc(1 - (a/(b+c))^2)
        # (l_a/sqrt(bc))^2 = 1 - (a/(b+c))^2
        # (a/(b+c))^2 = 1 - (l_a/sqrt(bc))^2
        # a = (b+c) * sqrt(1 - ...)
        # Это сложно. Пойдем от ответа.
        
        l_a = random.randint(3, 8) # Желаемый ответ
        # a = (b+c)/sqrt(bc) * sqrt(bc - l_a^2)
        # Попробуем подобрать 'a' перебором
        a = 1
        found = False
        for a_candidate in range(2, b+c-1):
             # Проверяем неравенство треугольника
            if not (a_candidate < b+c and b < a_candidate+c and c < a_candidate+b):
                continue
            
            p = (a_candidate + b + c) / 2
            # Считаем квадрат биссектрисы по правильной формуле
            la_squared_float = b*c - (a_candidate**2 * b * c) / ((b+c)**2)

            if la_squared_float > 0:
                la_float = math.sqrt(la_squared_float)
                # Если ответ получился почти целым, используем его
                if abs(la_float - round(la_float)) < 1e-9:
                    a = a_candidate
                    l_a = round(la_float)
                    found = True
                    break
        if found:
            break
    
    p = (a + b + c) / 2
    l_a_html = "l<sub>a</sub>"
    formula_text = f"{l_a_html}<sup>2</sup> = bc - a<sup>2</sup>bc/(b+c)<sup>2</sup>" # Используем другую, более понятную формулу
    intro_text = (
        f"Длину биссектрисы треугольника, проведенной к стороне a, можно вычислить по формуле {formula_text}, "
        "где a, b, c — стороны треугольника."
    )
    known_text = f"стороны треугольника равны a = {a}, b = {b} и c = {c}"
    task_text = f"Вычисли длину биссектрисы {l_a_html}, если {known_text}."
    return {
        "subtype": "bisector_length_general",
        "plot_id": "bisector_length_general",
        "text": f"{intro_text}\n{task_text}",
        "answer": format_answer(l_a),
        "params": {"a": a, "b": b, "c": c},
        "hidden_params": {"_hidden_l_a": l_a},
        "constants": None
    }