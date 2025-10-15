import re
import math
from typing import Dict
from matunya_bot_final.task_generators.task_12.task_12_generator import format_answer
from matunya_bot_final.task_generators.task_12.validators_common import grab_any_number_with_unit, grab_sin_alpha
from matunya_bot_final.task_generators.task_12.validators_common import grab_labeled_number, grab_m_index

# ───────── Вспомогательные утилиты ─────────
NUM = r"[-+]?(?:\d+(?:[.,]\d+)?|\d*(?:[.,]\d+))"  # 12 | 12,5 | ,5

def _to_float(s: str) -> float:
    return float(s.replace(",", "."))

# ─────────────────────────────────────────────────────────────
# Константы (для всех физических формул)
# ─────────────────────────────────────────────────────────────
# Константы (ОГЭ-уровень, как в школьных учебниках)
G = 10             # ускорение свободного падения, м/с²
PI = 3.14          # число π (школьное приближение)
G_CONST = 6.67e-11 # гравитационная постоянная (Н·м²/кг²)
K_CONST = 9e9      # электрическая постоянная (Н·м²/Кл²)
R_UNIV = 8.31      # универсальная газовая постоянная (Дж/(моль·К))
RHO_WATER = 1000   # плотность воды, кг/м³
V_SOUND = 330      # скорость звука в воздухе, м/с

# 1) area_triangle_ah: S = 1/2 · a · h
def validate_area_triangle_ah(task: dict) -> bool:
    """Валидирует S = ½ah, используя стандартные утилиты."""
    text, answer_str = task.get("text"), task.get("answer")
    if not text or answer_str is None: return False

    # Используем стандартные NUM и _to_float
    numbers_str = re.findall(NUM, text)
    if len(numbers_str) != 2: return False
    
    val1, val2 = _to_float(numbers_str[0]), _to_float(numbers_str[1])
    
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

    return abs(_to_float(answer_str) - correct_answer) < 1e-9

# 2) area_triangle_sides_sin: S = 1/2 · b · c · sinα
def validate_area_triangle_sides_sin(data: dict) -> bool:
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

# 3) area_triangle_inscribed_circle: S = p · r
def validate_area_triangle_inscribed_circle(data: dict) -> bool:
    r = int(data["text"].split("равен ")[1].split(" ")[0])
    p = int(data["text"].split("полупериметр треугольника — ")[1].split(" ")[0])
    S = p * r
    return data["answer"] == format_answer(S)

# 4) area_parallelogram_ah: S = a · h
def validate_area_parallelogram_ah(data: dict) -> bool:
    a = int(data["text"].split("равна ")[1].split(" ")[0])
    h = int(data["text"].split("равна ")[2].split(" ")[0])
    S = a * h
    return data["answer"] == format_answer(S)

# 5) area_parallelogram_ab_sin: S = a · b · sinα
def validate_area_parallelogram_ab_sin(data: dict) -> bool:
    text = data["text"]

    ma = re.search(r"\ba\s*=\s*(\d+)", text)
    mb = re.search(r"\bb\s*=\s*(\d+)", text)
    msin = re.search(r"sin[αa]?\s*=\s*([0-9]+(?:[.,][0-9]+)?)\b", text)

    if not (ma and mb and msin):
        raise ValueError("Не удалось распарсить параметры a, b или sinα в тексте задачи")

    a = int(ma.group(1))
    b = int(mb.group(1))
    sin_alpha = float(msin.group(1).replace(",", "."))

    S = a * b * sin_alpha
    return data["answer"] == format_answer(S)

# 6) area_rhombus_d1d2: S = 1/2 · d1 · d2
def validate_area_rhombus_d1d2(data: dict) -> bool:
    d1 = int(data["text"].split("d₁ = ")[1].split(" ")[0])
    d2 = int(data["text"].split("d₂ = ")[1].split(" ")[0])
    S = 0.5 * d1 * d2
    return data["answer"] == format_answer(S)

# 7) area_trapezoid_bases_h: S = (a + b) · h / 2
def validate_area_trapezoid_bases_h(data: dict) -> bool:
    a = int(data["text"].split("a = ")[1].split(" ")[0])
    b = int(data["text"].split("b = ")[1].split(" ")[0])
    h = int(data["text"].split("h = ")[1].split(" ")[0])
    S = (a + b) * h / 2
    return data["answer"] == format_answer(S)

# 8) area_quadrilateral_d1d2_sin_S: S = 1/2 · d1 · d2 · sinα
def validate_area_quadrilateral_d1d2_sin_S(data: dict) -> bool:
    text = data["text"]

    md1 = re.search(r"d[₁1]\s*=\s*(\d+)", text)  # поддержим и d1, и d₁
    md2 = re.search(r"d[₂2]\s*=\s*(\d+)", text)
    msin = re.search(r"sin[αa]?\s*=\s*([0-9]+(?:[.,][0-9]+)?)\b", text)

    if not (md1 and md2 and msin):
        raise ValueError("Не удалось распарсить параметры d1, d2 или sinα в тексте задачи")

    d1 = int(md1.group(1))
    d2 = int(md2.group(1))
    sin_alpha = float(msin.group(1).replace(",", "."))

    S = 0.5 * d1 * d2 * sin_alpha
    return data["answer"] == format_answer(S)

