# utils/answer_utils.py
"""
УНИВЕРСАЛЬНЫЕ УТИЛИТЫ V3.0: Для сравнения ответов пользователей.
- Понимает дроби, корни, десятичные числа.
- Понимает смысл слов "уменьшится/увеличится" для задач с +/-.
"""
import re
import math
from fractions import Fraction
from typing import Union, Any, Dict, Optional



def _parse_answer_to_number(value: str) -> Optional[Union[Fraction, float]]:
    """
    (Интегрировано из answer_check.py)
    Универсальный парсер, который преобразует строку ответа в число.
    Понимает: целые, десятичные, дроби (простые и смешанные), корни.
    """
    if not isinstance(value, str): return None
    # Нормализуем строку: убираем пробелы, меняем знаки и запятые
    s = value.strip().replace("−", "-").replace(",", ".")
    
    try:
        # 1. Проверяем на корень (e.g., "-2 √ 3")
        match = re.match(r'^(-?)([\d\.]*)\s*√\s*([\d\.]+)$', s)
        if match:
            sign = -1.0 if match.group(1) == '-' else 1.0
            multiplier_str = match.group(2)
            multiplier = float(multiplier_str) if multiplier_str else 1.0
            number_under_root = float(match.group(3))
            return sign * multiplier * math.sqrt(number_under_root)

        # 2. Пробуем обработать как смешанную дробь (e.g., "1 1/2")
        if ' ' in s:
            parts = s.split()
            if len(parts) == 2:
                whole = int(parts[0])
                frac = Fraction(parts[1])
                return whole + frac if whole >= 0 else whole - frac

        # 3. Пробуем обработать как обычную дробь (e.g., "1/3")
        if '/' in s:
            return Fraction(s)

        # 4. Пробуем обработать как десятичную или целое
        return float(s)

    except (ValueError, IndexError):
        return None

def normalize_answer_string(answer: str) -> str:
    """
    Нормализует текстовую часть ответа для сравнения.
    """
    if not answer:
        return ""
    normalized = answer.lower().strip()
    normalized = re.sub(r'\s+', ' ', normalized)
    # Заменяем запятые на точки ВНЕ зависимости от чисел, для текста
    normalized = normalized.replace(',', '.')
    normalized = re.sub(r'[.,!?;:]+$', '', normalized)
    return normalized.strip()

def answers_equal(user_answer: str, correct_answer: Union[str, int, float]) -> bool:
    """
    УНИВЕРСАЛЬНЫЙ СУДЬЯ V3.0: Сравнивает ответы, объединяя все наши правила.
    """
    if not user_answer:
        return False

    user_str_norm = normalize_answer_string(user_answer)
    correct_str_norm = normalize_answer_string(str(correct_answer))

    # --- ЛОГИКА для задач с +/- ("уменьшится/увеличится") ---
    if correct_str_norm.startswith('-'):
        correct_value_abs = correct_str_norm[1:]
        
        # Ищем слова-маркеры "уменьшения"
        decrease_markers = ['уменьш', 'сниз', 'меньше']
        has_decrease_word = any(marker in user_str_norm for marker in decrease_markers)
        
        # Ищем число в ответе пользователя
        user_value_match = re.search(r'(\d+(\.\d+)?)', user_str_norm)
        user_value_str = user_value_match.group(0) if user_value_match else ""

        # Правило 1: Пользователь написал отрицательное число (e.g., "-3.8")
        if user_str_norm == correct_str_norm:
            return True
        # Правило 2: Пользователь написал слово "уменьшится" и правильное число без знака
        if has_decrease_word and user_value_str == correct_value_abs:
            return True
        
        return False

    # --- ОСНОВНАЯ ЛОГИКА для всех остальных задач ---
    user_val = _parse_answer_to_number(user_str_norm)
    correct_val = _parse_answer_to_number(correct_str_norm)

    # Если оба ответа успешно распознаны как числа, сравниваем их математически
    if user_val is not None and correct_val is not None:
        # Сравниваем с погрешностью, чтобы 0.333... было равно 1/3
        return abs(float(user_val) - float(correct_val)) < 0.001
        
    # Если это не числа (или одно из них), сравниваем как нормализованные строки
    return user_str_norm == correct_str_norm

# --- Вспомогательные функции (оставляем без изменений) ---

def format_answer_for_display(answer: Union[str, int, float]) -> str:
    """
    Форматирует ответ для отображения пользователю.
    """
    if isinstance(answer, (int, float)):
        if isinstance(answer, float) and answer.is_integer():
            return str(int(answer))
        return str(answer)
    
    return str(answer).strip()

def is_perfect_square(n: int) -> bool:
    root = int(math.sqrt(n))
    return root * root == n


def parse_sqrt_option(opt: str) -> Optional[int]:
    """
    Преобразует строку типа '√17' → 17.
    Если не подходит — возвращает None.
    """
    if opt.startswith("√"):
        try:
            return int(opt[1:])
        except:
            return None
    return None


def extract_point_pos(img: Dict[str, Any], label: str) -> Optional[float]:
    """
    Возвращает координату точки по её label из image_params
    """
    points = img.get("points", [])
    for pt in points:
        if pt.get("label") == label:
            return pt.get("pos")
    return None


def validate_axis(img: Dict[str, Any]) -> Optional[tuple[float, float]]:
    """
    Проверка и возврат (min_val, max_val) из image_params
    """
    try:
        min_val = img["min_val"]
        max_val = img["max_val"]
        if isinstance(min_val, (int, float)) and isinstance(max_val, (int, float)) and min_val < max_val:
            return min_val, max_val
    except:
        pass
    return None


def strictly_between(x: float, a: float, b: float, tol: float = 1e-9) -> bool:
    """
    Проверка: находится ли x строго внутри (a; b), с учётом допуска tol
    """
    return (x - a) > tol and (b - x) > tol


def unique(lst: list) -> bool:
    return len(lst) == len(set(lst))