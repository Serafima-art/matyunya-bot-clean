"""
Модуль для рендеринга HTML-таблиц для заданий 1-5 ("Шины").
Содержит две публичные функции для генерации HTML-строк на основе переданных данных.
Все вспомогательные функции приватные (начинаются с _).
Нет внешних зависимостей, кроме стандартных библиотек.
"""

from typing import Dict, List, Any, Tuple


# Константы для таблицы автосервисов (из tires_service_schema.py)
OPS_DICT: List[Dict[str, str]] = [
    {"key": "remove",  "title": "Снятие колеса"},
    {"key": "mount",   "title": "Замена шины"},
    {"key": "balance", "title": "Балансировка колеса"},
    {"key": "install", "title": "Установка колеса"},
]

# Удобный список ключей операций
SERVICE_OP_KEYS: List[str] = [op["key"] for op in OPS_DICT]

# Значения по умолчанию
DEFAULT_CURRENCY: str = "руб."


def validate_service_table(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Лёгкая валидация структуры данных для таблицы автосервисов.
    Проверяет wheels_count, services и значения операций.
    
    Args:
        data: Словарь с данными для таблицы.
    
    Returns:
        Tuple[bool, List[str]]: (валидно, список ошибок).
    """
    errors: List[str] = []

    wheels = data.get("wheels_count", 4)
    if not isinstance(wheels, int) or wheels < 1:
        errors.append("wheels_count должен быть целым числом >= 1")

    services = data.get("services", [])
    if not isinstance(services, list) or not services:
        errors.append("services должен быть непустым списком")

    for idx, svc in enumerate(services, start=1):
        sid = svc.get("id", f"#{idx}")
        road_cost = svc.get("road_cost")
        if not (isinstance(road_cost, (int, float)) and road_cost >= 0):
            errors.append(f"service {sid}: road_cost должен быть числом >= 0")
        ops = svc.get("ops", {})
        for k in SERVICE_OP_KEYS:
            v = ops.get(k)
            if not (isinstance(v, (int, float)) and v >= 0):
                errors.append(f"service {sid}: ops['{k}'] должен быть числом >= 0")

    return (len(errors) == 0, errors)


def render_tire_sizes_table(data: Dict[str, Dict[str, List[str]]]) -> str:
    """
    Генерирует HTML-таблицу с размерами шин для вопроса Q1.
    Формат: карточки по диаметрам диска с ширинами и профилями.
    
    Args:
        data: Словарь {ширина: {диаметр: [профили шин]}} (ширина и диаметр как строки).
    
    Returns:
        str: Готовая HTML-строка для таблицы.
    """
    if not data:
        return "<b><u>Таблица размеров шин:</u></b>\n\n<i>Данные недоступны</i>"

    # Собираем все уникальные диаметры и сортируем их
    all_diameters = set()
    for width_data in data.values():
        all_diameters.update(width_data.keys())
    sorted_diameters = sorted([int(d) for d in all_diameters])

    # Начинаем сборку HTML
    html_parts = ['<b><u>Таблица размеров шин:</u></b>\n']

    for diameter in sorted_diameters:
        diameter_str = str(diameter)
        html_parts.append(f'\n<b>Диаметр диска: {diameter}"</b>')

        # Собираем ширины и профили для этого диаметра
        width_entries = []
        for width, diameter_data in data.items():
            if diameter_str in diameter_data:
                profiles = diameter_data[diameter_str]
                if profiles:
                    # Извлекаем профили из маркировок (e.g., "185/65" -> "/65")
                    profile_list = []
                    for marking in profiles:
                        if '/' in marking:
                            profile = marking.split('/')[-1]
                            profile_list.append(f"/{profile}")
                        else:
                            profile_list.append(marking)
                    if profile_list:
                        width_entries.append((int(width), ", ".join(profile_list)))

        # Сортируем по ширине и добавляем в HTML
        width_entries.sort()
        if width_entries:
            for width, profiles in width_entries:
                html_parts.append(f'• Ширина {width}: {profiles}')
        else:
            html_parts.append('• <i>Нет доступных размеров</i>')

    return '\n'.join(html_parts)


def _get_service_html(service: Dict[str, Any], currency: str, ops_dict: List[Dict[str, str]]) -> List[str]:
    """
    Приватная функция: генерирует HTML-части для одного автосервиса.
    
    Args:
        service: Данные одного сервиса.
        currency: Валюта.
        ops_dict: Список операций с ключами и заголовками.
    
    Returns:
        List[str]: Список строк HTML для сервиса.
    """
    html_parts = []
    service_name = service.get('title', service.get('name', 'Автосервис'))
    service_id = service.get('id', '')

    # Заголовок сервиса
    if service_id:
        html_parts.append(f'<b>Сервис {service_id}:</b>')
    else:
        html_parts.append(f'<b>{service_name}:</b>')

    # Стоимость дороги (выезд)
    road_cost = service.get('road_cost', 0)
    if road_cost > 0:
        html_parts.append(f'• Стоимость дороги: <b>{int(road_cost)} {currency}</b>')

    # Стоимость операций
    ops = service.get('ops', {})
    for op in ops_dict:
        key = op['key']
        cost = ops.get(key, 0)
        if cost > 0:
            html_parts.append(f'• {op["title"]}: <b>{int(cost)} {currency}</b>')

    return html_parts


def render_service_costs_table(data: Dict[str, Any]) -> str:
    """
    Генерирует HTML-таблицу с стоимостью услуг в автосервисах для вопроса Q6.
    Формат: карточки по сервисам с дорогой и операциями.
    
    Args:
        data: Словарь {
            'services': List[Dict] (каждый: {'id': str, 'title': str, 'road_cost': float, 'ops': {key: float}}),
            'currency': str (опционально),
            'wheels_count': int (опционально, для валидации)
        }.
    
    Returns:
        str: Готовая HTML-строка для таблицы.
    """
    # Валидация данных
    is_valid, errors = validate_service_table(data)
    if not is_valid:
        return f"<b><u>Стоимость услуг в автосервисах:</u></b>\n\n<i>Ошибка в данных: {', '.join(errors)}</i>"

    services = data.get('services', [])
    currency = data.get('currency', DEFAULT_CURRENCY)

    if not services:
        return "<b><u>Стоимость услуг в автосервисах:</u></b>\n\n<i>Данные недоступны</i>"

    # Сборка HTML
    html_parts = ['<b><u>Стоимость услуг в автосервисах:</u></b>\n']

    for service in services:
        service_html = _get_service_html(service, currency, OPS_DICT)
        html_parts.extend(service_html)
        html_parts.append('')  # Разделитель между сервисами

    return '\n'.join(html_parts)