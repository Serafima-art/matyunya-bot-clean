# task_12_generators.py
# ─────────────────────────────────────────────────────────────────────────────
# Полный генератор заданий №12 ОГЭ
# Охвачены все 66 подтипов (геометрия, физика, разные жизненные задачи)

import random
import math
from typing import Optional, Dict, Any, Callable, Tuple

# ─────────────────────────────────────────────────────────────
# Константы
# ─────────────────────────────────────────────────────────────
# Константы (ОГЭ-уровень, как в школьных учебниках)
G = 10             # ускорение свободного падения, м/с²
PI = 3.14          # число π (школьное приближение)
G_CONST = 6.67e-11 # гравитационная постоянная (Н·м²/кг²)
K_CONST = 9e9      # электрическая постоянная (Н·м²/Кл²)
R_UNIV = 8.31      # универсальная газовая постоянная (Дж/(моль·К))
RHO_WATER = 1000   # плотность воды, кг/м³
V_SOUND = 330      # скорость звука в воздухе, м/с

# ─────────────────────────────────────────────────────────────────────────────
# Минимальный форматтер (общий для всех частей)
# ─────────────────────────────────────────────────────────────────────────────
def format_answer(value: float | int) -> str:
    """Возвращает число без .0, дробные с запятой."""
    if float(value).is_integer():
        return str(int(value))
    return str(value).replace('.', ',')

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
# 3) Площадь треугольника через радиус вписанной окружности: S = p · r
#    Берём p и r так, чтобы S было целым.
# ─────────────────────────────────────────────────────────────────────────────
def _generate_area_triangle_inscribed_circle() -> dict:
    subtype = "area_triangle_inscribed_circle"
    plot_id = "area_triangle_inscribed_circle"

    p = random.choice([18, 20, 24, 28, 30, 36, 40, 45])  # полупериметр (см)
    r = random.choice([2, 3, 4, 5, 6])                  # радиус (см)
    S = p * r

    text = (
        "Найди площадь треугольника, если радиус вписанной окружности равен "
        f"{r} см, а полупериметр треугольника — {p} см."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(S),
        "params": {"p": p, "r": r},
        "hidden_params": {"_hidden_S": S},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 4) Площадь параллелограмма через сторону и высоту: S = a · h
# ─────────────────────────────────────────────────────────────────────────────
def _generate_area_parallelogram_ah() -> dict:
    subtype = "area_parallelogram_ah"
    plot_id = "area_parallelogram_ah"

    a = random.choice([6, 7, 8, 9, 10, 12, 14])  # см
    h = random.choice([4, 5, 6, 7, 8, 9])        # см
    S = a * h

    text = (
        f"Найди площадь параллелограмма (в см²), если его сторона равна {a} см, "
        f"а высота, опущенная на эту сторону, равна {h} см."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(S),
        "params": {"a": a, "h": h},
        "hidden_params": {"_hidden_S": S},
        "constants": None
    }
# ─────────────────────────────────────────────────────────────────────────────
# 5) Площадь параллелограмма через стороны и угол: S = a · b · sin(α)
#    Для «красивого» S берём sin(α) = 1 или 1/2.
# ─────────────────────────────────────────────────────────────────────────────
def _generate_area_parallelogram_ab_sin() -> dict:
    subtype = "area_parallelogram_ab_sin"
    plot_id = "area_parallelogram_ab_sin"

    sin_alpha = random.choice([1, 0.5])
    if sin_alpha == 1:
        a = random.choice([6, 7, 8, 9, 10, 12])
        b = random.choice([6, 8, 9, 10, 12, 14, 15])
        S = a * b
        sin_text = "1"
    else:
        # S = a*b/2 → берём a*b кратно 2
        a = random.choice([8, 10, 12, 14, 16])
        b = random.choice([6, 8, 10, 12, 14, 18])
        S = (a * b) // 2
        sin_text = "0,5"

    text = (
        "Площадь параллелограмма вычисляется по формуле S = a·b·sinα. "
        f"Найди S, если a = {a} см, b = {b} см, sinα = {sin_text}."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(S),
        "params": {"a": a, "b": b, "sinα": sin_text},
        "hidden_params": {"_hidden_S": S},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 6) Площадь ромба по диагоналям: S = 1/2 · d1 · d2
# ─────────────────────────────────────────────────────────────────────────────
def _generate_area_rhombus_d1d2() -> dict:
    subtype = "area_rhombus_d1d2"
    plot_id = "area_rhombus_d1d2"

    d1 = random.choice([8, 10, 12, 14, 16, 18, 20])
    d2 = random.choice([6, 8, 10, 12, 14, 16])

    if (d1 * d2) % 2 == 0:
        S = (d1 * d2) // 2
    else:
        d2 = d2 + 1
        S = (d1 * d2) // 2

    text = (
        "Площадь ромба вычисляется по формуле S = ½·d₁·d₂. "
        f"Найди S, если диагонали равны d₁ = {d1} см и d₂ = {d2} см."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(S),
        "params": {"d1": d1, "d2": d2},
        "hidden_params": {"_hidden_S": S},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 7) Площадь трапеции: S = (a + b) · h / 2
#    Подбираем (a + b)·h чётным → S целое.
# ─────────────────────────────────────────────────────────────────────────────
def _generate_area_trapezoid_bases_h() -> dict:
    subtype = "area_trapezoid_bases_h"
    plot_id = "area_trapezoid_bases_h"

    a = random.choice([8, 10, 12, 14, 16, 18])
    b = random.choice([4, 6, 8, 10, 12, 14])
    h = random.choice([4, 6, 8, 10, 12])

    if ((a + b) * h) % 2 != 0:
        h += 1  # лёгкая коррекция для чётности произведения

    S = ((a + b) * h) // 2

    text = (
        "Площадь трапеции вычисляется по формуле S = (a + b)·h/2, где a и b — основания. "
        f"Найди S, если a = {a} см, b = {b} см, h = {h} см."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(S),
        "params": {"a": a, "b": b, "h": h},
        "hidden_params": {"_hidden_S": S},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 8) Площадь выпуклого четырёхугольника: S = 1/2 · d1 · d2 · sin(α)
#    Берём sin(α) = 1 или 1/2; подбираем d1, d2 для целого S.
# ─────────────────────────────────────────────────────────────────────────────
def _generate_area_quadrilateral_d1d2_sin_S() -> dict:
    subtype = "area_quadrilateral_d1d2_sin_S"
    plot_id = "area_quadrilateral_d1d2_sin_S"

    sin_alpha = random.choice([1, 0.5])
    if sin_alpha == 1:
        d1 = random.choice([10, 12, 14, 16, 18, 20])
        d2 = random.choice([6, 8, 10, 12, 14, 16])
        S = (d1 * d2) // 2
        sin_text = "1"
    else:
        d1 = random.choice([8, 12, 16, 20, 24])
        d2 = random.choice([8, 12, 16, 20, 24])
        S = (d1 * d2) // 4
        sin_text = "0,5"

    text = (
        "Площадь выпуклого четырёхугольника, у которого даны диагонали и угол между ними, "
        "вычисляется по формуле S = ½·d₁·d₂·sinα. "
        f"Найди S, если d₁ = {d1} см, d₂ = {d2} см, sinα = {sin_text}."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(S),
        "params": {"d1": d1, "d2": d2, "sinα": sin_text},
        "hidden_params": {"_hidden_S": S},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 9) Найти диагональ по площади (та же формула):  S = 1/2 · d1 · d2 · sin(α)
