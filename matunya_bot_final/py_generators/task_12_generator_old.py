# py_generators/task_12_generator.py

import random
import math
from typing import Optional, Dict, Any, Callable, Tuple

# Тип для наших "маленьких" генераторов
GeneratorFunc = Callable[[], Tuple[str, str, str]]

# =================================================================
# Вспомогательные функции
# =================================================================
def create_task_object(task_id: str, subtype: str, text: str, answer: str) -> Dict[str, Any]:
    """Собирает финальный JSON-объект для одного задания."""
    return {
        "id": task_id,
        "task_type": "12",
        "subtype": subtype,
        "text": text,
        "answer": str(answer)
    }

def format_answer(value: float) -> str:
    """Форматируем число под требования ОГЭ:
    - целое без .0
    - дробные с запятой
    - максимум 4 знака после запятой
    """
    if isinstance(value, (int, float)) and float(value).is_integer():
        return str(int(value))
    return f"{value:.4f}".rstrip("0").rstrip(".").replace(".", ",")

# =================================================================
# "Маленькие" функции-генераторы
# =================================================================

# =================================================================
# Группа 1: Геометрия
# =================================================================

def _generate_area_rhombus() -> Tuple[str, str, str]:
    subtype_key = "area_rhombus"
    # Подбираем числа так, чтобы площадь была целой
    d1 = random.randint(10, 20)            # искомая диагональ
    d2 = random.randint(10, 20) * 2        # чётная, чтобы 0.5*d1*d2 было целым
    area = 0.5 * d1 * d2                   # площадь

    text = (
        "Площадь ромба вычисляется по формуле S = d1·d2/2.\n"
        f"Найдите диагональ d1 (в метрах), если d2 = {format_answer(d2)} м, "
        f"а площадь ромба S = {format_answer(area)} м².\n\n"
        "В ответ запиши только число без единиц измерений."
    )
    answer = format_answer(d1)             # без .0 и с запятой при необходимости
    return subtype_key, text, answer

def _generate_area_triangle() -> Tuple[str, str, str]:
    subtype_key = "area_triangle"
    h = random.randint(5, 15)              # искомая высота
    a = random.randint(10, 20) * 2         # чётная сторона для «красивой» площади
    area = 0.5 * a * h                     # будет целой благодаря чётному a

    text = (
        "Площадь треугольника вычисляется по формуле S = a·h/2.\n"
        f"Найдите высоту h (в сантиметрах), если сторона a = {format_answer(a)} см, "
        f"а площадь S = {format_answer(area)} см².\n\n"
        "В ответ запиши только число без единиц измерений."
    )
    answer = format_answer(h)              # «чистое» число
    return subtype_key, text, answer

def _generate_area_parallelogram() -> Tuple[str, str, str]:
    subtype_key = "area_parallelogram"
    a = random.randint(10, 20)
    h = random.randint(5, 15)
    area = a * h

    text = (
        "Площадь параллелограмма вычисляется по формуле S=a·h.\n"
        f"Найдите сторону a (в сантиметрах), если высота h = {format_answer(h)}, "
        f"а площадь параллелограмма S = {format_answer(area)}.\n\n"
        "В ответ запиши только число без единиц измерений."
    )
    answer = format_answer(area / h)
    return subtype_key, text, answer


def _generate_area_trapezoid() -> Tuple[str, str, str]:
    subtype_key = "area_trapezoid"
    a = random.randint(5, 10)
    b = random.randint(a + 2, 20)
    h = random.randint(4, 10) * 2
    area = (a + b) / 2 * h

    text = (
        "Площадь трапеции вычисляется по формуле S=(a+b)/2·h.\n"
        f"Найдите основание b, если основание a = {format_answer(a)}, "
        f"высота h = {format_answer(h)}, а площадь S = {format_answer(area)}.\n\n"
        "В ответ запиши только число без единиц измерений."
    )
    answer = format_answer(2 * area / h - a)
    return subtype_key, text, answer

