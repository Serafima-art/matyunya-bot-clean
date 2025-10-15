import re
import math
from matunya_bot_final.utils.text_formatters import bold_numbers


# =============================================================================
# --- УНИВЕРСАЛЬНЫЕ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ЭТОГО МОДУЛЯ ---
# =============================================================================

def _parse_tire_marking(tire_str: str) -> tuple[int, int, int, str]:
    """
    Парсит строку маркировки шины, например, '205/50 R17'.
    Возвращает кортеж (ширина, профиль, диаметр, исходная_строка).
    """
    if not tire_str or tire_str == "0/0 R0":
        return 0, 0, 0, ""
    try:
        parts = tire_str.replace('R', ' ').replace('/', ' ').split()
        if len(parts) < 3: return 0, 0, 0, tire_str
        
        width = int(parts[0])
        profile = int(parts[1])
        diameter = int(parts[2])
        return width, profile, diameter, tire_str
    except (ValueError, IndexError):
        return 0, 0, 0, tire_str

def calculate_tire_diameter(B: float, H: float, d: float) -> float:
    """
    Вспомогательная функция для расчета диаметра колеса в миллиметрах.
    
    Args:
        B (float): Ширина шины в мм
        H (float): Высота профиля в процентах
        d (float): Диаметр диска в дюймах
        
    Returns:
        float: Диаметр колеса в миллиметрах
    """
    return (B * H / 100) * 2 + d * 25.4