#    Здесь вычисляем d2: d2 = 2S / (d1 · sinα). Подбираем так, чтобы d2 было целым.
# ─────────────────────────────────────────────────────────────────────────────
def _generate_area_quadrilateral_find_d_by_S() -> dict:
    subtype = "area_quadrilateral_find_d_by_S"
    plot_id = "area_quadrilateral_find_d_by_S"

    sin_alpha = random.choice([1, 0.5])
    if sin_alpha == 1:
        d1 = random.choice([8, 10, 12, 14, 16, 18, 20])
        d2 = random.choice([6, 8, 10, 12, 14, 16])
        S = (d1 * d2) // 2
        sin_text = "1"
    else:
        d1 = random.choice([8, 12, 16, 20, 24])
        d2 = random.choice([8, 12, 16, 20, 24])
        S = (d1 * d2) // 4
        sin_text = "0,5"

    text = (
        "Площадь выпуклого четырёхугольника выражается формулой S = ½·d₁·d₂·sinα. "
        f"Пусть S = {S} см², d₁ = {d1} см, sinα = {sin_text}. Найди d₂ (в см)."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(d2),
        "params": {"S": S, "d1": d1, "sinα": sin_text},
        "hidden_params": {"_hidden_d2": d2},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 10) Длина биссектрисы (особый случай b = c), биссектриса к стороне a.
#     Для равнобедренного треугольника b = c, a = 2k (чтобы было красиво):
#     l_a = 2/(b+c) * sqrt(b*c*p*(p-a))
#     При b=c формула упрощается до: l_a = sqrt(b^2 - k^2), где a = 2k.
#     Выбираем (b, k, m) как пифагорову тройку: b^2 - k^2 = m^2 → l_a = m — целое.
# ─────────────────────────────────────────────────────────────────────────────
def _generate_bisector_length_equal_legs() -> dict:
    subtype = "bisector_length_equal_legs"
    plot_id = "bisector_length_equal_legs"

    # «Малые» пифагоровы тройки (b, k, m), где b² - k² = m² → l_a = m
    triples = [(5, 3, 4), (13, 5, 12), (10, 6, 8), (25, 7, 24), (15, 9, 12)]
    b, k, m = random.choice(triples)
    a = 2 * k  # основание
    l_a = m    # длина биссектрисы

    # Проверка неравенства треугольника
    if not (a < 2*b and b < a + b):
        return _generate_bisector_length_equal_legs()

    text = (
        f"В равнобедренном треугольнике стороны равны {b} см и {b} см, а основание равно {a} см. "
        "Найди длину биссектрисы, проведённой к основанию."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(l_a),
        "params": {"a": a, "b": b},
        "hidden_params": {"_hidden_l_a": l_a, "_hidden_k": k},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 11) Радиус вписанной окружности в треугольник: r = S / p
# ─────────────────────────────────────────────────────────────────────────────
def _generate_inscribed_circle_radius_triangle() -> dict:
    subtype = "inscribed_circle_radius_triangle"
    plot_id = "inscribed_circle_radius_triangle"

    p = random.choice([18, 20, 24, 28, 30, 36])  # полупериметр
    r = random.choice([2, 3, 4, 5])              # радиус
    S = p * r

    text = (
        f"Найди радиус вписанной окружности треугольника, "
        f"если его площадь равна {S} см², а полупериметр {p} см."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(r),
        "params": {"S": S, "p": p},
        "hidden_params": {"_hidden_r": r},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 12) Радиус вписанной окружности в прямоугольный треугольник: r = (a + b − c)/2
# ─────────────────────────────────────────────────────────────────────────────
def _generate_inscribed_circle_radius_right_triangle() -> dict:
    subtype = "inscribed_circle_radius_right_triangle"
    plot_id = "inscribed_circle_radius_right_triangle"

    # Пифагоровы тройки → r получается целым
    a, b, c = random.choice([(6, 8, 10), (9, 12, 15), (5, 12, 13), (8, 15, 17)])
    r = (a + b - c) / 2

    text = (
        f"В прямоугольном треугольнике катеты равны {a} см (a) и {b} см (b). "
        "Найди радиус вписанной окружности."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(r),
        "params": {"a": a, "b": b},
        "hidden_params": {"_hidden_c": c, "_hidden_r": r},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 13) Площадь треугольника через радиус описанной окружности: S = abc / 4R
# ─────────────────────────────────────────────────────────────────────────────
def _generate_circumscribed_circle_area_by_R() -> dict:
    subtype = "circumscribed_circle_area_by_R"
    plot_id = "circumscribed_circle_area_by_R"

    # возьмём правильный треугольник
    a = random.choice([6, 8, 10, 12])
    R = a / math.sqrt(3)
    S = (a * a * math.sqrt(3)) / 4

    text = (
        f"Стороны правильного треугольника равны {a} см. "
        "Найди площадь треугольника, используя формулу через радиус описанной окружности."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(S),
        "params": {"a": a},
        "hidden_params": {"_hidden_R": R},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 14) Радиус описанной окружности через сторону и угол: R = a / (2·sinA)
# ─────────────────────────────────────────────────────────────────────────────
def _generate_circumscribed_circle_R_by_side_angle() -> dict:
    subtype = "circumscribed_circle_R_by_side_angle"
    plot_id = "circumscribed_circle_R_by_side_angle"

    if random.choice([True, False]):
        # Вариант с sin = 0,5 → ответ всегда целое (R = a)
        sin_text = "0,5"
        sinA = 0.5
        a = random.choice([6, 8, 10, 12, 14])
        R = a / (2 * sinA)
    else:
        # Вариант с sin = 0,866 → честный расчёт (может быть дробным)
        sin_text = "0,866"
        sinA = 0.866
        a = random.choice([9, 17, 26])
        R = a / (2 * sinA)

    text = (
        f"Сторона треугольника равна {a} см, противолежащий угол имеет sin = {sin_text}. "
        "Найди радиус описанной окружности."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(R),
        "params": {"a": a, "sinA": sin_text},
        "hidden_params": {"_hidden_R": R},
        "constants": None
    }
# ─────────────────────────────────────────────────────────────────────────────
# 15) Сумма углов n-угольника: Σ = (n−2)·180
# ─────────────────────────────────────────────────────────────────────────────
def _generate_polygon_angles_sum() -> dict:
    subtype = "polygon_angles_sum"
    plot_id = "polygon_angles_sum"

    n = random.randint(5, 12)
    S = (n - 2) * 180

    text = (
        f"Сумма углов выпуклого n-угольника равна {S}°. "
        "Найди число сторон n."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(n),
        "params": {"S": S},
        "hidden_params": {"_hidden_n": n},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 16) Высота пирамиды из формулы объёма: V = S·h / 3
# ─────────────────────────────────────────────────────────────────────────────
def _generate_height_pyramid_by_V() -> dict:
    subtype = "height_pyramid_by_V"
    plot_id = "height_pyramid_by_V"

    S = random.choice([12, 18, 24, 30])   # площадь основания
    h = random.choice([6, 9, 12])         # высота
    V = S * h // 3

    text = (
        f"Объём пирамиды равен {V} см³, площадь основания {S} см². "
        "Найди высоту пирамиды."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(h),
        "params": {"S": S, "V": V},
        "hidden_params": {"_hidden_h": h},
        "constants": None
    }
