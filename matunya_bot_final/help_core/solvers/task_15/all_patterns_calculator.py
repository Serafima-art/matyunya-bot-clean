"""
Калькулятор для решения всех подтипов задания 15 ОГЭ по математике
Пошаговое решение с объяснениями и формулами
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Tuple
import math

@dataclass
class SolutionStep:
    """Шаг решения задачи"""
    step_number: int
    formula: str
    calculation: str
    explanation: str
    result: str = ""

@dataclass
class StepBuilder:
    """Построитель шагов решения"""
    steps: List[SolutionStep] = field(default_factory=list)
    
    def add_step(self, step_number: int, formula: str, calculation: str, explanation: str, result: str = ""):
        """Добавление нового шага"""
        step = SolutionStep(
            step_number=step_number,
            formula=formula,
            calculation=calculation,
            explanation=explanation,
            result=result
        )
        self.steps.append(step)
        return step
    
    def get_steps(self) -> List[SolutionStep]:
        """Получение всех шагов"""
        return self.steps

class AllPatternsCalculator:
    """Калькулятор для всех подтипов задания 15"""
    
    def __init__(self):
        """Инициализация калькулятора"""
        self.standard_trigonometric_values = {
            0: {'sin': 0, 'cos': 1, 'tg': 0},
            30: {'sin': 0.5, 'cos': 0.866, 'tg': 0.577},
            45: {'sin': 0.707, 'cos': 0.707, 'tg': 1},
            60: {'sin': 0.866, 'cos': 0.5, 'tg': 1.732},
            90: {'sin': 1, 'cos': 0, 'tg': None},  # undefined
        }
    
    def solve_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Решение задачи определенного подтипа
        
        Args:
            task: Данные задачи с полями subtype, data и text
        
        Returns:
            Словарь с решением и шагами
        """
        subtype = task.get('subtype')
        data = task.get('data', {})
        
        # Маршрутизация к соответствующему методу решения
        if subtype == "right_triangle_angles_sum":
            return self._solve_right_triangle_angles_sum(data)
        elif subtype == "isosceles_triangle_angles":
            return self._solve_isosceles_triangle_angles(data)
        elif subtype == "triangle_external_angle":
            return self._solve_triangle_external_angle(data)
        elif subtype == "pythagoras_find_leg":
            return self._solve_pythagoras_find_leg(data)
        elif subtype == "pythagoras_find_hypotenuse":
            return self._solve_pythagoras_find_hypotenuse(data)
        elif subtype == "find_cos_sin_tg_from_sides":
            return self._solve_find_cos_sin_tg_from_sides(data)
        elif subtype == "equilateral_height_to_side":
            return self._solve_equilateral_height_to_side(data)
        elif subtype == "equilateral_side_to_height":
            return self._solve_equilateral_side_to_height(data)
        elif subtype == "triangle_area_by_sin":
            return self._solve_triangle_area_by_sin(data)
        elif subtype == "cosine_law_find_cos":
            return self._solve_cosine_law_find_cos(data)
        else:
            return self._solve_unknown_type(subtype)
    
    def _solve_right_triangle_angles_sum(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Решение: Сумма углов прямоугольного треугольника"""
        builder = StepBuilder()
        
        known_angle = data['known_angle']
        unknown_angle = 90 - known_angle
        
        builder.add_step(
            1,
            "Сумма острых углов в прямоугольном треугольнике",
            "∠A + ∠B = 90°",
            "В прямоугольном треугольнике сумма острых углов равна 90°"
        )
        
        builder.add_step(
            2,
            f"∠A = {known_angle}°",
            f"∠B = 90° - {known_angle}° = {unknown_angle}°",
            f"Подставляем известный угол ∠A = {known_angle}°"
        )
        
        return {
            'steps': builder.get_steps(),
            'final_result': f"∠B = {unknown_angle}°",
            'task_type': 'angles_calculation'
        }
    
    def _solve_isosceles_triangle_angles(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Решение: Углы равнобедренного треугольника"""
        builder = StepBuilder()
        
        base_angle = data['base_angle']
        vertex_angle = data['vertex_angle']
        
        builder.add_step(
            1,
            "Углы при основании равны",
            "∠A = ∠C = base_angle",
            "В равнобедренном треугольнике углы при основании равны"
        )
        
        builder.add_step(
            2,
            "Сумма углов треугольника",
            "∠A + ∠B + ∠C = 180°",
            "Сумма внутренних углов любого треугольника равна 180°"
        )
        
        builder.add_step(
            3,
            f"∠B = 180° - 2 × {base_angle}° = {vertex_angle}°",
            "∠B = 180° - 2∠A",
            "Подставляем известные значения: ∠A = ∠C = base_angle"
        )
        
        return {
            'steps': builder.get_steps(),
            'final_result': f"Угол при вершине B = {vertex_angle}°",
            'task_type': 'isosceles_angles'
        }
    
    def _solve_triangle_external_angle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Решение: Внешний угол треугольника"""
        builder = StepBuilder()
        
        angle1 = data['internal_angle1']
        angle2 = data['internal_angle2']
        third_angle = data['third_angle']
        external_angle = data['external_angle']
        
        builder.add_step(
            1,
            "Сумма внутренних углов треугольника",
            f"∠A + ∠B + ∠C = 180°\n{angle1}° + {angle2}° + ∠C = 180°",
            "Сумма внутренних углов любого треугольника равна 180°"
        )
        
        builder.add_step(
            2,
            "Нахождение угла C",
            f"∠C = 180° - {angle1}° - {angle2}° = {third_angle}°",
            f"∠C = 180° - {angle1}° - {angle2}°"
        )
        
        builder.add_step(
            3,
            "Внешний угол = 180° - внутренний угол",
            f"Внешний угол = 180° - {third_angle}° = {external_angle}°",
            "Внешний угол равен сумме двух внутренних углов, не смежных с ним"
        )
        
        return {
            'steps': builder.get_steps(),
            'final_result': f"Внешний угол = {external_angle}°",
            'task_type': 'external_angle'
        }
    
    def _solve_pythagoras_find_leg(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Решение: Теорема Пифагора - нахождение катета"""
        builder = StepBuilder()
        
        known_leg = data['known_leg']
        hypotenuse = data['hypotenuse']
        unknown_leg = data['unknown_leg']
        
        builder.add_step(
            1,
            "Теорема Пифагора",
            "a² + b² = c²",
            "В прямоугольном треугольнике квадрат гипотенузы равен сумме квадратов катетов"
        )
        
        builder.add_step(
            2,
            f"{known_leg}² + b² = {hypotenuse}²",
            f"b² = {hypotenuse}² - {known_leg}²",
            f"Подставляем известный катет = {known_leg} и гипотенуза = {hypotenuse}"
        )
        
        builder.add_step(
            3,
            "Вычисления",
            f"b² = {hypotenuse**2} - {known_leg**2} = {hypotenuse**2 - known_leg**2}",
            "Возводим в квадрат и вычисляем разность"
        )
        
        builder.add_step(
            4,
            "Извлечение квадратного корня",
            f"b = √{hypotenuse**2 - known_leg**2} = {unknown_leg}",
            "Извлекаем квадратный корень из результата"
        )
        
        return {
            'steps': builder.get_steps(),
            'final_result': f"Неизвестный катет = {unknown_leg}",
            'task_type': 'pythagoras'
        }
    
    def _solve_pythagoras_find_hypotenuse(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Решение: Теорема Пифагора - нахождение гипотенузы"""
        builder = StepBuilder()
        
        leg1 = data['leg1']
        leg2 = data['leg2']
        hypotenuse = data['hypotenuse']
        
        builder.add_step(
            1,
            "Теорема Пифагора",
            "a² + b² = c²",
            "В прямоугольном треугольнике квадрат гипотенузы равен сумме квадратов катетов"
        )
        
        builder.add_step(
            2,
            f"{leg1}² + {leg2}² = c²",
            f"c² = {leg1**2} + {leg2**2}",
            f"Подставляем катеты: a = {leg1}, b = {leg2}"
        )
        
        builder.add_step(
            3,
            "Вычисления",
            f"c² = {leg1**2} + {leg2**2} = {leg1**2 + leg2**2}",
            "Возводим в квадрат и суммируем"
        )
        
        builder.add_step(
            4,
            "Извлечение квадратного корня",
            f"c = √{leg1**2 + leg2**2} = {hypotenuse}",
            "Извлекаем квадратный корень из результата"
        )
        
        return {
            'steps': builder.get_steps(),
            'final_result': f"Гипотенуза = {hypotenuse}",
            'task_type': 'pythagoras'
        }
    
    def _solve_find_cos_sin_tg_from_sides(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Решение: Тригонометрические функции через стороны"""
        builder = StepBuilder()
        
        leg_a = data['leg_a']
        leg_b = data['leg_b']
        hypotenuse = data['hypotenuse']
        angle_type = data['angle_type']
        trig_function = data['trig_function']
        
        if angle_type == 'opposite':
            opposite = leg_a
            adjacent = leg_b
            angle_desc = "при катете a"
        else:
            opposite = leg_b
            adjacent = leg_a
            angle_desc = "при катете b"
        
        builder.add_step(
            1,
            "Определение сторон треугольника",
            f"Противолежащий катет = {opposite}, прилежащий катет = {adjacent}",
            f"Анализируем угол {angle_desc}"
        )
        
        if trig_function == 'sin':
            formula = f"sin α = противолежащий катет / гипотенуза = {opposite} / {hypotenuse}"
            result = f"{opposite}/{hypotenuse:.3f} = {opposite/hypotenuse:.3f}"
        elif trig_function == 'cos':
            formula = f"cos α = прилежащий катет / гипотенуза = {adjacent} / {hypotenuse}"
            result = f"{adjacent}/{hypotenuse:.3f} = {adjacent/hypotenuse:.3f}"
        elif trig_function == 'tg':
            formula = f"tg α = противолежащий катет / прилежащий катет = {opposite} / {adjacent}"
            result = f"{opposite}/{adjacent:.3f} = {opposite/adjacent:.3f}"
        
        builder.add_step(
            2,
            "Тригонометрическая функция",
            formula,
            f"Используем определение {trig_function} угла α"
        )
        
        builder.add_step(
            3,
            "Вычисления",
            result,
            "Выполняем деление и округляем до 3 знаков после запятой"
        )
        
        return {
            'steps': builder.get_steps(),
            'final_result': f"{trig_function} α = {result.split('=')[-1].strip()}",
            'task_type': 'trigonometry'
        }
    
    def _solve_equilateral_height_to_side(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Решение: Высота равностороннего треугольника"""
        builder = StepBuilder()
        
        height = data['height']
        side = data['side']
        
        builder.add_step(
            1,
            "Формула высоты равностороннего треугольника",
            "h = (√3/2) × a",
            "В равностороннем треугольнике высота равна (√3/2) от стороны"
        )
        
        builder.add_step(
            2,
            f"Подстановка значений",
            f"{height} = (√3/2) × a",
            f"Подставляем известную высоту h = {height}"
        )
        
        builder.add_step(
            3,
            "Нахождение стороны",
            f"a = {height} × 2/√3 = {side}",
            "Выражаем сторону a из формулы: a = h × 2/√3"
        )
        
        return {
            'steps': builder.get_steps(),
            'final_result': f"Сторона равностороннего треугольника = {side}",
            'task_type': 'equilateral'
        }
    
    def _solve_equilateral_side_to_height(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Решение: Сторона равностороннего треугольника"""
        builder = StepBuilder()
        
        side = data['side']
        height = data['height']
        
        builder.add_step(
            1,
            "Формула высоты равностороннего треугольника",
            "h = (√3/2) × a",
            "В равностороннем треугольнике высота равна (√3/2) от стороны"
        )
        
        builder.add_step(
            2,
            "Подстановка значений",
            f"h = (√3/2) × {side} = {height}",
            f"Подставляем сторону a = {side}"
        )
        
        return {
            'steps': builder.get_steps(),
            'final_result': f"Высота равностороннего треугольника = {height}",
            'task_type': 'equilateral'
        }
    
    def _solve_triangle_area_by_sin(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Решение: Площадь через две стороны и синус угла"""
        builder = StepBuilder()
        
        side_a = data['side_a']
        side_b = data['side_b']
        angle_c = data['angle_c']
        area = data['area']
        
        builder.add_step(
            1,
            "Формула площади через две стороны и синус угла",
            "S = ½ × a × b × sin C",
            "Основная формула для площади треугольника через две стороны и угол между ними"
        )
        
        sin_value = "sin(данный угол)"
        builder.add_step(
            2,
            f"Подстановка значений",
            f"S = ½ × {side_a} × {side_b} × {sin_value}",
            f"Подставляем известные стороны a = {side_a}, b = {side_b}, угол C = {angle_c}°"
        )
        
        builder.add_step(
            3,
            "Вычисления",
            f"S = ½ × {side_a} × {side_b} × {sin_value} = {area}",
            "Выполняем вычисления согласно формуле"
        )
        
        return {
            'steps': builder.get_steps(),
            'final_result': f"Площадь треугольника = {area}",
            'task_type': 'area_calculation'
        }
    
    def _solve_cosine_law_find_cos(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Решение: Закон косинусов"""
        builder = StepBuilder()
        
        side_a = data['side_a']
        side_b = data['side_b']
        side_c = data['side_c']
        cos_a = data['cos_a']
        
        builder.add_step(
            1,
            "Закон косинусов",
            "cos A = (b² + c² - a²) / (2bc)",
            "Закон косинусов для нахождения косинуса угла A"
        )
        
        builder.add_step(
            2,
            "Подстановка значений",
            f"cos A = ({side_b}² + {side_c}² - {side_a}²) / (2 × {side_b} × {side_c})",
            f"Подставляем стороны a = {side_a}, b = {side_b}, c = {side_c}"
        )
        
        numerator = side_b**2 + side_c**2 - side_a**2
        denominator = 2 * side_b * side_c
        builder.add_step(
            3,
            "Вычисления",
            f"cos A = ({side_b**2} + {side_c**2} - {side_a**2}) / (2 × {side_b} × {side_c}) = {numerator}/{denominator} = {cos_a}",
            f"Выполняем вычисления: числитель = {numerator}, знаменатель = {denominator}"
        )
        
        return {
            'steps': builder.get_steps(),
            'final_result': f"cos A = {cos_a}",
            'task_type': 'cosine_law'
        }
    
    def _solve_unknown_type(self, subtype: str) -> Dict[str, Any]:
        """Решение для неизвестного типа задачи"""
        builder = StepBuilder()
        builder.add_step(
            1,
            "Неизвестный тип задачи",
            f"Тип задачи '{subtype}' не распознан",
            "Обратитесь к разработчику для добавления поддержки этого типа"
        )
        
        return {
            'steps': builder.get_steps(),
            'final_result': f"Решение для типа '{subtype}' не реализовано",
            'task_type': 'unknown'
        }
