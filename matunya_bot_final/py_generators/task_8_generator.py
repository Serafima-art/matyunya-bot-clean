# gpt/task_templates/task_8_generator.py

import random
from typing import Tuple, Dict, Callable, Optional

# Вспомогательная функция, нужна для нового генератора.
# Можно разместить ее где-нибудь наверху, после импортов.
def is_perfect_square(n):
    """Проверяет, является ли число полным квадратом."""
    if n < 0:
        return False
    if n == 0:
        return True
    x = int(n**0.5)
    return x * x == n

# =================================================================================
# --- ГЕНЕРАТОРЫ ЗАДАНИЙ (НОВЫЙ СТАНДАРТ) ---
# Каждая функция возвращает: (subtype, text, correct_answer)
# =================================================================================

def _generate_same_base() -> Tuple[str, str, str]:
    """
    (1/17) Генерирует задания для подтипа 'same_base' (одинаковое основание).
    """
    subtype = "same_base"

    while True:
        base = random.randint(2, 7)
        p1 = random.randint(-7, 7)
        p2 = random.randint(-7, 7)
        p3 = random.randint(-7, 7)
        
        template_choice = random.choice(['A', 'B'])

        if template_choice == 'A':
            result_power = p1 + p2 - p3
            task_text = f"Найди значение выражения {base}**{p1} · {base}**{p2} / {base}**{p3}"
        else: # template_choice == 'B'
            result_power = (p1 * p2) + p3
            task_text = f"Найди значение выражения ({base}**{p1})**{p2} · {base}**{p3}"
            
        is_valid = False
        if 0 <= result_power <= 4:
            is_valid = True
        elif (result_power == 5 or result_power == 6) and base == 2:
            is_valid = True
        
        if is_valid:
            break 

    correct_answer = base ** result_power

    # Красивые степени
    replacements = {
        '**-9': '⁻⁹', '**-8': '⁻⁸', '**-7': '⁻⁷', '**-6': '⁻⁶', '**-5': '⁻⁵', 
        '**-4': '⁻⁴', '**-3': '⁻³', '**-2': '⁻²', '**-1': '⁻¹',
        '**0': '⁰', '**1': '¹', '**2': '²', '**3': '³', '**4': '⁴', '**5': '⁵',
        '**6': '⁶', '**7': '⁷', '**8': '⁸', '**9': '⁹'
    }
    for old, new in replacements.items():
        task_text = task_text.replace(old, new)
        
    return subtype, task_text, str(correct_answer)


def _generate_root_fraction_variable_power() -> Tuple[str, str, str]:
    """
    (2/17) Генерирует задания для подтипа 'root_fraction_variable_power'.
    """
    subtype = "root_fraction_variable_power"

    k_base = random.randint(2, 7)
    k = k_base ** 2
    base = random.randint(2, 5)
    var = random.choice(['a', 'b', 'x', 'm'])
    result_power = random.randint(1, 3)
    p2 = random.randint(2, 6) * 2
    p1 = p2 + 2 * result_power

    correct_answer = k_base * (base ** result_power)

    task_text = f"Найди значение выражения √({k}{var}**{p1} / {var}**{p2}) при {var} = {base}"

    # Красивые степени
    replacements = {
        '**2': '²', '**3': '³', '**4': '⁴', '**5': '⁵', '**6': '⁶', '**7': '⁷',
        '**8': '⁸', '**9': '⁹', '**10': '¹⁰', '**11': '¹¹', '**12': '¹²',
        '**13': '¹³', '**14': '¹⁴', '**15': '¹⁵', '**16': '¹⁶', '**17': '¹⁷',
        '**18': '¹⁸', '**19': '¹⁹', '**20': '²⁰'
    }
    for old, new in replacements.items():
        task_text = task_text.replace(old, new)

    return subtype, task_text, str(correct_answer)

def _generate_difference_of_squares_with_roots() -> Tuple[str, str, str]:
    """
    (3/17) Генерирует задания для подтипа 'difference_of_squares_with_roots'.
    Примеры: (√13 - 2)(√13 + 2) или (√7 - √3)(√7 + √3)
    """
    subtype = "difference_of_squares_with_roots"
    
    # Случайно выбираем один из двух шаблонов
    variant = random.choice(['root_number', 'root_root'])

    if variant == 'root_number':
        # Шаблон: (√a - b)(√a + b) = a - b²
        b = random.randint(2, 12)
        
        # Выбираем 'a' так, чтобы оно не было полным квадратом для интереса
        a = random.randint(b + 1, 150)
        while is_perfect_square(a):
            a = random.randint(b + 1, 150)
            
        task_text = f"Найди значение выражения (√{a} - {b})(√{a} + {b})"
        correct_answer = a - b**2
    
    else: # variant == 'root_root'
        # Шаблон: (√a - √b)(√a + √b) = a - b
        a = random.randint(10, 150)
        b = random.randint(2, a - 1)

        # Убедимся, что оба числа не являются полными квадратами
        while is_perfect_square(a):
            a = random.randint(10, 150)
        while is_perfect_square(b):
            b = random.randint(2, a - 1)

        task_text = f"Найди значение выражения (√{a} - √{b})(√{a} + √{b})"
        correct_answer = a - b

    return subtype, task_text, str(correct_answer)