# ─────────────────────────────────────────────────────────────────────────────
# 17) Радиус по длине окружности: ℓ = 2πR
# ─────────────────────────────────────────────────────────────────────────────
def _generate_circumference_length_find_R() -> dict:
    subtype = "circumference_length_find_R"
    plot_id = "circumference_length_find_R"

    R = random.choice([7, 10, 14, 21])
    L = 2 * PI * R

    text = f"Длина окружности равна {format_answer(L)} см. Найди её радиус."

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(R),
        "params": {"L": L},
        "hidden_params": {"_hidden_R": R},
        "constants": {"PI": PI}
    }

# ─────────────────────────────────────────────────────────────────────────────
# 18) Диагональ четырёхугольника по площади (обратная задача к 8-му)
# ─────────────────────────────────────────────────────────────────────────────
def _generate_area_quadrilateral_d1d2_sin_find_d() -> dict:
    subtype = "area_quadrilateral_d1d2_sin_find_d"
    plot_id = "area_quadrilateral_d1d2_sin_find_d"

    d1 = random.choice([6, 8, 10, 12])
    d2 = random.choice([6, 8, 10, 12])
    sinA = 0.5
    S = 0.5 * d1 * d2 * sinA

    if random.choice([True, False]):
        # дано d1 → найти d2
        text = (
            f"Пусть S = {format_answer(S)} см², d₁ = {d1} см, sinα = {format_answer(sinA)}; "
            "Найди d₂."
        )
        answer = format_answer(d2)
        params = {"S": S, "d1": d1, "sinα": sinA}
        hidden_params = {"_hidden_d2": d2}
    else:
        # дано d2 → найти d1
        text = (
            f"Пусть S = {format_answer(S)} см², d₂ = {d2} см, sinα = {format_answer(sinA)}; "
            "Найди d₁."
        )
        answer = format_answer(d1)
        params = {"S": S, "d2": d2, "sinα": sinA}
        hidden_params = {"_hidden_d1": d1}

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": answer,
        "params": params,
        "hidden_params": hidden_params,
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 19) Общая формула биссектрисы (разносторонний треугольник)
#     l_a = 2bc cos(A/2) / (b+c) или через полу-периметр
# ─────────────────────────────────────────────────────────────────────────────
def _generate_bisector_length_general() -> dict:
    subtype = "bisector_length_general"
    plot_id = "bisector_length_general"

    # фиксируем треугольник (7,8,9)
    a, b, c = 7, 8, 9
    p = (a + b + c) / 2
    l_a = 2 * math.sqrt(b * c * p * (p - a)) / (b + c)

    text = (
        f"В треугольнике со сторонами {a} см, {b} см и {c} см "
        f"найди длину биссектрисы, проведённой к стороне длиной {a} см."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(l_a),
        "params": {"a": a, "b": b, "c": c},
        "hidden_params": {"_hidden_p": p},
        "constants": None
    }
# ─────────────────────────────────────────────────────────────────────────────
# 20) Радиус описанной окружности правильного треугольника: R = a/√3
# ─────────────────────────────────────────────────────────────────────────────
def _generate_circumscribed_circle_radius_equilateral() -> dict:
    subtype = "circumscribed_circle_radius_equilateral"
    plot_id = "circumscribed_circle_radius_equilateral"

    a = random.choice([6, 9, 12, 15])
    R = a / math.sqrt(3)

    text = (
        f"Сторона правильного треугольника равна {a} см. "
        "Найди радиус описанной окружности."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(R),
        "params": {"a": a},
        "hidden_params": None,
        "constants": {"PI": PI}
    }

# ─────────────────────────────────────────────────────────────────────────────
# 21) Период маятника по длине: T = 2π√(l/g)
# ─────────────────────────────────────────────────────────────────────────────
def _generate_pendulum_period_by_length() -> dict:
    subtype = "pendulum_period_by_length"
    plot_id = "pendulum_period_by_length"

    l = random.choice([1, 2.25, 4, 6.25, 9])  # метры, чтобы √(l/g) был красивым
    T = 2 * PI * math.sqrt(l / G)

    text = (
        f"Найди период колебаний математического маятника длиной {format_answer(l)} м. "
        f"Ускорение свободного падения принять равным {G} м/с²."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(T),
        "params": {"l": l},
        "hidden_params": {"_hidden_formula": "T = 2π√(l/g)"},
        "constants": {"PI": PI, "G": G}
    }

# ─────────────────────────────────────────────────────────────────────────────
# 22) Длина маятника по периоду: l = gT² / (4π²)
# ─────────────────────────────────────────────────────────────────────────────
def _generate_pendulum_length_by_T() -> dict:
    subtype = "pendulum_length_by_T"
    plot_id = "pendulum_length_by_T"

    T = random.choice([2, 4])  # секунды
    l = G * T**2 / (4 * PI**2)

    text = (
        f"Период колебаний маятника равен {T} с. "
        f"Найди длину нити маятника. Ускорение свободного падения принять равным {G} м/с²."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(l),
        "params": {"T": T},
        "hidden_params": {"_hidden_formula": "l = gT² / (4π²)"},
        "constants": {"PI": PI, "G": G}
    }

# ─────────────────────────────────────────────────────────────────────────────
# 23) Кинетическая энергия: найти v по m и E
# ─────────────────────────────────────────────────────────────────────────────
def _generate_kinetic_energy_find_v() -> dict:
    subtype = "kinetic_energy_find_v"
    plot_id = "kinetic_energy_find_v"

    m = random.choice([2, 4, 5, 10])  # кг
    v = random.choice([3, 4, 5, 6])   # м/с
    E = m * v**2 / 2

    text = (
        f"Кинетическая энергия тела массой {m} кг равна {format_answer(E)} Дж. "
        "Найди скорость тела."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(v),
        "params": {"m": m, "E": E},
        "hidden_params": {"_hidden_v": v},
        "constants": None
    }
# ─────────────────────────────────────────────────────────────────────────────
# 24) Кинетическая энергия: найти E по m и v
# ─────────────────────────────────────────────────────────────────────────────
def _generate_kinetic_energy_find_E() -> dict:
    subtype = "kinetic_energy_find_E"
    plot_id = "kinetic_energy_find_E"

    m = random.choice([2, 3, 5, 8])   # кг
    v = random.choice([2, 3, 4, 5])   # м/с
    E = m * v**2 / 2

    text = (
        f"Найди кинетическую энергию тела массой {m} кг, движущегося со скоростью {v} м/с."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(E),
        "params": {"m": m, "v": v},
        "hidden_params": {"_hidden_E": E},
        "constants": None
    }
# ─────────────────────────────────────────────────────────────────────────────
# 25) Потенциальная энергия: найти m по E и h
# ─────────────────────────────────────────────────────────────────────────────
def _generate_potential_energy_find_m() -> dict:
    subtype = "potential_energy_find_m"
    plot_id = "potential_energy_find_m"

    h = random.choice([2, 3, 4, 5])  # м
    m = random.choice([2, 4, 5, 8])  # кг
    E = m * G * h

    text = (
        f"Потенциальная энергия тела равна {E} Дж при высоте {h} м. "
        "Найди массу тела."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(m),
        "params": {"E": E, "h": h},
        "hidden_params": {"_hidden_m": m},
        "constants": {"G": G}
    }