def solve_q1_tires(task_data: dict) -> dict:
    """
    Решатель для вопросов типа Q1. Версия 2.0.
    Читает данные из новой структуры после архитектурного сдвига.
    """
    
    # ИСПРАВЛЕНО: Все данные теперь в plot_data['task_specific_data']
    plot_data = task_data.get("plot_data", {})
    task_specific_data = plot_data.get("task_specific_data", {})
    task_1_data = task_specific_data.get("task_1_data", {})
    
    # allowed_tire_sizes теперь тоже в plot_data
    allowed_sizes_table = plot_data.get("allowed_tire_sizes", {})
    
    question_type = task_1_data.get("question_type", "")
    
    # Определяем, что ищем, на основе question_type
    if question_type in ["minimum_width", "maximum_width"]:
        column_to_search = "tire_width"
        disk_in = task_1_data.get("target_diameter", 0)
        tire_width_mm = None
    elif question_type in ["minimum_diameter", "maximum_diameter"]:
        column_to_search = "disk_diameter"
        tire_width_mm = task_1_data.get("target_width", 0)
        disk_in = None
    else:
        error_msg = f"Неизвестный question_type для Q1: '{question_type}'. "
        error_msg += f"Доступные данные task_1_data: {task_1_data}. "
        error_msg += f"Ожидаемые значения: minimum_width, maximum_width, minimum_diameter, maximum_diameter"
        raise ValueError(error_msg)

    search_type = "min" if "minimum" in question_type else "max"
    question_id = task_1_data.get("question_id", "tires_q1_unknown")
    calculation_steps = []
    
    if column_to_search == "tire_width":
        disk_key = str(disk_in)
        tire_sizes = []
        widths = []
        
        for width_str, diameter_data in allowed_sizes_table.items():
            if isinstance(diameter_data, dict) and disk_key in diameter_data:
                sizes_for_diameter = diameter_data.get(disk_key, [])
                tire_sizes.extend(sizes_for_diameter)
                
                for size in sizes_for_diameter:
                    if size:
                        width_match = re.match(r'(\d+)/', str(size))
                        if width_match:
                            widths.append(int(width_match.group(1)))
                        else:
                            try:
                                widths.append(int(width_str))
                            except ValueError:
                                pass
        
        if not tire_sizes:
            raise ValueError(f"Диаметр диска {disk_in} дюймов не найден в таблице")
        
        calculation_steps.append({
            "step_number": 1,
            "description": f"Находим все размеры шин для диска диаметром {disk_in} дюймов",
            "formula_representation": "N/A",
            "calculation_result": f"Размеры: {', '.join(tire_sizes)}",
            "result_unit": ""
        })
        
        calculation_steps.append({
            "step_number": 2,
            "description": "Извлекаем ширины шин из размеров",
            "formula_representation": "N/A",
            "calculation_result": f"Ширины: {', '.join(map(str, widths))} мм",
            "result_unit": "мм"
        })
        
        if not widths:
            raise ValueError(f"Не удалось извлечь ширины для диаметра {disk_in} дюймов")
            
        if search_type == "min":
            result_width = min(widths)
            step3_desc = "Находим наименьшую ширину среди найденных значений"
            explanation_idea = f"Для диска диаметром {disk_in} дюймов ищем шину с наименьшей шириной среди доступных размеров."
        else:
            result_width = max(widths)
            step3_desc = "Находим наибольшую ширину среди найденных значений"
            explanation_idea = f"Для диска диаметром {disk_in} дюймов ищем шину с наибольшей шириной среди доступных размеров."
        
        calculation_steps.append({
            "step_number": 3,
            "description": step3_desc,
            "formula_representation": "N/A",
            "calculation_result": f"{result_width} мм",
            "result_unit": "мм"
        })
        
        final_value = result_width
        final_unit = "мм"
        validation_code = f"return {result_width}"
        hints = [
            f"Для диска {disk_in}\" доступны размеры: {', '.join(tire_sizes)}",
            f"Ширина шины указывается первым числом в размере (например, в размере 205/45 ширина = 205 мм)"
        ]
        
    else:  # column_to_search == "disk_diameter"
        target_width_str = str(tire_width_mm)
        found_diameters = []
        found_sizes = []
        
        for width_str, diameter_data in allowed_sizes_table.items():
            if isinstance(diameter_data, dict):
                width_matches = False
                
                if width_str == target_width_str:
                    width_matches = True
                
                if not width_matches:
                    for diameter, sizes in diameter_data.items():
                        for size in sizes:
                            if size:
                                width_match = re.match(r'(\d+)/', str(size))
                                if width_match and width_match.group(1) == target_width_str:
                                    width_matches = True
                                    break
                        if width_matches:
                            break
                
                if width_matches:
                    for diameter, sizes in diameter_data.items():
                        if sizes:
                            try:
                                diameter_int = int(diameter)
                                if diameter_int not in found_diameters:
                                    found_diameters.append(diameter_int)
                                    found_sizes.append(f"{diameter}\" (ширина {width_str})")
                            except ValueError:
                                pass
        
        calculation_steps.append({
            "step_number": 1,
            "description": f"Ищем все диаметры дисков, для которых доступна ширина шины {tire_width_mm} мм",
            "formula_representation": "N/A",
            "calculation_result": f"Найдены диаметры: {', '.join(found_sizes)}",
            "result_unit": ""
        })
        
        if not found_diameters:
            raise ValueError(f"Ширина шины {tire_width_mm} мм не найдена в таблице")
        
        calculation_steps.append({
            "step_number": 2,
            "description": "Извлекаем значения диаметров дисков",
            "formula_representation": "N/A",
            "calculation_result": f"Диаметры: {', '.join(map(str, found_diameters))} дюймов",
            "result_unit": "дюймы"
        })
        
        if search_type == "min":
            result_diameter = min(found_diameters)
            step3_desc = "Находим наименьший диаметр среди найденных значений"
            explanation_idea = f"Для шины шириной {tire_width_mm} мм ищем диск с наименьшим диаметром среди доступных размеров."
        else:
            result_diameter = max(found_diameters)
            step3_desc = "Находим наибольший диаметр среди найденных значений"
            explanation_idea = f"Для шины шириной {tire_width_mm} мм ищем диск с наибольшим диаметром среди доступных размеров."
        
        calculation_steps.append({
            "step_number": 3,
            "description": step3_desc,
            "formula_representation": "N/A",
            "calculation_result": f"{result_diameter} дюймов",
            "result_unit": "дюймы"
        })
        
        final_value = result_diameter
        final_unit = "дюймы"
        validation_code = f"return {result_diameter}"
        hints = [
            f"Ширина шины {tire_width_mm} мм доступна для дисков: {', '.join(map(str, found_diameters))}\"",
            "Диаметр диска указывается в дюймах и определяет совместимость с размером шины"
        ]
    
    return {
        "question_group": "Q1_TABLE",
        "question_id": question_id,
        "explanation_idea": explanation_idea,
        "calculation_steps": calculation_steps,
        "final_answer": {
            "value_machine": final_value,
            "value_display": f"{final_value}",
            "unit": final_unit
        },
        "validation_code": validation_code,
        "hints": hints
    }