def _generate_area_quadrilateral_d1d2_sin() -> Tuple[str, str, str]:
    subtype_key = "area_quadrilateral_d1d2_sin"
    d1 = random.randint(10, 20)
    d2 = random.randint(10, 20)
    sin_a = random.choice([0.2, 0.25, 0.4, 0.5])
    area = 0.5 * d1 * d2 * sin_a
    area = round(area, 3)  # на всякий случай убираем артефакты float

    text = (
        "Площадь выпуклого четырёхугольника вычисляется по формуле S = d₁·d₂·sin(α)/2.\n"
        f"Найдите площадь S (в м²), если d₁ = {format_answer(d1)} м, d₂ = {format_answer(d2)} м, sin(α) = {format_answer(sin_a)}.\n\n"
        "В ответ запиши только число без единиц измерений."
    )
    answer = format_answer(area)
    return subtype_key, text, answer


def _generate_bisector_length() -> Tuple[str, str, str]:
    subtype_key = "bisector_length"
    a, b, c = 8, 10, 12
    l_a = math.sqrt(b * c * (1 - (a / (b + c)) ** 2))
    l_a = round(l_a, 2)

    text = (
        "Длина биссектрисы треугольника со сторонами a, b, c вычисляется по формуле "
        "lₐ = √(bc(1 − (a/(b+c))²)).\n"
        f"Найдите lₐ (в см), если a = {format_answer(a)} см, b = {format_answer(b)} см, c = {format_answer(c)} см.\n\n"
        "В ответ запиши только число без единиц измерений."
    )
    answer = format_answer(l_a)
    return subtype_key, text, answer

def _generate_radius_inscribed_rt_triangle() -> Tuple[str, str, str]:
    subtype_key = "radius_inscribed_rt_triangle"
    # Пифагоровы тройки и масштабирование
    a, b, c = random.choice([(3, 4, 5), (5, 12, 13), (8, 15, 17)])
    k = random.randint(1, 3)
    a, b, c = a * k, b * k, c * k
    r = (a + b - c) / 2  # r = (a + b − c)/2

    text = (
        "Радиус вписанной в прямоугольный треугольник окружности вычисляется по формуле r = (a+b−c)/2, "
        "где a и b — катеты, c — гипотенуза.\n"
        f"Найдите радиус r (в см), если a = {format_answer(a)} см, b = {format_answer(b)} см, c = {format_answer(c)} см.\n\n"
        "В ответ запиши только число без единиц измерений."
    )
    answer = format_answer(r)
    return subtype_key, text, answer

def _generate_height_pyramid() -> Tuple[str, str, str]:
    subtype_key = "height_pyramid"
    S_base = random.randint(10, 20)        # площадь основания
    h_true = random.randint(5, 12)         # «скрытая» высота, чтобы V получилось аккуратным
    V = S_base * h_true / 3                # объём

    text = (
        "Объём пирамиды вычисляется по формуле V = S_осн·h/3.\n"
        f"Найдите высоту h (в м), если объём пирамиды V = {format_answer(V)} м³, "
        f"а площадь основания S_осн = {format_answer(S_base)} м².\n\n"
        "В ответ запиши только число без единиц измерений."
    )
    answer = format_answer(3 * V / S_base)  # должно вернуться ровно h_true
    return subtype_key, text, answer

def _generate_length_circle() -> Tuple[str, str, str]:
    subtype_key = "length_circle"
    pi = 3.14
    R = random.randint(5, 20)
    length = round(2 * pi * R, 2)
    # Красиво оформим число в тексте: без хвостов и с запятой
    length_str = str(length).rstrip("0").rstrip(".").replace(".", ",")
    text = (
        f"Длину окружности можно вычислить по формуле ℓ = 2πR, где π ≈ 3,14. "
        f"Найдите радиус R (в метрах), если длина окружности ℓ = {length_str} м. "
        f"В ответ запиши только число без единиц измерений."
    )
    answer = format_answer(R)
    return subtype_key, text, answer


def _generate_triangle_area_circumradius() -> Tuple[str, str, str]:
    subtype_key = "triangle_area_circumradius"
    a, c = 12, 13
    R = 6.5
    S = 30
    # Формула: S = abc / (4R) ⇒ b = 4RS / (ac)
    b = 4 * R * S / (a * c)
    R_str = str(R).replace(".", ",")
    text = (
        f"Площадь треугольника можно вычислить по формуле S = abc / (4R). "
        f"Найдите сторону b, если a = {a}, c = {c}, площадь S = {S} и радиус описанной окружности R = {R_str}. "
        f"В ответ запиши только число без единиц измерений."
    )
    answer = format_answer(b)
    return subtype_key, text, answer