# ─────────────────────────────────────────────────────────────────────────────
# 26) Потенциальная энергия: найти E по m и h
# ─────────────────────────────────────────────────────────────────────────────
def _generate_potential_energy_find_E() -> dict:
    subtype = "potential_energy_find_E"
    plot_id = "potential_energy_find_E"

    m = random.choice([2, 3, 5, 7])  # кг
    h = random.choice([2, 4, 6, 8])  # м
    E = m * G * h

    text = (
        f"Найди потенциальную энергию тела массой {m} кг на высоте {h} м."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(E),
        "params": {"m": m, "h": h},
        "hidden_params": {"_hidden_E": E},
        "constants": {"G": G}
    }

# ─────────────────────────────────────────────────────────────────────────────
# 27) Полная механическая энергия: E = Eₖ + Eₚ
# ─────────────────────────────────────────────────────────────────────────────
def _generate_mechanical_energy_total() -> dict:
    subtype = "mechanical_energy_total"
    plot_id = "mechanical_energy_total"

    m = random.choice([1, 2, 3])  # кг
    v = random.choice([2, 3, 4])  # м/с
    h = random.choice([2, 3, 4])  # м

    E_k = m * v**2 / 2
    E_p = m * G * h
    E = E_k + E_p

    text = (
        f"Тело массой {m} кг движется со скоростью {v} м/с и находится на высоте {h} м. "
        "Найди полную механическую энергию тела."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(E),
        "params": {"m": m, "v": v, "h": h},
        "hidden_params": {"_hidden_Ek": E_k, "_hidden_Ep": E_p, "_hidden_E": E},
        "constants": {"G": G}
    }

# ─────────────────────────────────────────────────────────────────────────────
# 28) Механическая энергия: найти m по E и h (Eₚ = mgh)
# ─────────────────────────────────────────────────────────────────────────────
def _generate_mechanical_energy_find_m() -> dict:
    subtype = "mechanical_energy_find_m"
    plot_id = "mechanical_energy_find_m"

    h = random.choice([2, 4, 6])  # м
    m = random.choice([2, 4, 6])  # кг
    E = m * G * h

    text = (
        f"Потенциальная энергия тела равна {E} Дж при высоте {h} м. "
        "Найди массу тела."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(m),
        "params": {"E": E, "h": h},
        "hidden_params": {"_hidden_m": m},
        "constants": {"G": G}
    }
# ─────────────────────────────────────────────────────────────────────────────
# 29) Сила Архимеда: F = ρgV
# ─────────────────────────────────────────────────────────────────────────────
def _generate_archimedes_force_find_F() -> dict:
    subtype = "archimedes_force_find_F"
    plot_id = "archimedes_force_find_F"

    V = random.choice([0.002, 0.003, 0.004])  # м³
    F = RHO_WATER * G * V  # ← ИСПОЛЬЗУЕМ КОНСТАНТУ

    text = (
        f"Определите силу Архимеда, действующую на тело объёмом {format_answer(V)} м³, "
        f"погружённое в воду (ρ = {RHO_WATER} кг/м³). Ускорение свободного падения {G} м/с²."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(F),
        "params": {"V": V, "rho": RHO_WATER},  # ← ИСПОЛЬЗУЕМ КОНСТАНТУ
        "hidden_params": {"_hidden_F": F},
        "constants": {"G": G, "RHO_WATER": RHO_WATER}  # ← ДОБАВЛЯЕМ В КОНСТАНТЫ
    }

# ─────────────────────────────────────────────────────────────────────────────
# 30) Сила Архимеда: найти V по F
# ─────────────────────────────────────────────────────────────────────────────
def _generate_archimedes_force_find_V() -> dict:
    subtype = "archimedes_force_find_V"
    plot_id = "archimedes_force_find_V"

    V = random.choice([0.002, 0.003, 0.004])  # м³
    F = RHO_WATER * G * V  # ← ИСПОЛЬЗУЕМ КОНСТАНТУ

    text = (
        f"Сила Архимеда, действующая на тело, равна {format_answer(F)} Н. "
        f"Плотность воды {RHO_WATER} кг/м³, g = {G} м/с². Найди объём тела."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(V),
        "params": {"F": F, "rho": RHO_WATER},  # ← ИСПОЛЬЗУЕМ КОНСТАНТУ
        "hidden_params": {"_hidden_V": V},
        "constants": {"G": G, "RHO_WATER": RHO_WATER}  # ← ДОБАВЛЯЕМ В КОНСТАНТЫ
    }

# ─────────────────────────────────────────────────────────────────────────────
# 31) Закон всемирного тяготения: найти m1 по F, r, m2
# ─────────────────────────────────────────────────────────────────────────────
def _generate_newton_gravity_find_m() -> dict:
    subtype = "newton_gravity_find_m"
    plot_id = "newton_gravity_find_m"

    # Подбираем "красивые" числа
    m1 = random.choice([1e12, 2e12, 5e12])   # кг
    m2 = random.choice([1e12, 2e12, 5e12])   # кг
    r = random.choice([1e6, 2e6, 5e6])       # м

    F = G_CONST * m1 * m2 / (r**2)

    text = (
        f"Сила притяжения F = {format_answer(F)} Н. "
        f"Расстояние r = {int(r)} м. "
        f"Масса второго тела m₂ = {int(m2)} кг. "
        f"Гравитационная постоянная γ = {G_CONST} Н·м²/кг². "
        "Найди массу первого тела m₁."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(m1),
        "params": {"F": F, "r": r, "m2": m2},
        "hidden_params": {"_hidden_m1": m1},
        "constants": {"G_CONST": G_CONST}
    }

# ─────────────────────────────────────────────────────────────────────────────
# 32) Закон всемирного тяготения: найти F
# ─────────────────────────────────────────────────────────────────────────────
def _generate_newton_gravity_find_F() -> dict:
    subtype = "newton_gravity_find_F"
    plot_id = "newton_gravity_find_F"

    # Подбираем "красивые" числа
    m1 = random.choice([1e12, 2e12, 5e12])   # кг
    m2 = random.choice([1e12, 2e12, 5e12])   # кг
    r = random.choice([1e6, 2e6, 5e6])       # м

    F = G_CONST * m1 * m2 / (r**2)

    text = (
        f"Масса первого тела m₁ = {int(m1)} кг. "
        f"Масса второго тела m₂ = {int(m2)} кг. "
        f"Расстояние между телами r = {int(r)} м. "
        f"Гравитационная постоянная γ = {G_CONST} Н·м²/кг². "
        "Найди силу притяжения F."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(F),
        "params": {"m1": m1, "m2": m2, "r": r},
        "hidden_params": {"_hidden_F": F},
        "constants": {"G_CONST": G_CONST}
    }

# ─────────────────────────────────────────────────────────────────────────────
# 33) Закон Кулона: найти q
# ─────────────────────────────────────────────────────────────────────────────
def _generate_coulomb_law_find_q() -> dict:
    subtype = "coulomb_law_find_q"
    plot_id = "coulomb_law_find_q"

    # заряды в микрокулонах (целые, "школьные")
    q1_uC = random.choice([2, 3, 4, 5, 6])   # μКл
    q2_uC = random.choice([2, 3, 4, 5])      # μКл (нужно найти)
    r = random.choice([1, 2, 3])             # м

    # переводим в Кл для вычислений
    q1 = q1_uC * 1e-6
    q2 = q2_uC * 1e-6

    # сила в Ньютонах
    F = K_CONST * q1 * q2 / (r ** 2)

    text = (
        f"Сила взаимодействия F = {format_answer(F)} Н. "
        f"Расстояние r = {r} м. "
        f"Известный заряд q₁ = {q1_uC} мкКл. "
        "Найдите второй заряд q₂ (в мкКл)."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(q2_uC),  # в мкКл
        "params": {"q1_uC": q1_uC, "r": r, "F": F},
        "hidden_params": {"_hidden_q2_uC": q2_uC, "_hidden_q2_C": q2},
        "constants": {"K_CONST": K_CONST}
    }