def solve_q2_tires(task_package: dict) -> dict:
    """
    Решает задачу Q2 для шин: расчет разницы в диаметрах/радиусах колес.
    ФИНАЛЬНАЯ ВЕРСИЯ: Использует общие вспомогательные функции.
    """
    
    # 1. ПРАВИЛЬНОЕ извлечение данных из новой структуры
    plot_data = task_package.get("plot_data", {})
    task_specific_data = plot_data.get("task_specific_data", {})
    task_2_data = task_specific_data.get("task_2_data", {})
    
    # 2. Извлекаем маркировки шин из task_2_data
    tire_1_marking = task_2_data.get("tire_1", "0/0 R0")
    tire_2_marking = task_2_data.get("tire_2", "0/0 R0")
    comparison_type = task_2_data.get("comparison_type", "")
    
    # 3. Парсим обе шины с помощью ОБЩЕЙ функции _parse_tire_marking
    factory_B, factory_H, factory_d, factory_marking = _parse_tire_marking(tire_1_marking)
    new_B, new_H, new_d, new_marking = _parse_tire_marking(tire_2_marking)
    
    # 4. Рассчитываем диаметры
    factory_diameter = calculate_tire_diameter(factory_B, factory_H, factory_d)
    new_diameter = calculate_tire_diameter(new_B, new_H, new_d)
    
    diameter_diff = abs(new_diameter - factory_diameter)
    
    is_radius_question = "radius" in comparison_type.lower()
    
    # 5. Формируем шаги расчета
    calculation_steps = [
        {
            "step_number": 1,
            "description": bold_numbers(f"Сначала рассчитаем диаметр первого колеса ({factory_marking})."),
            "formula_representation": f"({factory_B} · {factory_H} / 100) · 2 + {factory_d} · 25.4",
            "calculation_result": f"{factory_diameter:.2f} мм",
            "result_unit": "мм"
        },
        {
            "step_number": 2,
            "description": f"Теперь рассчитаем диаметр второго колеса ({new_marking}).",
            "formula_representation": f"({new_B} · {new_H} / 100) · 2 + {new_d} · 25.4",
            "calculation_result": f"{new_diameter:.2f} мм",
            "result_unit": "мм"
        },
        {
            "step_number": 3,
            "description": "Теперь найдем разницу в диаметрах.",
            "formula_representation": f"|{new_diameter:.2f} - {factory_diameter:.2f}|",
            "calculation_result": f"{diameter_diff:.2f} мм",
            "result_unit": "мм"
        }
    ]
    
    if is_radius_question:
        radius_diff = diameter_diff / 2
        calculation_steps.append({
            "step_number": 4,
            "description": "Вопрос был про разницу радиусов. Радиус — это половина диаметра, поэтому разницу диаметров нужно поделить на 2.",
            "formula_representation": f"{diameter_diff:.2f} / 2",
            "calculation_result": f"{radius_diff:.2f} мм",
            "result_unit": "мм"
        })
        final_value = radius_diff
        question_id = "tires_q2_radius_diff"
        explanation_idea = "Чтобы сравнить радиусы двух колес, нам нужно найти полный диаметр каждого, найти разницу и поделить её на 2."
    else:
        final_value = diameter_diff
        question_id = "tires_q2_diameter_diff"
        explanation_idea = "Чтобы сравнить диаметры двух колес, нам нужно найти полный диаметр каждого из них, а затем найти разницу."
    
    final_value_rounded = round(final_value, 2)
    
    return {
        "question_group": "Q2_Tires_Comparison",
        "question_id": question_id,
        "explanation_idea": explanation_idea,
        "calculation_steps": calculation_steps,
        "final_answer": {
            "value_machine": final_value_rounded,
            "value_display": str(final_value_rounded).replace('.', ','),
            "unit": "мм"
        },
        "validation_code": f"return {final_value_rounded}",
        "hints": [
            "Формула диаметра колеса: (Ширина · Профиль / 100) · 2 · Диаметр диска · 25.4.",
            "1 дюйм = 25.4 мм.",
            "Внимательно читай вопрос: спрашивают про разницу диаметров или радиусов."
        ]
    }


