import re
import math
from ..common import NUM, to_float, PI, format_answer
from ..common import to_float, grab_labeled_number


# 1) area_triangle_find_sin_alpha: sinα = 2S / (b·c)
def _validate_area_triangle_find_sin_alpha(task: dict) -> bool:
    """Валидирует задачу на поиск sinα по площади треугольника."""
    text, answer_str = task.get("text"), task.get("answer")
    if not text or answer_str is None: return False
    
    # Надежно извлекаем все три параметра по их меткам
    S = grab_labeled_number(text, labels=['S'])
    b = grab_labeled_number(text, labels=['b'])
    c = grab_labeled_number(text, labels=['c'])
    
    # Проверяем, что все данные найдены
    if S is None or b is None or c is None:
        return False
        
    # Проверяем, что не будем делить на ноль
    if b == 0 or c == 0:
        return False
        
    # Вычисляем правильный ответ
    correct_answer = (2 * S) / (b * c)
    
    return abs(to_float(answer_str) - correct_answer) < 1e-9