# ─────────────────────────────────────────────────────────────────────────────
# 34) Закон Кулона: найти F
# ─────────────────────────────────────────────────────────────────────────────
def _generate_coulomb_law_find_F() -> dict:
    subtype = "coulomb_law_find_F"
    plot_id = "coulomb_law_find_F"

    q1 = random.choice([2e-6, 3e-6])  # Кл
    q2 = random.choice([4e-6, 5e-6])  # Кл
    r = random.choice([2, 3])         # м
    F = K_CONST * q1 * q2 / (r**2)

    text = (
        f"Найди силу взаимодействия зарядов q₁ = {format_answer(q1)} Кл и "
        f"q₂ = {format_answer(q2)} Кл, расположенных на расстоянии {r} м. "
        f"Электрическая постоянная k = {K_CONST} Н·м²/Кл²."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(F),
        "params": {"q1": q1, "q2": q2, "r": r},
        "hidden_params": {"_hidden_F": F},
        "constants": {"K_CONST": K_CONST}
    }

# ─────────────────────────────────────────────────────────────────────────────
# 35) Закон Джоуля-Ленца (P = I²R): найти R по P и I
# ─────────────────────────────────────────────────────────────────────────────
def _generate_ohm_power_find_R() -> dict:
    subtype = "ohm_power_find_R"
    plot_id = "ohm_power_find_R"

    I = random.choice([2, 3, 4])   # А
    R = random.choice([5, 10, 15]) # Ом
    P = I**2 * R

    text = (
        f"Мощность тока равна {P} Вт при силе тока {I} А. "
        "Найди сопротивление проводника."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(R),
        "params": {"I": I, "P": P},
        "hidden_params": {"_hidden_R": R},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 36) Закон Джоуля-Ленца: найти P
# ─────────────────────────────────────────────────────────────────────────────
def _generate_ohm_power_find_P() -> dict:
    subtype = "ohm_power_find_P"
    plot_id = "ohm_power_find_P"

    I = random.choice([2, 3, 4])   # А
    R = random.choice([5, 10, 15]) # Ом
    P = I**2 * R

    text = (
        f"Найди мощность тока в цепи при силе тока {I} А и сопротивлении {R} Ом."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(P),
        "params": {"I": I, "R": R},
        "hidden_params": {"_hidden_P": P},
        "constants": None
    }
# ─────────────────────────────────────────────────────────────────────────────
# 37) Закон Джоуля-Ленца (Q = I²Rt): найти t
# ─────────────────────────────────────────────────────────────────────────────
def _generate_joule_lenz_find_t() -> dict:
    subtype = "joule_lenz_find_t"
    plot_id = "joule_lenz_find_t"

    I = random.choice([2, 3])       # А
    R = random.choice([4, 5, 6])    # Ом
    t = random.choice([10, 20, 30]) # с
    Q = I**2 * R * t

    text = (
        f"Количество теплоты, выделившееся при прохождении тока, равно {Q} Дж. "
        f"Сила тока {I} А, сопротивление {R} Ом. Найди время протекания тока."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(t),
        "params": {"I": I, "R": R, "Q": Q},
        "hidden_params": {"_hidden_t": t},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 38) Закон Джоуля-Ленца: найти R
# ─────────────────────────────────────────────────────────────────────────────
def _generate_joule_lenz_find_R() -> dict:
    subtype = "joule_lenz_find_R"
    plot_id = "joule_lenz_find_R"

    I = random.choice([2, 3])     # А
    t = random.choice([10, 20])   # с
    R = random.choice([4, 6, 8])  # Ом
    Q = I**2 * R * t

    text = (
        f"Количество теплоты, выделившееся при прохождении тока, равно {Q} Дж. "
        f"Сила тока {I} А, время {t} с. Найди сопротивление проводника."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(R),
        "params": {"I": I, "t": t, "Q": Q},
        "hidden_params": {"_hidden_R": R},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 39) Работа тока: A = U²t / R
# ─────────────────────────────────────────────────────────────────────────────
def _generate_work_of_current_find_A() -> dict:
    subtype = "work_of_current_find_A"
    plot_id = "work_of_current_find_A"

    U = random.choice([10, 20])  # В
    t = random.choice([10, 20])  # с
    R = random.choice([5, 10])   # Ом
    A = U**2 * t / R

    text = (
        f"Найди работу тока в цепи, если напряжение {U} В, время {t} с, "
        f"сопротивление {R} Ом."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(A),
        "params": {"U": U, "t": t, "R": R},
        "hidden_params": {"_hidden_A": A},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 40) Энергия конденсатора: W = CU²/2
# ─────────────────────────────────────────────────────────────────────────────
def _generate_capacitor_energy_find_W() -> dict:
    subtype = "capacitor_energy_find_W"
    plot_id = "capacitor_energy_find_W"

    C = random.choice([2e-6, 4e-6, 6e-6])   # Ф
    U = random.choice([10, 20, 30])         # В
    W = C * U**2 / 2

    text = (
        f"Найди энергию, запасённую в конденсаторе ёмкостью {format_answer(C)} Ф, "
        f"если напряжение на его обкладках равно {U} В."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(W),
        "params": {"C": C, "U": U},
        "hidden_params": {"_hidden_W": W},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 41) Энергия конденсатора по заряду: W = q² / (2C)
# ─────────────────────────────────────────────────────────────────────────────
def _generate_capacitor_energy_find_W_q() -> dict:
    subtype = "capacitor_energy_find_W_q"
    plot_id = "capacitor_energy_find_W_q"

    # ёмкость в микрофарадах (целое число)
    C_uF = random.choice([2, 4, 5])        # μФ
    q_uC = random.choice([2, 3, 4])        # μКл

    # переводим в СИ
    C = C_uF * 1e-6  # Ф
    q = q_uC * 1e-6  # Кл

    # энергия в Дж
    W = q**2 / (2 * C)

    # переводим в μДж (целое)
    W_uJ = round(W * 1e6)

    text = (
        f"Пусть C = {C_uF} мкФ, q = {q_uC} мкКл. "
        "Найди энергию W, запасённую в конденсаторе (в мкДж)."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(W_uJ),
        "params": {"C_uF": C_uF, "q_uC": q_uC},
        "hidden_params": {
            "_hidden_C_F": C,
            "_hidden_q_C": q,
            "_hidden_W_J": W,
            "_hidden_W_uJ": W_uJ
        },
        "constants": None
    }
# ─────────────────────────────────────────────────────────────────────────────
# 42) Газовый закон: найти давление P = νRT/V
# ─────────────────────────────────────────────────────────────────────────────
def _generate_gas_law_find_P() -> dict:
    subtype = "gas_law_find_P"
    plot_id = "gas_law_find_P"

    n = random.choice([1, 2, 3])       # моль
    T = random.choice([300, 400])      # K
    V = random.choice([0.01, 0.02])    # м³

    P = n * R_UNIV * T / V

    text = (
        f"Количество вещества {n} моль, температура {T} К, объём {format_answer(V)} м³. "
        "Найди давление газа."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(P),
        "params": {"n": n, "T": T, "V": V},
        "hidden_params": {"_hidden_P": P},
        "constants": {"R": R_UNIV}
    }
