"""
Универсальный форматер текста и чисел для решений Задания 15.
Поддерживает перевод десятичных дробей в обыкновенные (0.666... -> 2/3).
"""
from typing import Union
from fractions import Fraction

def format_number(value: Union[float, int, None]) -> Union[int, str, None]:
    """
    Форматирование числа для Ответа в задании 15 (ОГЭ):

    1. 5.0 -> 5
    2. 0.8 -> "0,8"
    3. 1.25 -> "1,25"
    4. None -> None
    """

    if value is None:
        return None

    # Убираем погрешности float
    if abs(value - round(value)) < 1e-9:
        return int(round(value))

    # Формируем строку без лишних нулей
    text = f"{value:.6f}".rstrip("0").rstrip(".")

    # Меняем точку на запятую
    return text.replace(".", ",")
