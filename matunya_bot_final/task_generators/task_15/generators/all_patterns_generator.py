"""
Генератор всех подтипов задания 15 ОГЭ по математике
ИСПРАВЛЕННАЯ ВЕРСИЯ v2 - шаблоны без f-строк при создании
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import random
from datetime import datetime

@dataclass
class Task15Pattern:
    """Модель паттерна задания 15"""
    subtype: str
    category: str
    description: str
    difficulty: str
    required_data: Dict[str, Any]
    solution_steps: List[str]
    formula_template: str

class AllPatternsGenerator:
    """Генератор всех подтипов задания 15"""
    
    # Полный список всех подтипов из требований ОГЭ-2026
    SUBTYPES = {
        # 🔹 A. Геометрические зависимости углов
        "right_triangle_angles_sum": "Один из острых углов прямоугольного треугольника известен. Нужно найти второй острый угол (90° − α).",
        "isosceles_triangle_angles": "В равнобедренном треугольнике даны равные стороны и один угол. Найди оставшиеся углы, используя сумму углов треугольника.",
        "triangle_external_angle": "Известны два внутренних угла треугольника. Найди внешний угол при третьей вершине (сумма внешнего и внутреннего углов = 180°).",

        # 🔹 B. Прямоугольные треугольники и Пифагор
        "pythagoras_find_leg": "Известны катет и гипотенуза прямоугольного треугольника. Найди другой катет по теореме Пифагора.",
        "pythagoras_find_hypotenuse": "Известны оба катета прямоугольного треугольника. Найди гипотенузу по теореме Пифагора.",
        "find_cos_sin_tg_from_sides": "Даны стороны прямоугольного треугольника. Найди sin, cos или tg одного из острых углов.",
        "find_side_from_trig_ratio": "Известно тригонометрическое значение угла (sin, cos или tg) и одна сторона прямоугольного треугольника. Найди неизвестную сторону.",
        "right_triangle_median_to_hypotenuse": "В прямоугольном треугольнике медиана, проведённая к гипотенузе, равна половине гипотенузы. Используй свойства медианы.",

        # 🔹 C. Площадь треугольника
        "triangle_area_by_sin": "Известны две стороны треугольника и угол между ними. Найди площадь с помощью формулы S = ½·a·b·sinC.",
        "triangle_area_by_dividing_point": "На стороне треугольника отмечена точка, делящая её в отношении AD:DC. Найди площадь меньшего треугольника через пропорцию площадей.",
        "triangle_area_by_parallel_line": "Через вершину проведена прямая, параллельная стороне. Используй подобие треугольников: площади относятся как квадраты сходственных сторон.",
        "triangle_area_by_midpoints": "Точки — середины сторон треугольника. Используй подобие: площадь малого треугольника равна ¼ площади большого.",

        # 🔹 D. Равносторонний треугольник
        "equilateral_height_to_side": "По высоте равностороннего треугольника найди сторону, используя h = (√3/2)·a.",
        "equilateral_side_to_height": "По стороне равностороннего треугольника найди высоту, медиану или биссектрису (они равны). Используй a·√3/2.",

        # 🔹 E. Биссектриса и углы
        "angle_bisector_find_half_angle": "В треугольнике проведена биссектриса угла. Нужно найти угол между биссектрисой и стороной — половину данного угла.",
        
        # 🔹 F. Закон косинусов
        "cosine_law_find_cos": "По трем сторонам треугольника найди косинус угла, используя теорему косинусов.",
        
        # 🔹 G. Дополнительные типы
        "triangle_by_two_angles_and_side": "Известны два угла и сторона треугольника. Найди третью сторону через подобие треугольников."
    }
    
    # Категоризация подтипов
    CATEGORIES = {
        "angles": [
            "right_triangle_angles_sum",
            "triangle_external_angle", 
            "angle_bisector_find_half_angle"
        ],
        "right_triangles": [
            "pythagoras_find_leg",
            "pythagoras_find_hypotenuse", 
            "find_cos_sin_tg_from_sides",
            "find_side_from_trig_ratio",
            "right_triangle_median_to_hypotenuse"
        ],
        "general_triangles": [
            "triangle_area_by_sin",
            "triangle_area_by_dividing_point",
            "triangle_area_by_parallel_line", 
            "triangle_area_by_midpoints",
            "equilateral_height_to_side",
            "equilateral_side_to_height",
            "cosine_law_find_cos",
            "triangle_by_two_angles_and_side"
        ],
        "isosceles_triangles": [
            "isosceles_triangle_angles"
        ]
    }

    def __init__(self):
        """Инициализация генератора"""
        self.task_templates = self._load_task_templates()
        self.standard_values = self._load_standard_values()
    
    def generate_task(self, subtype: str = None, difficulty: str = "medium") -> Dict[str, Any]:
        """
        Генерация задачи определенного подтипа
        
        Args:
            subtype: Подтип задачи (если None - случайный)
            difficulty: Сложность (easy, medium, hard)
        
        Returns:
            Словарь с данными задачи
        """
        if subtype is None:
            subtype = random.choice(list(self.SUBTYPES.keys()))
        elif subtype not in self.SUBTYPES:
            raise ValueError(f"Подтип '{subtype}' не поддерживается")
        
        # Генерируем данные для задачи
        task_data = self._generate_task_data(subtype, difficulty)
        
        # Формируем полную задачу
        task = {
            'id': f"task15_{subtype}_{random.randint(1000, 9999)}",
            'subtype': subtype,
            'category': self._get_category(subtype),
            'difficulty': difficulty,
            'description': self.SUBTYPES[subtype],
            'text': self._generate_task_text(subtype, task_data),
            'data': task_data,
            'timestamp': datetime.now().isoformat(),
            'requires_visualization': self._needs_visualization(subtype)
        }
        
        return task
    
    def _generate_task_data(self, subtype: str, difficulty: str) -> Dict[str, Any]:
        """Генерация данных для конкретного подтипа"""
        
        if subtype == "right_triangle_angles_sum":
            # Случайный острый угол (15-75 градусов для разнообразия)
            known_angle = random.choice([15, 30, 45, 60, 75])
            return {
                'known_angle': known_angle,
                'second_angle': 90 - known_angle
            }
        
        elif subtype == "isosceles_triangle_angles":
            # Равнобедренный треугольник с разными сценариями
            if difficulty == "easy":
                # Известен угол при основании
                base_angle = random.choice([30, 45, 60])
                vertex_angle = 180 - 2 * base_angle
            else:
                # Известен угол при вершине
                vertex_angle = random.choice([40, 80, 100])
                base_angle = (180 - vertex_angle) / 2
            
            return {
                'base_angle': base_angle,
                'vertex_angle': vertex_angle,
                'equal_sides': True
            }
        
        elif subtype == "triangle_external_angle":
            # Два внутренних угла
            angle1 = random.choice([30, 40, 50, 60, 70])
            angle2 = random.choice([20, 35, 45, 55, 65])
            third_angle = 180 - angle1 - angle2
            external_angle = 180 - third_angle
            
            return {
                'internal_angle1': angle1,
                'internal_angle2': angle2,
                'third_angle': third_angle,
                'external_angle': external_angle
            }
        
        elif subtype == "pythagoras_find_leg":
            # Прямоугольный треугольник, известны катет и гипотенуза
            leg = random.choice([3, 4, 5, 6, 7, 8, 9, 12])
            hypotenuse = random.choice([5, 5, 10, 13, 15, 17, 25, 15])
            if hypotenuse <= leg:  # Гипотенуза должна быть больше катета
                hypotenuse = leg + 2
            
            second_leg = (hypotenuse**2 - leg**2)**0.5
            
            return {
                'known_leg': leg,
                'hypotenuse': hypotenuse,
                'unknown_leg': round(second_leg, 2)
            }
        
        elif subtype == "pythagoras_find_hypotenuse":
            # Прямоугольный треугольник, известны оба катета
            leg1 = random.choice([3, 4, 5, 6, 7, 8])
            leg2 = random.choice([3, 4, 5, 6, 7, 8])
            hypotenuse = (leg1**2 + leg2**2)**0.5
            
            return {
                'leg1': leg1,
                'leg2': leg2,
                'hypotenuse': round(hypotenuse, 2)
            }
        
        elif subtype == "find_cos_sin_tg_from_sides":
            # Прямоугольный треугольник с целыми сторонами
            leg_a = random.choice([3, 4, 5, 6, 7, 8])
            leg_b = random.choice([3, 4, 5, 6, 7, 8])
            hypotenuse = (leg_a**2 + leg_b**2)**0.5
            
            # Выбираем угол и тригонометрическую функцию
            angle_type = random.choice(['opposite', 'adjacent'])
            trig_function = random.choice(['sin', 'cos', 'tg'])
            
            return {
                'leg_a': leg_a,
                'leg_b': leg_b,
                'hypotenuse': round(hypotenuse, 2),
                'angle_type': angle_type,
                'trig_function': trig_function
            }
        
        elif subtype == "find_side_from_trig_ratio":
            # Найди сторону по тригонометрическому отношению
            angle = random.choice([30, 45, 60])
            known_side = random.choice([3, 4, 5, 6, 7, 8])
            trig_ratio = random.choice(['sin', 'cos', 'tg'])
            
            # Рассчитываем неизвестную сторону
            if trig_ratio == 'sin':
                sin_values = [0.5, 0.707, 0.866]  # sin30, sin45, sin60
                unknown_side = known_side / sin_values[angle//30 - 1]
            elif trig_ratio == 'cos':
                cos_values = [0.866, 0.707, 0.5]  # cos30, cos45, cos60
                unknown_side = known_side / cos_values[angle//30 - 1]
            else:  # tg
                tg_values = [0.577, 1, 1.732]  # tg30, tg45, tg60
                unknown_side = known_side * tg_values[angle//30 - 1]
            
            return {
                'angle': angle,
                'known_side': known_side,
                'trig_ratio': trig_ratio,
                'unknown_side': round(unknown_side, 2),
                'type': random.choice(['opposite', 'adjacent', 'hypotenuse'])
            }
        
        elif subtype == "right_triangle_median_to_hypotenuse":
            # Медиана к гипотенузе
            leg_a = random.choice([3, 4, 5, 6, 8])
            leg_b = random.choice([3, 4, 5, 6, 8])
            hypotenuse = (leg_a**2 + leg_b**2)**0.5
            median = hypotenuse / 2  # Медиана к гипотенузе равна половине гипотенузы
            
            return {
                'leg_a': leg_a,
                'leg_b': leg_b,
                'hypotenuse': round(hypotenuse, 2),
                'median': round(median, 2),
                'given_element': random.choice(['median', 'hypotenuse'])
            }
        
        elif subtype == "equilateral_height_to_side":
            # Равносторонний треугольник
            side = random.choice([2, 4, 6, 8, 10, 12])
            height = (side * 3**0.5) / 2
            
            return {
                'side': side,
                'height': round(height, 2),
                'given_element': random.choice(['height', 'side'])
            }
        
        elif subtype == "equilateral_side_to_height":
            # Равносторонний треугольник (обратная задача)
            side = random.choice([2, 4, 6, 8, 10, 12])
            height = (side * 3**0.5) / 2
            
            return {
                'side': side,
                'height': round(height, 2)
            }
        
        elif subtype == "triangle_area_by_sin":
            # Площадь по двум сторонам и углу между ними
            side_a = random.choice([3, 4, 5, 6, 7, 8])
            side_b = random.choice([3, 4, 5, 6, 7, 8])
            angle_c = random.choice([30, 45, 60, 90, 120])
            
            # Рассчитываем площадь: S = 1/2 * a * b * sin(C)
            import math
            area = 0.5 * side_a * side_b * math.sin(math.radians(angle_c))
            
            return {
                'side_a': side_a,
                'side_b': side_b,
                'angle_c': angle_c,
                'area': round(area, 2)
            }
        
        elif subtype == "triangle_area_by_dividing_point":
            # Площадь с точкой деления
            side_a = random.choice([6, 8, 10, 12])
            side_b = random.choice([4, 6, 8, 10])
            side_c = random.choice([5, 7, 9, 11])
            ratio = random.choice([1, 2, 3])  # AD:DC = ratio:1
            area_large = random.choice([20, 30, 40, 50])
            
            # Площадь малого треугольника через отношение
            if ratio == 1:
                area_small = area_large / 2  # Точка в середине
            else:
                area_small = area_large / (ratio + 1)  # Пропорционально отношению
            
            return {
                'side_a': side_a,
                'side_b': side_b,
                'side_c': side_c,
                'ratio': ratio,
                'area_large': area_large,
                'area_small': round(area_small, 2)
            }
        
        elif subtype == "triangle_area_by_parallel_line":
            # Площадь с параллельной прямой
            side_large = random.choice([8, 10, 12, 16])
            ratio = random.choice([2, 3, 4])  # Отношение сторон
            side_small = side_large / ratio
            area_large = random.choice([40, 60, 80, 100])
            
            # Площади относятся как квадраты сторон
            area_small = area_large / (ratio**2)
            
            return {
                'side_large': side_large,
                'side_small': side_small,
                'ratio': ratio,
                'area_large': area_large,
                'area_small': round(area_small, 2)
            }
        
        elif subtype == "triangle_area_by_midpoints":
            # Площадь с серединами сторон
            side_large = random.choice([8, 10, 12, 14])
            area_large = random.choice([48, 75, 96, 108])
            area_small = area_large / 4  # Площадь малого треугольника = 1/4 площади большого
            
            return {
                'side_large': side_large,
                'side_small': side_large / 2,  # Сторона малого треугольника
                'area_large': area_large,
                'area_small': round(area_small, 2)
            }
        
        elif subtype == "angle_bisector_find_half_angle":
            # Биссектриса угла
            full_angle = random.choice([60, 80, 100, 120])
            half_angle = full_angle / 2
            
            return {
                'full_angle': full_angle,
                'half_angle': half_angle,
                'bisector_drawn': True
            }
        
        elif subtype == "cosine_law_find_cos":
            # Закон косинусов
            side_a = random.choice([5, 6, 7, 8, 9, 10])
            side_b = random.choice([5, 6, 7, 8, 9, 10])
            side_c = random.choice([4, 5, 6, 7, 8, 9])
            cos_a = (side_b**2 + side_c**2 - side_a**2) / (2 * side_b * side_c)
            
            return {
                'side_a': side_a,
                'side_b': side_b,
                'side_c': side_c,
                'cos_a': round(cos_a, 3)
            }
        
        elif subtype == "triangle_by_two_angles_and_side":
            # Два угла и сторона
            angle1 = random.choice([30, 45, 60])
            angle2 = random.choice([45, 60, 75])
            angle3 = 180 - angle1 - angle2
            known_side = random.choice([5, 6, 7, 8, 10])
            
            return {
                'angle1': angle1,
                'angle2': angle2,
                'angle3': angle3,
                'known_side': known_side,
                'proportional_side': round(known_side * angle3 / angle1, 2) if angle1 != 0 else known_side
            }
        
        else:
            # Общие данные для других паттернов
            return {
                'value_a': random.randint(1, 20),
                'value_b': random.randint(1, 20),
                'value_c': random.randint(1, 20)
            }
    
    def _generate_task_text(self, subtype: str, data: Dict[str, Any]) -> str:
        """Генерация текста задачи на основе данных"""
        
        # Шаблоны без f-строк при создании
        template_functions = {
            "right_triangle_angles_sum": lambda d: f"В прямоугольном треугольнике ABC угол A = {d['known_angle']}°. Найдите угол B.",
            
            "isosceles_triangle_angles": lambda d: f"В равнобедренном треугольнике ABC AB = BC. Угол при основании AC равен {d['base_angle']}°. Найдите угол при вершине B.",
            
            "triangle_external_angle": lambda d: f"В треугольнике ABC угол A = {d['internal_angle1']}°, угол B = {d['internal_angle2']}°. Найдите внешний угол при вершине C.",
            
            "pythagoras_find_leg": lambda d: f"В прямоугольном треугольнике известны катет = {d['known_leg']} и гипотенуза = {d['hypotenuse']}. Найдите другой катет.",
            
            "pythagoras_find_hypotenuse": lambda d: f"В прямоугольном треугольнике катеты равны {d['leg1']} и {d['leg2']}. Найдите гипотенузу.",
            
            "find_cos_sin_tg_from_sides": lambda d: f"В прямоугольном треугольнике катеты равны {d['leg_a']} и {d['leg_b']}, гипотенуза ≈ {d['hypotenuse']}. Найдите {d['trig_function']} угла при катете {d['leg_a']}.",
            
            "find_side_from_trig_ratio": lambda d: f"В прямоугольном треугольнике известно {d['trig_ratio']}({d['angle']}°) = {d['known_side']}/{d.get('unknown_side', '?')} и известна сторона = {d['known_side']}. Найдите неизвестную сторону.",
            
            "right_triangle_median_to_hypotenuse": lambda d: f"В прямоугольном треугольнике медиана к гипотенузе равна {d['median']}. Найдите гипотенузу (медиана = гипотенуза ÷ 2).",
            
            "equilateral_height_to_side": lambda d: f"В равностороннем треугольнике высота равна {d['height']}. Найдите сторону треугольника.",
            
            "equilateral_side_to_height": lambda d: f"В равностороннем треугольнике сторона равна {d['side']}. Найдите высоту треугольника.",
            
            "triangle_area_by_sin": lambda d: f"В треугольнике две стороны равны {d['side_a']} и {d['side_b']}, угол между ними {d['angle_c']}°. Найдите площадь треугольника.",
            
            "triangle_area_by_dividing_point": lambda d: f"На стороне треугольника отмечена точка, делящая её в отношении {d['ratio']}:1. Площадь большого треугольника = {d['area_large']}. Найдите площадь меньшего треугольника.",
            
            "triangle_area_by_parallel_line": lambda d: f"Через вершину треугольника проведена прямая, параллельная стороне. Отношение сторон = {d['ratio']}. Площадь большого треугольника = {d['area_large']}. Найдите площадь малого треугольника.",
            
            "triangle_area_by_midpoints": lambda d: f"Точки — середины сторон треугольника. Площадь большого треугольника = {d['area_large']}. Найдите площадь малого треугольника (1/4 от большого).",
            
            "angle_bisector_find_half_angle": lambda d: f"В треугольнике проведена биссектриса угла {d['full_angle']}°. Найдите угол между биссектрисой и стороной (половину данного угла).",
            
            "cosine_law_find_cos": lambda d: f"В треугольнике стороны равны a={d['side_a']}, b={d['side_b']}, c={d['side_c']}. Найдите cos угла A.",
            
            "triangle_by_two_angles_and_side": lambda d: f"В треугольнике известны углы {d['angle1']}° и {d['angle2']}°, а также сторона = {d['known_side']}. Найдите пропорциональную сторону."
        }
        
        # Получаем функцию для этого подтипа
        template_func = template_functions.get(subtype)
        if template_func:
            return template_func(data)
        else:
            return f"Задача подтипа '{subtype}' - данные: {data}"
    
    def _get_category(self, subtype: str) -> str:
        """Определение категории подтипа"""
        for category, subtypes in self.CATEGORIES.items():
            if subtype in subtypes:
                return category
        return "other"
    
    def _needs_visualization(self, subtype: str) -> bool:
        """Определение, нужна ли визуализация для подтипа"""
        # Большинство геометрических задач нуждаются в визуализации
        return True
    
    def _load_task_templates(self) -> Dict[str, str]:
        """Загрузка шаблонов задач (заглушка)"""
        return {}
    
    def _load_standard_values(self) -> Dict[str, Dict]:
        """Загрузка стандартных тригонометрических значений"""
        return {
            0: {'sin': '0', 'cos': '1', 'tg': '0'},
            30: {'sin': '1/2', 'cos': '√3/2', 'tg': '√3/3'},
            45: {'sin': '√2/2', 'cos': '√2/2', 'tg': '1'},
            60: {'sin': '√3/2', 'cos': '1/2', 'tg': '√3'},
            90: {'sin': '1', 'cos': '0', 'tg': 'undefined'}
        }

    def get_subtypes_by_category(self, category: str) -> List[str]:
        """Получение всех подтипов определенной категории"""
        return self.CATEGORIES.get(category, [])
    
    def get_all_subtypes(self) -> List[str]:
        """Получение всех подтипов"""
        return list(self.SUBTYPES.keys())
    
    def get_subtype_info(self, subtype: str) -> Dict[str, str]:
        """Получение информации о подтипе"""
        if subtype not in self.SUBTYPES:
            raise ValueError(f"Подтип '{subtype}' не найден")
        
        return {
            'subtype': subtype,
            'category': self._get_category(subtype),
            'description': self.SUBTYPES[subtype],
            'visualization': 'needed' if self._needs_visualization(subtype) else 'optional'
        }