# ─────────────────────────────────────────────────────────────────────────────
# 43) Газовый закон: найти температуру T
# ─────────────────────────────────────────────────────────────────────────────
def _generate_gas_law_find_T() -> dict:
    subtype = "gas_law_find_T"
    plot_id = "gas_law_find_T"

    n = random.choice([1, 2])        # моль
    V = random.choice([0.01, 0.02])  # м³
    P = random.choice([200000, 300000])  # Па

    T = P * V / (n * R_UNIV)

    text = (
        f"Давление газа равно {P} Па, объём {format_answer(V)} м³, "
        f"количество вещества {n} моль. Найди температуру газа."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(T),
        "params": {"P": P, "V": V, "n": n},
        "hidden_params": {"_hidden_T": T},
        "constants": {"R": R_UNIV}
    }

# ─────────────────────────────────────────────────────────────────────────────
# 44) Газовый закон: найти объём V
# ─────────────────────────────────────────────────────────────────────────────
def _generate_gas_law_find_V() -> dict:
    subtype = "gas_law_find_V"
    plot_id = "gas_law_find_V"

    n = random.choice([1, 2])         # моль
    T = random.choice([300, 350])     # K
    P = random.choice([100000, 200000])  # Па

    V = n * R_UNIV * T / P

    text = (
        f"Давление газа {P} Па, количество вещества {n} моль, температура {T} К. "
        "Найди объём газа."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(V),
        "params": {"P": P, "n": n, "T": T},
        "hidden_params": {"_hidden_V": V},
        "constants": {"R": R_UNIV}
    }

# ─────────────────────────────────────────────────────────────────────────────
# 45) Газовый закон: найти количество вещества n
# ─────────────────────────────────────────────────────────────────────────────
def _generate_gas_law_find_n() -> dict:
    subtype = "gas_law_find_n"
    plot_id = "gas_law_find_n"

    V = random.choice([0.01, 0.02])    # м³
    T = random.choice([300, 400])      # K
    P = random.choice([100000, 200000])  # Па

    n = P * V / (R_UNIV * T)

    text = (
        f"Давление газа {P} Па, температура {T} К, объём {format_answer(V)} м³. "
        "Найди количество вещества газа."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(n),
        "params": {"P": P, "V": V, "T": T},
        "hidden_params": {"_hidden_n": n},
        "constants": {"R": R_UNIV}
    }

# ─────────────────────────────────────────────────────────────────────────────
# 46) Центростремительное ускорение: найти R по a = ω²R
# ─────────────────────────────────────────────────────────────────────────────
def _generate_centripetal_acceleration_find_R() -> dict:
    subtype = "centripetal_acceleration_find_R"
    plot_id = "centripetal_acceleration_find_R"

    ω = random.choice([2, 3])   # рад/с
    R = random.choice([2, 4])   # м
    a = ω**2 * R

    text = (
        f"Центростремительное ускорение равно {a} м/с² при угловой скорости {ω} рад/с. "
        "Найди радиус окружности."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(R),
        "params": {"a": a, "ω": ω},
        "hidden_params": {"_hidden_R": R},
        "constants": None
    }
# ─────────────────────────────────────────────────────────────────────────────
# 47) Центростремительное ускорение: найти a
# ─────────────────────────────────────────────────────────────────────────────
def _generate_centripetal_acceleration_find_a() -> dict:
    subtype = "centripetal_acceleration_find_a"
    plot_id = "centripetal_acceleration_find_a"

    ω = random.choice([2, 3])   # рад/с
    R = random.choice([2, 4])   # м
    a = ω**2 * R

    text = (
        f"Пусть ω = {ω} рад/с, R = {R} м. "
        "Найди центростремительное ускорение a."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(a),
        "params": {"ω": ω, "R": R},
        "hidden_params": {"_hidden_a": a},
        "constants": None
    }
# ─────────────────────────────────────────────────────────────────────────────
# 48) Центростремительное ускорение: найти ω
# ─────────────────────────────────────────────────────────────────────────────
def _generate_centripetal_acceleration_find_omega() -> dict:
    subtype = "centripetal_acceleration_find_omega"
    plot_id = "centripetal_acceleration_find_omega"

    R = random.choice([2, 3])  # м
    ω = random.choice([2, 3])  # рад/с
    a = ω**2 * R

    text = (
        f"Пусть a = {format_answer(a)} м/с², R = {R} м. "
        "Найди угловую скорость ω."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(ω),
        "params": {"a": a, "R": R},
        "hidden_params": {"_hidden_omega": ω},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 49) Работа тока: найти R (A = U²t/R)
# ─────────────────────────────────────────────────────────────────────────────
def _generate_work_of_current_find_R() -> dict:
    subtype = "work_of_current_find_R"
    plot_id = "work_of_current_find_R"

    U = random.choice([10, 20])   # В
    t = random.choice([10, 20])   # с
    R = random.choice([5, 10])    # Ом
    A = U**2 * t / R

    text = (
        f"Работа тока равна {format_answer(A)} Дж при напряжении {U} В и времени {t} с. "
        "Найди сопротивление цепи."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(R),
        "params": {"U": U, "t": t, "A": A},
        "hidden_params": {"_hidden_R": R},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 50) Закон Джоуля-Ленца: найти Q (Q = I²Rt)
# ─────────────────────────────────────────────────────────────────────────────
def _generate_joule_lenz_find_Q() -> dict:
    subtype = "joule_lenz_find_Q"
    plot_id = "joule_lenz_find_Q"

    I = random.choice([2, 3])    # А
    R = random.choice([4, 6])    # Ом
    t = random.choice([10, 20])  # с
    Q = I**2 * R * t

    text = (
        f"Найди количество теплоты, выделившееся при прохождении тока силой {I} А "
        f"через проводник сопротивлением {R} Ом за время {t} с."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(Q),
        "params": {"I": I, "R": R, "t": t},
        "hidden_params": {"_hidden_Q": Q},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 51) Длина шага в метрах
# ─────────────────────────────────────────────────────────────────────────────
def _generate_step_length_meters() -> dict:
    subtype = "step_length_meters"
    plot_id = "step_length_meters"

    step = random.choice([0.6, 0.7, 0.8])  # м
    n = random.randint(20, 50)
    s = step * n

    text = (
        f"Во время прогулки школьник сделал {n} шагов, длина каждого шага {format_answer(step)} м. "
        "Найди путь, пройденный школьником (в метрах)."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(s),
        "params": {"step": step, "n": n},
        "hidden_params": {"_hidden_s": s},
        "constants": None
    }
# ─────────────────────────────────────────────────────────────────────────────
# 52) Длина шага в сантиметрах
# ─────────────────────────────────────────────────────────────────────────────
def _generate_step_length_cm() -> dict:
    subtype = "step_length_cm"
    plot_id = "step_length_cm"

    step = random.choice([60, 70, 80])  # см
    n = random.randint(50, 100)
    s = step * n / 100  # переводим в метры

    text = (
        f"Девочка идёт по дорожке, делая шаги длиной {step} см. "
        f"За {n} шагов она прошла путь. Найди его длину (в метрах)."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(s),
        "params": {"step_cm": step, "n": n},
        "hidden_params": {"_hidden_s_m": s},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 53) Перевод шагов в километры
