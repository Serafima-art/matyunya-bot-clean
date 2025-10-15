# py_generators/task_9_generator.py

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
        "task_type": "9",
        "subtype": subtype,
        "text": text,
        "answer": str(answer)
    }

def get_solvable_quadratic(target_roots):
    """Конструирует квадратное уравнение по заданным корням."""
    x1, x2 = target_roots
    # По теореме Виета
    p = -(x1 + x2)
    q = x1 * x2

    a = 1
    # Если коэффициенты дробные, домножим, чтобы стали целыми
    if isinstance(p, float) or isinstance(q, float):
        denominators = []
        if isinstance(p, float):
            denominators.append(float(p).as_integer_ratio()[1])
        if isinstance(q, float):
            denominators.append(float(q).as_integer_ratio()[1])

        lcm = 1
        if denominators:
            lcm = max(denominators) # Упрощенный поиск НОК для простых случаев
            if len(denominators) > 1 and denominators[0] != denominators[1]:
                lcm = denominators[0] * denominators[1] // math.gcd(denominators[0], denominators[1])

        a = lcm
        b = p * lcm
        c = q * lcm
    else:
        b = p
        c = q

    return int(a), int(b), int(c)

def format_equation(a, b, c):
    """Красиво форматирует уравнение ax^2 + bx + c = 0."""
    parts = []
    if a != 0:
        if a == 1: parts.append("x²")
        elif a == -1: parts.append("-x²")
        else: parts.append(f"{a}x²")

    if b != 0:
        sign = "+" if b > 0 else "-"
        val = abs(b)
        if parts: # Если это не первый член
            if val == 1: parts.append(f" {sign} x")
            else: parts.append(f" {sign} {val}x")
        else: # Если это первый член
            if val == 1: parts.append(f"{sign.replace('+','')}x")
            else: parts.append(f"{sign.replace('+','')}{val}x")

    if c != 0:
        sign = "+" if c > 0 else "-"
        val = abs(c)
        if parts:
            parts.append(f" {sign} {val}")
        else:
            parts.append(f"{sign.replace('+','')}{val}")

    return "".join(parts) + " = 0"

# =================================================================
# 18 "маленьких" функций-генераторов
# =================================================================

def _generate_linear_equation_integer() -> Tuple[str, str, str]:
    subtype_key = "linear_equation_integer"
    x = random.randint(-10, 10)
    a, b, c, d = [random.randint(1, 10) for _ in range(4)]

    # Конструируем уравнение ax + b = cx + d
    # d = ax + b - cx
    d = a*x + b - c*x

    text = f"Реши уравнение: {a}x + {b} = {c}x + {d}"
    return subtype_key, text, str(x)

def _generate_linear_equation_fractional() -> Tuple[str, str, str]:
    subtype_key = "linear_equation_fractional"
    x = random.randint(-10, 10)
    a, c = [random.randint(1, 5) for _ in range(2)]
    b, d = [random.randint(2, 10) for _ in range(2)]

    # x/a + b = x/c + d
    # x/a - x/c = d - b
    # x(1/a - 1/c) = d - b
    # x * (c-a)/ac = d - b
    b = (x * (c-a)/(a*c)) + d

    # Округляем b для простоты
    b = round(b)

    # Пересчитываем x
    x = (d - b) * (a*c) / (c-a) if c-a != 0 else 0

    text = f"Реши уравнение: x/{a} + {b} = x/{c} + {d}"
    return subtype_key, text, str(round(x, 2))

def _generate_linear_equation_rational() -> Tuple[str, str, str]:
    subtype_key = "linear_equation_rational"
    x = round(random.uniform(-9.9, 9.9), 1)
    a = random.randint(1, 20)
    c = random.randint(-10, 10)
    while c == 0: c = random.randint(1,10)

    # a / (x+b) = c  => x+b = a/c => b = a/c - x
    b = round(a/c - x, 1)

    text = f"Реши уравнение: {a}/(x + {b}) = {c}"
    return subtype_key, text, str(x)

