from matunya_bot_final.utils import db_manager
from matunya_bot_final.utils.text_formatters import bold_numbers
import json
import os
import random
import importlib
import logging
import re
from pathlib import Path
from typing import Any, List, Optional, Set
from string import Template
from collections import defaultdict
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

logger = logging.getLogger(__name__)

class TaskGenerator:
    """
    Универсальный оркестратор для генерации задач подтипа (e.g., 'tires').
    Загружает данные, выбирает совместимые шаблоны, выполняет расчёты и регистрирует задачи в БД.
    """

    def __init__(self, subtype: str, session_maker: async_sessionmaker[AsyncSession]):
        """
        Инициализация генератора.

        Args:
            subtype: Название подтипа (e.g., 'tires').
            session_maker: Фабрика асинхронных сессий SQLAlchemy.
        """
        self.subtype = subtype
        self.session_maker = session_maker
        self.config = None
        self.intros: List[dict[str, Any]] = []
        self.conditions: List[dict[str, Any]] = []
        self.questions: dict[str, List[dict[str, Any]]] = {}
        self.lexemes: dict[str, dict[str, str]] = {}
        self.plot_files: List[Path] = []
        self.calculator = None
        self.table_renderer = None

        self._load_config()
        self._load_text_data()
        self._load_plots_list()
        self._initialize_specialists()
        logger.info(f"TaskGenerator для подтипа '{subtype}' инициализирован")

    def _load_config(self) -> None:
        """Динамически импортирует конфигурацию подтипа."""
        try:
            config_module_path = f"matunya_bot_final.task_generators.tasks_1_5.{self.subtype}.config"
            self.config = importlib.import_module(config_module_path)
            logger.info(f"Конфигурация '{config_module_path}' загружена")
        except ImportError as e:
            logger.error(f"Не удалось загрузить конфигурацию для подтипа '{self.subtype}': {e}")
            raise RuntimeError(f"Ошибка конфигурации: {e}")

    def _load_text_data(self) -> None:
        """Загружает текстовые данные из JSON-файлов."""
        try:
            for key, path in self.config.TEXT_FILES.items():
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if key == "intros":
                        self.intros = data if data else []
                    elif key == "conditions":
                        self.conditions = data if data else []
                    elif key == "questions":
                        self.questions = data if data else {}
                    elif key == "lexemes":
                        self.lexemes = data if data else {}
                logger.info(f"Загружены данные из {path}")

            if not self.intros:
                raise ValueError("Список вступлений пуст")
            if not self.conditions:
                raise ValueError("Список условий пуст")
            if not all(self.questions.get(q) for q in self.config.QUESTION_KEYS + self.config.Q5_ALTERNATIVES):
                raise ValueError("Не все типы вопросов найдены в questions.json")
        except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
            logger.error(f"Ошибка загрузки текстовых данных: {e}")
            raise RuntimeError(f"Ошибка загрузки текстовых данных: {e}")

    def _load_plots_list(self) -> None:
        """Загружает список доступных файлов плотов."""
        plots_dir = Path(self.config.PLOTS_DIR)
        if not plots_dir.exists():
            raise RuntimeError(f"Папка с плотами не найдена: {plots_dir}")

        self.plot_files = list(plots_dir.glob("*.json"))
        if not self.plot_files:
            raise RuntimeError(f"Не найдено файлов плотов в {plots_dir}")

        logger.info(f"Найдено {len(self.plot_files)} файлов плотов")

    def _initialize_specialists(self) -> None:
        """Динамически импортирует специалистов."""
        try:
            calc_path = self.config.SPECIALISTS["calculator_path"]
            calc_module_path, calc_class_name = calc_path.rsplit(".", 1)
            calc_module = importlib.import_module(calc_module_path)
            calc_class = getattr(calc_module, calc_class_name)
            self.calculator = calc_class()

            renderer_path = self.config.SPECIALISTS["renderer_path"]
            self.table_renderer = importlib.import_module(renderer_path)
            logger.info("Специалисты загружены")
        except (ImportError, AttributeError) as e:
            logger.error(f"Ошибка загрузки специалистов: {e}")
            raise RuntimeError(f"Ошибка загрузки специалистов: {e}")

    def _load_plot_data(self, plot_file: Path) -> dict[str, Any]:
        """Загружает данные из файла плота."""
        try:
            with open(plot_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Ошибка загрузки плота {plot_file}: {e}")
            raise RuntimeError(f"Ошибка загрузки плота: {e}")

    def _get_template_requirements(self, template_text: str) -> Set[str]:
        """Извлекает все плейсхолдеры из шаблона."""
        placeholders = re.findall(r'\$([a-zA-Z_][a-zA-Z0-9_]*)', template_text)
        return set(placeholders)

    def _analyze_plot_capabilities(self, plot_data: dict[str, Any]) -> dict[str, Set[str]]:
        """
        Анализирует доступные плейсхолдеры для каждого типа вопроса.
        """
        capabilities = {q: set() for q in self.config.QUESTION_KEYS + self.config.Q5_ALTERNATIVES}
        task_specific_data = plot_data.get("task_specific_data", {})
        base_marking = plot_data.get("base_tire_marking", {}).get("full_marking", "")

        for i, q_key in enumerate(self.config.QUESTION_KEYS + ["q5"], 1):
            task_key = f"task_{i}_data"
            if task_key in task_specific_data:
                task_data = task_specific_data[task_key]
                capabilities[q_key].update(["veh_acc", "veh_nom", "veh_gen"])
                if base_marking:
                    capabilities[q_key].add("base_marking")
                capabilities[q_key].update(task_data.keys())

        if "task_5_data" in task_specific_data:
            task_5_data = task_specific_data["task_5_data"]
            if "service_choice_data" in task_5_data:
                capabilities["q6"].update(["wheels_count", "service_ids", "veh_acc", "veh_nom", "veh_gen"])
                if base_marking:
                    capabilities["q6"].add("base_marking")

        return capabilities

    def _select_compatible_questions(self, plot_capabilities: dict[str, Set[str]], plot_data: dict[str, Any]) -> List[dict[str, Any]]:
        """
        Выбирает совместимые шаблоны вопросов с учетом типов данных.
        """
        selected = []
        task_specific_data = plot_data.get("task_specific_data", {})

        for q_type in self.config.QUESTION_KEYS:
            if not self.questions.get(q_type):
                logger.warning(f"Нет вопросов для типа {q_type}")
                selected.append({"type": q_type, "data": {"id": f"{q_type}_fallback", "text": "Ошибка: вопрос не найден"}})
                continue

            # Специальная логика для Q1 (V3.0 - "Финальное Уточнение")
            if q_type == "q1":
                task_1_data = task_specific_data.get("task_1_data", {})
                question_subtype = task_1_data.get("question_type")

                # ЖЕСТКО СВЯЗЫВАЕМ question_type С КОНКРЕТНЫМИ ID ШАБЛОНОВ
                if question_subtype == "minimum_width":
                    # Вопрос про НАИМЕНЬШУЮ ШИРИНУ
                    allowed_template_ids = {"tires_q1_01"}
                elif question_subtype == "minimum_diameter":
                     # Вопрос про НАИМЕНЬШИЙ ДИАМЕТР
                    allowed_template_ids = {"tires_q1_02"}
                elif question_subtype == "maximum_width":
                    # Вопрос про НАИБОЛЬШУЮ ШИРИНУ
                    allowed_template_ids = {"tires_q1_03"}
                elif question_subtype == "maximum_diameter":
                    # Вопрос про НАИБОЛЬШИЙ ДИАМЕТР
                    allowed_template_ids = {"tires_q1_04"}
                else:
                    # Аварийный случай, если тип не распознан
                    allowed_template_ids = set()

                suitable_templates = [t for t in self.questions.get(q_type, []) if t.get("id") in allowed_template_ids]

                if suitable_templates:
                    template = random.choice(suitable_templates) # random.choice из одного элемента вернет этот элемент
                else:
                    logger.warning(f"Не найден подходящий шаблон для q1 с типом '{question_subtype}'.")
                    template = self.questions.get(q_type, [{}])[0]

            # Специальная логика для Q2
            elif q_type == "q2":
                task_2_data = task_specific_data.get("task_2_data", {})
                if task_2_data.get("comparison_with_base") or task_2_data.get("comparison_type") == "base_comparison":
                    # Ищем шаблоны с {base_marking}
                    suitable_templates = [t for t in self.questions[q_type] if "{base_marking}" in t["text"]]
                else:
                    # Ищем шаблоны с {tire_1} и {tire_2}
                    suitable_templates = [t for t in self.questions[q_type] if "{tire_1}" in t["text"] and "{tire_2}" in t["text"]]

                template = random.choice(suitable_templates) if suitable_templates else self.questions[q_type][0]

            else:
                # Для остальных типов используем старую логику
                compatible_templates = [
                    t for t in self.questions[q_type]
                    if self._get_template_requirements(t["text"]).issubset(plot_capabilities.get(q_type, set()))
                ]
                template = random.choice(compatible_templates) if compatible_templates else self.questions[q_type][0]

            selected.append({"type": q_type, "data": template})

        # Остальной код для q5/q6 без изменений
        q5_type = random.choice(self.config.Q5_ALTERNATIVES)
        if not self.questions.get(q5_type):
            q5_type = "q5"

        compatible_templates = [
            t for t in self.questions.get(q5_type, [])
            if self._get_template_requirements(t["text"]).issubset(plot_capabilities.get(q5_type, set()))
        ]
        selected.append({
            "type": q5_type,
            "data": random.choice(compatible_templates) if compatible_templates else self.questions.get(q5_type, self.questions["q5"])[0]
        })

        logger.info(f"Выбраны вопросы: {[q['type'] for q in selected]}")
        return selected

    def _select_matching_condition(self, vehicle_id: str) -> dict[str, str]:
        """Выбирает подходящий condition в зависимости от типа автомобиля"""
        vehicle_mapping = {
            "car_crossover": ["tires_condition_08"],  # Кроссовер
            "car_sedan": ["tires_condition_10"],      # Городской седан
            "car_ev": ["tires_condition_11"],         # Электромобиль
            "car_hybrid": ["tires_condition_12"],     # Гибридная модификация
            "car_universal": ["tires_condition_13"],  # Универсал
            "car_minivan": ["tires_condition_15"]     # Минивэн
        }

        # Нейтральные conditions для остальных типов
        neutral_conditions = [
            "tires_condition_01", "tires_condition_02", "tires_condition_03",
            "tires_condition_04", "tires_condition_05", "tires_condition_06", "tires_condition_07"
        ]

        if vehicle_id in vehicle_mapping:
            condition_ids = vehicle_mapping[vehicle_id]
        else:
            condition_ids = neutral_conditions

        # Находим подходящий condition по id
        for condition in self.conditions:
            if condition["id"] in condition_ids:
                return condition

        # Fallback - любой первый condition
        return self.conditions[0] if self.conditions else {"id": "fallback", "text": "Ошибка: условие не найдено"}

    def _collect_available_tire_markings(self, plot_data: dict[str, Any]) -> List[str]:
        """Возвращает список всех доступных маркировок шин для текущего сюжета."""
        markings: Set[str] = set()

        allowed_sizes = plot_data.get("allowed_tire_sizes", {})
        if isinstance(allowed_sizes, dict):
            for diameter_map in allowed_sizes.values():
                if not isinstance(diameter_map, dict):
                    continue
                for diameter, variants in diameter_map.items():
                    if not isinstance(variants, list):
                        continue
                    for variant in variants:
                        if not isinstance(variant, str):
                            continue
                        candidate = variant.strip()
                        if not candidate:
                            continue
                        if "R" in candidate.upper():
                            full_marking = candidate
                        else:
                            full_marking = f"{candidate} R{diameter}".replace("  ", " ")
                        markings.add(full_marking.strip())

        base_marking = plot_data.get("base_tire_marking", {}).get("full_marking")
        if isinstance(base_marking, str) and base_marking.strip():
            markings.add(base_marking.strip())

        task_specific = plot_data.get("task_specific_data", {})
        if isinstance(task_specific, dict):
            for task_data in task_specific.values():
                if not isinstance(task_data, dict):
                    continue
                for value in task_data.values():
                    if isinstance(value, str) and "/" in value:
                        markings.add(value.strip())

        return sorted(markings)

    def _pick_alternative_tire(self, exclude: Set[str], pool: List[str]) -> Optional[str]:
        """Возвращает альтернативную маркировку шины, исключая переданные значения."""
        candidates = [marking for marking in pool if marking and marking not in exclude]
        if not candidates:
            return None
        return random.choice(candidates)

    def _ensure_unique_tire_variants(self, plot_data: dict[str, Any]) -> None:
        """Гарантирует, что пары шин для сравнений не совпадают между собой."""
        task_specific = plot_data.get("task_specific_data", {})
        if not isinstance(task_specific, dict):
            return

        available_markings = self._collect_available_tire_markings(plot_data)
        if not available_markings:
            return

        def _ensure_pair_difference(data: dict[str, Any], original_key: str, replacement_key: str) -> None:
            if not isinstance(data, dict):
                return
            original_value = data.get(original_key)
            replacement_value = data.get(replacement_key)
            if (
                isinstance(original_value, str)
                and isinstance(replacement_value, str)
                and original_value.strip()
                and replacement_value.strip()
                and original_value == replacement_value
            ):
                alternative = self._pick_alternative_tire({original_value}, available_markings)
                if alternative:
                    data[replacement_key] = alternative

        task_2 = task_specific.get("task_2_data")
        if task_2:
            _ensure_pair_difference(task_2, "tire_1", "tire_2")

        task_4 = task_specific.get("task_4_data")
        if task_4:
            _ensure_pair_difference(task_4, "original_tire", "replacement_tire")

        task_5 = task_specific.get("task_5_data")
        if task_5:
            _ensure_pair_difference(task_5, "original_tire", "replacement_tire")


    def _build_comprehensive_context(self, question_type: str, task_number: int, plot_data: dict[str, Any],
                                   lexemes: dict[str, str], base_context: dict[str, Any]) -> dict[str, Any]:
        """
        Создаёт исчерпывающий контекст для форматирования шаблона.
        Гарантирует наличие всех возможных плейсхолдеров.

        Args:
            question_type: Тип вопроса (q1-q6).
            task_number: Номер задачи (1-5).
            plot_data: Данные сюжета.
            lexemes: Выбранные лексемы.

        Returns:
            Полный словарь с контекстом для подстановки.
        """
        # Начинаем с пустого контекста - никаких defaultdict
        context = base_context.copy()

        # 1. Добавляем все лексемы
        context.update(lexemes)

        # 2. Добавляем veh_ префиксы для совместимости с шаблонами
        for key, value in lexemes.items():
            context[f"veh_{key}"] = value

        # 3. Общие данные из plot_data
        base_tire = plot_data.get("base_tire_marking", {})
        context["base_marking"] = base_tire.get("full_marking", "")

        # 4. Task-specific данные для текущего номера задачи
        task_data_key = f"task_{task_number}_data"
        task_specific_data = plot_data.get("task_specific_data", {})
        if task_data_key in task_specific_data:
            current_task_data = task_specific_data[task_data_key]
            context.update(current_task_data)

        # 5. Специфичные маппинги по типам вопросов
        if question_type == "q1":
            # Все возможные синонимы для q1
            if "target_diameter" in context:
                context["disk_in"] = context["target_diameter"]
            if "target_width" in context:
                context["width_mm"] = context["target_width"]
            # Дополнительные синонимы на всякий случай
            context.setdefault("disk_in", context.get("target_diameter", "16"))
            context.setdefault("width_mm", context.get("target_width", "205"))

        elif question_type == "q2":
            # Синонимы для шин
            if "tire_1" in context:
                context["tire_from"] = context["tire_1"]
            if "tire_2" in context:
                context["tire_to"] = context["tire_2"]
            # Заглушки если данных нет
            context.setdefault("tire_from", context.get("tire_1", context["base_marking"]))
            context.setdefault("tire_to", context.get("tire_2", context["base_marking"]))

        elif question_type == "q3":
            # Для q3 обычно используется base_marking
            context.setdefault("tire_marking", context["base_marking"])

        elif question_type in ["q4", "q5"]:
            # Синонимы для замены шин
            if "replacement_tire" in context:
                context["new_tire"] = context["replacement_tire"]
            context.setdefault("original_tire", context["base_marking"])
            context.setdefault("new_tire", context.get("replacement_tire", context["base_marking"]))

        elif question_type == "q6":
            # Данные для автосервисов
            service_data = task_specific_data.get("task_5_data", {}).get("service_choice_data", {})
            if service_data:
                context["wheels_count"] = service_data.get("wheels_count", 4)
                services = service_data.get("services", [])
                context["service_ids"] = ", ".join(str(s.get("name", "")) for s in services)
            else:
                context["wheels_count"] = 4
                context["service_ids"] = "A, B"

        # 6. Добавляем все данные из всех task_*_data на случай перекрестных ссылок
        for i in range(1, 7):
            other_task_key = f"task_{i}_data"
            if other_task_key in task_specific_data:
                other_data = task_specific_data[other_task_key]
                for key, value in other_data.items():
                    context.setdefault(key, value)

        # 7. Гарантированные значения для самых частых плейсхолдеров
        guaranteed_values = {
            "base_marking": context.get("base_marking", "205/55 R16"),
            "veh_acc": context.get("veh_acc", context.get("acc", "автомобиль")),
            "veh_gen": context.get("veh_gen", context.get("gen", "автомобиля")),
            "veh_nom": context.get("veh_nom", context.get("nom", "автомобиль")),
            "wheels_count": context.get("wheels_count", 4),
            "disk_in": context.get("disk_in", "16"),
            "width_mm": context.get("width_mm", "205")
        }

        for key, fallback_value in guaranteed_values.items():
            context.setdefault(key, fallback_value)

        logger.info(f"DEBUG: Полный контекст для {question_type}: {dict(context)}")
        return context

    def _safe_format_template(self, template: str, context: dict[str, Any]) -> str:
        """
        Безопасно форматирует шаблон с гарантированной подстановкой.

        Args:
            template: Шаблон с плейсхолдерами.
            context: Контекст для подстановки.

        Returns:
            Отформатированная строка без пустых плейсхолдеров.
        """
        try:
            # Поддерживаем оба формата: {variable} и $variable
            if '{' in template and '}' in template:
                # Используем format_map для безопасной подстановки
                class SafeDict(dict):
                    def __missing__(self, key):
                        return f"[ОТСУТСТВУЕТ:{key}]"

                safe_context = SafeDict(context)
                result = template.format_map(safe_context)
            else:
                # Формат $variable
                result = Template(template).safe_substitute(context)

            logger.info(f"DEBUG: Результат форматирования: {result}")
            return result

        except Exception as e:
            logger.error(f"Критическая ошибка форматирования шаблона: {template}, ошибка: {e}")
            # Возвращаем шаблон как есть в крайнем случае
            return template

    def _generate_html_tables(self, plot_data: dict[str, Any], q5_type: str) -> dict[str, Optional[str]]:
        """
        Генерирует HTML-таблицы для Q1 и Q6 (если выбрано).
        """
        tables = {"tire_sizes": None, "service_costs": None}
        allowed_sizes = plot_data.get("allowed_tire_sizes", {})
        if allowed_sizes:
            tables["tire_sizes"] = self.table_renderer.render_tire_sizes_table(allowed_sizes)

        if q5_type == "q6":
            service_data = plot_data.get("task_specific_data", {}).get("task_5_data", {}).get("service_choice_data", {})
            if service_data:
                services_formatted = [
                    {
                        "id": s.get("name", ""),
                        "title": f"Автосервис {s.get('name', '')}",
                        "road_cost": s.get("road_cost", 0),
                        "ops": {
                            "remove": s.get("operations", {}).get("removal", 0),
                            "mount": s.get("operations", {}).get("tire_change", 0),
                            "balance": s.get("operations", {}).get("balancing", 0),
                            "install": s.get("operations", {}).get("installation", 0)
                        }
                    } for s in service_data.get("services", [])
                ]
                tables["service_costs"] = self.table_renderer.render_service_costs_table({
                    "services": services_formatted,
                    "currency": "руб.",
                    "wheels_count": service_data.get("wheels_count", 4)
                })

        return tables

    async def generate_task_package(self) -> dict[str, Any]:
        """
        Главный метод: генерирует task_package и регистрирует задачи в БД.

        Returns:
            Словарь с task_package, включая db_task_ids.
        """
        try:
            # --- НАШ ГЛАВНЫЙ ШПИОН ---
            print("🕵️‍♂️ ГЛАВНЫЙ ШПИОН: ЗАШЕЛ В generate_task_package")
            # ---------------------------

            # Выбор компонентов
            plot_file = random.choice(self.plot_files)
            plot_data = self._load_plot_data(plot_file)
            self._ensure_unique_tire_variants(plot_data)
            vehicle_id = plot_data.get("vehicle_id", "car_any")
            lexemes = self.lexemes.get(vehicle_id, self.lexemes.get("car_any", {}))

            # --- НАША НОВАЯ, ЕДИНСТВЕННАЯ ПРАВКА ---
            # Создаем базовый контекст, который будет ЕДИНЫМ для всех.
            base_context = lexemes.copy()
            for key, value in lexemes.items():
                base_context[f"veh_{key}"] = value
            base_tire = plot_data.get("base_tire_marking", {})
            base_context["base_marking"] = base_tire.get("full_marking", "")
            # ----------------------------------------

            plot_capabilities = self._analyze_plot_capabilities(plot_data)
            selected_questions = self._select_compatible_questions(plot_capabilities, plot_data)

            # Расчёты
            answers = self.calculator.calculate_all_tasks(plot_data)

            # Таблицы
            q5_type = selected_questions[-1]["type"]
            html_tables = self._generate_html_tables(plot_data, q5_type)

            # Сценарий отображения
            display_scenario = self.config.IMAGES.copy()

            # Используем ЕДИНЫЙ базовый контекст для intro и condition
            intro_text = self._safe_format_template(random.choice(self.intros)["text"], base_context)
            display_scenario.append({"type": "text", "content": bold_numbers(intro_text)})

            condition_template = self._select_matching_condition(vehicle_id)
            condition_text = self._safe_format_template(condition_template["text"], base_context)
            display_scenario.append({"type": "text", "content": bold_numbers(condition_text)})

            # НОВАЯ УЛУЧШЕННАЯ СБОРКА ЗАДАЧ
            tasks = []
            db_task_ids: list[Optional[int]] = []

            async with self.session_maker() as session:
                for i, q_info in enumerate(selected_questions):
                    q_type = q_info["type"]
                    q_data = q_info["data"]
                    task_number = i + 1

                    # 1. Создаем НОВЫЙ, полный контекст для каждой задачи
                    comprehensive_context = self._build_comprehensive_context(
                        q_type, task_number, plot_data, lexemes, base_context=base_context
                    )

                    # 2. Безопасно форматируем текст
                    text = self._safe_format_template(q_data["text"], comprehensive_context)
                    text = bold_numbers(text)

                    # 3. Определяем HTML таблицу
                    html_table = None
                    if i == 0:  # Первая задача
                        html_table = html_tables["tire_sizes"]
                    elif i == 4 and q_type == "q6":  # Пятая задача и тип q6
                        html_table = html_tables["service_costs"]

                    # 4. Получаем правильный ответ
                    answer_key = f"task_{task_number}_answer" if q_type != "q6" else "task_6_answer"
                    answer = str(answers.get(answer_key, "0"))

                    # 5. Собираем финальный объект задачи
                    task = {
                        "skill_source_id": q_data["id"],
                        "text": text,
                        "answer": answer,
                        "html_table": html_table
                    }
                    tasks.append(task)

                    # 6. Регистрация в БД
                    task_id = await register_task(session, q_data["id"], text, answer)
                    if task_id is not None:
                        db_task_ids.append(task_id)
                    else:
                        logger.warning(f"Задача {i+1} не зарегистрирована в БД (task_id is None)")
                        db_task_ids.append(None)

            task_package = {
                "subtype": self.subtype,
                "display_scenario": display_scenario,
                "tasks": tasks,
                "db_task_ids": db_task_ids,
                "plot_data": plot_data,
                "metadata": self.config.DEFAULT_METADATA.copy()
            }

            logger.info(f"Task_package сгенерирован: {len(tasks)} задач, {len(db_task_ids)} ID в БД")
            return task_package

        except Exception as e:
            logger.error(f"Ошибка генерации task_package: {e}", exc_info=True)
            raise RuntimeError(f"Ошибка генерации: {e}")

# Добавьте эти функции в конец файла generator.py

async def register_task(session: AsyncSession, skill_source_id: str, text: str, answer: str) -> Optional[int]:
    """
    Регистрирует задачу в БД и возвращает её ID.

    Args:
        session: Асинхронная сессия SQLAlchemy
        skill_source_id: ID источника навыка
        text: Текст задачи
        answer: Правильный ответ

    Returns:
        ID зарегистрированной задачи или None при ошибке
    """
    try:
        task_id = await db_manager.register_task(
            session=session,
            skill_source_id=skill_source_id,
            text=text,
            answer=answer
        )
        return task_id
    except Exception as e:
        logger.error(f"Ошибка регистрации задачи в БД: {e}")
        return None


async def generate_task(subtype: str, session_maker: async_sessionmaker[AsyncSession],
                       question_type: Optional[str] = None) -> dict[str, Any]:
    """
    Основная функция генерации задач для подтипа.

    Args:
        subtype: Название подтипа (например, 'tires')
        session_maker: Фабрика асинхронных сессий SQLAlchemy
        question_type: Опциональный тип вопроса для фильтрации

    Returns:
        Словарь с task_package
    """
    try:
        generator = TaskGenerator(subtype, session_maker)
        task_package = await generator.generate_task_package()

        # Фильтрация по типу вопроса, если указан
        if question_type:
            filtered_tasks = []
            filtered_db_ids = []
            for i, task in enumerate(task_package["tasks"]):
                filtered_tasks.append(task)
                filtered_db_ids.append(task_package["db_task_ids"][i])

            task_package["tasks"] = filtered_tasks
            task_package["db_task_ids"] = filtered_db_ids

        return task_package

    except Exception as e:
        logger.error(f"Ошибка в generate_task для подтипа '{subtype}': {e}")
        raise


def generate_task_sync(subtype: str, question_type: Optional[str] = None) -> dict[str, Any]:
    """
    Синхронная версия generate_task для обратной совместимости.

    ВНИМАНИЕ: Эта функция создает свой event loop и может конфликтовать
    с существующим async кодом. Используйте async версию когда возможно.
    """
    import asyncio
    from matunya_bot_final.utils.db_manager import get_session_maker

    try:
        session_maker = get_session_maker()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(generate_task(subtype, session_maker, question_type))
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"Ошибка в синхронной обертке generate_task: {e}")
        raise