def _generate_polygon_angles_sum() -> Tuple[str, str, str]:
    subtype_key = "polygon_angles_sum"
    n = random.randint(5, 12)
    sum_angles = (n - 2) * 180
    text = (
        f"Сумма углов выпуклого n-угольника вычисляется по формуле Σ = (n − 2)·180°. "
        f"Найдите число сторон n, если сумма углов равна {sum_angles}°. "
        f"В ответ запиши только число без единиц измерений."
    )
    answer = format_answer(n)
    return subtype_key, text, answer

# =================================================================
# Группа 2: Физика - механика
# =================================================================

def _generate_pendulum_period() -> Tuple[str, str, str]:
    subtype_key = "pendulum_period"
    g = 10  # упрощаем g для ОГЭ
    T = random.randint(2, 5) * 2  # чётное для красивого ответа
    # Формула: T = 2√(l/g) ⇒ l = (T²·g)/4
    length = (T**2 * g) / 4
    text = (
        f"Период колебания математического маятника (в секундах) вычисляется по формуле "
        f"T = 2√(l/g), где l — длина нити в метрах. "
        f"Найдите длину нити маятника (в метрах), если период колебаний составляет {T} с. "
        f"(При расчетах принять g = 10 м/с².) "
        f"В ответ запиши только число без единиц измерений."
    )
    answer = format_answer(length)
    return subtype_key, text, answer


def _generate_kinetic_energy() -> Tuple[str, str, str]:
    subtype_key = "kinetic_energy"
    v = random.randint(10, 30)
    m = random.randint(1, 5) * 200
    energy = m * (v**2) / 2
    # Нужно найти скорость v
    text = (
        f"Кинетическая энергия тела (в джоулях) вычисляется по формуле E = mv²/2. "
        f"Найдите скорость v (в м/с), если масса тела m = {m} кг, а его кинетическая энергия E = {energy} Дж. "
        f"В ответ запиши только число без единиц измерений."
    )
    answer = format_answer((2 * energy / m) ** 0.5)
    return subtype_key, text, answer


def _generate_potential_energy() -> Tuple[str, str, str]:
    subtype_key = "potential_energy"
    m = random.randint(10, 50)
    h = random.randint(5, 20)
    g = 9.8
    energy = m * g * h
    energy_str = str(round(energy, 1)).replace(".", ",")
    text = (
        f"Потенциальная энергия тела (в джоулях) вычисляется по формуле E = mgh, где g ≈ 9,8 м/с². "
        f"Найдите массу тела m (в кг), если оно поднято на высоту h = {h} м, а его энергия E = {energy_str} Дж. "
        f"В ответ запиши только число без единиц измерений."
    )
    answer = format_answer(energy / (g * h))
    return subtype_key, text, answer


def _generate_mechanical_energy() -> Tuple[str, str, str]:
    subtype_key = "mechanical_energy"
    m, v, h, g = 10, 4, 5, 10  # фиксированные значения для красивого ответа
    E = m * (v**2) / 2 + m * g * h
    text = (
        f"Полная механическая энергия тела вычисляется по формуле E = mv²/2 + mgh. "
        f"Найдите полную энергию E (в джоулях), если m = {m} кг, v = {v} м/с, h = {h} м, а g = 10 м/с². "
        f"В ответ запиши только число без единиц измерений."
    )
    answer = format_answer(E)
    return subtype_key, text, answer


def _generate_gravity_law() -> Tuple[str, str, str]:
    subtype_key = "gravity_law"
    # F = G·m1·m2 / r²
    F = 66.7
    G = 6.67e-11
    m2 = 10**12
    r = 100
    m1 = F * (r**2) / (G * m2)
    G_str = str(G).replace("e-11", "·10⁻¹¹")
    text = (
        f"Закон всемирного тяготения описывается формулой F = G·m₁m₂ / r². "
        f"Найдите массу тела m₁ (в кг), если F = {F} Н, m₂ = {m2} кг, r = {r} м, "
        f"а гравитационная постоянная G = {G_str} Н·м²/кг². "
        f"В ответ запиши только число без единиц измерений."
    )
    answer = format_answer(m1)
    return subtype_key, text, answer

