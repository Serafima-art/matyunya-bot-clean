# handlers/callbacks/navigators/task_12_navigator.py
"""
Навигатор Задания 12 (Расчёты по формулам)

Ответственность:
- Человеческие названия подтипов (UI-слой)
- Пулы для «🎲 Случайная тема»
- Безопасный вызов генератора по ключу (tuple | dict)
- Утилиты выбора случайной темы
"""

from __future__ import annotations

import random
from typing import Tuple, Dict, Callable, Optional, List

# ──────────────────────────────────────────────────────────────────────────────
# Человеческие названия подтипов (для экранов «🎲» и возможных списков)
# ──────────────────────────────────────────────────────────────────────────────

SUBTYPE_TITLES: Dict[str, str] = {
    # Геометрия
    "area_rhombus": "Площадь ромба",
    "area_triangle": "Площадь треугольника",
    "area_parallelogram": "Площадь параллелограмма",
    "area_trapezoid": "Площадь трапеции",
    "area_quadrilateral_d1d2_sin": "Площадь четырёхугольника",
    "bisector_length": "Длина биссектрисы",
    "radius_inscribed_rt_triangle": "Радиус вписанной (прям.)",
    "height_pyramid": "Высота пирамиды",
    "length_circle": "Длина окружности",
    "triangle_area_circumradius": "S треуг. через R",
    "polygon_angles_sum": "Сумма углов n-уг.",

    # Физика: механика
    "pendulum_period": "Маятник",
    "kinetic_energy": "Кинетическая энергия (v)",
    "potential_energy": "Потенциальная энергия (m)",
    "mechanical_energy": "Полная мех. энергия (E)",
    "gravity_law": "Всемирное тяготение",

    # Физика: электричество/теплота
    "joul_lenz_law": "Закон Джоуля–Ленца (t)",
    "electric_power": "Мощность тока (R/P)",
    "coulomb_law": "Закон Кулона",
    "work_of_current": "Работа тока (A)",
    "capacitor_energy": "Энергия конденсатора (W)",

    # Физика: МКТ/газы (Менделеев–Клапейрон)
    "gas_law_find_P": "МК: найти P",
    "gas_law_find_T": "МК: найти T",
    "gas_law_find_V": "МК: найти V",
    "gas_law_find_n": "МК: найти ν",

    # Движение по окружности
    "centripetal_acceleration": "Центростремит. ускорение (R)",

    # Разное
    "steps_distance": "Расстояние по шагам",
    "lightning_distance": "Расстояние до молнии",
    "temperature_conversion": "Перевод температур",
    "taxi_cost": "Стоимость такси",
    "well_cost": "Стоимость колодца",
}

# ──────────────────────────────────────────────────────────────────────────────
# Пулы для «🎲 Случайная тема»
# (согласованы ранее; 31 подтип суммарно)
# ──────────────────────────────────────────────────────────────────────────────

# 12.1 «Вычисление по формуле» — только подтипы с прямой подстановкой
POOL_T12_FORMULA_RANDOM: List[str] = [
    "mechanical_energy",
    "capacitor_energy",
    "work_of_current",
    "gas_law_find_P",
    "gas_law_find_T",
    "gas_law_find_V",
    "gas_law_find_n",
    "temperature_conversion",  # договорённость: оставляем в 1 как «чистая формула»
]

# 12.2 «Линейные уравнения» — всё, что сводится к выражению неизвестного
POOL_T12_LINEAR_RANDOM: List[str] = [
    # Геометрия
    "area_rhombus",
    "area_triangle",
    "area_parallelogram",
    "area_trapezoid",
    "area_quadrilateral_d1d2_sin",
    "bisector_length",
    "radius_inscribed_rt_triangle",
    "height_pyramid",
    "length_circle",
    "triangle_area_circumradius",
    "polygon_angles_sum",
    # Физика
    "pendulum_period",
    "kinetic_energy",
    "potential_energy",
    "gravity_law",
    "electric_power",
    "joul_lenz_law",
    "coulomb_law",
    "centripetal_acceleration",
]

# 12.3 «Разные задачи»
POOL_T12_MISC_RANDOM: List[str] = [
    "steps_distance",
    "lightning_distance",
    "temperature_conversion",
    "taxi_cost",
    "well_cost",
]

# Объединённый пул без дублей (порядок стабилизируем через dict.fromkeys)
POOL_T12_ALL: List[str] = list(
    dict.fromkeys(POOL_T12_FORMULA_RANDOM + POOL_T12_LINEAR_RANDOM + POOL_T12_MISC_RANDOM)
)

