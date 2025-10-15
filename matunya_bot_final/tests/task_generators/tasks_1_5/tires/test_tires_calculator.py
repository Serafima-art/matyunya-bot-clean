# test_calculator.py
"""
Автотестер для калькулятора шин.
Проверяет все задачи автоматически и показывает ошибки.
"""
import json
from pathlib import Path
from matunya_bot_final.task_generators.tasks_1_5.tires.calculator import TiresCalculator

def load_test_plot():
    """Загружает тестовый плот"""
    plot_path = Path("data/tasks_1_5/tires/plots/plot_01.json")
    with open(plot_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def manual_calculate_task_2(plot_data):
    """Ручной расчет задачи 2 для проверки"""
    # Данные из плота
    tire_1 = "185/70 R16"  # из task_2_data
    tire_2 = "215/50 R16"  # base_marking из логов: 205/55 R16
    
    print(f"Проверяем задачу 2:")
    print(f"  tire_1: {tire_1}")
    print(f"  tire_2: {tire_2}")
    
    # Ручной расчет
    # 185/70 R16: радиус = 70% от 185 + 16×25.4/2 = 129.5 + 203.2 = 332.7 мм
    # 205/55 R16: радиус = 55% от 205 + 16×25.4/2 = 112.75 + 203.2 = 315.95 мм
    # Разность: 332.7 - 315.95 = 16.75 мм
    
    r1 = 185 * 0.70 + 16 * 25.4 / 2
    r2 = 205 * 0.55 + 16 * 25.4 / 2
    diff = abs(r1 - r2)
    
    print(f"  Ручной расчет:")
    print(f"    r1 ({tire_1}): {r1:.2f} мм") 
    print(f"    r2 (205/55 R16): {r2:.2f} мм")
    print(f"    Разность: {diff:.2f} мм")
    
    return diff

def test_all_tasks():
    """Тестирует все задачи"""
    plot_data = load_test_plot()
    calculator = TiresCalculator()
    
    print("="*60)
    print("АВТОТЕСТ КАЛЬКУЛЯТОРА ШИН")
    print("="*60)
    
    # Запускаем калькулятор
    results = calculator.calculate_all_tasks(plot_data)
    
    print(f"\nРезультаты калькулятора:")
    for key, value in results.items():
        print(f"  {key}: {value}")
    
    print(f"\n" + "-"*40)
    print("ПРОВЕРКА ЗАДАЧИ 2:")
    print("-"*40)
    
    manual_result = manual_calculate_task_2(plot_data)
    calc_result = results.get("task_2_answer", 0)
    
    print(f"Калькулятор выдал: {calc_result}")
    print(f"Должно быть: {manual_result:.1f}")
    
    if abs(float(calc_result) - manual_result) < 0.1:
        print("✅ Задача 2: ПРАВИЛЬНО")
    else:
        print("❌ Задача 2: ОШИБКА")
        print(f"   Разница: {abs(float(calc_result) - manual_result):.2f}")
    
    print(f"\n" + "-"*40)
    print("АНАЛИЗ ДАННЫХ ПЛОТА:")
    print("-"*40)
    
    task_2_data = plot_data["task_specific_data"]["task_2_data"]
    print(f"task_2_data: {task_2_data}")
    
    base_marking = plot_data["base_tire_marking"]["full_marking"] 
    print(f"base_marking: {base_marking}")
    
    print(f"\n" + "="*60)

def test_specific_calculation():
    """Тестирует конкретные расчеты"""
    from matunya_bot_final.task_generators.tasks_1_5.tires.calculator import parse_tire_marking, calculate_tire_parameters
    
    constants = {"inch_to_mm": 25.4, "pi": 3.141592653589793}
    
    print("\n" + "="*60)
    print("ДЕТАЛЬНЫЙ ТЕСТ РАСЧЕТОВ")
    print("="*60)
    
    # Тестируем парсинг
    tire_1_data = parse_tire_marking("185/70 R16")
    tire_2_data = parse_tire_marking("205/55 R16")
    
    print(f"Парсинг 185/70 R16: {tire_1_data}")
    print(f"Парсинг 205/55 R16: {tire_2_data}")
    
    # Тестируем расчеты
    if tire_1_data:
        params_1 = calculate_tire_parameters(tire_1_data, constants)
        print(f"Параметры 185/70 R16: {params_1}")
    
    if tire_2_data:
        params_2 = calculate_tire_parameters(tire_2_data, constants)
        print(f"Параметры 205/55 R16: {params_2}")

if __name__ == "__main__":
    test_all_tasks()
    test_specific_calculation()