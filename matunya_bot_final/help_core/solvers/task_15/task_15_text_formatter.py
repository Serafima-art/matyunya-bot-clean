"""
Универсальный форматер текста и чисел для решений Задания 15.
Поддерживает перевод десятичных дробей в обыкновенные (0.666... -> 2/3).
"""
from typing import Union
from fractions import Fraction

def format_number(value: Union[float, int, None]) -> Union[int, str, None]:
    """
    1. Если число целое (5.0) -> int (5).
    2. Если число дробное (0.6666666667) -> "2/3".
    3. Если дробь сложная или конечная (0.75) -> "3/4" (или 0,75, но Fraction предпочтительнее для коэффициентов).
    """
    if value is None:
        return None

    # Защита от маленьких погрешностей float
    if abs(value - round(value)) < 1e-9:
        return int(round(value))

    # Пробуем конвертировать в дробь
    try:
        # limit_denominator(100) находит ближайшую дробь с знаменателем не больше 100.
        # Это идеально для школьных задач (2/3, 5/7, 4/9), отсекая мусор типа 317/981.
        frac = Fraction(value).limit_denominator(100)

        # Если дробь "красивая" (знаменатель <= 100), возвращаем её строкой "2/3"
        # Для школьной геометрии это лучше, чем 0,666667
        return f"{frac.numerator}/{frac.denominator}"
    except Exception:
        # Если что-то пошло не так, возвращаем старый добрый float с запятой
        pass

    # Fallback (на всякий случай)
    text = f"{value:.6f}".rstrip('0').rstrip('.')
    return text.replace('.', ',')