def solve_q3_tires(task_package: dict) -> dict:
    """
    Решает задачу Q3: расчет диаметра колеса.
    ФИНАЛЬНАЯ ВЕРСИЯ: Ответ в МИЛЛИМЕТРАХ.
    """
    
    # 1. Извлекаем данные (здесь все правильно)
    plot_data = task_package.get("plot_data", {})
    task_specific_data = plot_data.get("task_specific_data", {})
    task_3_data = task_specific_data.get("task_3_data", {})
    
    tire_marking = task_3_data.get("tire_marking", "0/0 R0")
    
    # 2. Парсим маркировку (здесь все правильно)
    factory_B, factory_H, factory_d, factory_marking = _parse_tire_marking(tire_marking)
    
    # 3. Рассчитываем диаметр в мм (здесь все правильно)
    factory_diameter_mm = calculate_tire_diameter(factory_B, factory_H, factory_d)
    
    # 4. ---- УДАЛЯЕМ ЛИШНИЙ КОД ----
    # factory_diameter_cm = factory_diameter_mm / 10 # <-- ЭТО БОЛЬШЕ НЕ НУЖНО
    
    # 5. Формируем шаги расчета (теперь только ОДИН шаг)
    calculation_steps = [
        {
            "step_number": 1,
            "description": f"Рассчитаем диаметр колеса ({factory_marking}) в миллиметрах, используя стандартную формулу.",
            "formula_representation": f"({factory_B} · {factory_H} / 100) · 2 + {factory_d} · 25.4",
            "calculation_result": f"{factory_diameter_mm:.2f} мм",
            "result_unit": "мм"
        }
    ]
    
    # 6. ---- ИСПРАВЛЯЕМ ФИНАЛЬНЫЙ ОТВЕТ ----
    final_value_rounded = round(factory_diameter_mm, 2)
    
    return {
        "question_group": "Q3_Tires_Diameter_Calculation",
        "question_id": "tires_q3_factory_diameter_mm",
        "explanation_idea": "Нам нужно найти диаметр заводского колеса. Для этого используем стандартную формулу для расчета диаметра в миллиметрах.",
        "calculation_steps": calculation_steps,
        "final_answer": {
            "value_machine": final_value_rounded,
            "value_display": str(final_value_rounded).replace('.', ','),
            "unit": "мм"
        },
        "validation_code": f"return {final_value_rounded}",
        "hints": [
            "Формула диаметра колеса: (Ширина · Профиль / 100) · 2 · Диаметр диска · 25.4.",
            "Внимательно проверь, в каких единицах (мм или см) требуется дать ответ в задании."
        ]
    }