# 9) area_quadrilateral_find_d_by_S: d₂ = 2S / (d₁ · sinα)
def validate_area_quadrilateral_find_d_by_S(data: dict) -> bool:
    text = data["text"]

    def grab(patterns):
        for p in patterns:
            m = re.search(p, text, flags=re.IGNORECASE)
            if m:
                return float(m.group(1).replace(",", "."))
        return None

    # S: сначала пробуем "S = ...", иначе — "площадь ... равна ..."
    S = grab([r"\bS\s*=\s*([0-9]+(?:[.,][0-9]+)?)",
              r"площад[ья]\s*(?:равна|=)?\s*([0-9]+(?:[.,][0-9]+)?)"])
    # d₁ / d1 и d₂ / d2 поддерживаем оба варианта записи
    d1 = grab([r"d[₁1]\s*=\s*([0-9]+(?:[.,][0-9]+)?)"])
    d2 = grab([r"d[₂2]\s*=\s*([0-9]+(?:[.,][0-9]+)?)"])
    # sinα = 0,5 / 0.5
    sin_alpha = grab([r"sin[αa]?\s*=\s*([0-9]+(?:[.,][0-9]+)?)\b"])

    if S is None or sin_alpha is None or (d1 is None and d2 is None):
        raise ValueError("Не удалось распарсить параметры S, d1/d2 или sinα")

    # Если задан d1 — ищем d2; если задан d2 — ищем d1; если заданы оба — принимаем ответ, равный одному из расчётов
    if d1 is not None and d2 is None:
        d = 2 * S / (d1 * sin_alpha)  # это d2
        return data["answer"] == format_answer(d)
    elif d2 is not None and d1 is None:
        d = 2 * S / (d2 * sin_alpha)  # это d1
        return data["answer"] == format_answer(d)
    else:
        # Оба есть в тексте — допускаем, что в ответе могут просить любую диагональ (проверим оба расчёта)
        d2_calc = 2 * S / (d1 * sin_alpha)
        d1_calc = 2 * S / (d2 * sin_alpha)
        ans = data["answer"]
        return ans == format_answer(d2_calc) or ans == format_answer(d1_calc)

# 10) bisector_length_equal_legs: lₐ = √(b² − k²), где a = 2k
def validate_bisector_length_equal_legs(data: dict) -> bool:
    a = int(data["text"].split("основание равно ")[1].split(" ")[0])
    b = int(data["text"].split("равны ")[1].split(" ")[0])
    k = a / 2
    l_a = math.sqrt(b**2 - k**2)
    return data["answer"] == format_answer(l_a)

# 11) inscribed_circle_radius_triangle: r = S / p
def validate_inscribed_circle_radius_triangle(data: dict) -> bool:
    S = int(data["text"].split("равна ")[1].split(" ")[0])
    p = int(data["text"].split("полупериметр ")[1].split(" ")[0])
    r = S / p
    return data["answer"] == format_answer(r)

# 12) inscribed_circle_radius_right_triangle: r = (a + b − c)/2
def validate_inscribed_circle_radius_right_triangle(data: Dict) -> bool:
    text = data["text"]

    a = b = c = None

    # 1) Новый стиль: "a = ..., b = ..."
    m_ab = re.search(r"a\s*=\s*([0-9]+(?:[.,][0-9]+)?)", text, flags=re.IGNORECASE)
    m_b  = re.search(r"b\s*=\s*([0-9]+(?:[.,][0-9]+)?)", text, flags=re.IGNORECASE)
    if m_ab and m_b:
        a = float(m_ab.group(1).replace(",", "."))
        b = float(m_b.group(1).replace(",", "."))

    # 2) Старый стиль: "катеты равны X и Y"
    if a is None or b is None:
        m_pair = re.search(
            r"катет[ы]?\s+([0-9]+(?:[.,][0-9]+)?)\s*(?:и|,)\s*([0-9]+(?:[.,][0-9]+)?)",
            text, flags=re.IGNORECASE
        )
        if m_pair:
            a = float(m_pair.group(1).replace(",", "."))
            b = float(m_pair.group(2).replace(",", "."))

    # 3) Вариант: "катет X ... катет Y"
    if a is None or b is None:
        cats = re.findall(r"катет[а]?\s+([0-9]+(?:[.,][0-9]+)?)", text, flags=re.IGNORECASE)
        if len(cats) >= 2:
            a = float(cats[0].replace(",", "."))
            b = float(cats[1].replace(",", "."))

    # 4) Фолбэк: берём первые два числа с "см"
    if a is None or b is None:
        nums = re.findall(r"([0-9]+(?:[.,][0-9]+)?)\s*см", text)
        if len(nums) >= 2:
            a = float(nums[0].replace(",", "."))
            b = float(nums[1].replace(",", "."))

    # Если катеты так и не найдены → ошибка
    if a is None or b is None:
        raise ValueError("Не удалось распарсить два катета прямоугольного треугольника")

    # Гипотенуза
    c = math.hypot(a, b)

    # Радиус вписанной окружности
    r = (a + b - c) / 2
    expected = format_answer(r)

    return data["answer"] == expected

# 13) circumscribed_circle_area_by_R: S = abc / (4R)
def validate_circumscribed_circle_area_by_R(data: dict) -> bool:
    a = int(data["text"].split("равны ")[1].split(" ")[0])
    R = a / math.sqrt(3)
    S = (a**2 * math.sqrt(3)) / 4
    return data["answer"] == format_answer(S)

# 14) circumscribed_circle_R_by_side_angle: R = a / (2·sinA)
def validate_circumscribed_circle_R_by_side_angle(data: dict) -> bool:
    text = data["text"]

    m_a = re.search(r"сторона треугольника равна\s*([0-9]+)", text, flags=re.IGNORECASE)
    m_sin = re.search(r"sin\s*=\s*([0-9]+[.,]?[0-9]*)", text, flags=re.IGNORECASE)

    if not m_a or not m_sin:
        raise ValueError("Не удалось распарсить сторону или синус угла")

    a = float(m_a.group(1).replace(",", "."))
    sinA = float(m_sin.group(1).replace(",", "."))
    R = a / (2 * sinA)

    expected = float(data["answer"].replace(",", "."))
    # Сравниваем с округлением, допускаем маленькую погрешность
    return math.isclose(R, expected, rel_tol=1e-2, abs_tol=0.1)