def _generate_quadratic_equation_all_roots() -> Tuple[str, str, str]:
    subtype_key = "quadratic_equation_all_roots"
    x1 = random.randint(-9, 8)
    x2 = random.randint(x1 + 1, 9)

    a, b, c = get_solvable_quadratic((x1, x2))
    equation = format_equation(a, b, c)

    text = f"Реши уравнение: {equation}\nЕсли корней несколько, запишите их в ответ без пробелов в порядке возрастания."
    answer = f"{x1}{x2}"
    return subtype_key, text, answer

def _generate_quadratic_equation_bigger_root_integer() -> Tuple[str, str, str]:
    subtype_key = "quadratic_equation_bigger_root_integer"
    x1 = random.randint(-9, 8)
    x2 = random.randint(x1 + 1, 9)

    a, b, c = get_solvable_quadratic((x1, x2))
    equation = format_equation(a, b, c)

    text = f"Реши уравнение: {equation} Если уравнение имеет более одного корня, в ответ запишите больший из корней."
    answer = str(max(x1, x2))
    return subtype_key, text, answer

def _generate_quadratic_equation_bigger_root_fractional() -> Tuple[str, str, str]:
    subtype_key = "quadratic_equation_bigger_root_fractional"
    x1 = random.choice([-0.5, -0.25, 0.25, 0.75])
    x2 = x1 + random.choice([1, 2, 0.5])

    a, b, c = get_solvable_quadratic((x1, x2))
    equation = format_equation(a, b, c)

    text = f"Реши уравнение: {equation} Если уравнение имеет более одного корня, в ответ запишите больший из корней."
    answer = str(max(x1, x2))
    return subtype_key, text, answer

def _generate_quadratic_equation_smaller_root_integer() -> Tuple[str, str, str]:
    subtype_key = "quadratic_equation_smaller_root_integer"
    x1 = random.randint(-9, 8)
    x2 = random.randint(x1 + 1, 9)

    a, b, c = get_solvable_quadratic((x1, x2))
    equation = format_equation(a, b, c)

    text = f"Реши уравнение: {equation} Если уравнение имеет более одного корня, в ответ запишите меньший из корней."
    answer = str(min(x1, x2))
    return subtype_key, text, answer

def _generate_quadratic_equation_smaller_root_fractional() -> Tuple[str, str, str]:
    subtype_key = "quadratic_equation_smaller_root_fractional"
    x1 = random.choice([-0.5, -0.25, 0.25, 0.75])
    x2 = x1 - random.choice([1, 2, 0.5])

    a, b, c = get_solvable_quadratic((x1, x2))
    equation = format_equation(a, b, c)

    text = f"Реши уравнение: {equation} Если уравнение имеет более одного корня, в ответ запишите меньший из корней."
    answer = str(min(x1, x2))
    return subtype_key, text, answer

def _generate_square_equals_square() -> Tuple[str, str, str]:
    subtype_key = "square_equals_square"
    a = random.randint(-10, 10)
    b = random.randint(-10, 10)
    while a == b: b = random.randint(-10, 10)

    # (x+a)^2 = (x+b)^2 => x^2+2ax+a^2 = x^2+2bx+b^2 => 2ax-2bx = b^2-a^2 => 2x(a-b) = (b-a)(b+a) => 2x = -(a+b)
    x = -(a+b) / 2

    text = f"Реши уравнение: (x + {a})² = (x - {b})²"
    return subtype_key, text, str(x)

def _generate_product_of_factors_all_roots() -> Tuple[str, str, str]:
    subtype_key = "product_of_factors_all_roots"
    a = random.randint(-9, 9)
    b = random.randint(-9, 9)
    while a == b: b = random.randint(-9, 9)

    x1, x2 = sorted([-a, -b])

    text = f"Реши уравнение: (x + {a})(x + {b}) = 0.\nЕсли уравнение имеет несколько корней, в ответ запишите их подряд без пробелов в порядке возрастания."
    answer = f"{x1}{x2}"
    return subtype_key, text, answer