def solve_q4_tires(task_package: dict) -> dict:
    """
    Решает задачу Q4 для шин: расчет изменения диаметра колеса при замене шин.
    ИСПРАВЛЕНО для новой архитектуры данных.
    """
    # 1. Извлекаем данные из правильного места
    plot_data = task_package.get("plot_data", {})
    task_specific_data = plot_data.get("task_specific_data", {})
    task_4_data = task_specific_data.get("task_4_data", {})
    
    original_marking = task_4_data.get("original_tire", "0/0 R0")
    replacement_marking = task_4_data.get("replacement_tire", "0/0 R0")

    # 2. Парсим обе шины с помощью универсальной функции
    original_B, original_H, original_d, _ = _parse_tire_marking(original_marking)
    replacement_B, replacement_H, replacement_d, _ = _parse_tire_marking(replacement_marking)

    # 3. Рассчитываем диаметры
    original_diameter = calculate_tire_diameter(original_B, original_H, original_d)
    replacement_diameter = calculate_tire_diameter(replacement_B, replacement_H, replacement_d)
    
    # 4. Находим ИЗМЕНЕНИЕ (может быть положительным или отрицательным)
    diameter_change = replacement_diameter - original_diameter
    
    # 5. Формируем шаги расчета
    calculation_steps = [
        {
            "step_number": 1,
            "description": f"Сначала рассчитаем диаметр исходного колеса ({original_marking}).",
            "formula_representation": f"({original_B} · {original_H} / 100) · 2 + {original_d} · 25.4",
            "calculation_result": f"{original_diameter:.2f} мм",
            "result_unit": "мм"
        },
        {
            "step_number": 2,
            "description": f"Теперь рассчитаем диаметр нового колеса ({replacement_marking}).",
            "formula_representation": f"({replacement_B} · {replacement_H} / 100) · 2 + {replacement_d} · 25.4",
            "calculation_result": f"{replacement_diameter:.2f} мм",
            "result_unit": "мм"
        },
        {
            "step_number": 3,
            "description": "Находим, на сколько новый диаметр больше или меньше старого.",
            "formula_representation": f"{replacement_diameter:.2f} - {original_diameter:.2f}",
            "calculation_result": f"{diameter_change:.2f} мм",
            "result_unit": "мм"
        }
    ]
    
    final_value_rounded = round(diameter_change, 1)
    
    return {
        "question_group": "Q4_Tires_Diameter_Increase",
        "question_id": "tires_q4_diameter_increase_mm",
        "explanation_idea": "Чтобы узнать, на сколько изменится диаметр колеса, нам нужно рассчитать диаметр старого и нового колеса, а затем найти разницу между ними.",
        "calculation_steps": calculation_steps,
        "final_answer": {
            "value_machine": final_value_rounded,
            "value_display": str(final_value_rounded).replace('.', ','),
            "unit": "мм"
        },
        "validation_code": f"return {final_value_rounded}",
        "hints": [
            "Эта задача очень похожа на Q2, но здесь всегда ищется разница диаметров.",
            "Положительное значение означает увеличение диаметра, отрицательное - уменьшение."
        ]
    }

def solve_q5_tires(task_package: dict) -> dict:
    """
    Решает задачу Q5: расчет процентного изменения пробега за один оборот колеса.
    ИСПРАВЛЕНО для новой архитектуры данных.
    """
    # 1. Извлекаем данные
    plot_data = task_package.get("plot_data", {})
    task_specific_data = plot_data.get("task_specific_data", {})
    task_5_data = task_specific_data.get("task_5_data", {})
    
    original_marking = task_5_data.get("original_tire", "0/0 R0")
    replacement_marking = task_5_data.get("replacement_tire", "0/0 R0")
    pi = plot_data.get("constants", {}).get("pi", 3.14159)

    # 2. Парсим и считаем диаметры
    original_B, original_H, original_d, _ = _parse_tire_marking(original_marking)
    replacement_B, replacement_H, replacement_d, _ = _parse_tire_marking(replacement_marking)
    original_diameter = calculate_tire_diameter(original_B, original_H, original_d)
    replacement_diameter = calculate_tire_diameter(replacement_B, replacement_H, replacement_d)
    
    # 3. Считаем длины окружностей
    original_circumference = pi * original_diameter
    replacement_circumference = pi * replacement_diameter
    
    # 4. Считаем процентное изменение
    if original_circumference == 0:
        percentage_change = 0.0
    else:
        percentage_change = ((replacement_circumference - original_circumference) / original_circumference) * 100
        
    # 5. Формируем шаги
    calculation_steps = [
        {"step_number": 1, "description": f"Рассчитываем диаметр исходного колеса ({original_marking}).", "calculation_result": f"{original_diameter:.2f} мм", "formula_representation": "...", "result_unit": "мм"},
        {"step_number": 2, "description": f"Рассчитываем диаметр нового колеса ({replacement_marking}).", "calculation_result": f"{replacement_diameter:.2f} мм", "formula_representation": "...", "result_unit": "мм"},
        {"step_number": 3, "description": "Находим длину окружности исходного колеса (L = πD).", "formula_representation": f"{pi:.4f} * {original_diameter:.2f}", "calculation_result": f"{original_circumference:.2f} мм", "result_unit": "мм"},
        {"step_number": 4, "description": "Находим длину окружности нового колеса.", "formula_representation": f"{pi:.4f} * {replacement_diameter:.2f}", "calculation_result": f"{replacement_circumference:.2f} мм", "result_unit": "мм"},
        {"step_number": 5, "description": "Считаем, на сколько процентов новая длина больше/меньше старой.", "formula_representation": f"(({replacement_circumference:.2f} - {original_circumference:.2f}) / {original_circumference:.2f}) * 100", "calculation_result": f"{percentage_change:.2f} %", "result_unit": "%"}
    ]
    
    final_value_rounded = round(percentage_change, 1)
    
    return {
        "question_group": "Q5_Tires_Mileage_Percentage",
        "question_id": "tires_q5_mileage_increase_percent",
        "explanation_idea": "Пробег за один оборот колеса — это его длина окружности. Чтобы найти процентное изменение, нужно сравнить длины окружностей нового и старого колес.",
        "calculation_steps": calculation_steps,
        "final_answer": {"value_machine": final_value_rounded, "value_display": str(final_value_rounded).replace('.', ','), "unit": "%"},
        "validation_code": f"return {final_value_rounded}",
        "hints": ["Длина окружности L = π * D.", "Для нахождения процента используй формулу: ((Новое - Старое) / Старое) * 100."]
    }