# ─────────────────────────────────────────────────────────────────────────────
def _generate_step_length_km() -> dict:
    subtype = "step_length_km"
    plot_id = "step_length_km"

    step = random.choice([0.7, 0.8])  # м
    n = random.randint(1000, 2000)
    s = step * n / 1000  # переводим в километры

    text = (
        f"Во время экскурсии турист прошёл {n} шагов длиной {format_answer(step)} м каждый. "
        "Найди путь в километрах."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(s),
        "params": {"step_m": step, "n": n},
        "hidden_params": {"_hidden_s_km": s},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 54) Расстояние до молнии: s = 330t
# ─────────────────────────────────────────────────────────────────────────────
def _generate_lightning_distance() -> dict:
    subtype = "lightning_distance"
    plot_id = "lightning_distance"

    t = random.randint(2, 6)       # время в секундах
    s = V_SOUND * t                # ← ИСПОЛЬЗУЕМ КОНСТАНТУ

    text = (
        f"Во время грозы мальчик увидел молнию, а через {t} с услышал гром. "
        "Определите расстояние до места удара молнии (в метрах)."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(s),
        "params": {"t": t},
        "hidden_params": {"_hidden_s": s},
        "constants": {"V_SOUND": V_SOUND}  # ← ИСПОЛЬЗУЕМ КОНСТАНТУ
    }
# ─────────────────────────────────────────────────────────────────────────────
# 55) Стоимость поездки на такси (линейная): C = k·t
# ─────────────────────────────────────────────────────────────────────────────
def _generate_taxi_cost_linear() -> dict:
    subtype = "taxi_cost_linear"
    plot_id = "taxi_cost_linear"

    k = random.choice([5, 10])   # руб/мин
    t = random.randint(10, 30)   # минуты
    C = k * t                    # стоимость

    text = (
        f"Стоимость поездки на такси рассчитывается по формуле C = {k}·t, "
        "где t — время в минутах. Найди стоимость поездки при времени "
        f"{t} минут."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(C),
        "params": {"k": k, "t": t},
        "hidden_params": {"_hidden_C": C},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 56) Стоимость поездки с порогом времени
# ─────────────────────────────────────────────────────────────────────────────
def _generate_taxi_cost_with_threshold() -> dict:
    subtype = "taxi_cost_with_threshold"
    plot_id = "taxi_cost_with_threshold"

    c0 = 100  # фиксированная цена за первые 5 минут
    c1 = 10   # цена за каждую следующую минуту
    t = random.randint(6, 20)  # общее время поездки (мин)
    C = c0 + c1 * (t - 5)

    text = (
        "Стоимость поездки на такси составляет 100 руб за первые 5 минут, "
        "а за каждую последующую минуту — 10 руб. "
        f"Сколько стоит поездка длительностью {t} минут?"
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(C),
        "params": {"c0": c0, "c1": c1, "t": t},
        "hidden_params": {"_hidden_C": C},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 57) Стоимость рытья колодца (линейная): C = k·n
# ─────────────────────────────────────────────────────────────────────────────
def _generate_well_cost_linear() -> dict:
    subtype = "well_cost_linear"
    plot_id = "well_cost_linear"

    k = random.choice([500, 600])  # руб/кольцо
    n = random.randint(5, 15)      # количество колец
    C = k * n

    text = (
        f"Фирма берёт {k} руб за установку одного кольца колодца. "
        f"Сколько стоит колодец из {n} колец?"
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(C),
        "params": {"k": k, "n": n},
        "hidden_params": {"_hidden_C": C},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 58) Стоимость колодца с постоянным и переменным членом
# ─────────────────────────────────────────────────────────────────────────────
def _generate_well_cost_with_constant() -> dict:
    subtype = "well_cost_with_constant"
    plot_id = "well_cost_with_constant"

    c0 = 1000  # фиксированная доставка
    c1 = random.choice([400, 500])  # руб/кольцо
    n = random.randint(5, 10)       # количество колец
    C = c0 + c1 * n

    text = (
        f"Фирма берёт {c0} руб за доставку и {c1} руб за каждое кольцо. "
        f"Сколько будет стоить колодец из {n} колец?"
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(C),
        "params": {"c0": c0, "c1": c1, "n": n},
        "hidden_params": {"_hidden_C": C},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 59) Две фирмы: сравнить стоимость
# ─────────────────────────────────────────────────────────────────────────────
def _generate_well_cost_two_companies() -> dict:
    subtype = "well_cost_two_companies"
    plot_id = "well_cost_two_companies"

    c1, k1 = 800, 500  # первая фирма: фикс + за кольцо
    c2, k2 = 0, 600    # вторая фирма: только за кольцо
    n = random.randint(5, 15)

    C1 = c1 + k1 * n
    C2 = c2 + k2 * n
    cheaper = "первая" if C1 < C2 else "вторая"

    text = (
        f"Первая фирма берёт {c1} руб + {k1} руб за кольцо. "
        f"Вторая фирма берёт {k2} руб за кольцо. "
        f"При установке {n} колец колодца у какой фирмы дешевле?"
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": cheaper,
        "params": {"c1": c1, "k1": k1, "c2": c2, "k2": k2, "n": n},
        "hidden_params": {"_hidden_C1": C1, "_hidden_C2": C2},
        "constants": None
    }
# ─────────────────────────────────────────────────────────────────────────────
# 60) Перевод температуры: F → C
# ─────────────────────────────────────────────────────────────────────────────
def _generate_temperature_F_to_C() -> dict:
    subtype = "temperature_F_to_C"
    plot_id = "temperature_F_to_C"

    F = random.choice([32, 50, 68, 86])
    C = (F - 32) / 1.8

    text = f"Температура воздуха равна {F}°F. Переведите её в градусы Цельсия."

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(C),
        "params": {"F": F},
        "hidden_params": {"_hidden_C": C},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 61) Перевод температуры: C → F
# ─────────────────────────────────────────────────────────────────────────────
def _generate_temperature_C_to_F() -> dict:
    subtype = "temperature_C_to_F"
    plot_id = "temperature_C_to_F"

    C = random.choice([-10, 0, 10, 20, 30])
    F = 1.8 * C + 32

    text = f"Температура воздуха равна {C}°C. Переведите её в градусы Фаренгейта."

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(F),
        "params": {"C": C},
        "hidden_params": {"_hidden_F": F},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 62) Отрицательные температуры (вариация)
# ─────────────────────────────────────────────────────────────────────────────
def _generate_temperature_negative() -> dict:
    subtype = "temperature_negative"
    plot_id = "temperature_negative"

    C = random.choice([-20, -15, -5])
    F = 1.8 * C + 32

    text = f"Температура на улице {C}°C. Сколько это градусов Фаренгейта?"

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(F),
        "params": {"C": C},
        "hidden_params": {"_hidden_F": F},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# 63–66) Дополнительные жизненные варианты (чтобы всё покрыть)
# ─────────────────────────────────────────────────────────────────────────────
def _generate_step_daily_walk() -> dict:
    subtype = "step_daily_walk"
    plot_id = "step_daily_walk"

    step = 0.75
    n = 4000
    s = step * n / 1000

    text = (
        "Ученик идёт домой пешком каждый день, делая около 4000 шагов длиной 0,75 м. "
        "Найди длину пути (в км)."
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(s),
        "params": {"step": step, "n": n},
        "hidden_params": {"_hidden_s_km": s},
        "constants": None
    }


def _generate_taxi_night_tariff() -> dict:
    subtype = "taxi_night_tariff"
    plot_id = "taxi_night_tariff"

    c0 = 150
    c1 = 15
    t = 12
    C = c0 + c1 * (t - 5)

    text = (
        "Ночью такси берёт 150 руб за первые 5 минут и 15 руб за каждую последующую. "
        f"Сколько стоит поездка длительностью {t} минут?"
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(C),
        "params": {"c0": c0, "c1": c1, "t": t},
        "hidden_params": {"_hidden_cost": C},
        "constants": None
    }


