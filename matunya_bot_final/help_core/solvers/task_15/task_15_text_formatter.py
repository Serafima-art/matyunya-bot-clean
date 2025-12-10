"""
Универсальный форматер текста и чисел для решений Задания 15.
"""
from typing import Union

def format_number(value: Union[float, int, None]) -> Union[int, str, None]:
    """
    Приводит число к int, если оно целое, иначе к строке с запятой и без лишних нулей.
    Например: 5.0 -> 5; 5.1200 -> "5,12"; 5.000001 -> "5,000001"
    """
    if value is None:
        return None

    # Проверяем, является ли число "почти целым"
    if abs(value - round(value)) < 1e-9:
        return int(round(value))

    # Форматируем в строку с 6 знаками после запятой, убираем лишние нули
    text = f"{value:.6f}".rstrip('0').rstrip('.')
    return text.replace('.', ',')