def solve_q6_tires(task_package: dict) -> dict:
    """
    Решает задачу Q6: выбор наиболее выгодного шиномонтажа.
    ИСПРАВЛЕНО для новой архитектуры данных.
    """
    # 1. Извлекаем данные
    plot_data = task_package.get("plot_data", {})
    task_specific_data = plot_data.get("task_specific_data", {})
    # Данные для Q6 могут лежать в разных местах, ищем надежно
    task_data = task_specific_data.get("task_6_data", task_specific_data.get("task_5_data", {}))
    service_data = task_data.get("service_choice_data", {})
    services = service_data.get("services", [])
    wheels_count = service_data.get("wheels_count", 4)

    calculation_steps = []
    step_number = 1
    total_costs = {}

    # 2. Рассчитываем стоимость для каждого шиномонтажа
    for service in services:
        name = service.get("name", "N/A")
        road_cost = service.get("road_cost", 0)
        ops = service.get("operations", {})
        work_per_wheel = sum(ops.values())
        
        # Шаг: стоимость работы
        total_work_cost = work_per_wheel * wheels_count
        calculation_steps.append({"step_number": step_number, "description": f"Считаем стоимость работы в шиномонтаже '{name}'.", "formula_representation": f"{work_per_wheel} * {wheels_count}", "calculation_result": f"{total_work_cost:.2f} руб", "result_unit": "руб"})
        step_number += 1
        
        # Шаг: общая стоимость (дорога уже посчитана в генераторе)
        total_cost = total_work_cost + road_cost
        total_costs[name] = total_cost
        calculation_steps.append({"step_number": step_number, "description": f"Суммарная стоимость для '{name}' (работа + дорога).", "formula_representation": f"{total_work_cost:.2f} + {road_cost}", "calculation_result": f"{total_cost:.2f} руб", "result_unit": "руб"})
        step_number += 1

    # 3. Шаг: сравнение и выбор минимальной стоимости
    if total_costs:
        min_cost = min(total_costs.values())
        costs_str = ", ".join([f"{cost:.2f}" for cost in total_costs.values()])
        calculation_steps.append({"step_number": step_number, "description": "Сравниваем общие затраты и выбираем минимальную.", "formula_representation": f"min({costs_str})", "calculation_result": f"{min_cost:.2f} руб", "result_unit": "руб"})
    else:
        min_cost = 0

    final_value_rounded = round(min_cost)
    
    return {
        "question_group": "Q6_Tires_Service_Optimization",
        "question_id": "tires_q6_cheapest_service",
        "explanation_idea": "Чтобы выбрать самый выгодный шиномонтаж, нужно для каждого варианта посчитать полную стоимость: работа плюс дорога. А потом сравнить.",
        "calculation_steps": calculation_steps,
        "final_answer": {"value_machine": final_value_rounded, "value_display": str(final_value_rounded).replace('.', ','), "unit": "руб"},
        "validation_code": f"return {final_value_rounded}",
        "hints": ["Не забудь учесть стоимость дороги.", "Стоимость работы нужно умножить на количество колес."]
    }