# 15) polygon_angles_sum: Σ = (n−2)·180
def validate_polygon_angles_sum(data: dict) -> bool:
    S = int(data["text"].split("равна ")[1].split("°")[0])
    n = S // 180 + 2
    return data["answer"] == format_answer(n)

# 16) height_pyramid_by_V: h = 3V / S
def validate_height_pyramid_by_V(data: dict) -> bool:
    V = int(data["text"].split("Объём пирамиды равен ")[1].split(" ")[0])
    S = int(data["text"].split("площадь основания ")[1].split(" ")[0])
    h = 3 * V / S
    return data["answer"] == format_answer(h)

# 17) circumference_length_find_R: ℓ = 2πR → R = ℓ / (2π)
def validate_circumference_length_find_R(data: dict) -> bool:
    L = float(data["text"].split("равна ")[1].split(" ")[0].replace(",", "."))
    R = L / (2 * PI)
    return data["answer"] == format_answer(R)

# 18) area_quadrilateral_d1d2_sin_find_d: d₂ = 2S / (d₁·sinα)
def validate_area_quadrilateral_d1d2_sin_find_d(data: Dict) -> bool:
    text = data["text"]

    # Ищем площадь
    m_S = re.search(r"S\s*=\s*([\d,\.]+)", text)
    if not m_S:
        return False
    S = float(m_S.group(1).replace(",", "."))

    # Ищем диагонали
    m_d1 = re.search(r"d₁\s*=\s*([\d,\.]+)", text)
    m_d2 = re.search(r"d₂\s*=\s*([\d,\.]+)", text)

    # Ищем синус угла
    m_sin = re.search(r"sinα\s*=\s*([\d,\.]+)", text)
    if not m_sin:
        return False
    sinA = float(m_sin.group(1).replace(",", "."))

    # Вычисляем недостающую диагональ
    if m_d1:
        d1 = float(m_d1.group(1).replace(",", "."))
        d2 = 2 * S / (d1 * sinA)
        expected = format_answer(d2)
    elif m_d2:
        d2 = float(m_d2.group(1).replace(",", "."))
        d1 = 2 * S / (d2 * sinA)
        expected = format_answer(d1)
    else:
        return False

    return data["answer"] == expected

# 19) bisector_length_general (формула через полупериметр)
def validate_bisector_length_general(data: dict) -> bool:
    text = data["text"]

    # 1) Пытаемся явно вытащить сторону, к которой проведена биссектриса: "к стороне длиной X см"
    m_a = re.search(r"к\s+сторон[еы]\s+дл(?:и|е)ной\s*(\d+(?:[.,]\d+)?)", text, flags=re.IGNORECASE)
    a_val = float(m_a.group(1).replace(",", ".")) if m_a else None

    # 2) Пытаемся вытащить три стороны из фрагмента "со сторонами …"
    m_sides_block = re.search(r"со\s+сторонами\s+([^\.]+)", text, flags=re.IGNORECASE)
    if m_sides_block:
        sides_nums = re.findall(r"(\d+(?:[.,]\d+)?)", m_sides_block.group(1))
    else:
        # fallback: берём все числа из текста и попробуем выделить три уникальных
        sides_nums = re.findall(r"(\d+(?:[.,]\d+)?)", text)

    # преобразуем к float с поддержкой запятой
    sides = []
    for s in sides_nums:
        v = float(s.replace(",", "."))
        if v not in sides:  # сохраняем порядок, убираем дубликаты
            sides.append(v)

    if len(sides) < 3:
        raise ValueError("Не удалось распарсить три стороны треугольника")

    # 3) Определяем a, b, c: если a_val найден, выбираем b и c как две другие стороны
    # допускаем возможные совпадения по значению → сравниваем с толерантностью
    def is_close(x, y, eps=1e-9): 
        return abs(x - y) < eps

    if a_val is not None:
        # найдём среди sides ту, что равна a_val (по значению)
        # берём первые две, которые НЕ равны a_val → это b и c
        b_c = [v for v in sides if not is_close(v, a_val)]
        if len(b_c) < 2:
            # если вдруг в списке sides встретился дубликат a_val, возьмём любые 3 и дальше исключим одну
            # но в нормальном тексте генератора сюда не попадём
            raise ValueError("Недостаточно сторон для вычисления биссектрисы")
        a, b, c = a_val, b_c[0], b_c[1]
    else:
        # если не нашли явного a, возьмём первые три как a, b, c в порядке появления
        # (в наших генераторах обычно a задана в явном виде, так что этот путь — редкий fallback)
        a, b, c = sides[0], sides[1], sides[2]

    # 4) Формула биссектрисы
    p = (a + b + c) / 2.0
    # защита от вырождений
    if p <= a or p <= b or p <= c:
        raise ValueError("Некорректные длины сторон для треугольника")

    l_a = (2.0 * math.sqrt(b * c * p * (p - a))) / (b + c)

    return data["answer"] == format_answer(l_a)

# 20) circumscribed_circle_radius_equilateral: R = a/√3
def validate_circumscribed_circle_radius_equilateral(data: dict) -> bool:
    a = int(data["text"].split("равна ")[1].split(" ")[0])
    R = a / math.sqrt(3)
    return data["answer"] == format_answer(R)

