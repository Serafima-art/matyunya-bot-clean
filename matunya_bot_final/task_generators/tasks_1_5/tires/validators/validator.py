# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
# Validator для подтипа "Шины"
# Проверка JSON данных от GPT-Архитектора на корректность
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---

import re
from typing import Dict, Any, List, Optional, Tuple
import logging
from matunya_bot_final.task_generators.tasks_1_5.tires.calculator import TiresCalculator

logger = logging.getLogger(__name__)

class TiresDataValidator:
    """Валидатор данных для задач про шины"""
    
    def __init__(self):
        self.valid_widths = [175, 185, 195, 205, 215, 225, 235]
        self.valid_diameters = [14, 15, 16, 17, 18]
        self.valid_profile_range = (40, 70)
        self.tire_marking_pattern = re.compile(r'^(\d{3})/(\d{2})\s+R(\d{2})$')
    
    def validate_complete_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Полная валидация данных от GPT-Архитектора
        
        Args:
            data: Словарь с данными для валидации
            
        Returns:
            Кортеж (валидность, список_ошибок)
        """
        errors = []
        
        # 1. Структурная валидация
        struct_valid, struct_errors = self._validate_structure(data)
        errors.extend(struct_errors)
        
        if not struct_valid:
            return False, errors
        
        # 2. Валидация маркировок шин
        marking_valid, marking_errors = self._validate_tire_markings(data)
        errors.extend(marking_errors)
        
        # 3. Валидация таблицы допустимых размеров
        table_valid, table_errors = self._validate_allowed_sizes_table(data)
        errors.extend(table_errors)
        
        # 4. Валидация данных задач
        tasks_valid, tasks_errors = self._validate_tasks_data(data)
        errors.extend(tasks_errors)
        
        # 5. Логическая валидация (соответствие маркировок таблице)
        logic_valid, logic_errors = self._validate_logic_consistency(data)
        errors.extend(logic_errors)
        
        # 6. Математическая валидация (проверка решаемости)
        math_valid, math_errors = self._validate_mathematical_solvability(data)
        errors.extend(math_errors)
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info("✅ Все проверки пройдены успешно")
        else:
            logger.warning(f"⚠️ Найдено {len(errors)} ошибок в данных")
            for error in errors[:5]:  # Показываем только первые 5 ошибок
                logger.warning(f"  - {error}")
        
        return is_valid, errors
    
    def _validate_structure(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Валидация базовой структуры данных для новой архитектуры"""
        errors = []
        
        # Обязательные ключи верхнего уровня для новой структуры
        required_keys = ['base_tire_marking', 'allowed_tire_sizes', 'constants', 'task_specific_data']
        for key in required_keys:
            if key not in data:
                errors.append(f"Отсутствует обязательный ключ: {key}")
        
        # Проверка constants
        if 'constants' in data:
            constants = data['constants']
            if 'inch_to_mm' not in constants:
                errors.append("Отсутствует constants.inch_to_mm")
            elif constants['inch_to_mm'] != 25.4:
                errors.append(f"constants.inch_to_mm должно быть 25.4, получено: {constants['inch_to_mm']}")
            
            if 'pi' not in constants:
                errors.append("Отсутствует constants.pi")
        
        # Структура base_tire_marking
        if 'base_tire_marking' in data:
            base_tire = data['base_tire_marking']
            required_tire_keys = ['width', 'profile', 'construction', 'diameter', 'full_marking']
            for key in required_tire_keys:
                if key not in base_tire:
                    errors.append(f"Отсутствует base_tire_marking.{key}")
        
        # Структура task_specific_data
        if 'task_specific_data' in data:
            task_data = data['task_specific_data']
            required_tasks = ['task_1_data', 'task_2_data', 'task_3_data', 'task_4_data', 'task_5_data']
            for task in required_tasks:
                if task not in task_data:
                    errors.append(f"Отсутствует {task} в task_specific_data")
        
        return len(errors) == 0, errors
    
    def _validate_tire_markings(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Валидация маркировок шин для новой структуры"""
        errors = []
        
        # Проверка базовой маркировки
        if 'base_tire_marking' in data:
            base_tire = data['base_tire_marking']
            full_marking = base_tire.get('full_marking', '')
            if not self._validate_single_marking(full_marking):
                errors.append(f"Некорректная базовая маркировка: {full_marking}")
        
        # Проверка маркировок в задачах
        if 'task_specific_data' in data:
            task_data = data['task_specific_data']
            
            # Task 2 - две маркировки для сравнения
            if 'task_2_data' in task_data:
                task2 = task_data['task_2_data']
                if 'tire_1' in task2 and not self._validate_single_marking(task2['tire_1']):
                    errors.append(f"Некорректная маркировка tire_1 в task_2: {task2['tire_1']}")
                if 'tire_2' in task2 and not self._validate_single_marking(task2['tire_2']):
                    errors.append(f"Некорректная маркировка tire_2 в task_2: {task2['tire_2']}")
            
            # Task 3 - маркировка для расчета
            if 'task_3_data' in task_data:
                task3 = task_data['task_3_data']
                if 'tire_marking' in task3 and not self._validate_single_marking(task3['tire_marking']):
                    errors.append(f"Некорректная маркировка в task_3: {task3['tire_marking']}")
            
            # Task 4 - оригинальная и заменяемая шины
            if 'task_4_data' in task_data:
                task4 = task_data['task_4_data']
                if 'original_tire' in task4 and not self._validate_single_marking(task4['original_tire']):
                    errors.append(f"Некорректная маркировка original_tire в task_4: {task4['original_tire']}")
                if 'replacement_tire' in task4 and not self._validate_single_marking(task4['replacement_tire']):
                    errors.append(f"Некорректная маркировка replacement_tire в task_4: {task4['replacement_tire']}")
            
            # Task 5 - оригинальная и заменяемая шины
            if 'task_5_data' in task_data:
                task5 = task_data['task_5_data']
                if 'original_tire' in task5 and not self._validate_single_marking(task5['original_tire']):
                    errors.append(f"Некорректная маркировка original_tire в task_5: {task5['original_tire']}")
                if 'replacement_tire' in task5 and not self._validate_single_marking(task5['replacement_tire']):
                    errors.append(f"Некорректная маркировка replacement_tire в task_5: {task5['replacement_tire']}")
        
        return len(errors) == 0, errors

    def _validate_allowed_sizes_table(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Валидация таблицы допустимых размеров для новой структуры"""
        errors = []
        
        allowed_sizes = data.get('allowed_tire_sizes', {})
        
        # Проверка ширин
        for width_str in allowed_sizes.keys():
            try:
                width = int(width_str)
                if width not in self.valid_widths:
                    errors.append(f"Некорректная ширина шины: {width}")
            except ValueError:
                errors.append(f"Ширина шины не является числом: {width_str}")
        
        # Проверка диаметров и размеров
        for width_str, diameters in allowed_sizes.items():
            for diameter_str, sizes in diameters.items():
                try:
                    diameter = int(diameter_str)
                    if diameter not in self.valid_diameters:
                        errors.append(f"Некорректный диаметр: {diameter}")
                except ValueError:
                    errors.append(f"Диаметр не является числом: {diameter_str}")
                
                # Проверка размеров
                if not isinstance(sizes, list):
                    errors.append(f"Размеры для {width_str}/{diameter_str} должны быть списком")
                    continue
                
                for size in sizes:
                    if not self._is_valid_size_format(size, width_str):
                        errors.append(f"Некорректный формат размера: {size}")
        
        return len(errors) == 0, errors
    
    def _validate_tasks_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Валидация данных задач для новой структуры"""
        errors = []
        
        if 'task_specific_data' not in data:
            errors.append("Отсутствует task_specific_data")
            return False, errors
        
        task_data = data['task_specific_data']
        
        # Задача 1 - различные типы вопросов о ширине/диаметре
        if 'task_1_data' in task_data:
            task1 = task_data['task_1_data']
            valid_question_types = ['minimum_width', 'maximum_width', 'minimum_diameter']
            
            question_type = task1.get('question_type', 'minimum_width')
            if question_type not in valid_question_types:
                errors.append(f"Task 1: некорректный question_type: {question_type}. Ожидаемые: {valid_question_types}")
            
            if question_type in ['minimum_width', 'maximum_width']:
                if 'target_diameter' not in task1:
                    errors.append("Отсутствует target_diameter в task_1_data")
                elif task1['target_diameter'] not in self.valid_diameters:
                    errors.append(f"Task 1: некорректный target_diameter: {task1['target_diameter']}")
            
            elif question_type == 'minimum_diameter':
                if 'target_width' not in task1:
                    errors.append("Отсутствует target_width в task_1_data")
                elif task1['target_width'] not in self.valid_widths:
                    errors.append(f"Task 1: некорректная target_width: {task1['target_width']}")
        
        # Задача 2 - сравнение шин
        if 'task_2_data' in task_data:
            task2 = task_data['task_2_data']
            valid_question_types = ['radius_difference', 'diameter_difference']
            
            question_type = task2.get('question_type', task2.get('comparison_type', 'radius_difference'))
            if question_type not in valid_question_types:
                errors.append(f"Task 2: некорректный question_type: {question_type}. Ожидаемые: {valid_question_types}")
            
            for tire_key in ['tire_1', 'tire_2']:
                if tire_key not in task2:
                    errors.append(f"Отсутствует {tire_key} в task_2_data")
        
        # Задача 3 - расчет параметров колеса
        if 'task_3_data' in task_data:
            task3 = task_data['task_3_data']
            valid_question_types = ['wheel_diameter', 'wheel_radius']
            
            question_type = task3.get('question_type', task3.get('calculation_type', 'wheel_diameter'))
            if question_type not in valid_question_types:
                errors.append(f"Task 3: некорректный question_type: {question_type}. Ожидаемые: {valid_question_types}")
            
            if 'tire_marking' not in task3:
                errors.append("Отсутствует tire_marking в task_3_data")
        
        # Задача 4 - изменение диаметра при замене
        if 'task_4_data' in task_data:
            task4 = task_data['task_4_data']
            # Task 4 обычно имеет фиксированный calculation_type
            if 'calculation_type' in task4 and task4['calculation_type'] != 'diameter_change':
                errors.append(f"Task 4: некорректный calculation_type: {task4['calculation_type']}")
            
            for tire_key in ['original_tire', 'replacement_tire']:
                if tire_key not in task4:
                    errors.append(f"Отсутствует {tire_key} в task_4_data")
        
        # Задача 5 - сложная задача с разными типами
        if 'task_5_data' in task_data:
            task5 = task_data['task_5_data']
            valid_calculation_types = ['mileage_change_percent', 'service_choice_cost']
            
            calculation_type = task5.get('calculation_type', 'mileage_change_percent')
            if calculation_type not in valid_calculation_types:
                errors.append(f"Task 5: некорректный calculation_type: {calculation_type}. Ожидаемые: {valid_calculation_types}")
            
            # Проверка сервисов (если есть)
            if 'service_choice_data' in task5:
                service_data = task5['service_choice_data']
                if 'services' not in service_data:
                    errors.append("Отсутствует services в service_choice_data")
                else:
                    services = service_data['services']
                    if not isinstance(services, list) or len(services) < 2:
                        errors.append("Задача 5: должно быть минимум 2 автосервиса")
                    
                    for service in services:
                        if not isinstance(service, dict):
                            continue
                        
                        # Проверка стоимости дороги
                        road_cost = service.get('road_cost', 0)
                        if not isinstance(road_cost, (int, float)) or road_cost < 100 or road_cost > 1000:
                            errors.append(f"Некорректная стоимость дороги: {road_cost}")
                        
                        # Проверка операций
                        operations = service.get('operations', {})
                        required_ops = ['removal', 'tire_change', 'balancing', 'installation']
                        for op in required_ops:
                            if op not in operations:
                                errors.append(f"Отсутствует операция {op} в сервисе {service.get('name')}")
                            else:
                                cost = operations[op]
                                if not isinstance(cost, (int, float)) or cost < 30 or cost > 500:
                                    errors.append(f"Некорректная стоимость операции {op}: {cost}")
                
                if 'wheels_count' not in service_data:
                    errors.append("Отсутствует wheels_count в service_choice_data")
            
            # Проверка маркировок для расчета пробега
            for tire_key in ['original_tire', 'replacement_tire']:
                if tire_key not in task5:
                    errors.append(f"Отсутствует {tire_key} в task_5_data")
        
        return len(errors) == 0, errors
    
    def _validate_logic_consistency(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Валидация логической согласованности данных для новой структуры"""
        errors = []
        
        allowed_sizes = data.get('allowed_tire_sizes', {})
        task_data = data.get('task_specific_data', {})
        
        # Проверка, что все маркировки из задач соответствуют допустимым размерам
        markings_to_check = []
        
        # Базовая маркировка
        if 'base_tire_marking' in data:
            base_tire = data['base_tire_marking']
            full_marking = base_tire.get('full_marking')
            if full_marking:
                markings_to_check.append(('base_tire_marking', full_marking))
        
        # Маркировки из задач
        if 'task_2_data' in task_data:
            task2 = task_data['task_2_data']
            if 'tire_1' in task2:
                markings_to_check.append(('task_2.tire_1', task2['tire_1']))
            if 'tire_2' in task2:
                markings_to_check.append(('task_2.tire_2', task2['tire_2']))
        
        if 'task_3_data' in task_data:
            task3 = task_data['task_3_data']
            if 'tire_marking' in task3:
                markings_to_check.append(('task_3.tire_marking', task3['tire_marking']))
        
        if 'task_4_data' in task_data:
            task4 = task_data['task_4_data']
            if 'original_tire' in task4:
                markings_to_check.append(('task_4.original_tire', task4['original_tire']))
            if 'replacement_tire' in task4:
                markings_to_check.append(('task_4.replacement_tire', task4['replacement_tire']))
        
        if 'task_5_data' in task_data:
            task5 = task_data['task_5_data']
            if 'original_tire' in task5:
                markings_to_check.append(('task_5.original_tire', task5['original_tire']))
            if 'replacement_tire' in task5:
                markings_to_check.append(('task_5.replacement_tire', task5['replacement_tire']))
        
        # Проверяем каждую маркировку
        for source, marking in markings_to_check:
            if not self._is_marking_in_allowed_sizes(marking, allowed_sizes):
                errors.append(f"Маркировка {marking} из {source} не найдена в таблице допустимых размеров")
        
        return len(errors) == 0, errors
    
    def _is_marking_in_allowed_sizes(self, marking: str, allowed_sizes: dict) -> bool:
        """Проверяет, что маркировка соответствует допустимым размерам"""
        # Парсим маркировку для извлечения параметров
        try:
            parts = marking.replace('/', ' ').replace('R', ' ').split()
            if len(parts) != 3:
                return False
            
            width, profile, diameter = parts[0], parts[1], parts[2]
            
            # Проверяем, что ширина есть в допустимых размерах
            if width not in allowed_sizes:
                return False
            
            # Проверяем, что диаметр есть в размерах для данной ширины
            if diameter not in allowed_sizes[width]:
                return False
            
            # Проверяем, что конкретный размер есть в списке
            expected_size = f"{width}/{profile}"
            available_sizes = allowed_sizes[width][diameter]
            
            return expected_size in available_sizes
            
        except (ValueError, IndexError, KeyError):
            return False

    def _validate_single_marking(self, marking: str) -> bool:
        """Проверяет синтаксис и диапазоны ОДНОЙ маркировки."""
        # --- ИСПРАВЛЕННАЯ ЛОГИКА ---
        try:
            # Разделяем по "/" и "R"
            parts = marking.replace('/', ' ').replace('R', ' ').split()
            if len(parts) != 3:
                return False
            
            width, profile, diameter = int(parts[0]), int(parts[1]), int(parts[2])
            
            # Здесь можно будет добавить проверку диапазонов из VALIDATION_RANGES
            # if width not in self.validation_ranges["widths"]: return False
            
            return True
        except (ValueError, IndexError):
            return False
        
    def _is_valid_size_format(self, size_str: str, width_str: str) -> bool:
        """
        Проверяет, что формат размера в таблице (например, "185/65") корректен.
        """
        if not isinstance(size_str, str): return False
        parts = size_str.split('/')
        if len(parts) != 2: return False
        
        # Проверяем, что ширина в размере совпадает с шириной в строке таблицы
        if parts[0] != width_str: return False
        
        # Проверяем, что обе части - числа
        return parts[0].isdigit() and parts[1].isdigit()
    
    def _validate_mathematical_solvability(self, data: dict) -> tuple:
        """
        Проверяет математическую решаемость, "прогоняя" данные через калькулятор.
        """
        try:
            # Создаем временный экземпляр калькулятора
            calculator = TiresCalculator()
            # Пытаемся решить все задачи
            results = calculator.calculate_all_tasks(data)
            
            # Проверяем, что все ответы - это числа
            if not all(isinstance(v, (int, float)) for v in results.values()):
                return False, ["Некоторые ответы не являются числами."]
            
            # Если всё посчиталось без ошибок - отлично!
            return True, []
            
        except Exception as e:
            # Если калькулятор "упал" - значит, данные нерешаемые
            import traceback
            return False, [f"Математическая ошибка при решении: {e}\n{traceback.format_exc()}"]
    

# Глобальные функции для совместимости
def validate_tires_data(data: dict) -> tuple:
    """
    Полная валидация всего JSON-объекта с данными.
    """
    validator = TiresDataValidator()
    return validator.validate_complete_data(data)

def is_valid_tire_marking(marking: str) -> bool:
    """
    Проверяет ТОЛЬКО ОДНУ конкретную маркировку.
    """
    validator = TiresDataValidator()
    # Напрямую вызываем внутренний метод, который умеет работать с одной строкой
    return validator._validate_single_marking(marking)