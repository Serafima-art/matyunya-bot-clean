import math
import json
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

def parse_tire_marking(marking: str) -> Optional[Dict[str, Any]]:
    """
    Парсит маркировку шины вида '195/65 R16' и возвращает словарь с параметрами.
    
    Args:
        marking: Строка с маркировкой шины.
    
    Returns:
        Словарь с параметрами (width, profile, construction, diameter) или None при ошибке.
    """
    try:
        parts = marking.strip().split()
        size_part = parts[0]  # '195/65'
        construction = parts[1][0]  # 'R'
        diameter = int(parts[1][1:])  # 16
        
        width, profile = size_part.split('/')
        
        return {
            "width": int(width),
            "profile": int(profile),
            "construction": construction,
            "diameter": diameter
        }
    except (ValueError, IndexError) as e:
        logger.error(f"Ошибка парсинга маркировки шины '{marking}': {e}")
        return None

def calculate_tire_parameters(tire_data: Dict[str, Any], constants: Dict[str, Any]) -> Dict[str, float]:
    """
    Вычисляет параметры шины с высокой точностью, используя Decimal.
    
    Args:
        tire_data: Словарь с параметрами шины (width, profile, diameter).
        constants: Константы (inch_to_mm, pi).
    
    Returns:
        Словарь с вычисленными параметрами (width, profile, sidewall_height, rim_diameter_mm,
        wheel_radius, wheel_diameter, circumference).
    """
    try:
        width = Decimal(str(tire_data["width"]))
        profile = Decimal(str(tire_data["profile"]))
        diameter_inches = Decimal(str(tire_data["diameter"]))
        inch_to_mm = Decimal(str(constants["inch_to_mm"]))
        pi = Decimal(str(constants["pi"]))
        
        sidewall_height = width * profile / Decimal('100')
        rim_diameter_mm = diameter_inches * inch_to_mm
        wheel_radius = sidewall_height + rim_diameter_mm / Decimal('2')
        wheel_diameter = Decimal('2') * sidewall_height + rim_diameter_mm
        circumference = pi * wheel_diameter
        
        return {
            "width": float(width),
            "profile": float(profile),
            "sidewall_height": float(sidewall_height),
            "rim_diameter_mm": float(rim_diameter_mm),
            "wheel_radius": float(wheel_radius),
            "wheel_diameter": float(wheel_diameter),
            "circumference": float(circumference)
        }
    except (KeyError, ValueError) as e:
        logger.error(f"Ошибка вычисления параметров шины: {e}")
        return {}

def solve_task_1(tire_data: Dict[str, Any]) -> int:
    try:
        task_data = tire_data["task_specific_data"]["task_1_data"]
        allowed_sizes = tire_data["allowed_tire_sizes"]
        question_type = task_data.get("question_type", "minimum_width")
        
        print(f"DEBUG solve_task_1:")
        print(f"  question_type: {question_type}")
        print(f"  task_data: {task_data}")
        
        if question_type == "minimum_width" and "target_diameter" in task_data:
            target_diameter = str(task_data["target_diameter"])
            available_widths = []
            
            # Ищем все ширины, у которых есть шины для этого диаметра
            for width, diameter_data in allowed_sizes.items():
                if target_diameter in diameter_data and diameter_data[target_diameter]:
                    available_widths.append(int(width))
            
            result = min(available_widths) if available_widths else 0
            print(f"  Результат: {result}")
            return result
            
        elif question_type == "minimum_diameter" and "target_width" in task_data:
            target_width = str(task_data["target_width"])
            
            if target_width in allowed_sizes:
                width_data = allowed_sizes[target_width]
                available_diameters = [
                    int(diameter) for diameter, profiles in width_data.items() 
                    if profiles
                ]
                result = min(available_diameters) if available_diameters else 0
                print(f"  Результат: {result}")
                return result
        
        return 0
        
    except Exception as e:
        print(f"ERROR solve_task_1: {e}")
        return 0

def solve_task_2(tire_data: Dict[str, Any]) -> float:
    try:
        task_data = tire_data["task_specific_data"]["task_2_data"]
        constants = tire_data["constants"]
        
        tire_1_marking = task_data["tire_1"]
        
        # ИСПРАВЛЕНИЕ: проверяем тип сравнения
        if task_data.get("comparison_with_base", False) or task_data.get("comparison_type") == "base_comparison":
            # Сравниваем с базовой шиной
            tire_2_marking = tire_data["base_tire_marking"]["full_marking"]
            print(f"DEBUG: Сравнение с базовой: {tire_1_marking} vs {tire_2_marking}")
        else:
            # Обычное сравнение с tire_2
            tire_2_marking = task_data["tire_2"]
            print(f"DEBUG: Обычное сравнение: {tire_1_marking} vs {tire_2_marking}")
        
        tire_1 = parse_tire_marking(tire_1_marking)
        tire_2 = parse_tire_marking(tire_2_marking)
        
        # Остальной код без изменений
        if not tire_1 or not tire_2:
            return 0.0
        
        params_1 = calculate_tire_parameters(tire_1, constants)
        params_2 = calculate_tire_parameters(tire_2, constants)
        
        radius_1 = Decimal(str(params_1.get("wheel_radius", 0)))
        radius_2 = Decimal(str(params_2.get("wheel_radius", 0)))
        radius_difference = abs(radius_1 - radius_2)
        
        # УБИРАЕМ ОКРУГЛЕНИЕ:
        result = float(radius_difference)
        print(f"DEBUG: difference = {result}")
        return result
        
    except (KeyError, ValueError) as e:
        logger.error(f"Ошибка в solve_task_2: {e}")
        return 0.0
    