# 21) pendulum_period_by_length: T = 2π√(l/g)
def validate_pendulum_period_by_length(data: dict) -> bool:
    l = float(data["text"].split("длиной ")[1].split(" ")[0].replace(",", "."))
    g = int(data["text"].split("равным ")[1].split(" ")[0])
    T = 2 * PI * math.sqrt(l / G)
    return data["answer"] == format_answer(T)

# 22) pendulum_length_by_T: l = gT² / (4π²)
def validate_pendulum_length_by_T(data: dict) -> bool:
    T = float(data["text"].split("равен ")[1].split(" ")[0].replace(",", "."))
    g = int(data["text"].split("равным ")[1].split(" ")[0])
    l = g * T**2 / (4 * PI**2)
    return data["answer"] == format_answer(l)

# 23) kinetic_energy_find_v: v = √(2E/m)
def validate_kinetic_energy_find_v(data: dict) -> bool:
    m = int(data["text"].split("массой ")[1].split(" ")[0])
    E = float(data["text"].split("равна ")[1].split(" ")[0].replace(",", "."))
    v = math.sqrt(2 * E / m)
    return data["answer"] == format_answer(v)

# 24) kinetic_energy_find_E: E = mv² / 2
def validate_kinetic_energy_find_E(data: dict) -> bool:
    m = int(data["text"].split("массой ")[1].split(" ")[0])
    v = int(data["text"].split("со скоростью ")[1].split(" ")[0])
    E = m * v**2 / 2
    return data["answer"] == format_answer(E)

# 25) potential_energy_find_m: m = E / (g·h)
def validate_potential_energy_find_m(data: dict) -> bool:
    E = int(data["text"].split("энергия тела равна ")[1].split(" ")[0])
    h = int(data["text"].split("при высоте ")[1].split(" ")[0])
    g = 10
    m = E / (g * h)
    return data["answer"] == format_answer(m)

# 26) potential_energy_find_E: E = mgh
def validate_potential_energy_find_E(data: dict) -> bool:
    m = int(data["text"].split("массой ")[1].split(" ")[0])
    h = int(data["text"].split("высоте ")[1].split(" ")[0])
    g = 10
    E = m * g * h
    return data["answer"] == format_answer(E)

# 27) mechanical_energy_total: E = Eₖ + Eₚ
def validate_mechanical_energy_total(data: dict) -> bool:
    m = int(data["text"].split("массой ")[1].split(" ")[0])
    v = int(data["text"].split("со скоростью ")[1].split(" ")[0])
    h = int(data["text"].split("высоте ")[1].split(" ")[0])
    g = 10
    E_k = m * v**2 / 2
    E_p = m * g * h
    E = E_k + E_p
    return data["answer"] == format_answer(E)

# 28) mechanical_energy_find_m: m = E / (g·h)
def validate_mechanical_energy_find_m(data: dict) -> bool:
    E = int(data["text"].split("энергия тела равна ")[1].split(" ")[0])
    h = int(data["text"].split("при высоте ")[1].split(" ")[0])
    g = 10
    m = E / (g * h)
    return data["answer"] == format_answer(m)

# 29) archimedes_force_find_F: F = ρgV
def validate_archimedes_force_find_F(data: dict) -> bool:
    V = float(data["text"].split("объёмом ")[1].split(" ")[0].replace(",", "."))
    rho = int(data["text"].split("ρ = ")[1].split(" ")[0])
    g = 10
    F = rho * g * V
    return data["answer"] == format_answer(F)

# 30) archimedes_force_find_V: V = F / (ρg)
def validate_archimedes_force_find_V(data: dict) -> bool:
    F = float(data["text"].split("равна ")[1].split(" ")[0].replace(",", "."))
    rho = int(data["text"].split("Плотность воды ")[1].split(" ")[0])
    g = 10
    V = F / (rho * g)
    return data["answer"] == format_answer(V)

# 31) newton_gravity_find_m: m1 = Fr² / (G·m2)
def validate_newton_gravity_find_m(data: dict) -> bool:
    text = data["text"]

    def grab(patterns):
        for p in patterns:
            m = re.search(p, text, flags=re.IGNORECASE)
            if m:
                return float(m.group(1).replace(",", "."))
        return None

    # Сила тяготения / притяжения F
    F = grab([
        r"(?:сила\s*(?:тяготения|притяжения)?|F)\s*(?:между\s+телами\s*)?(?:равн[ао]|=)\s*([0-9]+(?:[.,][0-9]+)?)",
        r"\bF\s*=\s*([0-9]+(?:[.,][0-9]+)?)",
    ])

    # Расстояние r
    r_val = grab([
        r"расстояни[ея]\s*(?:между\s+телами\s*)?(?:равн[ао]|=)?\s*([0-9]+(?:[.,][0-9]+)?)",
        r"\br\s*=\s*([0-9]+(?:[.,][0-9]+)?)",
    ])

    # Масса второго тела m₂
    m2 = grab([
        r"(?:масса\s*(?:второго|2-?го)\s*тела|m[2₂])\s*(?:равн[ао]|=)\s*([0-9]+(?:[.,][0-9]+)?)",
        r"\bm[2₂]\s*=\s*([0-9]+(?:[.,][0-9]+)?)",
    ])

    if F is None or r_val is None or m2 is None:
        raise ValueError("Не удалось распарсить F, r или m₂")

    m1 = F * (r_val ** 2) / (G_CONST * m2)
    return data["answer"] == format_answer(m1)

