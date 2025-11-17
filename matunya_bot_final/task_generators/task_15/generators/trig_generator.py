"""
Генератор задач по тригонометрии для ОГЭ (Задание 15)
Архитектура: Гибридный Интеллект
"""

from matunya_bot_final.core.templates.geometry_texts import geometry_templates
from matunya_bot_final.help_core.solvers.task_15.trig_calculator import TrigCalculator
import random
import math
from fractions import Fraction

class TrigonometryGenerator:
    """Генератор задач по тригонометрии"""
    
    def __init__(self):
        self.templates = geometry_templates.get('trigonometry', [])
        self.calculator = TrigCalculator()
    
    def generate_task(self, difficulty="medium"):
        """Генерация задачи по тригонометрии"""
        
        # Выбираем тип задачи
        task_types = ['find_cos', 'find_sin', 'find_tg', 'find_side', 'find_angle']
        task_type = random.choice(task_types)
        
        # Генерируем угол
        angle = self._generate_angle(difficulty)
        
        # Генерируем дополнительные параметры
        additional_params = self._generate_additional_params(task_type, angle)
        
        # Создаем задачу
        task = {
            'id': f'trig_{task_type}_{random.randint(1000, 9999)}',
            'type': 'trigonometry',
            'task_type': task_type,
            'angle': angle,
            'difficulty': difficulty,
            'additional_params': additional_params,
            'text': self._generate_task_text(task_type, angle, additional_params)
        }
        
        return task
    
    def _generate_angle(self, difficulty):
        """Генерация угла в зависимости от сложности"""
        if difficulty == "easy":
            angles = [30, 45, 60]
        elif difficulty == "medium":
            angles = [30, 45, 60, 120, 135, 150]
        else:  # hard
            angles = [15, 75, 105, 165, 15, 75]
        
        return random.choice(angles)
    
    def _generate_additional_params(self, task_type, angle):
        """Генерация дополнительных параметров для задачи"""
        params = {}
        
        if task_type == 'find_side':
            # Генерируем одну известную сторону
            params['known_side'] = random.randint(3, 12)
            params['side_name'] = random.choice(['AB', 'BC', 'AC'])
        
        elif task_type in ['find_cos', 'find_sin', 'find_tg']:
            # Для нахождения триг. функций нужны только углы
            pass
        
        elif task_type == 'find_angle':
            # Генерируем значение триг. функции
            trig_functions = ['cos', 'sin', 'tg']
            func = random.choice(trig_functions)
            params['function'] = func
            params['value'] = self._generate_trig_value(func, angle)
        
        return params
    
    def _generate_task_text(self, task_type, angle, params):
        """Генерация текста задачи"""
        
        if task_type == 'find_cos':
            return f"В треугольнике ABC известен угол A = {angle}°. Найдите cos A."
        
        elif task_type == 'find_sin':
            return f"В треугольнике ABC известен угол A = {angle}°. Найдите sin A."
        
        elif task_type == 'find_tg':
            return f"В треугольнике ABC известен угол A = {angle}°. Найдите tg A."
        
        elif task_type == 'find_side':
            return f"В прямоугольном треугольнике ABC угол A = {angle}°, катет {params['side_name']} = {params['known_side']}. Найдите гипотенузу."
        
        elif task_type == 'find_angle':
            return f"В треугольнике ABC {params['function']}(A) = {params['value']}. Найдите угол A."
        
        return "Задача по тригонометрии"
    
    def _generate_trig_value(self, func, angle):
        """Генерация точного значения тригонометрической функции"""
        radians = math.radians(angle)
        
        if func == 'cos':
            if angle == 30:
                return Fraction('√3', 2)
            elif angle == 45:
                return Fraction(1, 2) * '√2'
            elif angle == 60:
                return Fraction(1, 2)
        
        elif func == 'sin':
            if angle == 30:
                return Fraction(1, 2)
            elif angle == 45:
                return Fraction(1, 2) * '√2'
            elif angle == 60:
                return Fraction('√3', 2)
        
        elif func == 'tg':
            if angle == 30:
                return Fraction(1, '√3')
            elif angle == 45:
                return 1
            elif angle == 60:
                return '√3'
        
        return "√2/2"  # fallback