def _generate_product_of_factors_bigger_root() -> Tuple[str, str, str]:
    subtype_key = "product_of_factors_bigger_root"
    a = random.randint(-9, 9)
    b = random.randint(-9, 9)
    while a == b: b = random.randint(-9, 9)

    x1, x2 = -a, -b

    text = f"Реши уравнение: (x + {a})(x + {b}) = 0. Если уравнение имеет более одного корня, в ответ запишите больший из корней."
    answer = str(max(x1, x2))
    return subtype_key, text, answer

def _generate_product_of_factors_smaller_root() -> Tuple[str, str, str]:
    subtype_key = "product_of_factors_smaller_root"
    a = random.randint(-9, 9)
    b = random.randint(-9, 9)
    while a == b: b = random.randint(-9, 9)

    x1, x2 = -a, -b

    text = f"Реши уравнение: (x + {a})(x + {b}) = 0. Если уравнение имеет более одного корня, в ответ запишите меньший из корней."
    answer = str(min(x1, x2))
    return subtype_key, text, answer

def _generate_difference_of_squares() -> Tuple[str, str, str]:
    subtype_key = "difference_of_squares"
    a = random.randint(2, 15)
    a_sq = a**2

    text = f"Реши уравнение: x² − {a_sq} = 0. Если уравнение имеет более одного корня, в ответ запишите больший из корней."
    answer = str(a)
    return subtype_key, text, answer

def _generate_quadratic_both_sides() -> Tuple[str, str, str]:
    subtype_key = "quadratic_both_sides_smaller_root_integer"
    x1 = random.randint(-5, 4)
    x2 = random.randint(x1 + 1, 5)

    a, b, c = get_solvable_quadratic((x1, x2))

    # ax^2+bx+c = 0 => ax^2 = -bx-c
    b_split = random.randint(1, b-1) if b > 1 else 0
    c_split = random.randint(1, c-1) if c > 1 else 0

    left = f"{a}x²"
    right = f"{-(b-b_split)}x + {-c_split}"

    text = f"Реши уравнение: {left} = {right}. Если уравнение имеет более одного корня, в ответ запишите меньший из корней."
    answer = str(min(x1, x2))
    return subtype_key, text, answer

def _generate_system_sum() -> Tuple[str, str, str]:
    subtype_key = "system_sum"
    x = random.randint(-5, 5)
    y = random.randint(-5, 5)

    a1, b1, a2, b2 = [random.randint(1, 5) for _ in range(4)]

    # a1*x + b1*y = c1
    # a2*x + b2*y = c2
    c1 = a1*x + b1*y
    c2 = a2*x + b2*y

    answer = x + y

    text = (
    "Реши систему уравнений:\n"
    f"<code>{a1}x + {b1}y = {c1}\n"
    f"{a2}x + {b2}y = {c2}</code>\n\n"
    "В ответ запишите x + y."
)
    return subtype_key, text, str(answer)

def _generate_expressions_equal() -> Tuple[str, str, str]:
    subtype_key = "expressions_equal"
    x = random.randint(-10, 10)
    a, b, c, d = [random.randint(1, 10) for _ in range(4)]

    # ax + b = cx + d
    d = a*x + b - c*x

    text = f"При каком значении x выражения {a}x + {b} и {c}x + {d} равны?"
    return subtype_key, text, str(x)

def _generate_given_roots_find() -> Tuple[str, str, str]:
    subtype_key = "given_roots_find"
    x1 = random.randint(-9, 0)
    x2 = random.randint(1, 9)

    q = x1 * x2
    p = -(x1 + x2)

    text = f"Уравнение x² + {p}x + {q} = 0 имеет корни {x1} и {x2}. Найдите их произведение."
    answer = str(q)
    return subtype_key, text, answer