# =================================================================
# Группа 3: Физика - электричество и тепло
# =================================================================

def _generate_joul_lenz_law() -> Tuple[str, str, str]:
    subtype_key = "joul_lenz_law"
    I = random.randint(2, 10)
    R = random.randint(2, 10)
    t = random.randint(10, 60)
    Q = (I**2) * R * t
    text = (
        f"Количество теплоты (в джоулях), выделяемое проводником, вычисляется по формуле Q = I²Rt. "
        f"Найдите время t (в секундах), если Q = {Q} Дж, I = {I} А, R = {R} Ом. "
        f"В ответ запиши только число без единиц измерений."
    )
    answer = format_answer(Q / (I**2 * R))
    return subtype_key, text, answer


def _generate_electric_power() -> Tuple[str, str, str]:
    subtype_key = "electric_power"
    I = random.randint(2, 10)
    R = random.randint(2, 10)
    P = (I**2) * R
    text = (
        f"Мощность постоянного тока (в ваттах) вычисляется по формуле P = I²R. "
        f"Найдите сопротивление R (в омах), если мощность P = {P} Вт, а сила тока I = {I} А. "
        f"В ответ запиши только число без единиц измерений."
    )
    answer = format_answer(P / (I**2))
    return subtype_key, text, answer


def _generate_coulomb_law() -> Tuple[str, str, str]:
    subtype_key = "coulomb_law"
    k = 9 * (10**9)
    # F = k·q1·q2 / r² ⇒ q1 = F·r² / (k·q2)
    q1 = random.randint(2, 5) * (10**-3)  # красивый ответ вида 0,00X
    r = 1000
    q2 = 2 * (10**-3)
    F = k * q1 * q2 / (r**2)
    k_str = f"{k}".replace("9", "9·10⁹", 1)
    text = (
        f"Закон Кулона описывает силу взаимодействия зарядов: F = k·q₁q₂ / r². "
        f"Найдите заряд q₁ (в кулонах), если сила F = {format_answer(F)} Н, "
        f"заряд q₂ = {format_answer(q2)} Кл, расстояние r = {r} м, а коэффициент k = {k_str} Н·м²/Кл². "
        f"В ответ запиши только число без единиц измерений."
    )
    answer = format_answer(q1)
    return subtype_key, text, answer


def _generate_work_of_current() -> Tuple[str, str, str]:
    subtype_key = "work_of_current"
    U = random.randint(5, 20)
    t = random.randint(10, 60)
    # Берём R только из {2, 4, 5, 8, 10} → десятичная дробь всегда конечная
    R = random.choice([2, 4, 5, 8, 10])
    A = U * U * t / R
    text = (
        f"Работа постоянного тока (в джоулях) вычисляется по формуле A = U²t / R. "
        f"Найдите работу A, если время t = {t} с, напряжение U = {U} В, а сопротивление R = {R} Ом. "
        f"В ответ запиши только число без единиц измерений."
    )
    answer = format_answer(round(A, 4))
    return subtype_key, text, answer


def _generate_capacitor_energy() -> Tuple[str, str, str]:
    subtype_key = "capacitor_energy"
    variant = random.choice(['U', 'q'])
    # базовая ёмкость
    C = random.randint(2, 8) * (10**-4)

    if variant == 'U':
        U = random.randint(1, 5) * 10
        W = C * (U**2) / 2
        text = (
            f"Энергия конденсатора (в джоулях) вычисляется по формуле W = CU² / 2. "
            f"Найдите энергию W, если ёмкость C = {format_answer(C)} Ф, а напряжение U = {U} В. "
            f"В ответ запиши только число без единиц измерений."
        )
    else:  # variant == 'q'
        q_base = random.randint(2, 9)
        q = q_base * (10**-4)
        k = random.choice([0.5, 1, 2, 4])
        C_base = (q_base**2) / (2 * k)
        if C_base != int(C_base):
            C_base = int(C_base) + 1
        C = C_base * (10**-4)
        W = (q**2) / (2 * C)
        text = (
            f"Энергия конденсатора (в джоулях) вычисляется по формуле W = q² / (2C). "
            f"Найдите энергию W, если ёмкость C = {format_answer(C)} Ф, а заряд q = {format_answer(q)} Кл. "
            f"В ответ запиши только число без единиц измерений."
        )

    answer = format_answer(W)
    return subtype_key, text, answer