def _generate_fraction_with_powers() -> Tuple[str, str, str]:
    """
    (4, 7, 10, 15). Генерирует задания для 4-х схожих подтипов,
    с детальным контролем размера итогового ответа.
    """
    subtypes = [
        "fraction_with_powers", 
        "fraction_with_powers_and_substitution",
        "powers_with_variables_and_substitution",
        "negative_exponents"
    ]
    subtype = random.choice(subtypes)

    while True:
        # Теперь основание может быть больше, т.к. мы контролируем его парой со степенью
        base = random.randint(2, 9)
        
        if subtype == "negative_exponents":
            p1 = random.randint(-9, -2)
            p2 = random.randint(-9, -2)
            p3 = random.randint(-9, -2)
        else:
            p1 = random.randint(-5, 5)
            p2 = random.randint(2, 5)
            p3 = random.randint(2, 5)
        
        variant = random.choice(['A', 'B'])

        if variant == 'A':
            result_power = p1 + (p2 * p3)
        else:
            result_power = (p1 * p2) - p3

        # --- "ЗОЛОТОЙ СТАНДАРТ" ПРОВЕРКИ ОТВЕТА ---
        is_valid = False
        if result_power in [0, 1, 2]: # Для степеней 0, 1, 2 - любое основание до 9
            is_valid = True
        elif result_power == 3 and base <= 5: # Для степени 3 - основание до 5
            is_valid = True
        elif result_power == 4 and base <= 4: # Для степени 4 - основание до 4
            is_valid = True
        elif result_power in [5, 6] and base == 2: # Для степеней 5, 6 - только основание 2
            is_valid = True
        
        if is_valid:
            break

    correct_answer = base ** result_power
    
    var = random.choice(['a', 'b', 't', 'x', 'm', 'y'])
    template = "{var}**{p1} · ({var}**{p2})**{p3}" if variant == 'A' else "({var}**{p1})**{p2} / {var}**{p3}"
    task_text = f"Найди значение выражения {template.format(var=var, p1=p1, p2=p2, p3=p3)} при {var} = {base}"

    replacements = {
        '**-9': '⁻⁹', '**-8': '⁻⁸', '**-7': '⁻⁷', '**-6': '⁻⁶', '**-5': '⁻⁵', 
        '**-4': '⁻⁴', '**-3': '⁻³', '**-2': '⁻²', '**-1': '⁻¹',
        '**0': '⁰', '**1': '¹', '**2': '²', '**3': '³', '**4': '⁴', '**5': '⁵',
        '**6': '⁶', '**7': '⁷', '**8': '⁸', '**9': '⁹'
    }
    for old, new in replacements.items():
        task_text = task_text.replace(old, new)

    return subtype, task_text, str(correct_answer)

# --- ШАГ 3: ДОБАВЬ ЭТУ СТРОЧКУ СРАЗУ ПОСЛЕ ФУНКЦИИ ВЫШЕ ---
generate_fraction_with_powers_and_substitution = _generate_fraction_with_powers
powers_with_variables_and_substitution = _generate_fraction_with_powers
negative_exponents = _generate_fraction_with_powers 

