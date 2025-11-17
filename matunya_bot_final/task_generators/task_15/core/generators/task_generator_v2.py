"""
Основной генератор задач "Матюня" - обновленная версия
Архитектура: Поддержка всех 16 подтипов задания 15 ОГЭ

Боевой режим - онлайн генерация задач с визуализацией
"""

from matunya_bot_final.task_generators.task_15.all_patterns_generator import AllPatternsGenerator
from matunya_bot_final.help_core.solvers.task_15.all_patterns_calculator import AllPatternsCalculator
from matunya_bot_final.utils.visuals.task_15.geometry_visualizer import GeometryVisualizer
from matunya_bot_final.core.templates.geometry_texts import geometry_templates
import json
import os
from datetime import datetime

class MatyunyaGenerator:
    """
    Основной генератор задач "Матюня"
    
    Режимы работы:
    - Режим накопления: офлайн подготовка задач и шаблонов
    - Боевой режим: онлайн генерация и решение задач
    - Поддержка всех 16 подтипов задания 15 ОГЭ
    """
    
    def __init__(self, save_dir="utils/visuals/task_15/examples"):
        """Инициализация генератора"""
        self.save_dir = save_dir
        self.visualizer = GeometryVisualizer(save_dir)
        
        # Инициализация новых генераторов и калькуляторов
        self.all_patterns_generator = AllPatternsGenerator()
        self.all_patterns_calculator = AllPatternsCalculator()
        
        # Совместимость с старыми методами
        self.generators = {
            'trigonometry': self.all_patterns_generator,
            # Другие генераторы будут добавлены позже
            # 'angles': AnglesGenerator(),
            # 'areas': AreasGenerator(),
            # 'similarity': SimilarityGenerator(),
            # 'equilateral': EquilateralGenerator()
        }
        
        # Создание папки для сохранения
        os.makedirs(save_dir, exist_ok=True)
    
    def generate_task(self, task_type="all_patterns", difficulty="medium", subtype=None):
        """Генерация задачи определенного типа"""
        if task_type == "all_patterns":
            # Используем новый генератор всех паттернов
            task = self.all_patterns_generator.generate_task(subtype, difficulty)
            return {
                'task': task,
                'timestamp': datetime.now().isoformat(),
                'generator': 'all_patterns_generator'
            }
        elif task_type in self.generators:
            # Совместимость с старыми генераторами
            generator = self.generators[task_type]
            task = generator.generate_task(difficulty)
            
            return {
                'task': task,
                'timestamp': datetime.now().isoformat(),
                'generator': task_type
            }
        else:
            raise ValueError(f"Тип задачи '{task_type}' не поддерживается")
    
    def solve_task(self, task):
        """Решение задачи с пошаговым объяснением"""
        # Используем новый калькулятор всех паттернов
        solution = self.all_patterns_calculator.solve_task(task)
        return solution
    
    def generate_with_visualization(self, task_type="all_patterns", difficulty="medium", subtype=None):
        """Полная генерация задачи с решением и визуализацией"""
        try:
            # 1. Генерируем задачу
            task_data = self.generate_task(task_type, difficulty, subtype)
            task = task_data['task']
            
            # 2. Решаем задачу
            solution = self.solve_task(task)
            
            # 3. Создаем визуализацию
            image_path = self._create_visualization(task, task_type)
            
            # 4. Формируем финальный результат
            result = {
                'task': task,
                'solution': solution,
                'image_path': image_path,
                'timestamp': task_data['timestamp'],
                'complete': True
            }
            
            # 5. Сохраняем отчет
            self._save_task_report(result)
            
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'task': task if 'task' in locals() else None,
                'complete': False
            }
    
    def get_available_subtypes(self):
        """Получение всех доступных подтипов"""
        return self.all_patterns_generator.get_all_subtypes()
    
    def get_subtypes_by_category(self, category):
        """Получение подтипов по категории"""
        return self.all_patterns_generator.get_subtypes_by_category(category)
    
    def get_subtype_info(self, subtype):
        """Получение информации о подтипе"""
        return self.all_patterns_generator.get_subtype_info(subtype)
    
    def _create_visualization(self, task, task_type):
        """Создание визуализации для задачи"""
        if task_type == "all_patterns":
            subtype = task.get('subtype', 'general')
            
            # Создаем треугольник в зависимости от подтипа
            if subtype in ['right_triangle_angles_sum', 'pythagoras_find_leg', 'pythagoras_find_hypotenuse']:
                # Прямоугольный треугольник
                A = (1, 1)
                B = (3, 1)
                C = (3, 2.5)  # Прямой угол в точке B
                title_prefix = "Прямоугольный треугольник"
            elif subtype in ['equilateral_height_to_side', 'equilateral_side_to_height']:
                # Равносторонний треугольник
                A = (1, 1)
                B = (3, 1)
                C = (2, 2.732)  # √3 ≈ 1.732 + 1 = 2.732
                title_prefix = "Равносторонний треугольник"
            elif subtype == 'isosceles_triangle_angles':
                # Равнобедренный треугольник
                A = (1, 1)
                B = (3, 1)
                C = (2, 2.5)  # Симметричный относительно середины
                title_prefix = "Равнобедренный треугольник"
            else:
                # Общий треугольник
                A = (1, 1)
                B = (3, 1)
                C = (2, 2)
                title_prefix = "Треугольник"
            
            # Формируем заголовок
            task_text = task.get('text', 'Геометрическая задача')
            if len(task_text) > 50:
                task_text = task_text[:47] + "..."
            
            filename = f"task15_{subtype}_{task.get('id', 'unknown')}.png"
            
            image_path = self.visualizer.create_triangle(
                A, B, C,
                title=f"{title_prefix}\n{task_text}",
                show_lengths=True,
                show_angles=True,
                filename=filename
            )
        else:
            # Базовый треугольник для других типов задач
            A = (1, 1)
            B = (3, 1)
            C = (2, 2)
            
            filename = f"demo_{task_type}_{task.get('id', 'unknown')}.png"
            
            image_path = self.visualizer.create_triangle(
                A, B, C,
                title=f"Задача: {task.get('text', 'Геометрическая задача')}",
                show_lengths=True,
                show_angles=True,
                filename=filename
            )
        
        return image_path
    
    def _save_task_report(self, result):
        """Сохранение отчета о задаче"""
        # Создаем папку для отчетов
        reports_dir = "data/exercise_reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        # Формируем имя файла
        task_id = result['task'].get('id', 'unknown')
        filename = f"{reports_dir}/report_{task_id}.json"
        
        # Убираем излишние поля для сохранения
        report_data = {
            'task': result['task'],
            'solution': {
                'steps': result['solution'].get('steps', []),
                'final_result': result['solution'].get('final_result', ''),
                'task_type': result['solution'].get('task_type', '')
            },
            'image_path': result['image_path'],
            'timestamp': result['timestamp'],
            'generated_by': 'MatyunyaGenerator v2.0 - All Patterns'
        }
        
        # Сохраняем в JSON
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        return filename