def _generate_well_cost_example_story() -> dict:
    subtype = "well_cost_example_story"
    plot_id = "well_cost_example_story"

    c0, k = 1200, 550
    n = 8
    C = c0 + k * n

    text = (
        "Семья решила выкопать колодец из 8 колец. "
        f"Фирма берёт {c0} руб за выезд и {k} руб за кольцо. "
        "Сколько стоит колодец?"
    )

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(C),
        "params": {"c0": c0, "k": k, "n": n},
        "hidden_params": {"_hidden_cost": C},
        "constants": None
    }


def _generate_temperature_extreme() -> dict:
    subtype = "temperature_extreme"
    plot_id = "temperature_extreme"

    C = -40
    F = 1.8 * C + 32

    text = "В Якутске зимой температура опустилась до −40°C. Сколько это градусов Фаренгейта?"

    return {
        "subtype": subtype,
        "plot_id": plot_id,
        "text": text,
        "answer": format_answer(F),
        "params": {"C": C},
        "hidden_params": {"_hidden_F": F},
        "constants": None
    }

# ─────────────────────────────────────────────────────────────────────────────
# Общая карта генераторов
# ─────────────────────────────────────────────────────────────────────────────
GENERATOR_MAP: Dict[str, Callable[[], Tuple[str, str, str]]] = {
    # Геометрия (расчёты)
    "area_triangle_ah": _generate_area_triangle_ah,
    "area_triangle_sides_sin": _generate_area_triangle_sides_sin,
    "area_triangle_inscribed_circle": _generate_area_triangle_inscribed_circle,
    "area_parallelogram_ah": _generate_area_parallelogram_ah,
    "area_parallelogram_ab_sin": _generate_area_parallelogram_ab_sin,
    "area_rhombus_d1d2": _generate_area_rhombus_d1d2,
    "area_trapezoid_bases_h": _generate_area_trapezoid_bases_h,
    "area_quadrilateral_d1d2_sin_S": _generate_area_quadrilateral_d1d2_sin_S,
    "area_quadrilateral_find_d_by_S": _generate_area_quadrilateral_find_d_by_S,
    "bisector_length_equal_legs": _generate_bisector_length_equal_legs,
    "inscribed_circle_radius_triangle": _generate_inscribed_circle_radius_triangle,
    "inscribed_circle_radius_right_triangle": _generate_inscribed_circle_radius_right_triangle,
    "circumscribed_circle_area_by_R": _generate_circumscribed_circle_area_by_R,
    "circumscribed_circle_R_by_side_angle": _generate_circumscribed_circle_R_by_side_angle,
    "polygon_angles_sum": _generate_polygon_angles_sum,
    "height_pyramid_by_V": _generate_height_pyramid_by_V,
    "circumference_length_find_R": _generate_circumference_length_find_R,
    "area_quadrilateral_d1d2_sin_find_d": _generate_area_quadrilateral_d1d2_sin_find_d,
    "bisector_length_general": _generate_bisector_length_general,
    "circumscribed_circle_radius_equilateral": _generate_circumscribed_circle_radius_equilateral,
    # Физика (маятник, энергия)
    "pendulum_period_by_length": _generate_pendulum_period_by_length,
    "pendulum_length_by_T": _generate_pendulum_length_by_T,
    "kinetic_energy_find_v": _generate_kinetic_energy_find_v,
    "kinetic_energy_find_E": _generate_kinetic_energy_find_E,
    "potential_energy_find_m": _generate_potential_energy_find_m,
    "potential_energy_find_E": _generate_potential_energy_find_E,
    "mechanical_energy_total": _generate_mechanical_energy_total,
    "mechanical_energy_find_m": _generate_mechanical_energy_find_m,
    "archimedes_force_find_F": _generate_archimedes_force_find_F,
    "archimedes_force_find_V": _generate_archimedes_force_find_V,
    "newton_gravity_find_m": _generate_newton_gravity_find_m,
    "newton_gravity_find_F": _generate_newton_gravity_find_F,
    "coulomb_law_find_q": _generate_coulomb_law_find_q,
    "coulomb_law_find_F": _generate_coulomb_law_find_F,
    "ohm_power_find_R": _generate_ohm_power_find_R,
    "ohm_power_find_P": _generate_ohm_power_find_P,
    "joule_lenz_find_t": _generate_joule_lenz_find_t,
    "joule_lenz_find_R": _generate_joule_lenz_find_R,
    "work_of_current_find_A": _generate_work_of_current_find_A,
    "capacitor_energy_find_W": _generate_capacitor_energy_find_W,
    "capacitor_energy_find_W_q": _generate_capacitor_energy_find_W_q,
    "gas_law_find_P": _generate_gas_law_find_P,
    "gas_law_find_T": _generate_gas_law_find_T,
    "gas_law_find_V": _generate_gas_law_find_V,
    "gas_law_find_n": _generate_gas_law_find_n,
    "centripetal_acceleration_find_R": _generate_centripetal_acceleration_find_R,
    "centripetal_acceleration_find_a": _generate_centripetal_acceleration_find_a,
    "centripetal_acceleration_find_omega": _generate_centripetal_acceleration_find_omega,
    "work_of_current_find_R": _generate_work_of_current_find_R,
    "joule_lenz_find_Q": _generate_joule_lenz_find_Q,
    # Разные жизненные задачи
    "step_length_meters": _generate_step_length_meters,
    "step_length_cm": _generate_step_length_cm,
    "step_length_km": _generate_step_length_km,
    "lightning_distance": _generate_lightning_distance,
    "taxi_cost_linear": _generate_taxi_cost_linear,
    "taxi_cost_with_threshold": _generate_taxi_cost_with_threshold,
    "well_cost_linear": _generate_well_cost_linear,
    "well_cost_with_constant": _generate_well_cost_with_constant,
    "well_cost_two_companies": _generate_well_cost_two_companies,
    "temperature_F_to_C": _generate_temperature_F_to_C,
    "temperature_C_to_F": _generate_temperature_C_to_F,
    "temperature_negative": _generate_temperature_negative,
    "step_daily_walk": _generate_step_daily_walk,
    "taxi_night_tariff": _generate_taxi_night_tariff,
    "well_cost_example_story": _generate_well_cost_example_story,
    "temperature_extreme": _generate_temperature_extreme,
}

# ─────────────────────────────────────────────────────────────────────────────
# Главная функция-дирижёр
# ─────────────────────────────────────────────────────────────────────────────
async def generate_task_12_by_subtype(
    subtype_key: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    if subtype_key is None:
        subtype_key = random.choice(list(GENERATOR_MAP.keys()))
    generator = GENERATOR_MAP.get(subtype_key)
    if not generator:
        return None

    res = generator()

    # Если генератор уже возвращает dict — отдаем как есть
    if isinstance(res, dict):
        for k in ("subtype", "text", "answer"):
            if k not in res:
                raise ValueError(f"Generator '{subtype_key}' вернул dict без обязательного поля '{k}'")
        return res

    # Иначе поддерживаем старый формат (tuple)
    try:
        key, text, answer = res
    except Exception as e:
        raise ValueError(f"Generator '{subtype_key}' вернул неожиданный формат: {type(res)} ({e})")

    return {
        "subtype": key,
        "text": text,
        "answer": answer,
    }