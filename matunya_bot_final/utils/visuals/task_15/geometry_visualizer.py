"""
Визуализатор геометрических чертежей для ОГЭ
Архитектура: Гибридный Интеллект

Создание диаграмм для Telegram бота
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import math
import os

class GeometryVisualizer:
    """Визуализатор геометрических задач"""
    
    def __init__(self, save_dir="visualization/examples"):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        
        # Настройка стиля
        plt.style.use('default')
        plt.rcParams['font.size'] = 12
        plt.rcParams['axes.linewidth'] = 1.5
        plt.rcParams['grid.alpha'] = 0.3
    
    def create_triangle(self, A, B, C, title="Геометрическая задача", 
                       show_lengths=True, show_angles=True, filename=None):
        """
        Создание треугольника с подписями
        
        Args:
            A, B, C: кортежи (x, y) - координаты вершин
            title: заголовок задачи
            show_lengths: показывать длины сторон
            show_angles: показывать углы
            filename: имя файла для сохранения
        """
        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        
        # Рисуем треугольник
        triangle_x = [A[0], B[0], C[0], A[0]]
        triangle_y = [A[1], B[1], C[1], A[1]]
        ax.plot(triangle_x, triangle_y, 'b-', linewidth=2, label='AB')
        
        # Заливаем треугольник
        triangle = patches.Polygon([A, B, C], alpha=0.2, facecolor='lightblue', edgecolor='blue')
        ax.add_patch(triangle)
        
        # Подписи вершин
        ax.plot(A[0], A[1], 'ro', markersize=8)
        ax.plot(B[0], B[1], 'ro', markersize=8)
        ax.plot(C[0], C[1], 'ro', markersize=8)
        
        ax.text(A[0]-0.15, A[1]-0.15, 'A', fontsize=14, fontweight='bold')
        ax.text(B[0]+0.05, B[1]-0.15, 'B', fontsize=14, fontweight='bold')
        ax.text(C[0]+0.05, C[1]+0.05, 'C', fontsize=14, fontweight='bold')
        
        # Вычисляем длины сторон
        if show_lengths:
            self._add_side_length(ax, A, B, 'c', 0.5)
            self._add_side_length(ax, B, C, 'a', 0.5)
            self._add_side_length(ax, C, A, 'b', 0.5)
        
        # Вычисляем углы
        if show_angles:
            self._add_angle_label(ax, A, B, C, '∠A')
            self._add_angle_label(ax, B, C, A, '∠B')
            self._add_angle_label(ax, C, A, B, '∠C')
        
        # Настройка осей
        ax.set_xlim(-1, 4)
        ax.set_ylim(-1, 3)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        # Убираем оси
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        
        plt.tight_layout()
        
        # Сохранение файла
        if not filename:
            filename = f"triangle_{hash(title) % 10000}.png"
        
        filepath = os.path.join(self.save_dir, filename)
        plt.savefig(filepath, dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        
        return filepath
    
    def add_bisector(self, vertex, sides, filename=None):
        """
        Добавление биссектрисы к треугольнику
        
        Args:
            vertex: вершина, из которой проводится биссектриса
            sides: стороны треугольника (A, B, C)
            filename: имя файла
        """
        A, B, C = sides
        
        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        
        # Рисуем треугольник
        triangle_x = [A[0], B[0], C[0], A[0]]
        triangle_y = [A[1], B[1], C[1], A[1]]
        ax.plot(triangle_x, triangle_y, 'b-', linewidth=2)
        
        # Закрашиваем
        triangle = patches.Polygon([A, B, C], alpha=0.2, facecolor='lightblue', edgecolor='blue')
        ax.add_patch(triangle)
        
        # Находим середину противоположной стороны
        if vertex == A:
            opposite_side = [B, C]
            bisector_point = ((B[0] + C[0])/2, (B[1] + C[1])/2)
            bisector_angle = "∠A"
        elif vertex == B:
            opposite_side = [A, C]
            bisector_point = ((A[0] + C[0])/2, (A[1] + C[1])/2)
            bisector_angle = "∠B"
        else:  # vertex == C
            opposite_side = [A, B]
            bisector_point = ((A[0] + B[0])/2, (A[1] + B[1])/2)
            bisector_angle = "∠C"
        
        # Рисуем биссектрису
        ax.plot([vertex[0], bisector_point[0]], [vertex[1], bisector_point[1]], 
               'r--', linewidth=3, label='Биссектриса')
        
        # Отмечаем точку пересечения
        ax.plot(bisector_point[0], bisector_point[1], 'ro', markersize=6)
        
        # Подписи вершин
        ax.plot(A[0], A[1], 'ro', markersize=8)
        ax.plot(B[0], B[1], 'ro', markersize=8)
        ax.plot(C[0], C[1], 'ro', markersize=8)
        
        ax.text(A[0]-0.15, A[1]-0.15, 'A', fontsize=14, fontweight='bold')
        ax.text(B[0]+0.05, B[1]-0.15, 'B', fontsize=14, fontweight='bold')
        ax.text(C[0]+0.05, C[1]+0.05, 'C', fontsize=14, fontweight='bold')
        
        # Подпись биссектрисы
        mid_bisector = ((vertex[0] + bisector_point[0])/2, (vertex[1] + bisector_point[1])/2)
        ax.text(mid_bisector[0], mid_bisector[1], 'l', fontsize=16, fontweight='bold', 
               bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="red"))
        
        # Подпись угла
        self._add_angle_label(ax, vertex, opposite_side[0], opposite_side[1], bisector_angle)
        
        # Настройка осей
        ax.set_xlim(-1, 4)
        ax.set_ylim(-1, 3)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_title('Биссектриса треугольника', fontsize=14, fontweight='bold', pad=20)
        
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        plt.tight_layout()
        
        if not filename:
            filename = f"triangle_bisector_{hash(str(vertex)) % 10000}.png"
        
        filepath = os.path.join(self.save_dir, filename)
        plt.savefig(filepath, dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        
        return filepath
    
    def add_parallel_line(self, point1, point2, distance, label=None, filename=None):
        """
        Добавление параллельной линии
        
        Args:
            point1, point2: точки на исходной линии
            distance: расстояние для параллельной линии
            label: подпись
            filename: имя файла
        """
        # Вычисляем направляющий вектор
        dx = point2[0] - point1[0]
        dy = point2[1] - point1[1]
        length = math.sqrt(dx**2 + dy**2)
        
        # Нормальный вектор
        normal_x = -dy / length * distance
        normal_y = dx / length * distance
        
        # Параллельная линия
        parallel_point1 = (point1[0] + normal_x, point1[1] + normal_y)
        parallel_point2 = (point2[0] + normal_x, point2[1] + normal_y)
        
        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        
        # Исходная линия
        ax.plot([point1[0], point2[0]], [point1[1], point2[1]], 'b-', linewidth=2, label='Исходная линия')
        
        # Параллельная линия
        ax.plot([parallel_point1[0], parallel_point2[0]], 
               [parallel_point1[1], parallel_point2[1]], 
               'r-', linewidth=2, label='Параллельная линия')
        
        # Перпендикуляр
        mid_point = ((point1[0] + point2[0])/2, (point1[1] + point2[1])/2)
        perp_end = (mid_point[0] + normal_x, mid_point[1] + normal_y)
        
        ax.plot([mid_point[0], perp_end[0]], [mid_point[1], perp_end[1]], 
               'g--', linewidth=1, alpha=0.7)
        
        # Подпись расстояния
        ax.text(mid_point[0] + normal_x/2, mid_point[1] + normal_y/2, 
               f'h = {distance}', fontsize=12, fontweight='bold',
               bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.8))
        
        # Отметки перпендикуляра
        ax.plot(mid_point[0], mid_point[1], 'go', markersize=6)
        ax.plot(perp_end[0], perp_end[1], 'go', markersize=6)
        
        ax.set_xlim(min(point1[0], point2[0]) - 1, max(point1[0], point2[0]) + 1)
        ax.set_ylim(min(point1[1], point2[1]) - 1, max(point1[1], point2[1]) + 1)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_title('Параллельные прямые', fontsize=14, fontweight='bold', pad=20)
        
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        if label:
            ax.text(0.02, 0.98, label, transform=ax.transAxes, fontsize=12,
                   verticalalignment='top', bbox=dict(boxstyle="round,pad=0.3", facecolor="white"))
        
        plt.tight_layout()
        
        if not filename:
            filename = f"parallel_line_{hash(str((point1, point2, distance))) % 10000}.png"
        
        filepath = os.path.join(self.save_dir, filename)
        plt.savefig(filepath, dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        
        return filepath
    
    def _add_side_length(self, ax, point1, point2, label, offset=0.5):
        """Добавление подписи длины стороны"""
        # Вычисляем середину стороны
        mid_x = (point1[0] + point2[0]) / 2
        mid_y = (point1[1] + point2[1]) / 2
        
        # Вычисляем перпендикулярное смещение
        dx = point2[0] - point1[0]
        dy = point2[1] - point1[1]
        length = math.sqrt(dx**2 + dy**2)
        
        if length > 0:
            perp_x = -dy / length * offset
            perp_y = dx / length * offset
            
            text_x = mid_x + perp_x
            text_y = mid_y + perp_y
            
            ax.text(text_x, text_y, f'{label}', fontsize=12, fontweight='bold',
                   ha='center', va='center',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    def _add_angle_label(self, ax, vertex, point1, point2, angle_label):
        """Добавление подписи угла"""
        # Вычисляем угол
        angle1 = math.atan2(point1[1] - vertex[1], point1[0] - vertex[0])
        angle2 = math.atan2(point2[1] - vertex[1], point2[0] - vertex[0])
        
        # Выбираем средний угол для размещения подписи
        avg_angle = (angle1 + angle2) / 2
        
        # Радиус для размещения текста
        radius = 0.3
        text_x = vertex[0] + radius * math.cos(avg_angle)
        text_y = vertex[1] + radius * math.sin(avg_angle)
        
        ax.text(text_x, text_y, angle_label, fontsize=12, fontweight='bold',
               ha='center', va='center',
               bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.8))
    
    def save(self, filepath):
        """Сохранение фигуры (заглушка для совместимости)"""
        return filepath