# Функция для демонстрации всех возможностей
def demo_all_patterns():
    """Демонстрация всех возможностей генератора"""
    print("🎯 ДЕМОНСТРАЦИЯ ВСЕХ ПАТТЕРНОВ ЗАДАНИЯ 15")
    print("=" * 60)
    
    # Инициализация
    generator = MatyunyaGenerator()
    
    # Показываем все доступные подтипы
    print("📋 Все доступные подтипы:")
    all_subtypes = generator.get_available_subtypes()
    for i, subtype in enumerate(all_subtypes, 1):
        info = generator.get_subtype_info(subtype)
        print(f"  {i:2d}. {subtype} ({info['category']})")
    
    print("\n🔍 Демонстрация случайных задач:")
    
    # Генерируем и решаем несколько задач разных типов
    categories = ['angles', 'right_triangles', 'general_triangles', 'isosceles_triangles']
    
    for category in categories:
        print(f"\n📂 Категория: {category}")
        subtypes = generator.get_subtypes_by_category(category)
        if subtypes:
            subtype = subtypes[0]  # Берем первый подтип из категории
            print(f"   🎲 Генерация задачи типа: {subtype}")
            
            result = generator.generate_with_visualization(subtype=subtype)
            if result['complete']:
                print(f"   ✅ Задача: {result['task']['text'][:60]}...")
                print(f"   🧮 Решение: {result['solution']['final_result']}")
                print(f"   🖼️  Изображение: {result['image_path']}")
            else:
                print(f"   ❌ Ошибка: {result['error']}")
    
    print("\n🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!")
    print("=" * 60)

if __name__ == "__main__":
    demo_all_patterns()
