"""
Основной генератор задач "Матюня"
Архитектура: Гибридный Интеллект
from matunya_bot_final.help_core.solvers.task_15.all_patterns_calculator import AllPatternsCalculator

Боевой режим - онлайн генерация задач с визуализацией
"""

from matunya_bot_final.task_generators.task_15.all_patterns_generator import AllPatternsGenerator
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
    """
    
    def __init__(self, save_dir="visualization/examples"):
        """Инициализация генератора"""
        self.save_dir = save_dir
        self.visualizer = GeometryVisualizer(save_dir)
        
        # Инициализация генераторов задач
        self.all_patterns_generator = AllPatternsGenerator()
        self.all_patterns_calculator = AllPatternsCalculator()
        self.generators = {
            'trigonometry': TrigonometryGenerator(),
            # Другие генераторы будут добавлены позже
            # 'angles': AnglesGenerator(),
            # 'areas': AreasGenerator(),
            # 'similarity': SimilarityGenerator(),
            # 'equilateral': EquilateralGenerator()
        }
        
        # Создание папки для сохранения
        os.makedirs(save_dir, exist_ok=True)
    
    def generate_task(self, task_type="trigonometry", difficulty="medium"):
        """Генерация задачи определенного типа"""
        if task_type not in self.generators:
            raise ValueError(f"Тип задачи '{task_type}' не поддерживается")
        
        generator = self.generators[task_type]
        task = generator.generate_task(difficulty)
        
        return {
            'task': task,
            'timestamp': datetime.now().isoformat(),
            'generator': task_type
        }
    
    def solve_task(self, task):
        """Решение задачи с пошаговым объяснением"""
        task_type = task.get('type', 'unknown')
        
        if task_type == 'trigonometry':
            return self._solve_trigonometry_task(task)
        else:
            return {
                'error': f'Решение для типа задач "{task_type}" не реализовано',
                'steps': [],
                'final_result': 'Неизвестная задача'
            }
    
    def generate_with_visualization(self, task_type="trigonometry", difficulty="medium"):
        """Полная генерация задачи с решением и визуализацией"""
        try:
            # 1. Генерируем задачу
            task_data = self.generate_task(task_type, difficulty)
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
    
    def _solve_trigonometry_task(self, task):
        """Решение тригонометрической задачи"""
        task_type = task.get('task_type', 'unknown')
        angle = task.get('angle', 0)
        params = task.get('additional_params', {})
        
        # Импортируем калькулятор
        from matunya_bot_final.help_core.solvers.task_15.trig_calculator import TrigCalculator
        
        calculator = TrigCalculator()
        
        if task_type == 'find_cos':
            return self._solve_find_cos(angle, calculator)
        elif task_type == 'find_sin':
            return self._solve_find_sin(angle, calculator)
        elif task_type == 'find_tg':
            return self._solve_find_tg(angle, calculator)
        elif task_type == 'find_side':
            return self._solve_find_side(angle, params, calculator)
        else:
            return {
                'steps': [],
                'final_result': f'Решение для {task_type} не реализовано'
            }
    
    def _solve_find_cos(self, angle, calculator):
        """Решение задачи нахождения cos"""
        cos_value = calculator.standard_values.get(angle, {}).get('cos', f'cos{angle}°')
        
        steps = []
        steps.append({
            'step': 1,
            'formula': 'Стандартное значение',
            'calculation': f'cos({angle}°) = {cos_value}',
            'explanation': f'Используем табличные значения для угла {angle}°'
        })
        
        return {
            'steps': steps,
            'final_result': f'cos({angle}°) = {cos_value}'
        }
    
    def _solve_find_sin(self, angle, calculator):
        """Решение задачи нахождения sin"""
        sin_value = calculator.standard_values.get(angle, {}).get('sin', f'sin{angle}°')
        
        steps = []
        steps.append({
            'step': 1,
            'formula': 'Стандартное значение',
            'calculation': f'sin({angle}°) = {sin_value}',
            'explanation': f'Используем табличные значения для угла {angle}°'
        })
        
        return {
            'steps': steps,
            'final_result': f'sin({angle}°) = {sin_value}'
        }
    
    def _solve_find_tg(self, angle, calculator):
        """Решение задачи нахождения tg"""
        tg_value = calculator.standard_values.get(angle, {}).get('tg', f'tg{angle}°')
        
        steps = []
        steps.append({
            'step': 1,
            'formula': 'Стандартное значение',
            'calculation': f'tg({angle}°) = {tg_value}',
            'explanation': f'Используем табличные значения для угла {angle}°'
        })
        
        return {
            'steps': steps,
            'final_result': f'tg({angle}°) = {tg_value}'
        }
    
    def _solve_find_side(self, angle, params, calculator):
        """Решение задачи нахождения стороны"""
        known_side = params.get('known_side', 'a')
        
        # Используем калькулятор для решения
        result = calculator.calculate_side_from_cos(angle, known_side)
        
        return {
            'steps': [step.__dict__ for step in result['steps']],
            'final_result': result['final_result']
        }
    
    def _create_visualization(self, task, task_type):
        """Создание визуализации для задачи"""
        if task_type == 'trigonometry':
            # Создаем простой треугольник для тригонометрии
            # Равносторонний треугольник с координатами
            A = (1, 1)
            B = (3, 1)
            C = (2, 2.732)  # √3 ≈ 1.732 + 1 = 2.732
            
            angle = task.get('angle', 45)
            filename = f"demo_trig_{task.get('task_type', 'default')}_{task.get('id', 'unknown')}.png"
            
            image_path = self.visualizer.create_triangle(
                A, B, C,
                title=f"Треугольник ABC\n∠A = {angle}°",
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
                'final_result': result['solution'].get('final_result', '')
            },
            'image_path': result['image_path'],
            'timestamp': result['timestamp'],
            'generated_by': 'MatyunyaGenerator v1.0'
        }
        
        # Сохраняем в JSON
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        return filename