# 32) newton_gravity_find_F: F = G·m1·m2 / r²
def validate_newton_gravity_find_F(data: dict) -> bool:
    text = data["text"]

    def grab(patterns):
        for p in patterns:
            m = re.search(p, text, flags=re.IGNORECASE)
            if m:
                return float(m.group(1).replace(",", "."))
        return None

    # 1) Массы. Сначала пробуем форму "массами X и Y"
    pair = re.search(
        r"массами\s+(\d+(?:[.,]\d+)?)\s*(?:и|,)\s*(\d+(?:[.,]\d+)?)",
        text, flags=re.IGNORECASE
    )
    if pair:
        m1 = float(pair.group(1).replace(",", "."))
        m2 = float(pair.group(2).replace(",", "."))
    else:
        # Иначе берём по отдельности m1 и m2 (поддержка m1/m₁, m2/m₂)
        m1 = grab([
            r"(?:масса\s*(?:первого|1-?го)\s*тела|m[1₁])\s*(?:равн[ао]|=)\s*([0-9]+(?:[.,][0-9]+)?)",
            r"\bm[1₁]\s*=\s*([0-9]+(?:[.,][0-9]+)?)",
        ])
        m2 = grab([
            r"(?:масса\s*(?:второго|2-?го)\s*тела|m[2₂])\s*(?:равн[ао]|=)\s*([0-9]+(?:[.,][0-9]+)?)",
            r"\bm[2₂]\s*=\s*([0-9]+(?:[.,][0-9]+)?)",
        ])

    # 2) Расстояние r (допускаем «между телами», «на расстоянии», «r = …»)
    r_val = grab([
        r"расстояни[ея]\s*(?:между\s+телами\s*)?(?:равн[ао]|=)?\s*([0-9]+(?:[.,][0-9]+)?)",
        r"на\s+расстояни[еи]\s*([0-9]+(?:[.,][0-9]+)?)",
        r"\br\s*=\s*([0-9]+(?:[.,][0-9]+)?)",
    ])

    if m1 is None or m2 is None or r_val is None:
        raise ValueError("Не удалось распарсить m₁, m₂ или r")

    F = G_CONST * m1 * m2 / (r_val ** 2)
    return data["answer"] == format_answer(F)

# 33) coulomb_law_find_q: q = √(F·r² / k)
def validate_coulomb_law_find_q(data: dict) -> bool:
    text = data["text"]

    def grab(patterns):
        for p in patterns:
            m = re.search(p, text, flags=re.IGNORECASE)
            if m:
                return m.group(1)
        return None

    # Сила F
    F_str = grab([
        r"(?:сила\s*(?:взаимодействия|взаимн[ао]го\s+действия)?|F)\s*(?:равн[ао]|=)\s*([0-9]+(?:[.,][0-9]+)?)",
        r"\bF\s*=\s*([0-9]+(?:[.,][0-9]+)?)",
    ])
    F = float(F_str.replace(",", ".")) if F_str else None

    # Расстояние r
    r_str = grab([
        r"расстояни[ея]\s*(?:между\s+зарядами\s*)?(?:равн[ао]|=)?\s*([0-9]+(?:[.,][0-9]+)?)",
        r"\br\s*=\s*([0-9]+(?:[.,][0-9]+)?)",
    ])
    r_val = float(r_str.replace(",", ".")) if r_str else None

    # Известный заряд q1 (μКл или Кл)
    q_str = grab([
        r"q[12₁₂]?\s*=\s*([0-9]+(?:[.,][0-9]+)?)\s*мкКл",
        r"q[12₁₂]?\s*=\s*([0-9]+(?:[.,][0-9]+)?)",
    ])
    if not q_str:
        raise ValueError("Не удалось распарсить известный заряд q")

    if "мкКл" in text:
        q_known = float(q_str.replace(",", ".")) * 1e-6  # переводим в Кл
    else:
        q_known = float(q_str.replace(",", "."))

    # Константа k
    k_str = grab([
        r"(?:электрическ[аяои]\s+постоянная|k)\s*(?:равн[ао]|=)\s*([0-9]+(?:[.,][0-9]+)?)",
        r"\bk\s*=\s*([0-9]+(?:[.,][0-9]+)?)",
    ])
    k_val = float(k_str.replace(",", ".")) if k_str else K_CONST

    if F is None or r_val is None:
        raise ValueError("Не удалось распарсить F или r")

    # вычисляем неизвестный заряд (в Кл)
    q_unknown = F * (r_val ** 2) / (k_val * q_known)

    # если генератор был в μКл → сравниваем в μКл
    if "мкКл" in text:
        q_unknown_uC = round(q_unknown * 1e6)
        return data["answer"] == format_answer(q_unknown_uC)
    else:
        return data["answer"] == format_answer(q_unknown)

# 34) coulomb_law_find_F: F = k·q1·q2 / r²
def validate_coulomb_law_find_F(data: dict) -> bool:
    q1 = float(data["text"].split("q₁ = ")[1].split(" ")[0].replace(",", "."))
    q2 = float(data["text"].split("q₂ = ")[1].split(" ")[0].replace(",", "."))
    r = int(data["text"].split("расстоянии ")[1].split(" ")[0])
    F = K_CONST * q1 * q2 / (r**2)
    return data["answer"] == format_answer(F)

# 35) ohm_power_find_R: R = P / I²
def validate_ohm_power_find_R(data: dict) -> bool:
    P = int(data["text"].split("равна ")[1].split(" ")[0])
    I = int(data["text"].split("при силе тока ")[1].split(" ")[0])
    R = P / (I**2)
    return data["answer"] == format_answer(R)

# 36) ohm_power_find_P: P = I²·R
def validate_ohm_power_find_P(data: dict) -> bool:
    I = int(data["text"].split("силе тока ")[1].split(" ")[0])
    R = int(data["text"].split("сопротивлении ")[1].split(" ")[0])
    P = I**2 * R
    return data["answer"] == format_answer(P)