# =================================================================
# Группа 4: Физика - молекулярка и газы
# =================================================================

def _generate_gas_law_find_P() -> Tuple[str, str, str]:
    subtype_key = "gas_law_find_P"
    R = 8.31
    nu = round(random.uniform(10, 50), 1)
    T = random.randint(200, 400)
    V = round(random.uniform(5, 15), 1)
    P = nu * R * T / V
    text = (
        f"Давление идеального газа (в паскалях) можно найти из уравнения PV = νRT, где R ≈ 8,31 Дж/(моль·К). "
        f"Найдите давление P, если ν = {nu} моль, T = {T} К, а объём V = {V} м³. "
        f"В ответ запиши только число без единиц измерений."
    )
    answer = format_answer(P)
    return subtype_key, text, answer


def _generate_gas_law_find_T() -> Tuple[str, str, str]:
    subtype_key = "gas_law_find_T"
    R = 8.31
    # подбираем ν и V «красивыми», чтобы P получилось целым
    nu = random.randint(10, 30)  # целое число молей
    V = random.choice([1, 2, 2.5, 4, 5])  # конечные дроби
    T = random.randint(200, 500)  # целевая температура (красивое целое)
    P = nu * R * T / V            # вычисляем P

    text = (
        f"Температуру идеального газа (в кельвинах) можно найти из уравнения PV = νRT, где R ≈ 8,31 Дж/(моль·К). "
        f"Найдите температуру T, если P = {format_answer(round(P, 2))} Па, ν = {nu} моль, а объём V = {format_answer(V)} м³. "
        f"В ответ запиши только число без единиц измерений."
    )
    answer = format_answer(T)
    return subtype_key, text, answer


def _generate_gas_law_find_V() -> Tuple[str, str, str]:
    subtype_key = "gas_law_find_V"
    R = 8.31
    # подбираем красивые значения
    nu = random.randint(5, 15)  # целое количество молей
    T = random.randint(200, 400)  # температура целое
    V = random.choice([1, 1.5, 2, 2.5, 3, 4, 5])  # конечная десятичная
    P = nu * R * T / V  # рассчитываем давление под выбранный V

    text = (
        f"Объём идеального газа (в м³) можно найти из уравнения PV = νRT, где R ≈ 8,31 Дж/(моль·К). "
        f"Найдите объём V, если P = {format_answer(round(P, 2))} Па, ν = {nu} моль, а температура T = {T} К. "
        f"В ответ запиши только число без единиц измерений."
    )
    answer = format_answer(V)
    return subtype_key, text, answer


def _generate_gas_law_find_n() -> Tuple[str, str, str]:
    subtype_key = "gas_law_find_n"
    R = 8.31
    # подбираем "красивые" значения
    nu = random.choice([5, 10, 12, 15, 20])  # конечное число молей
    V = random.choice([5, 6, 8, 10, 12, 15])  # м³, целое
    T = random.randint(500, 800)  # температура целое
    P = nu * R * T / V  # считаем давление

    text = (
        f"Количество вещества идеального газа (в молях) можно найти из уравнения PV = νRT, где R ≈ 8,31 Дж/(моль·К). "
        f"Найдите ν, если P = {format_answer(round(P, 2))} Па, V = {V} м³, а температура T = {T} К. "
        f"В ответ запиши только число без единиц измерений."
    )
    answer = format_answer(nu)
    return subtype_key, text, answer

# =================================================================
# Группа 5: Физика - движение по окружности
# =================================================================

def _generate_centripetal_acceleration() -> Tuple[str, str, str]:
    subtype_key = "centripetal_acceleration"
    # Берём ω целым (чтобы квадрат точно был целым)
    omega = random.randint(2, 10)
    # Берём R кратным 0.5, чтобы деление было аккуратным
    R = random.choice([x / 2 for x in range(2, 21)])  # 1.0, 1.5, 2.0 ... 10.0
    a = omega * omega * R  # без округлений — чистое значение
    text = (
        f"Центростремительное ускорение при движении по окружности (в м/с²) вычисляется по формуле a = ω²R. "
        f"Найдите радиус R (в метрах), если угловая скорость ω = {omega} с⁻¹, а ускорение a = {format_answer(a)} м/с². "
        f"В ответ запиши только число без единиц измерений."
    )
    answer = format_answer(R)
    return subtype_key, text, answer