def _generate_factorized_quadratic() -> Tuple[str, str, str]:
    subtype_key = "factorized_quadratic"
    a = random.randint(-9, 9)
    b = random.randint(-9, 9)
    while a == b: b = random.randint(-9, 9)

    x1, x2 = -a, -b

    text = f"Квадратный трёхчлен разложен на множители: (x + {a})(x + {b}). Найдите сумму корней уравнения (x + {a})(x + {b}) = 0."
    answer = str(x1 + x2)
    return subtype_key, text, answer

# =================================================================
# "Карта дирижера"
# =================================================================
GENERATOR_MAP: Dict[str, GeneratorFunc] = {
    "linear_equation_integer": _generate_linear_equation_integer,
    "linear_equation_fractional": _generate_linear_equation_fractional,
    "linear_equation_rational": _generate_linear_equation_rational,
    "quadratic_equation_all_roots": _generate_quadratic_equation_all_roots,
    "quadratic_equation_bigger_root_integer": _generate_quadratic_equation_bigger_root_integer,
    "quadratic_equation_bigger_root_fractional": _generate_quadratic_equation_bigger_root_fractional,
    "quadratic_equation_smaller_root_integer": _generate_quadratic_equation_smaller_root_integer,
    "quadratic_equation_smaller_root_fractional": _generate_quadratic_equation_smaller_root_fractional,
    "square_equals_square": _generate_square_equals_square,
    "product_of_factors_all_roots": _generate_product_of_factors_all_roots,
    "product_of_factors_bigger_root": _generate_product_of_factors_bigger_root,
    "product_of_factors_smaller_root": _generate_product_of_factors_smaller_root,
    "difference_of_squares": _generate_difference_of_squares,
    "quadratic_both_sides_smaller_root_integer": _generate_quadratic_both_sides,
    "system_sum": _generate_system_sum,
    "expressions_equal": _generate_expressions_equal,
    "given_roots_find": _generate_given_roots_find,
    "factorized_quadratic": _generate_factorized_quadratic,
}


# =================================================================
# Главная функция-"дирижер"
# =================================================================
async def generate_task_9_by_subtype(subtype_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Выбирает и запускает нужный генератор для Задания 9.
    Если subtype_key не указан, выбирает случайный.
    """
    if subtype_key is None:
        # Если тема не выбрана, выбираем случайную из карты
        subtype_key = random.choice(list(GENERATOR_MAP.keys()))

    # Ищем генератор в "карте"
    generator_func = GENERATOR_MAP.get(subtype_key)

    # Если ключ не найден, сообщаем об ошибке
    if generator_func is None:
        print(f"ОШИБКА: Неизвестный подтип задания 9: {subtype_key}")
        return None

    # Вызываем найденный генератор и СОХРАНЯЕМ его результат (кортеж)
    result = generator_func()

    # А теперь упаковываем этот кортеж в красивый словарь и возвращаем его
    return {
        "subtype": result[0],
        "text": result[1],
        "answer": result[2]
    }

# =================================================================
# Блок для тестирования генератора
# Запускается, если запустить этот файл напрямую: python py_generators/task_9_generator.py
# =================================================================
if __name__ == "__main__":
    print(f"--- Тестируем {len(GENERATOR_MAP)} подтипов Задания 9 ---")

    # Проходим по каждому генератору в нашей "карте"
    for subtype_key, generator_func in GENERATOR_MAP.items():
        print(f"\n--- Тест подтипа: {subtype_key} ---")
        try:
            # Запускаем "маленький" генератор
            subtype, text, answer = generator_func()

            # Проверяем, что результат адекватный
            if not text or not answer:
                print("❌ ОШИБКА: Генератор вернул пустой текст или ответ.")
                continue

            print(f"  ✅ Успешно сгенерировано!")
            print(f"     Текст: {text}")
            print(f"     Ответ: {answer}")

        except Exception as e:
            print(f"❌ КРИТИЧЕСКАЯ ОШИБКА в генераторе {subtype_key}: {e}")

    print("\n--- Тестирование завершено ---")