def _generate_expression_with_radicals_and_powers() -> Tuple[str, str, str]:
    """
    (5/17) Генерирует задания для подтипа 'expression_with_radicals_and_powers'.
    Добавлен контроль размера итогового ответа.
    """
    subtype = "expression_with_radicals_and_powers"
    
    while True:
        base = random.randint(2, 4)
        
        # p1 под корнем ОБЯЗАНА быть четной
        p1 = random.randint(2, 5) * 2 # Получаем 4, 6, 8, 10
        p2 = random.randint(1, 5) # Уменьшил p2, чтобы было больше шансов на успех

        # Вычисляем итоговую степень
        result_power = (p1 // 2) + p2
        
        # --- Проверка адекватности! ---
        is_valid = False
        if 0 <= result_power <= 4:
            is_valid = True
        elif (result_power == 5 or result_power == 6) and base == 2:
            is_valid = True
        
        if is_valid:
            break # Если комбинация удачная, выходим из цикла

    correct_answer = base ** result_power

    # --- Сборка текста ---
    var = random.choice(['a', 'b', 'x'])
    use_negative_base = random.choice([True, False])
    
    if use_negative_base:
        task_text = f"Найди значение выражения √((-{var})**{p1}) · {var}**{p2} при {var} = {base}"
    else:
        task_text = f"Найди значение выражения √({var}**{p1}) · {var}**{p2} при {var} = {base}"

    # Красивые степени
    replacements = {
        '**2': '²', '**3': '³', '**4': '⁴', '**5': '⁵', '**6': '⁶', '**7': '⁷',
        '**8': '⁸', '**9': '⁹', '**10': '¹⁰'
    }
    for old, new in replacements.items():
        task_text = task_text.replace(old, new)
        
    return subtype, task_text, str(correct_answer)

def _generate_expressions_with_powers() -> Tuple[str, str, str]:
    """
    (6/17) Генерирует задания для подтипа 'expressions_with_powers'.
    Добавлен "Золотой стандарт" контроля ответов.
    """
    subtype = "expressions_with_powers"

    while True:
        # Основание может быть до 9, т.к. фильтр is_valid его контролирует
        base = random.randint(2, 9)
        
        p2 = random.randint(2, 6)
        p1 = random.randint(p2 + 1, p2 + 4)

        result_power = p1 - p2
        
        # --- "ЗОЛОТОЙ СТАНДАРТ" ПРОВЕРКИ ОТВЕТА ---
        is_valid = False
        if result_power in [0, 1, 2]:
            is_valid = True
        elif result_power == 3 and base <= 5:
            is_valid = True
        elif result_power == 4 and base <= 4:
            is_valid = True
        # result_power > 4 здесь маловероятен, но оставим для надежности
        elif result_power in [5, 6] and base == 2:
            is_valid = True

        if is_valid:
            break

    correct_answer = base ** result_power
    
    task_text = f"Найди значение выражения 1 / {base}**-{p1} · 1 / {base}**{p2}"

    # Красивые степени
    replacements = {
        '**-9': '⁻⁹', '**-8': '⁻⁸', '**-7': '⁻⁷', '**-6': '⁻⁶', '**-5': '⁻⁵', 
        '**-4': '⁻⁴', '**-3': '⁻³', '**-2': '⁻²', '**-1': '⁻¹',
        '**0': '⁰', '**1': '¹', '**2': '²', '**3': '³', '**4': '⁴', '**5': '⁵',
        '**6': '⁶', '**7': '⁷', '**8': '⁸', '**9': '⁹'
    }
    for old, new in replacements.items():
        task_text = task_text.replace(old, new)

    return subtype, task_text, str(correct_answer)

def _generate_root_of_fraction_with_powers() -> Tuple[str, str, str]:
    """
    (8/17) Генерирует задания для подтипа 'root_of_fraction_with_powers'.
    Пример: √(25m⁶ / n²) при m = 2, n = 5
    """
    subtype = "root_of_fraction_with_powers"

    # --- Ингредиенты ---
    # Коэффициенты - полные квадраты
    k1_base = random.randint(2, 10)
    k1 = k1_base ** 2
    
    k2_base = random.randint(2, 10)
    k2 = k2_base ** 2

    # Значения для подстановки
    base1 = random.randint(2, 4)
    base2 = random.randint(2, 4)
    
    # Имена переменных
    var1 = random.choice(['a', 'm', 'p', 'z'])
    var2 = random.choice(['b', 'n', 'q', 'w'])
    while var1 == var2: # Убедимся, что переменные разные
        var2 = random.choice(['b', 'n', 'q', 'w'])

    # Степени - четные
    p1 = random.randint(2, 5) * 2 # 4, 6, 8, 10
    p2 = random.randint(1, 4) * 2 # 2, 4, 6, 8

    # --- Вычисления ---
    # √(k1 * var1ᵖ¹ / (k2 * var2ᵖ²)) = (k1_base * var1^(p1/2)) / (k2_base * var2^(p2/2))
    numerator = k1_base * (base1 ** (p1 // 2))
    denominator = k2_base * (base2 ** (p2 // 2))

    # Мы должны гарантировать, что ответ будет "красивым" (целым)
    # Для этого числитель должен делиться на знаменатель нацело
    # Проще всего этого добиться, "подделав" один из коэффициентов
    if numerator % denominator != 0:
        # Если не делится, пересчитываем числитель так, чтобы он стал кратен знаменателю
        # Например, numerator = denominator * какое-то число
        multiplier = random.randint(1, 4)
        numerator = denominator * multiplier
        # И теперь "подделываем" k1_base, чтобы он соответствовал новому числителю
        k1_base = numerator // (base1 ** (p1 // 2))
        # Проверяем, не стал ли k1_base нулем или слишком маленьким
        if k1_base < 2:
            k1_base = random.randint(2,5) # Просто даем ему адекватное значение
        k1 = k1_base ** 2
        
    correct_answer = numerator // denominator

    # --- Сборка ---
    task_text = f"Найди значение выражения √({k1}{var1}**{p1} / {k2}{var2}**{p2}) при {var1} = {base1}, {var2} = {base2}"

    # Красивые степени
    replacements = {
        '**2': '²', '**3': '³', '**4': '⁴', '**5': '⁵', '**6': '⁶', '**7': '⁷',
        '**8': '⁸', '**9': '⁹', '**10': '¹⁰'
    }
    for old, new in replacements.items():
        task_text = task_text.replace(old, new)
        
    return subtype, task_text, str(correct_answer)

def _generate_multiplication_of_roots() -> Tuple[str, str, str]:
    """
    (9/17) Генерирует задания для подтипа 'multiplication_of_roots'.
    Пример: √18 · √2  (результат = √36 = 6)
    """
    subtype = "multiplication_of_roots"

    # --- Конструируем "от ответа" ---
    # 1. Выбираем "красивый" ответ, который будет результатом извлечения корня
    answer = random.randint(4, 15)
    
    # 2. Находим квадрат этого ответа. Это число, которое должно получиться под корнем
    target_square = answer ** 2

    # 3. Ищем два множителя для target_square, которые сами НЕ являются квадратами
    # Это сделает задание интересным
    factors = []
    for i in range(2, int(target_square**0.5) + 1):
        if target_square % i == 0:
            j = target_square // i
            # Проверяем, что ни один из множителей не является полным квадратом
            if not is_perfect_square(i) and not is_perfect_square(j):
                factors.append((i, j))

    # Если мы не нашли подходящей пары (например, для target_square = 49),
    # то просто создадим ее искусственно
    if not factors:
        # Берем "маскирующий" множитель, который не является квадратом
        mask = random.choice([2, 3, 5, 6, 7])
        a = mask
        b = target_square // mask
        # Если b получилось нецелым, или a=b, или b - квадрат, перегенерируем
        if target_square % mask != 0 or a == b or is_perfect_square(b):
             # Простой запасной вариант
             a = 2
             b = target_square // 2
             if target_square % 2 != 0: # Если квадрат был нечетным
                 a = 3
                 b = target_square // 3
    else:
        # Если нашли хорошие пары, выбираем одну случайную
        a, b = random.choice(factors)

    # --- Сборка ---
    # Случайно решаем, в каком порядке будут множители в тексте
    if random.choice([True, False]):
        task_text = f"Найди значение выражения √{a} · √{b}"
    else:
        task_text = f"Найди значение выражения √{b} · √{a}"
        
    correct_answer = answer
        
    return subtype, task_text, str(correct_answer)

def _generate_product_and_division_of_roots_with_variables() -> Tuple[str, str, str]:
    """
    (11/17) Генерирует задания для подтипа 'product_and_division_of_roots_with_variables'.
    Добавлен финальный контроль размера ответа.
    """
    subtype = "product_and_division_of_roots_with_variables"

    while True:
        # --- Ингредиенты (с уже уменьшенными диапазонами) ---
        k1_base = random.randint(2, 5)
        k1 = k1_base ** 2
        k2_base = random.randint(2, 5)
        k2 = k2_base ** 2

        base1 = random.randint(2, 3)
        base2 = random.randint(2, 3)

        var1 = random.choice(['a', 'm', 'x'])
        var2 = random.choice(['b', 'n', 'y'])
        
        p3 = random.randint(1, 2) * 2
        p1 = random.randint(p3 // 2 + 1, 4) * 2

        p4 = random.randint(1, 2) * 2
        p2 = random.randint(p4 // 2 + 1, 4) * 2
        
        # --- Вычисления ---
        res_coeffs = k1_base * k2_base
        res_power1 = (p1 - p3) // 2
        res_power2 = (p2 - p4) // 2
        
        correct_answer = res_coeffs * (base1 ** res_power1) * (base2 ** res_power2)

        # --- ФИНАЛЬНЫЙ КОНТРОЛЬ ПРОДУКТА ---
        if 0 < correct_answer <= 1000:
            break # Если ответ в пределах нормы, выходим

    # --- Сборка ---
    term1_text = f"√({k1}{var1}**{p1})"
    term2_text = f"√({k2}{var2}**{p2})"
    denominator_text = f"√({var1}**{p3}{var2}**{p4})"
        
    task_text = f"Найди значение выражения ({term1_text} · {term2_text}) / {denominator_text} при {var1}={base1} и {var2}={base2}"

    # Красивые степени
    replacements = {
        '**2': '²', '**4': '⁴', '**6': '⁶', '**8': '⁸'
    }
    for old, new in replacements.items():
        task_text = task_text.replace(old, new)

    return subtype, task_text, str(correct_answer)

def _generate_power_of_product_and_division() -> Tuple[str, str, str]:
    """
    (12/17) Генерирует задания для подтипа 'power_of_product_and_division'.
    Добавлен контроль размера итогового ответа.
    """
    subtype = "power_of_product_and_division"

    while True:
        # --- Ингредиенты ---
        base1 = random.randint(2, 7)
        base2 = random.randint(base1 + 1, 9)

        # Генерируем степени
        p1 = random.randint(3, 9) # Внешняя степень
        p2 = random.randint(1, p1 - 2) # Степень второго основания в знаменателе

        # --- Вычисления ---
        # Выражение: (base1 · base2)ᵖ¹ / (base1ᵖ¹ · base2ᵖ²)
        # Решение: base2^(p1-p2)
        
        result_power = p1 - p2
        correct_answer_base = base2
        
        # --- Проверка адекватности! ---
        # Правило: степень 0-4 для любого основания, 5-6 только для основания 2
        is_valid = False
        if 0 <= result_power <= 4:
            is_valid = True
        elif (result_power == 5 or result_power == 6) and correct_answer_base == 2:
            is_valid = True
        
        if is_valid:
            break # Если комбинация удачная, выходим из цикла

    correct_answer = correct_answer_base ** result_power
    
    # --- Сборка ---
    task_text = f"Найди значение выражения ({base1}·{base2})**{p1} / ({base1}**{p1}·{base2}**{p2})"

    # Красивые степени
    replacements = {
        '**2': '²', '**3': '³', '**4': '⁴', '**5': '⁵', '**6': '⁶', 
        '**7': '⁷', '**8': '⁸', '**9': '⁹'
    }
    for old, new in replacements.items():
        task_text = task_text.replace(old, new)
        
    return subtype, task_text, str(correct_answer)

def _generate_powers_in_fraction_with_products() -> Tuple[str, str, str]:
    """
    (13/17) Генерирует задания для подтипа 'powers_in_fraction_with_products'.
    Добавлен "Золотой стандарт" контроля ответов.
    """
    subtype = "powers_in_fraction_with_products"

    while True:
        base = random.randint(2, 9)
        p_outer = random.randint(2, 5)

        p1 = random.randint(2, 7)
        p2 = random.randint(2, 7)
        p3 = random.randint(2, 7)
        
        inner_result_choice = random.choice([0, 1, -1, 2])
        p4 = p1 + p2 - p3 - inner_result_choice

        if not (0 < p4 < 10):
            continue

        inner_power = (p1 + p2) - (p3 + p4)
        result_power = inner_power * p_outer
        
        # --- "ЗОЛОТОЙ СТАНДАРТ" ПРОВЕРКИ ОТВЕТА ---
        is_valid = False
        if result_power in [0, 1, 2]:
            is_valid = True
        elif result_power == 3 and base <= 5:
            is_valid = True
        elif result_power == 4 and base <= 4:
            is_valid = True
        elif result_power in [5, 6] and base == 2:
            is_valid = True
        
        if is_valid:
            break

    correct_answer = base ** result_power
    
    task_text = f"Найди значение выражения (({base}**{p1}·{base}**{p2}) / ({base}**{p3}·{base}**{p4}))**{p_outer}"

    # Красивые степени
    replacements = {
        '**2': '²', '**3': '³', '**4': '⁴', '**5': '⁵', '**6': '⁶', 
        '**7': '⁷', '**8': '⁸', '**9': '⁹'
    }
    for old, new in replacements.items():
        task_text = task_text.replace(old, new)
        
    return subtype, task_text, str(correct_answer)

def _generate_product_of_roots_divided_by_root() -> Tuple[str, str, str]:
    """
    (14/17) Генерирует задания для подтипа 'product_of_roots_divided_by_root'.
    Пример: (√65 · √13) / √5
    """
    subtype = "product_of_roots_divided_by_root"

    # --- Конструируем "от ответа" ---
    # 1. Выбираем ответ, который должен получиться
    answer = random.randint(3, 15)
    
    # 2. Находим его квадрат - это число, которое должно остаться под корнем в итоге
    target_square = answer ** 2

    # 3. Выбираем "маскирующий" множитель, который не является квадратом
    mask = random.choice([2, 3, 5, 6, 7, 10, 11, 13])
    
    # 4. Конструируем числа a, b, c по хитрой схеме
    # Мы хотим, чтобы (a*b)/c = target_square
    # Пусть a = mask * k1, c = mask * k2. Тогда (k1*b)/k2 = target_square
    # Пусть b = k2, тогда k1 = target_square.
    # Итак: a = target_square, b = mask2, c = mask
    # Чтобы было интереснее: a = mask * k1, b = mask2, c = k1 * mask2
    
    a_mult = random.randint(2, 10)
    c_mult = random.randint(2, 10)
    while a_mult == c_mult:
        c_mult = random.randint(2, 10)

    a = mask * a_mult
    c = mask * c_mult
    b = target_square * c_mult // a_mult

    # Проверяем, что b получилось целым и не слишком простым
    if b <= 1 or (target_square * c_mult) % a_mult != 0:
        # Если что-то пошло не так, используем простую схему
        a = mask * random.randint(2,5)
        b = target_square
        c = mask * random.randint(2,5) # Может не сократиться, но для разнообразия
        # Самый надежный вариант
        a = target_square * mask
        c = random.randint(2,10)
        b = mask * c

    # Чтобы было еще интереснее, перемешаем a,b,c
    # (√a · √b) / √c  или (√c · √a) / √b ...
    # Мы сделаем проще - просто перемешаем значения
    values = [a, b, c]
    random.shuffle(values)
    final_a, final_b, final_c = values[0], values[1], values[2]
    
    # Пересчитываем ответ для перемешанных значений
    # Мы должны гарантировать, что под корнем будет target_square
    # (final_a * final_b) / final_c должно быть квадратом.
    # Проще всего этого достичь, подделав одно из чисел в конце
    
    final_a = target_square * random.randint(2,5)
    final_c = random.randint(2,5)
    final_b = final_c
    
    # (target_square * k * k) / k = target_square * k - не квадрат
    # (a * b) / c = target_square
    k = random.randint(2, 7)
    final_a = target_square
    final_b = k * random.randint(2,5)
    final_c = k * random.randint(2,5)

    # Самая надежная схема
    k = random.randint(2, 10)
    m = random.randint(2, 10)
    while k == m: m = random.randint(2,10)
    
    final_a = target_square * k
    final_b = m
    final_c = k * m
    
    # --- Сборка ---
    task_text = f"Найди значение выражения (√{final_a} · √{final_b}) / √{final_c}"
    correct_answer = answer
        
    return subtype, task_text, str(correct_answer)

def _generate_powered_fraction_with_root_denominator() -> Tuple[str, str, str]:
    """
    (16/17) Генерирует задания для подтипа 'powered_fraction_with_root_denominator'.
    Пример: (72 / (2√3))²
    """
    subtype = "powered_fraction_with_root_denominator"

    # --- Конструируем "от ответа" ---
    # 1. Выбираем "красивый" ответ
    answer = random.randint(3, 12)
    
    # 2. Выбираем число, которое будет под корнем
    root_val = random.choice([2, 3, 5, 6, 7])
    
    # 3. Выбираем коэффициент перед корнем
    k = random.randint(2, 5)
    
    # 4. Вычисляем, каким должен быть числитель, чтобы все сошлось
    # (numerator / (k * √root_val))² = answer
    # numerator² / (k² * root_val) = answer
    # numerator² = answer * k² * root_val
    # numerator = k * √(answer * root_val)
    # Чтобы numerator был целым, произведение answer * root_val должно быть квадратом
    # Мы "подделаем" answer, чтобы это условие выполнилось
    
    # Ищем квадрат, близкий к answer, который делится на root_val
    # Проще переопределить answer
    mult = random.randint(1, 4)
    answer = root_val * (mult**2)
    
    # Теперь вычисляем числитель по "правильной" формуле
    # numerator = k * √( (root_val * mult²) * root_val )
    # numerator = k * √( root_val² * mult² )
    # numerator = k * root_val * mult
    numerator = k * root_val * mult

    # --- Сборка ---
    task_text = f"Найди значение выражения ({numerator} / ({k}√{root_val}))**2"

    # Красивые степени
    replacements = {'**2': '²'}
    for old, new in replacements.items():
        task_text = task_text.replace(old, new)
        
    correct_answer = answer
        
    return subtype, task_text, str(correct_answer)

def _generate_multiplication_of_roots_and_numbers() -> Tuple[str, str, str]:
    """
    (17/17) Генерирует задания для подтипа 'multiplication_of_roots_and_numbers'.
    Пример: √5 · 3√10 · √2
    """
    subtype = "multiplication_of_roots_and_numbers"

    # --- Конструируем "от ответа" ---
    # 1. Задаем части будущего ответа
    final_coeff = random.randint(2, 5) # Коэффициент, который получится в итоге
    final_root_val = random.randint(2, 5) # Число, которое останется под корнем
    
    # 2. Вычисляем "красивый" ответ
    # answer = final_coeff * final_root_val
    # Мы хотим, чтобы в итоге получилось k * m, где m - извлеченный корень
    # Пусть итоговый ответ будет произведением двух чисел
    num1 = random.randint(2, 6)
    num2 = random.randint(2, 6)
    answer = num1 * num2 * random.randint(2,4)

    # 3. Конструируем множители для задания
    # k1 * √r1 * k2 * √r2 * k3 * √r3 = answer
    # (k1*k2*k3) * √(r1*r2*r3) = answer
    
    # Чтобы было интересно, пусть один из коэффициентов будет 1
    k1 = random.randint(2, 5)
    k2 = 1
    
    # Подбираем подкоренные выражения так, чтобы их произведение было квадратом
    r1 = random.randint(2, 7)
    r2 = random.randint(2, 7)
    # r3 должно "дополнить" r1*r2 до полного квадрата
    square_mult = random.randint(2, 5)
    r3 = r1 * r2 * (square_mult**2)
    
    # Теперь √(r1*r2*r3) = √(r1² * r2² * square_mult²) = r1 * r2 * square_mult
    
    # Итоговый ответ будет: k1 * 1 * (r1 * r2 * square_mult)
    correct_answer = k1 * r1 * r2 * square_mult

    # Чтобы задание было не слишком очевидным, "спрячем" r3
    # r3 = a * b. Например, r3 = 2 * (r1*r2*square_mult²/2)
    # Мы сделаем проще: "разобьем" r3 на два множителя
    temp_r1 = r1
    temp_r2 = r2 * (square_mult**2)
    temp_r3 = r1 * r2

    # Самая надежная схема
    k = random.randint(2, 5)
    r1 = random.randint(2, 5)
    r2 = random.randint(2, 5)
    square_base = random.randint(2, 4)
    r3 = r1 * r2 * (square_base**2)
    
    # "Разбиваем" r3 на два множителя, чтобы запутать
    # r3 = (r1 * square_base) * (r2 * square_base)
    # Нет, лучше так: r1, r2, r3
    # √(r1 * r2 * r3) -> должно быть "красивым"
    
    m1 = random.randint(2,5) # множитель 1
    m2 = random.randint(2,5) # множитель 2
    k = random.randint(2,4) # коэфф
    
    r1 = m1
    r2 = m2 * k
    r3 = m1 * m2 * k
    
    # √(r1*r2*r3) = √(m1 * m2*k * m1*m2*k) = m1*m2*k
    # Это слишком очевидно.
    
    # Финальная, самая лучшая схема:
    k = random.randint(2, 5) # Коэффициент в середине
    
    # Числа под корнями
    r1_part1 = random.randint(2,5)
    r1_part2 = random.randint(2,5)
    r2_part1 = r1_part1
    r2_part2 = random.randint(2,5)
    
    r1 = r1_part1 * r1_part2
    r2 = r2_part1 # == r1_part1
    r3 = r1_part2 * r2_part2
    
    # √(r1*r2*r3) = √( (r1_part1*r1_part2) * r1_part1 * (r1_part2*r2_part2) )
    # = √( r1_part1² * r1_part2² * r2_part2 ) = r1_part1 * r1_part2 * √r2_part2
    # Не подходит.
    
    # Последняя попытка, самая надежная.
    k = random.randint(2, 5)
    r1 = random.randint(2, 7)
    r2 = random.randint(2, 7)
    square_base = random.randint(2, 5)
    
    # √(r1 * r2 * r3) должно быть = r1 * r2 * square_base
    r3 = r1 * r2 * (square_base**2)
    
    # "Прячем" r3, разбивая его на два множителя
    
    # Проще! r1, r2, r3. √(r1*r2*r3) должно быть красивым
    # r1*r2*r3 = full_square
    full_square_base = random.randint(6, 20)
    full_square = full_square_base ** 2
    
    r1 = random.randint(2, 10)
    # r2*r3 = full_square / r1
    # Пусть r2 = 2
    r2 = 2
    if full_square % (r1*r2) != 0:
        # Если не делится, берем простые числа
        r1,r2 = 2,5
    r3 = full_square // (r1*r2)
    if r3 == 0: r3 = 2 # защита
    
    correct_answer = k * full_square_base
    
    # --- Сборка ---
    # Собираем части в случайном порядке
    parts = [f"√{r1}", f"{k}√{r2}", f"√{r3}"]
    random.shuffle(parts)
    task_text = f"Найди значение выражения {' · '.join(parts)}"
        
    return subtype, task_text, str(correct_answer) 

# =================================================================================
# --- ШАГ 2: СОЗДАЕМ "КАРТУ ГЕНЕРАТОРОВ" (Партитура для дирижера) ---
# =================================================================================

# Определяем тип для большей читаемости: функция-генератор
GeneratorFunc = Callable[[], Tuple[str, str, str]]

# Словарь, который связывает строковый ключ подтипа с конкретной функцией
GENERATOR_MAP: Dict[str, GeneratorFunc] = {
    "same_base": _generate_same_base,
    "root_fraction_variable_power": _generate_root_fraction_variable_power,
    "difference_of_squares_with_roots": _generate_difference_of_squares_with_roots,
    "fraction_with_powers": _generate_fraction_with_powers,
    "expression_with_radicals_and_powers": _generate_expression_with_radicals_and_powers,
    "expressions_with_powers": _generate_expressions_with_powers,
    "fraction_with_powers_and_substitution": _generate_fraction_with_powers, # Псевдоним
    "root_of_fraction_with_powers": _generate_root_of_fraction_with_powers,
    "multiplication_of_roots": _generate_multiplication_of_roots,
    "powers_with_variables_and_substitution": _generate_fraction_with_powers, # Псевдоним
    "product_and_division_of_roots_with_variables": _generate_product_and_division_of_roots_with_variables,
    "power_of_product_and_division": _generate_power_of_product_and_division,
    "powers_in_fraction_with_products": _generate_powers_in_fraction_with_products,
    "product_of_roots_divided_by_root": _generate_product_of_roots_divided_by_root,
    "negative_exponents": _generate_fraction_with_powers, # Псевдоним
    "powered_fraction_with_root_denominator": _generate_powered_fraction_with_root_denominator,
    "multiplication_of_roots_and_numbers": _generate_multiplication_of_roots_and_numbers,
}

# =================================================================================
# --- ШАГ 3: ПИШЕМ ФУНКЦИЮ-"ДИРИЖЕРА" ---
# Это единственная функция, которую мы будем вызывать извне.
# =================================================================================

async def generate_task_8_by_subtype(subtype_key: str) -> Optional[Tuple[str, str, str]]:
    """
    Главная функция для генерации задания №8 по указанному подтипу.
    
    :param subtype_key: Строковый ключ подтипа из GENERATOR_MAP или "random".
    :return: Кортеж (subtype, text, answer) или None, если подтип не найден.
    """
    if subtype_key == "random":
        # Выбираем случайный генератор из карты
        random_key = random.choice(list(GENERATOR_MAP.keys()))
        generator_func = GENERATOR_MAP[random_key]
    else:
        # Ищем генератор в карте по ключу. .get() безопаснее, чем [], т.к. вернет None
        generator_func = GENERATOR_MAP.get(subtype_key)

    if generator_func is None:
        # Если генератор не найден, сообщаем об ошибке и возвращаем None
        print(f"ОШИБКА: Неизвестный подтип задания: {subtype_key}")
        return None

    # Вызываем найденный генератор и СОХРАНЯЕМ его результат (кортеж) в переменную
    result = generator_func()

    # А теперь упаковываем этот кортеж в красивый словарь и возвращаем его
    return {
        "subtype": result[0],
        "text": result[1],
        "answer": result[2]
    }

# =================================================================================
# --- НОВЫЙ ТЕСТОВЫЙ БЛОК ДЛЯ ПРОВЕРКИ "ДИРИЖЕРА" ---
# =================================================================================

if __name__ == "__main__":
    print("--- Тестируем новую функцию-дирижера ---")

    # Тест 1: Запрос конкретного подтипа
    print("\n--- Пример 1: Конкретный подтип 'difference_of_squares_with_roots' ---")
    task_data = generate_task_8_by_subtype("difference_of_squares_with_roots")
    if task_data:
        subtype, text, answer = task_data
        print(f"Подтип: {subtype}")
        print(f"Задание: {text}")
        print(f"Правильный ответ: {answer}")

    # Тест 2: Запрос случайного подтипа
    print("\n--- Пример 2: Случайный подтип ('random') ---")
    task_data = generate_task_8_by_subtype("random")
    if task_data:
        subtype, text, answer = task_data
        print(f"Подтип: {subtype}")
        print(f"Задание: {text}")
        print(f"Правильный ответ: {answer}")

    # Тест 3: Запрос несуществующего подтипа
    print("\n--- Пример 3: Несуществующий подтип ---")
    task_data = generate_task_8_by_subtype("non_existent_subtype_key")
    if not task_data:
        print("Тест пройден: функция корректно обработала ошибку.")
    
    print("\n--- Тестирование завершено ---")