# =================================================================
# Группа 6: Разное
# =================================================================

def _generate_steps_distance() -> Tuple[str, str, str]:
    subtype_key = "steps_distance"
    steps = random.randint(10, 30) * 100
    # Берём длину шага кратной 5 см, чтобы в км всегда была конечная десятичная
    length_cm = random.choice(list(range(60, 91, 5)))  # 60, 65, ..., 90
    distance_km = steps * length_cm / 100 / 1000  # см → м → км
    text = (
        f"Человек сделал {steps} шагов, длина каждого из которых равна {length_cm} см. "
        f"Какое расстояние он прошёл? Ответ дайте в километрах. "
        f"В ответ запиши только число без единиц измерений."
    )
    answer = format_answer(round(distance_km, 4))
    return subtype_key, text, answer


def _generate_lightning_distance() -> Tuple[str, str, str]:
    subtype_key = "lightning_distance"
    t = random.randint(2, 20)
    s_km = 330 * t / 1000  # 0.33 * t — всегда конечная десятичная
    text = (
        f"Расстояние до места удара молнии (в метрах) приближённо вычисляется по формуле s = 330t, "
        f"где t — количество секунд между вспышкой и громом. "
        f"Определите расстояние (в километрах) до места удара молнии, если t = {t} с. "
        f"В ответ запиши только число без единиц измерений."
    )
    answer = format_answer(round(s_km, 4))
    return subtype_key, text, answer


def _generate_temperature_conversion() -> Tuple[str, str, str]:
    subtype_key = "temperature_conversion"
    variant = random.choice(['C_to_F', 'F_to_C'])

    if variant == 'C_to_F':
        C = random.randint(-30, 30)
        F = 1.8 * C + 32  # конечная десятичная
        text = (
            f"Температура по шкале Фаренгейта связана с градусами Цельсия формулой F = 1,8·C + 32. "
            f"Какая температура (в градусах Фаренгейта) соответствует {C}°C? "
            f"В ответ запиши только число без единиц измерений."
        )
        answer = format_answer(round(F, 4))
    else:  # F_to_C
        # Подбираем F так, чтобы (F − 32) было кратно 9 → C = (F−32)*5/9 — конечная десятичная/целая
        k_min = math.ceil((-4 - 32) / 9)   # для нижней границы
        k_max = math.floor((86 - 32) / 9)  # для верхней границы
        k = random.randint(k_min, k_max)
        F = 32 + 9 * k
        C = (F - 32) / 1.8
        text = (
            f"Температура по шкале Цельсия связана с градусами Фаренгейта формулой C = (F − 32) / 1,8. "
            f"Какая температура (в градусах Цельсия) соответствует {F}°F? "
            f"В ответ запиши только число без единиц измерений."
        )
        answer = format_answer(round(C, 4))

    return subtype_key, text, answer


def _generate_taxi_cost() -> Tuple[str, str, str]:
    subtype_key = "taxi_cost"
    base_cost = random.randint(10, 20) * 10
    per_minute_cost = random.randint(10, 15)
    free_minutes = 5
    total_minutes = random.randint(10, 25)
    cost = base_cost + per_minute_cost * (total_minutes - free_minutes)  # всегда целое
    text = (
        f"Стоимость поездки на такси (в рублях) рассчитывается по формуле "
        f"C = {base_cost} + {per_minute_cost}·(t − {free_minutes}), где t — длительность поездки в минутах (t > {free_minutes}). "
        f"Рассчитайте стоимость {total_minutes}-минутной поездки. "
        f"В ответ запиши только число без единиц измерений."
    )
    answer = format_answer(cost)
    return subtype_key, text, answer


