# generate_tire_plots.py
import json
import random
import copy
from pathlib import Path

# --- КОНФИГУРАЦИЯ ---
NUM_PLOTS_TO_GENERATE = 20
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data" / "tasks_1_5" / "tires"
PLOTS_DIR = DATA_DIR / "plots"
TEXTS_DIR = DATA_DIR / "texts"

ETALON_PLOT_PATH = PLOTS_DIR / "plot_00_Yashchenko_etalon.json"
LEXEMES_PATH = TEXTS_DIR / "lexemes.json"

def load_json(path: Path) -> dict:
    """Загружает JSON-файл."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data: dict, path: Path):
    """Сохраняет данные в JSON-файл с красивым форматированием."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_all_allowed_tires(allowed_sizes: dict) -> list[str]:
    """Собирает плоский список всех разрешенных маркировок шин."""
    all_tires = []
    for width, diameters in allowed_sizes.items():
        for diameter, profiles in diameters.items():
            for profile in profiles:
                # profile уже содержит `width/profile`
                full_marking = f"{profile} R{diameter}"
                all_tires.append(full_marking)
    return all_tires

def parse_tire_marking(marking: str) -> dict:
    """Разбирает полную маркировку шины на компоненты."""
    parts = marking.replace(' R', '/').split('/')
    return {
        "width": int(parts[0]),
        "profile": int(parts[1]),
        "construction": "R",
        "diameter": int(parts[2]),
        "full_marking": marking
    }

def mutate_plot(etalon_data: dict, lexemes: dict, all_tires: list[str]) -> dict:
    """Вносит случайные, но корректные изменения в копию эталонного плота."""
    plot = copy.deepcopy(etalon_data)

    # 1. Меняем автомобиль
    vehicle_ids = list(lexemes.keys())
    if vehicle_ids:
        plot["vehicle_id"] = random.choice(vehicle_ids)

    # 2. Меняем базовую шину
    new_base_tire_marking = random.choice(all_tires)
    plot["base_tire_marking"] = parse_tire_marking(new_base_tire_marking)

    # 3. Меняем данные для конкретных задач
    spec_data = plot["task_specific_data"]
    
    # Task 1: Выбираем случайный диаметр диска из доступных
    available_diameters = list(etalon_data["allowed_tire_sizes"]["185"].keys()) # Берем любой ключ для получения диаметров
    spec_data["task_1_data"]["target_diameter"] = int(random.choice(available_diameters))

    # Task 2: Выбираем две СЛУЧАЙНЫЕ РАЗНЫЕ шины для сравнения
    tire1, tire2 = random.sample(all_tires, 2)
    spec_data["task_2_data"]["tire_1"] = tire1
    spec_data["task_2_data"]["tire_2"] = tire2

    # Task 3: Всегда привязан к базовой шине, обновляем для консистентности
    spec_data["task_3_data"]["tire_marking"] = plot["base_tire_marking"]["full_marking"]

    # Task 4 & 5: Обновляем 'original_tire' и выбираем новую 'replacement_tire'
    spec_data["task_4_data"]["original_tire"] = plot["base_tire_marking"]["full_marking"]
    spec_data["task_4_data"]["replacement_tire"] = random.choice(all_tires)
    
    spec_data["task_5_data"]["original_tire"] = plot["base_tire_marking"]["full_marking"]
    spec_data["task_5_data"]["replacement_tire"] = random.choice(all_tires)

    # Task 5: Рандомизируем цены на шиномонтаж
    for service in spec_data["task_5_data"]["service_choice_data"]["services"]:
        service["road_cost"] = random.randint(200, 500)
        for op in service["operations"]:
            service["operations"][op] = random.randint(40, 350)
            
    return plot

def main():
    """Главная функция для генерации плотов."""
    print("--- Запуск Генератора Плотов 'Идеальный Клон' v1.0 ---")
    
    if not ETALON_PLOT_PATH.exists():
        print(f"❌ Ошибка: Эталонный плот не найден по пути: {ETALON_PLOT_PATH}")
        return
        
    if not LEXEMES_PATH.exists():
        print(f"❌ Ошибка: Файл с лексемами не найден по пути: {LEXEMES_PATH}")
        return

    etalon_data = load_json(ETALON_PLOT_PATH)
    lexemes = load_json(LEXEMES_PATH)
    
    # Собираем список всех возможных шин один раз
    all_tires = get_all_allowed_tires(etalon_data["allowed_tire_sizes"])
    
    print(f"✅ Эталон и лексемы загружены. Найдено {len(all_tires)} уникальных шин.")
    print(f"🚀 Начинаю генерацию {NUM_PLOTS_TO_GENERATE} новых плотов в папку '{PLOTS_DIR.name}'...")

    for i in range(1, NUM_PLOTS_TO_GENERATE + 1):
        new_plot_data = mutate_plot(etalon_data, lexemes, all_tires)
        
        # Формируем имя файла с ведущим нулем (plot_01.json, plot_02.json, ...)
        filename = f"plot_{i:02d}.json"
        save_path = PLOTS_DIR / filename
        
        save_json(new_plot_data, save_path)
        print(f"  -> ✅ Создан файл: {filename}")
        
    print(f"🎉 Готово! Успешно сгенерировано {NUM_PLOTS_TO_GENERATE} плотов.")
    print("--- Генератор Плотов завершил работу. ---")


if __name__ == "__main__":
    main()