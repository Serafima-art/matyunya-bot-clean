"""
Тригонометрические расчеты для ОГЭ (Задание 15)
Архитектура: Гибридный Интеллект

Пошаговые решения с формулами для ФИПИ
"""

import math
from fractions import Fraction
from dataclasses import dataclass
from dataclasses import field

@dataclass
class StepBuilder:
    """Пошаговое решение задачи"""
    step_number: int
    formula: str
    calculation: str
    result: str
    explanation: str
    angle: float = None
    values: dict = field(default_factory=dict)

class TrigCalculator:
    """Тригонометрический калькулятор для ОГЭ"""
    
    def __init__(self):
        self.standard_values = {
            30: {'cos': '√3/2', 'sin': '1/2', 'tg': '1/√3'},
            45: {'cos': '√2/2', 'sin': '√2/2', 'tg': '1'},
            60: {'cos': '1/2', 'sin': '√3/2', 'tg': '√3'}
        }
    
    def calculate_from_cos(self, cos_value, angle, operation="find_sin"):
        """Расчет по известному cos"""
        steps = []
        
        # Шаг 1: Формула
        steps.append(StepBuilder(
            step_number=1,
            formula="Основное тригонометрическое тождество",
            calculation=f"sin²A + cos²A = 1",
            result=f"sin²A = 1 - cos²A = 1 - ({cos_value})²",
            explanation="Используем основное тригонометрическое тождество"
        ))
        
        # Шаг 2: Вычисляем sin²A
        steps.append(StepBuilder(
            step_number=2,
            formula="Возведение в степень",
            calculation=f"({cos_value})² = {self._calculate_square(cos_value)}",
            result=f"sin²A = 1 - {self._calculate_square(cos_value)} = {self._calculate_1_minus_square(cos_value)}",
            explanation="Возводим cos в квадрат"
        ))
        
        # Шаг 3: Находим sin
        result_value = self._extract_sin(cos_value)
        steps.append(StepBuilder(
            step_number=3,
            formula="Извлечение корня",
            calculation=f"sinA = √({self._calculate_1_minus_square(cos_value)})",
            result=f"sinA = {result_value}",
            explanation="Извлекаем корень из sin²A"
        ))
        
        if operation == "find_tg":
            # Дополнительные шаги для tg
            steps.append(StepBuilder(
                step_number=4,
                formula="Определение тангенса",
                calculation=f"tgA = sinA / cosA = {result_value} / {cos_value}",
                result=f"tgA = {self._calculate_tg(result_value, cos_value)}",
                explanation="Используем определение тангенса"
            ))
        
        return {
            'steps': steps,
            'final_result': self._get_final_result(result_value, operation),
            'angle': angle
        }
    
    def calculate_from_tg(self, tg_value, angle):
        """Расчет по известному tg"""
        steps = []
        
        # Шаг 1: Используем определение tg
        steps.append(StepBuilder(
            step_number=1,
            formula="Определение тангенса",
            calculation=f"tgA = sinA / cosA = {tg_value}",
            result=f"sinA = {tg_value} × cosA",
            explanation="Из определения тангенса"
        ))
        
        # Шаг 2: Подставляем в основное тождество
        steps.append(StepBuilder(
            step_number=2,
            formula="Основное тригонометрическое тождество",
            calculation=f"sin²A + cos²A = 1",
            result=f"({tg_value} × cosA)² + cos²A = 1",
            explanation="Подставляем sinA через tgA"
        ))
        
        # Шаг 3: Решаем уравнение
        steps.append(StepBuilder(
            step_number=3,
            formula="Вынесение за скобки",
            calculation=f"cos²A({tg_value}² + 1) = 1",
            result=f"cosA = 1 / √({tg_value}² + 1)",
            explanation="Решаем квадратное уравнение"
        ))
        
        # Шаг 4: Упрощение
        simplified_cos = self._simplify_cos(tg_value)
        steps.append(StepBuilder(
            step_number=4,
            formula="Упрощение дроби",
            calculation=f"cosA = 1 / √({tg_value}² + 1) = {simplified_cos}",
            result=f"cosA = {simplified_cos}",
            explanation="Упрощаем выражение"
        ))
        
        # Шаг 5: Находим sin
        sin_value = self._calculate_sin_from_tg(tg_value, simplified_cos)
        steps.append(StepBuilder(
            step_number=5,
            formula="Нахождение sinA",
            calculation=f"sinA = {tg_value} × {simplified_cos}",
            result=f"sinA = {sin_value}",
            explanation="Используем связь sinA и cosA"
        ))
        
        return {
            'steps': steps,
            'final_result': f"sinA = {sin_value}, cosA = {simplified_cos}",
            'angle': angle
        }
    
    def calculate_side_from_cos(self, angle, adjacent_side, operation="find_hypotenuse"):
        """Расчет стороны по cos"""
        steps = []
        
        # Шаг 1: Определение cos
        steps.append(StepBuilder(
            step_number=1,
            formula="Определение косинуса",
            calculation=f"cosA = прилежащий катет / гипотенуза = {adjacent_side} / BC",
            result=f"BC = {adjacent_side} / cosA",
            explanation="Из определения косинуса"
        ))
        
        # Шаг 2: Подстановка значения
        cos_value = self._get_cos_value(angle)
        steps.append(StepBuilder(
            step_number=2,
            formula="Подстановка значения cosA",
            calculation=f"BC = {adjacent_side} / {cos_value}",
            result=f"BC = {self._calculate_side(adjacent_side, cos_value)}",
            explanation="Подставляем значение cosA"
        ))
        
        return {
            'steps': steps,
            'final_result': f"BC = {self._calculate_side(adjacent_side, cos_value)}",
            'angle': angle
        }
    
    def _calculate_square(self, cos_value):
        """Вычисляет квадрат значения"""
        try:
            if '√' in str(cos_value):
                return cos_value  # Оставляем как есть
            else:
                return float(cos_value) ** 2
        except:
            return cos_value
    
    def _calculate_1_minus_square(self, cos_value):
        """Вычисляет 1 - cos²"""
        # Упрощенная версия для стандартных углов
        if cos_value == '√3/2':
            return '1/4'
        elif cos_value == '√2/2':
            return '1/2'
        elif cos_value == '1/2':
            return '3/4'
        else:
            return f"1 - ({cos_value})²"
    
    def _extract_sin(self, cos_value):
        """Извлекает значение sin из cos"""
        if cos_value == '√3/2':
            return '1/2'
        elif cos_value == '√2/2':
            return '√2/2'
        elif cos_value == '1/2':
            return '√3/2'
        else:
            return f"√(1 - ({cos_value})²)"
    
    def _calculate_tg(self, sin_value, cos_value):
        """Вычисляет tg через sin и cos"""
        return f"{sin_value} / {cos_value}"
    
    def _get_final_result(self, sin_value, operation):
        """Возвращает окончательный результат"""
        if operation == "find_sin":
            return f"sinA = {sin_value}"
        elif operation == "find_tg":
            return f"tgA = {self._calculate_tg(sin_value, '√3/2')}"  # Пример
        else:
            return sin_value
    
    def _simplify_cos(self, tg_value):
        """Упрощает значение cos для стандартных tg"""
        if tg_value == '1/√3':
            return '√3/2'
        elif tg_value == '1':
            return '√2/2'
        elif tg_value == '√3':
            return '1/2'
        else:
            return "1 / √(1 + " + str(tg_value) + "²)"
    
    def _calculate_sin_from_tg(self, tg_value, cos_value):
        """Вычисляет sin через tg и cos"""
        if tg_value == '1/√3' and cos_value == '√3/2':
            return '1/2'
        elif tg_value == '1' and cos_value == '√2/2':
            return '√2/2'
        elif tg_value == '√3' and cos_value == '1/2':
            return '√3/2'
        else:
            return f"{tg_value} × {cos_value}"
    
    def _get_cos_value(self, angle):
        """Возвращает значение cos для угла"""
        return self.standard_values.get(angle, {}).get('cos', f'cos{angle}°')
    
    def _calculate_side(self, adjacent_side, cos_value):
        """Вычисляет длину стороны"""
        if cos_value == '√3/2':
            return f"{adjacent_side} × 2 / √3"
        elif cos_value == '√2/2':
            return f"{adjacent_side} × √2"
        elif cos_value == '1/2':
            return f"{adjacent_side} × 2"
        else:
            return f"{adjacent_side} / {cos_value}"