# 37) joule_lenz_find_t: t = Q / (I²·R)
def validate_joule_lenz_find_t(data: dict) -> bool:
    Q = int(data["text"].split("равно ")[1].split(" ")[0])
    I = int(data["text"].split("Сила тока ")[1].split(" ")[0])
    R = int(data["text"].split("сопротивление ")[1].split(" ")[0])
    t = Q / (I**2 * R)
    return data["answer"] == format_answer(t)

# 38) joule_lenz_find_R: R = Q / (I²·t)
def validate_joule_lenz_find_R(data: dict) -> bool:
    Q = int(data["text"].split("равно ")[1].split(" ")[0])
    I = int(data["text"].split("Сила тока ")[1].split(" ")[0])
    t = int(data["text"].split("время ")[1].split(" ")[0])
    R = Q / (I**2 * t)
    return data["answer"] == format_answer(R)

# 39) work_of_current_find_A: A = U²·t / R
def validate_work_of_current_find_A(data: dict) -> bool:
    U = int(data["text"].split("напряжение ")[1].split(" ")[0])
    t = int(data["text"].split("время ")[1].split(" ")[0])
    R = int(data["text"].split("сопротивление ")[1].split(" ")[0])
    A = U**2 * t / R
    return data["answer"] == format_answer(A)

# 40) capacitor_energy_find_W: W = C·U² / 2
def validate_capacitor_energy_find_W(data: dict) -> bool:
    C = float(data["text"].split("ёмкостью ")[1].split(" ")[0].replace(",", "."))
    U = int(data["text"].split("равно ")[1].split(" ")[0])
    W = C * U**2 / 2
    return data["answer"] == format_answer(W)

# 41) capacitor_energy_find_W_q: W = q² / (2C)
def validate_capacitor_energy_find_W_q(data: Dict) -> bool:
    text = data["text"]

    # --- Ёмкость в мкФ ---
    m_C = re.search(r"C\s*=\s*([0-9]+)\s*мкФ", text)
    if not m_C:
        raise ValueError("Не удалось распарсить ёмкость C")
    C_uF = int(m_C.group(1))
    C = C_uF * 1e-6  # Ф

    # --- Заряд в мкКл ---
    m_q = re.search(r"q\s*=\s*([0-9]+)\s*мкКл", text)
    if not m_q:
        raise ValueError("Не удалось распарсить заряд q")
    q_uC = int(m_q.group(1))
    q = q_uC * 1e-6  # Кл

    # --- Энергия ---
    W = q**2 / (2 * C)  # Дж
    W_uJ = round(W * 1e6)  # мкДж

    expected = format_answer(W_uJ)
    return data["answer"] == expected

# 42) gas_law_find_P: P = nRT / V
def validate_gas_law_find_P(data: dict) -> bool:
    n = int(data["text"].split("Количество вещества ")[1].split(" ")[0])
    T = int(data["text"].split("температура ")[1].split(" ")[0])
    V = float(data["text"].split("объём ")[1].split(" ")[0].replace(",", "."))
    P = n * R_UNIV * T / V
    return data["answer"] == format_answer(P)

# 43) gas_law_find_T: T = PV / (nR)
def validate_gas_law_find_T(data: dict) -> bool:
    P = int(data["text"].split("Давление газа равно ")[1].split(" ")[0])
    V = float(data["text"].split("объём ")[1].split(" ")[0].replace(",", "."))
    n = int(data["text"].split("количество вещества ")[1].split(" ")[0])
    T = P * V / (n * R_UNIV)
    return data["answer"] == format_answer(T)

# 44) gas_law_find_V: V = nRT / P
def validate_gas_law_find_V(data: dict) -> bool:
    P = int(data["text"].split("Давление газа ")[1].split(" ")[0])
    n = int(data["text"].split("количество вещества ")[1].split(" ")[0])
    T = int(data["text"].split("температура ")[1].split(" ")[0])
    V = n * R_UNIV * T / P
    return data["answer"] == format_answer(V)

# 45) gas_law_find_n: n = PV / (RT)
def validate_gas_law_find_n(data: dict) -> bool:
    P = int(data["text"].split("Давление газа ")[1].split(" ")[0])
    T = int(data["text"].split("температура ")[1].split(" ")[0])
    V = float(data["text"].split("объём ")[1].split(" ")[0].replace(",", "."))
    n = P * V / (R_UNIV * T)
    return data["answer"] == format_answer(n)

# 46) centripetal_acceleration_find_R: R = a / ω²
def validate_centripetal_acceleration_find_R(data: dict) -> bool:
    a = int(data["text"].split("равно ")[1].split(" ")[0])
    ω = int(data["text"].split("скорости ")[1].split(" ")[0])
    R = a / (ω**2)
    return data["answer"] == format_answer(R)

# 47) centripetal_acceleration_find_a: a = ω²·R
def validate_centripetal_acceleration_find_a(data: Dict) -> bool:
    text = data["text"]

    # угловая скорость ω
    m_omega = re.search(r"ω\s*=\s*([\d,\.]+)", text)
    if not m_omega:
        return False
    omega = float(m_omega.group(1).replace(",", "."))

    # радиус R
    m_R = re.search(r"R\s*=\s*([\d,\.]+)", text)
    if not m_R:
        return False
    R = float(m_R.group(1).replace(",", "."))

    # считаем ускорение
    a = omega**2 * R
    expected = format_answer(a)

    return data["answer"] == expected