def _generate_well_cost() -> Tuple[str, str, str]:
    subtype_key = "well_cost"
    base_cost = random.randint(5, 8) * 1000
    per_ring_cost = random.randint(3, 5) * 1000
    rings = random.randint(5, 12)
    cost = base_cost + per_ring_cost * rings  # всегда целое
    text = (
        f"Стоимость колодца (в рублях) из железобетонных колец рассчитывается по формуле "
        f"C = {base_cost} + {per_ring_cost}·n, где n — число колец. "
        f"Рассчитайте стоимость колодца из {rings} колец. "
        f"В ответ запиши только число без единиц измерений."
    )
    answer = format_answer(cost)
    return subtype_key, text, answer

# =================================================================
# "Карта дирижера"
# Связывает ключ подтипа с функцией, которая его генерирует
# =================================================================
GENERATOR_MAP: Dict[str, GeneratorFunc] = {
    # Геометрия
    "area_rhombus": _generate_area_rhombus,
    "area_triangle": _generate_area_triangle,
    "area_parallelogram": _generate_area_parallelogram,
    "area_trapezoid": _generate_area_trapezoid,
    "area_quadrilateral_d1d2_sin": _generate_area_quadrilateral_d1d2_sin,
    "bisector_length": _generate_bisector_length,
    "radius_inscribed_rt_triangle": _generate_radius_inscribed_rt_triangle,
    "height_pyramid": _generate_height_pyramid,
    "length_circle": _generate_length_circle,
    "triangle_area_circumradius": _generate_triangle_area_circumradius,
    "polygon_angles_sum": _generate_polygon_angles_sum,
    
    # Физика — механика
    "pendulum_period": _generate_pendulum_period,
    "kinetic_energy": _generate_kinetic_energy,
    "potential_energy": _generate_potential_energy,
    "mechanical_energy": _generate_mechanical_energy,
    "gravity_law": _generate_gravity_law,
    
    # Физика — электричество и тепло
    "joul_lenz_law": _generate_joul_lenz_law,
    "electric_power": _generate_electric_power,
    "coulomb_law": _generate_coulomb_law,
    "work_of_current": _generate_work_of_current,
    "capacitor_energy": _generate_capacitor_energy,
    
    # Физика — молекулярка и газы
    "gas_law_find_P": _generate_gas_law_find_P,
    "gas_law_find_T": _generate_gas_law_find_T,
    "gas_law_find_V": _generate_gas_law_find_V,
    "gas_law_find_n": _generate_gas_law_find_n,
    
    # Физика — движение по окружности
    "centripetal_acceleration": _generate_centripetal_acceleration,
    
    # Разное
    "steps_distance": _generate_steps_distance,
    "lightning_distance": _generate_lightning_distance,
    "temperature_conversion": _generate_temperature_conversion,
    "taxi_cost": _generate_taxi_cost,
    "well_cost": _generate_well_cost,
}

# =================================================================
# Главная функция-"дирижер"
# =================================================================
async def generate_task_12_by_subtype(subtype_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Выбирает и запускает нужный генератор для Задания 12.
    Если subtype_key не указан, выбирает случайный.
    """
    if subtype_key is None:
        subtype_key = random.choice(list(GENERATOR_MAP.keys()))

    generator_func = GENERATOR_MAP.get(subtype_key)

    if generator_func is None:
        print(f"ОШИБКА: Неизвестный подтип задания 12: {subtype_key}")
        return None

    result = generator_func()

    return {
        "subtype": result[0],
        "text": result[1],
        "answer": result[2]
    }

# =================================================================
# Блок для тестирования генератора
# =================================================================
if __name__ == "__main__":
    print(f"--- Тестируем {len(GENERATOR_MAP)} подтипов Задания 12 ---")

    for subtype_key, generator_func in GENERATOR_MAP.items():
        print(f"\n--- Тест подтипа: {subtype_key} ---")
        try:
            subtype, text, answer = generator_func()
            
            if not text or not answer:
                print("❌ ОШИБКА: Генератор вернул пустой текст или ответ.")
                continue
            
            print(f"  ✅ Успешно сгенерировано!")
            print(f"     Текст: {text}")
            print(f"     Ответ: {answer}")

        except Exception as e:
            print(f"❌ КРИТИЧЕСКАЯ ОШИБКА в генераторе {subtype_key}: {e}")
    
    print("\n--- Тестирование завершено ---")