def solve_task_3(data: Dict[str, Any]) -> float:
    """
    Решает Задание 3: диаметр колеса.
    
    Args:
        data: Данные сюжета с task_3_data и constants.
    
    Returns:
        Диаметр в мм, округлённый до 0.1.
    """
    try:
        task_data = data["task_specific_data"]["task_3_data"]
        constants = data["constants"]
        
        tire = parse_tire_marking(task_data["tire_marking"])
        if not tire:
            return 0.0
        
        params = calculate_tire_parameters(tire, constants)
        diameter = Decimal(str(params.get("wheel_diameter", 0)))
        
        return float(diameter.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
    except (KeyError, ValueError) as e:
        logger.error(f"Ошибка в solve_task_3: {e}")
        return 0.0

def solve_task_4(data: Dict[str, Any]) -> float:
    """
    Решает Задание 4: изменение диаметра при замене шины.
    
    Args:
        data: Данные сюжета с task_4_data и constants.
    
    Returns:
        Изменение диаметра в мм, округлённое до 0.1.
    """
    try:
        task_data = data["task_specific_data"]["task_4_data"]
        constants = data["constants"]
        
        original = parse_tire_marking(task_data["original_tire"])
        replacement = parse_tire_marking(task_data["replacement_tire"])
        
        if not original or not replacement:
            return 0.0
        
        original_params = calculate_tire_parameters(original, constants)
        replacement_params = calculate_tire_parameters(replacement, constants)
        
        original_diameter = Decimal(str(original_params.get("wheel_diameter", 0)))
        replacement_diameter = Decimal(str(replacement_params.get("wheel_diameter", 0)))
        diameter_change = replacement_diameter - original_diameter
        
        return float(diameter_change.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
    except (KeyError, ValueError) as e:
        logger.error(f"Ошибка в solve_task_4: {e}")
        return 0.0

def solve_task_5(data: Dict[str, Any]) -> float:
    """
    Решает Задание 5: процентное изменение пробега.
    
    Args:
        data: Данные сюжета с task_5_data и constants.
    
    Returns:
        Процентное изменение пробега, округлённое до 0.1.
    """
    try:
        task_data = data["task_specific_data"]["task_5_data"]
        constants = data["constants"]
        
        if "calculation_type" not in task_data or task_data["calculation_type"] != "mileage_change_percent":
            return 0.0
        
        original = parse_tire_marking(task_data["original_tire"])
        replacement = parse_tire_marking(task_data["replacement_tire"])
        
        if not original or not replacement:
            return 0.0
        
        original_params = calculate_tire_parameters(original, constants)
        replacement_params = calculate_tire_parameters(replacement, constants)
        
        original_circumference = Decimal(str(original_params.get("circumference", 0)))
        replacement_circumference = Decimal(str(replacement_params.get("circumference", 0)))
        
        if original_circumference == 0:
            return 0.0
        
        percent_change = ((replacement_circumference - original_circumference) / original_circumference) * Decimal('100')
        return float(percent_change.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
    except (KeyError, ValueError) as e:
        logger.error(f"Ошибка в solve_task_5: {e}")
        return 0.0

def solve_task_6(data: Dict[str, Any]) -> float:
    """
    Решает Задание 6: минимальная стоимость услуг автосервиса.
    
    Args:
        data: Данные сюжета с task_5_data (service_choice_data).
    
    Returns:
        Минимальная стоимость в рублях.
    """
    try:
        task_data = data["task_specific_data"]["task_5_data"]
        if "service_choice_data" not in task_data:
            return 0.0
        
        service_data = task_data["service_choice_data"]
        services = service_data["services"]
        wheels_count = service_data.get("wheels_count", 4)
        
        min_cost = None
        for service in services:
            per_wheel_cost = (
                Decimal(str(service["operations"].get("removal", 0))) +
                Decimal(str(service["operations"].get("tire_change", 0))) +
                Decimal(str(service["operations"].get("balancing", 0))) +
                Decimal(str(service["operations"].get("installation", 0)))
            )
            total_cost = Decimal(str(service.get("road_cost", 0))) + per_wheel_cost * Decimal(str(wheels_count))
            
            if min_cost is None or total_cost < min_cost:
                min_cost = total_cost
        
        return float(min_cost) if min_cost is not None else 0.0
    except (KeyError, ValueError) as e:
        logger.error(f"Ошибка в solve_task_6: {e}")
        return 0.0

class TiresCalculator:
    """
    Класс-обёртка для расчётов задач по шинам.
    """
    def calculate_all_tasks(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Выполняет расчёты для всех задач (1-6).
        
        Args:
            data: Данные сюжета (plot.json).
        
        Returns:
            Словарь с ответами {task_1_answer, ..., task_6_answer}.
        """
        try:
            return {
                "task_1_answer": solve_task_1(data),
                "task_2_answer": solve_task_2(data),
                "task_3_answer": solve_task_3(data),
                "task_4_answer": solve_task_4(data),
                "task_5_answer": solve_task_5(data),
                "task_6_answer": solve_task_6(data)
            }
        except Exception as e:
            logger.error(f"Ошибка в calculate_all_tasks: {e}")
            return {f"task_{i}_answer": 0 for i in range(1, 7)}