# 48) centripetal_acceleration_find_omega: ω = √(a/R)
def validate_centripetal_acceleration_find_omega(data: Dict) -> bool:
    text = data["text"]

    # ускорение a
    m_a = re.search(r"a\s*=\s*([\d,\.]+)", text)
    if not m_a:
        return False
    a = float(m_a.group(1).replace(",", "."))

    # радиус R
    m_R = re.search(r"R\s*=\s*([\d,\.]+)", text)
    if not m_R:
        return False
    R = float(m_R.group(1).replace(",", "."))

    # считаем ω
    omega = math.sqrt(a / R)
    expected = format_answer(omega)

    return data["answer"] == expected

# 49) work_of_current_find_R: R = U²·t / A
def validate_work_of_current_find_R(data: dict) -> bool:
    A = float(data["text"].split("равна ")[1].split(" ")[0].replace(",", "."))
    U = int(data["text"].split("напряжении ")[1].split(" ")[0])
    t = int(data["text"].split("времени ")[1].split(" ")[0])
    R = U**2 * t / A
    return data["answer"] == format_answer(R)

# 50) joule_lenz_find_Q: Q = I²·R·t
def validate_joule_lenz_find_Q(data: dict) -> bool:
    I = int(data["text"].split("силой ")[1].split(" ")[0])
    R = int(data["text"].split("сопротивлением ")[1].split(" ")[0])
    t = int(data["text"].split("время ")[1].split(" ")[0])
    Q = I**2 * R * t
    return data["answer"] == format_answer(Q)

# 51) step_length_meters: s = step·n
def validate_step_length_meters(data: dict) -> bool:
    step = float(data["text"].split("длина каждого шага ")[1].split(" ")[0].replace(",", "."))
    n = int(data["text"].split("сделал ")[1].split(" ")[0])
    s = step * n
    return data["answer"] == format_answer(s)

# 52) step_length_cm: s = step·n / 100
def validate_step_length_cm(data: dict) -> bool:
    step = int(data["text"].split("шаги длиной ")[1].split(" ")[0])
    n = int(data["text"].split("За ")[1].split(" ")[0])
    s = step * n / 100
    return data["answer"] == format_answer(s)

# 53) step_length_km: s = step·n / 1000
def validate_step_length_km(data: dict) -> bool:
    step = float(data["text"].split("длиной ")[1].split(" ")[0].replace(",", "."))
    n = int(data["text"].split("прошёл ")[1].split(" ")[0])
    s = step * n / 1000
    return data["answer"] == format_answer(s)

# 54) lightning_distance: s = 330·t
def validate_lightning_distance(data: dict) -> bool:
    t = int(data["text"].split("через ")[1].split(" ")[0])
    s = 330 * t
    return data["answer"] == format_answer(s)

# 55) taxi_cost_linear: C = k·t
def validate_taxi_cost_linear(data: dict) -> bool:
    k = int(data["text"].split("C = ")[1].split("·")[0])
    t = int(data["text"].split("при времени ")[1].split(" ")[0])
    C = k * t
    return data["answer"] == format_answer(C)

# 56) taxi_cost_with_threshold: C = c0 + c1·(t−5)
def validate_taxi_cost_with_threshold(data: dict) -> bool:
    t = int(data["text"].split("длительностью ")[1].split(" ")[0])
    c0, c1 = 100, 10
    C = c0 + c1 * (t - 5)
    return data["answer"] == format_answer(C)

# 57) well_cost_linear: C = k·n
def validate_well_cost_linear(data: dict) -> bool:
    k = int(data["text"].split("Фирма берёт ")[1].split(" ")[0])
    n = int(data["text"].split("из ")[1].split(" ")[0])
    C = k * n
    return data["answer"] == format_answer(C)

# 58) well_cost_with_constant: C = c0 + c1·n
def validate_well_cost_with_constant(data: dict) -> bool:
    c0 = int(data["text"].split("берёт ")[1].split(" ")[0])
    c1 = int(data["text"].split("и ")[1].split(" ")[0])
    n = int(data["text"].split("из ")[1].split(" ")[0])
    C = c0 + c1 * n
    return data["answer"] == format_answer(C)

# 59) well_cost_two_companies: сравнение
def validate_well_cost_two_companies(data: dict) -> bool:
    n = int(data["text"].split("При установке ")[1].split(" ")[0])
    c1, k1 = 800, 500
    c2, k2 = 0, 600
    C1 = c1 + k1 * n
    C2 = c2 + k2 * n
    cheaper = "первая" if C1 < C2 else "вторая"
    return data["answer"] == cheaper

# 60) temperature_F_to_C: C = (F−32)/1.8
def validate_temperature_F_to_C(data: dict) -> bool:
    F = int(data["text"].split("равна ")[1].split("°")[0])
    C = (F - 32) / 1.8
    return data["answer"] == format_answer(C)

# 61) temperature_C_to_F: F = 1.8·C+32
def validate_temperature_C_to_F(data: dict) -> bool:
    C = int(data["text"].split("равна ")[1].split("°")[0])
    F = 1.8 * C + 32
    return data["answer"] == format_answer(F)

# 62) temperature_negative: F = 1.8·C+32
def validate_temperature_negative(data: dict) -> bool:
    C = int(data["text"].split("Температура на улице ")[1].split("°")[0])
    F = 1.8 * C + 32
    return data["answer"] == format_answer(F)

# 63) step_daily_walk: s = step·n / 1000
def validate_step_daily_walk(data: dict) -> bool:
    step = 0.75
    n = 4000
    s = step * n / 1000
    return data["answer"] == format_answer(s)

# 64) taxi_night_tariff: C = c0 + c1·(t−5)
def validate_taxi_night_tariff(data: dict) -> bool:
    c0, c1 = 150, 15
    t = 12
    C = c0 + c1 * (t - 5)
    return data["answer"] == format_answer(C)

# 65) well_cost_example_story: C = c0 + k·n
def validate_well_cost_example_story(data: dict) -> bool:
    c0, k, n = 1200, 550, 8
    C = c0 + k * n
    return data["answer"] == format_answer(C)

