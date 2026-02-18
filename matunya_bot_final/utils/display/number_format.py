# number_format.py

import re


def normalize_decimal(value: float | int | str) -> str:
    s = str(value)

    # точка → запятая
    s = re.sub(r'(?<=\d)\.(?=\d)', ',', s)

    # убираем ,0 и ,00
    s = re.sub(r',0+$', '', s)

    return s


def normalize_minus(text: str) -> str:
    return text.replace("-", "−")


def normalize_multiplication(text: str) -> str:
    return text.replace("*", "·")