# ──────────────────────────────────────────────────────────────────────────────
# Публичные утилиты для UI и рандома
# ──────────────────────────────────────────────────────────────────────────────

def title_for(subtype_key: str) -> str:
    """Возвращает короткое человекочитаемое название подтипа."""
    return SUBTYPE_TITLES.get(subtype_key, subtype_key)

def pick_random_any() -> str:
    """Случайный подтип из всех 31."""
    return random.choice(POOL_T12_ALL)

def pick_random_formula() -> str:
    """Случайный подтип из 12.1 (формулы)."""
    return random.choice(POOL_T12_FORMULA_RANDOM)

def pick_random_linear() -> str:
    """Случайный подтип из 12.2 (линейные уравнения)."""
    return random.choice(POOL_T12_LINEAR_RANDOM)

def pick_random_misc() -> str:
    """Случайный подтип из 12.3 (разные задачи)."""
    return random.choice(POOL_T12_MISC_RANDOM)

def pick_random_by_pool(theme_key: str, sub_theme_key: str) -> Optional[str]:
    """
    Выбирает случайный подтип из нужного "пула" на основе ключей.
    Например: theme_key='formulas', sub_theme_key='geometry'.
    """
    # Эта логика пока упрощена. В будущем мы можем связать
    # 'geometry' с отдельным пулом. А пока просто берем из общего.
    if theme_key == "formulas":
        pool = POOL_T12_FORMULA_RANDOM
    elif theme_key == "linear_equations":
        pool = POOL_T12_LINEAR_RANDOM
    elif theme_key == "misc_tasks":
        pool = POOL_T12_MISC_RANDOM
    else:
        pool = POOL_T12_ALL

    if not pool:
        return None
    return random.choice(pool)

def all_subtypes() -> List[str]:
    """Полный список всех поддерживаемых подтипов (31 ключ)."""
    return list(SUBTYPE_TITLES.keys())

# ──────────────────────────────────────────────────────────────────────────────
# Безопасный вызов генератора №12
# ──────────────────────────────────────────────────────────────────────────────

_GEN_CALLABLE: Optional[Callable[..., object]] = None  # лениво кэшируем найденную функцию

def _load_generator_callable() -> Callable[..., object]:
    """
    Импортируем генератор №12, поддерживая разные имена функций.
    Ожидается одна из:
      - py_generators.task_12_generator.generate_by_subtype(subtype_key)
      - py_generators.task_12_generator.generate_task_12(subtype_key=...)
    """
    global _GEN_CALLABLE
    if _GEN_CALLABLE is not None:
        return _GEN_CALLABLE

    from importlib import import_module

    module = import_module("py_generators.task_12_generator")

    # возможные имена фабрики
    for fn_name in ("generate_by_subtype", "generate_task_12", "generate_task_12_by_subtype"):
        gen = getattr(module, fn_name, None)
        if callable(gen):
            _GEN_CALLABLE = gen
            return _GEN_CALLABLE

    raise ImportError(
        "Не найден генератор для задания 12. "
        "Ожидал функции: generate_by_subtype / generate_task_12 / generate_task_12_by_subtype."
    )

def run_subtype(subtype_key: str) -> Tuple[str, str, str]:
    """
    Запускает генерацию подтипа №12 и приводит результат к виду:
    (subtype_key, text, answer)

    Поддерживает форматы ответа генератора:
      - tuple/list: (subtype_key, text, answer)
      - dict: {"subtype_key": ..., "text": ..., "answer": ...}
    И сигнатуры вызова:
      - gen(subtype_key)
      - gen(subtype_key=subtype_key)
    """
    gen = _load_generator_callable()

    # вызов пробуем позиционный, затем именованный
    try:
        res = gen(subtype_key)
    except TypeError:
        res = gen(subtype_key=subtype_key)

    if isinstance(res, dict):
        sk = res.get("subtype_key", subtype_key)
        text = res["text"]
        answer = res["answer"]
        return str(sk), str(text), str(answer)

    if isinstance(res, (tuple, list)) and len(res) >= 3:
        sk, text, answer = res[0], res[1], res[2]
        return str(sk), str(text), str(answer)

    raise ValueError(
        "Генератор №12 вернул неожиданный формат. "
        "Жду (subtype_key, text, answer) или dict с этими ключами."
    )

__all__ = [
    "title_for",
    "pick_random_any",
    "pick_random_formula",
    "pick_random_linear",
    "pick_random_misc",
    "all_subtypes",
    "run_subtype",
    "SUBTYPE_TITLES",
    "POOL_T12_FORMULA_RANDOM",
    "POOL_T12_LINEAR_RANDOM",
    "POOL_T12_MISC_RANDOM",
    "POOL_T12_ALL",
]