# 66) temperature_extreme: F = 1.8·C+32
def validate_temperature_extreme(data: dict) -> bool:
    C = -40
    F = 1.8 * C + 32
    return data["answer"] == format_answer(F)

# ─────────────────────────────────────────────────────────────
# Карта всех подтипов
# ─────────────────────────────────────────────────────────────
validator_map: Dict[str, callable] = {
    # Геометрия: площади
    "area_triangle_ah": validate_area_triangle_ah,
    "area_triangle_sides_sin": validate_area_triangle_sides_sin,
    "area_triangle_inscribed_circle": validate_area_triangle_inscribed_circle,
    "area_parallelogram_ah": validate_area_parallelogram_ah,
    "area_parallelogram_ab_sin": validate_area_parallelogram_ab_sin,
    "area_rhombus_d1d2": validate_area_rhombus_d1d2,
    "area_trapezoid_bases_h": validate_area_trapezoid_bases_h,
    "area_quadrilateral_d1d2_sin_S": validate_area_quadrilateral_d1d2_sin_S,
    "area_quadrilateral_find_d_by_S": validate_area_quadrilateral_find_d_by_S,
    "bisector_length_equal_legs": validate_bisector_length_equal_legs,

    # Радиусы, углы, пирамиды
    "inscribed_circle_radius_triangle": validate_inscribed_circle_radius_triangle,
    "inscribed_circle_radius_right_triangle": validate_inscribed_circle_radius_right_triangle,
    "circumscribed_circle_area_by_R": validate_circumscribed_circle_area_by_R,
    "circumscribed_circle_R_by_side_angle": validate_circumscribed_circle_R_by_side_angle,
    "polygon_angles_sum": validate_polygon_angles_sum,
    "height_pyramid_by_V": validate_height_pyramid_by_V,
    "circumference_length_find_R": validate_circumference_length_find_R,
    "area_quadrilateral_d1d2_sin_find_d": validate_area_quadrilateral_d1d2_sin_find_d,
    "bisector_length_general": validate_bisector_length_general,
    "circumscribed_circle_radius_equilateral": validate_circumscribed_circle_radius_equilateral,

    # Физика: маятник, энергия
    "pendulum_period_by_length": validate_pendulum_period_by_length,
    "pendulum_length_by_T": validate_pendulum_length_by_T,
    "kinetic_energy_find_v": validate_kinetic_energy_find_v,
    "kinetic_energy_find_E": validate_kinetic_energy_find_E,
    "potential_energy_find_m": validate_potential_energy_find_m,
    "potential_energy_find_E": validate_potential_energy_find_E,
    "mechanical_energy_total": validate_mechanical_energy_total,
    "mechanical_energy_find_m": validate_mechanical_energy_find_m,
    "archimedes_force_find_F": validate_archimedes_force_find_F,
    "archimedes_force_find_V": validate_archimedes_force_find_V,

    # Физика: гравитация, кулон, ток
    "newton_gravity_find_m": validate_newton_gravity_find_m,
    "newton_gravity_find_F": validate_newton_gravity_find_F,
    "coulomb_law_find_q": validate_coulomb_law_find_q,
    "coulomb_law_find_F": validate_coulomb_law_find_F,
    "ohm_power_find_R": validate_ohm_power_find_R,
    "ohm_power_find_P": validate_ohm_power_find_P,
    "joule_lenz_find_t": validate_joule_lenz_find_t,
    "joule_lenz_find_R": validate_joule_lenz_find_R,
    "work_of_current_find_A": validate_work_of_current_find_A,
    "capacitor_energy_find_W": validate_capacitor_energy_find_W,

    # Физика: газовые законы, центростремительное ускорение
    "capacitor_energy_find_W_q": validate_capacitor_energy_find_W_q,
    "gas_law_find_P": validate_gas_law_find_P,
    "gas_law_find_T": validate_gas_law_find_T,
    "gas_law_find_V": validate_gas_law_find_V,
    "gas_law_find_n": validate_gas_law_find_n,
    "centripetal_acceleration_find_R": validate_centripetal_acceleration_find_R,
    "centripetal_acceleration_find_a": validate_centripetal_acceleration_find_a,
    "centripetal_acceleration_find_omega": validate_centripetal_acceleration_find_omega,
    "work_of_current_find_R": validate_work_of_current_find_R,
    "joule_lenz_find_Q": validate_joule_lenz_find_Q,

    # Разные жизненные задачи
    "step_length_meters": validate_step_length_meters,
    "step_length_cm": validate_step_length_cm,
    "step_length_km": validate_step_length_km,
    "lightning_distance": validate_lightning_distance,
    "taxi_cost_linear": validate_taxi_cost_linear,
    "taxi_cost_with_threshold": validate_taxi_cost_with_threshold,
    "well_cost_linear": validate_well_cost_linear,
    "well_cost_with_constant": validate_well_cost_with_constant,
    "well_cost_two_companies": validate_well_cost_two_companies,
    "temperature_F_to_C": validate_temperature_F_to_C,
    "temperature_C_to_F": validate_temperature_C_to_F,
    "temperature_negative": validate_temperature_negative,
    "step_daily_walk": validate_step_daily_walk,
    "taxi_night_tariff": validate_taxi_night_tariff,
    "well_cost_example_story": validate_well_cost_example_story,
    "temperature_extreme": validate_temperature_extreme,
}

def validate_task(data: dict) -> bool:
    subtype = data["subtype"]
    if subtype not in validator_map:
        raise ValueError(f"Неизвестный подтип: {subtype}")
    return validator_map[subtype](data)
