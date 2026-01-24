import re
from typing import Dict, Any, Tuple, List, Optional

class CentralAndInscribedAnglesValidator:
    """
    Валидатор для Темы 1: Центральные и вписанные углы.
    Соответствует стандарту ГОСТ-ВАЛИДАТОР-2026.

    UPD: Использует task_context вместо solution_vars.
    """

    def __init__(self):
        # ИСПРАВЛЕННАЯ РЕГУЛЯРКА:
        # (?!(?:\bугол\b|∠)) — теперь мы игнорируем "угол" только если это ОТДЕЛЬНОЕ слово.
        # Слова "треугольник", "многоугольник" больше не ломают поиск!

        self.angle_regex = re.compile(
            r"(?:угол|∠)\s*([A-Z]{1,3})(?:(?!(?:\bугол\b|∠)).)*?(?:равен|=)\s*(\d+(?:[.,]\d+)?)",
            re.IGNORECASE | re.DOTALL
        )

        self.find_regex = re.compile(r"(?:найди(?:те)?|чему\s+равен|определи).*?(?:угол|∠)\s*([A-Z]{1,3})", re.IGNORECASE)

    def validate(self, task: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        pattern = task.get("pattern")

        # Гарантируем наличие ID
        if "id" not in task:
            task["id"] = None

        if not pattern:
            errors.append("В задаче отсутствует ключ 'pattern'.")
            return False, errors

        is_valid = False

        if pattern == "cyclic_quad_angles":
            is_valid, errors = self._validate_cyclic_quad_angles(task)
        elif pattern == "central_inscribed":
            is_valid, errors = self._validate_central_inscribed(task)
        elif pattern == "radius_chord_angles":
            is_valid, errors = self._validate_radius_chord_angles(task)
        elif pattern == "arc_length_ratio":
            is_valid, errors = self._validate_arc_length_ratio(task)
        elif pattern == "diameter_right_triangle":
            is_valid, errors = self._validate_diameter_right_triangle(task)
        elif pattern == "two_diameters_angles":
            is_valid, errors = self._validate_two_diameters_angles(task)
        else:
            errors.append(f"Неизвестный паттерн: {pattern}")
            return False, errors

        if is_valid:
            self._reorder_task_keys(task)

        return is_valid, errors

    def _reorder_task_keys(self, task: Dict[str, Any]) -> None:
        """
        Устанавливает порядок ключей: id -> pattern -> narrative -> text -> answer -> images -> context
        """
        temp = task.copy()
        task.clear()

        ordered_keys = [
            "id",
            "pattern",
            "narrative",
            "question_text",
            "answer",
            "image_file",
            "help_image_file",
            "task_context" # Новое имя
        ]

        for key in ordered_keys:
            if key in temp:
                task[key] = temp[key]

        for key, val in temp.items():
            if key not in task:
                task[key] = val

    # =========================================================================
    # ПАТТЕРН 1.1: cyclic_quad_angles
    # =========================================================================

    def _validate_cyclic_quad_angles(self, task: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        text = task.get("question_text", "")
        narrative = task.get("narrative")
        answer = task.get("answer") # Может быть -1 при отладке

        # 1. Парсинг
        angles_found = [(m.group(1).upper(), int(m.group(2))) for m in self.angle_regex.finditer(text)]
        target_match = self.find_regex.search(text)
        target_angle_name = target_match.group(1).upper() if target_match else None

        if not angles_found or not target_angle_name:
            errors.append(f"Не удалось распарсить углы или вопрос. Найдено углов: {len(angles_found)}, Цель: {target_angle_name}")
            return False, errors

        # 2. Фигура
        figure_name = "KLMN" if set("KLM").intersection(set(text.upper())) else "ABCD"

        task_context = {}
        task_image = None
        help_image = None

        # Переменная для хранения вычисленного ответа
        final_calc_answer = None

        try:
            if narrative == "find_opposite_angle":
                if len(angles_found) != 1:
                    errors.append(f"Для {narrative} нужен 1 угол, найдено {len(angles_found)}.")
                    return False, errors

                given_angle, given_value = angles_found[0]
                final_calc_answer = 180 - given_value

                version = self._get_simple_image_version(given_angle, given_value, figure_name)
                task_image = f"task_cyclic_quad_angles_{figure_name.lower()}_simple_{version}.png"
                help_image = None

                task_context = {
                    "narrative_type": "opposite_sum",
                    "angle_given_name": given_angle,
                    "angle_given_val": given_value,
                    "angle_target_name": target_angle_name
                }

            elif narrative == "same_arc_angles":
                if len(angles_found) != 2:
                    errors.append(f"Для {narrative} нужно 2 угла, найдено {len(angles_found)}.")
                    return False, errors

                arc_data = self._identify_arc_and_roles(target_angle_name, angles_found[0][0], angles_found[1][0], figure_name)
                if not arc_data:
                    errors.append("Не удалось определить дугу/роли.")
                    return False, errors

                if arc_data["role_1"] == "alien":
                    alien_data = angles_found[0]
                    known_part_data = angles_found[1]
                else:
                    alien_data = angles_found[1]
                    known_part_data = angles_found[0]

                final_calc_answer = alien_data[1] + known_part_data[1]

                task_image = f"task_cyclic_quad_angles_{figure_name.lower()}_diags.png"
                help_image = f"help_cyclic_quad_angles_{figure_name.lower()}_diags_arc_{arc_data['arc']}.png"

                task_context = {
                    "narrative_type": "part_sum",
                    "angle_whole_name": target_angle_name,
                    "angle_known_part_name": known_part_data[0],
                    "angle_known_part_val": known_part_data[1],
                    "angle_alien_name": alien_data[0],
                    "angle_alien_val": alien_data[1],
                    "angle_hidden_part_name": arc_data["hidden_part_name"],
                    "arc_name": arc_data["arc"].upper()
                }

            elif narrative == "find_diagonal_angle_abd":
                if len(angles_found) != 2:
                    errors.append("Нужно 2 известных угла.")
                    return False, errors

                sorted_angles = sorted(angles_found, key=lambda x: x[1], reverse=True)
                whole_angle = sorted_angles[0]
                alien_angle = sorted_angles[1]

                final_calc_answer = whole_angle[1] - alien_angle[1]

                parasite_name = self._get_parasite_name(whole_angle[0], target_angle_name)
                arc_name = self._get_arc_by_small_angles(parasite_name, alien_angle[0], figure_name)

                if not arc_name:
                    errors.append(f"Не удалось определить дугу.")
                    return False, errors

                task_image = f"task_cyclic_quad_angles_{figure_name.lower()}_diags.png"
                help_image = f"help_cyclic_quad_angles_{figure_name.lower()}_diags_arc_{arc_name}.png"

                task_context = {
                    "narrative_type": "part_diff",
                    "angle_target_name": target_angle_name,
                    "angle_whole_name": whole_angle[0],
                    "angle_whole_val": whole_angle[1],
                    "angle_alien_name": alien_angle[0],
                    "angle_alien_val": alien_angle[1],
                    "angle_parasite_name": parasite_name,
                    "arc_name": arc_name.upper()
                }

            # --- ПРОВЕРКА ОТВЕТА ---
            # Если в задаче есть ответ (и он не фейковый -1), проверяем его
            if answer is not None and int(answer) != -1:
                if final_calc_answer != int(answer):
                    errors.append(f"Математическая ошибка: {final_calc_answer} != {answer}")

            # --- ВАЖНО: ЗАПИСЫВАЕМ ПРАВИЛЬНЫЙ ОТВЕТ ---
            # Валидатор всегда обновляет поле answer правильным значением
            task["answer"] = final_calc_answer

        except Exception as e:
            errors.append(f"Exception: {str(e)}")
            return False, errors

        task["image_file"] = task_image
        task["help_image_file"] = help_image
        task["task_context"] = task_context # Переименовали

        return len(errors) == 0, errors

    # =========================================================================
    # ПАТТЕРН 1.2: central_inscribed
    # =========================================================================

    def _validate_central_inscribed(self, task: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []

        text = task.get("question_text", "")
        raw_narrative = task.get("narrative")
        answer = task.get("answer")

        # ------------------------------------------------------------------
        # 1. Маппинг нарративов (16 → 2 логики)
        # ------------------------------------------------------------------
        NARRATIVE_MAP = {
            # central → inscribed
            "central_acute_inner_aoc_to_abc": "find_inscribed_by_central",
            "central_acute_outer_aoc_to_abc": "find_inscribed_by_central",
            "central_obtuse_inner_aoc_to_abc": "find_inscribed_by_central",
            "central_obtuse_outer_aoc_to_abc": "find_inscribed_by_central",
            "central_acute_inner_dof_to_def": "find_inscribed_by_central",
            "central_acute_outer_dof_to_def": "find_inscribed_by_central",
            "central_obtuse_inner_dof_to_def": "find_inscribed_by_central",
            "central_obtuse_outer_dof_to_def": "find_inscribed_by_central",

            # inscribed → central
            "central_acute_inner_abc_to_aoc": "find_central_by_inscribed",
            "central_acute_outer_abc_to_aoc": "find_central_by_inscribed",
            "central_obtuse_inner_abc_to_aoc": "find_central_by_inscribed",
            "central_obtuse_outer_abc_to_aoc": "find_central_by_inscribed",
            "central_acute_inner_def_to_dof": "find_central_by_inscribed",
            "central_acute_outer_def_to_dof": "find_central_by_inscribed",
            "central_obtuse_inner_def_to_dof": "find_central_by_inscribed",
            "central_obtuse_outer_def_to_dof": "find_central_by_inscribed",
        }

        logic_type = NARRATIVE_MAP.get(raw_narrative)
        if not logic_type:
            return False, [f"Неизвестный нарратив: {raw_narrative}"]

        # ------------------------------------------------------------------
        # 2. ИСКОМЫЙ угол — СТРОГО из raw_narrative (канон)
        # ------------------------------------------------------------------
        parts = raw_narrative.split("_")
        target_angle_name = parts[-1].upper() # abc, aoc, def, dof

        # ------------------------------------------------------------------
        # 3. Парсим ИЗВЕСТНЫЙ угол (строго по логике нарратива)
        # ------------------------------------------------------------------
        angles_found = []
        for m in self.angle_regex.finditer(text):
            name = m.group(1).upper()
            val_str = m.group(2).replace(',', '.')
            try:
                val = float(val_str)
                if val.is_integer(): val = int(val)
                angles_found.append((name, val))
            except ValueError:
                continue

        if not angles_found:
            return False, ["Не найдено ни одного угла с числовым значением"]

        known_angle_name = None
        known_angle_val = None

        # Ищем первый подходящий угол
        for name, val in angles_found:
            # Если ищем вписанный -> нам нужен угол с 'O' (центральный)
            if logic_type == "find_inscribed_by_central" and "O" in name:
                known_angle_name = name
                known_angle_val = val
                break
            # Если ищем центральный -> нам нужен угол БЕЗ 'O' (вписанный)
            if logic_type == "find_central_by_inscribed" and "O" not in name:
                known_angle_name = name
                known_angle_val = val
                break

        if known_angle_name is None:
            return False, [
                f"Не удалось найти подходящий известный угол для логики '{logic_type}'. Кандидаты: {angles_found}"
            ]

        # ------------------------------------------------------------------
        # 4. Защита от логических ошибок
        # ------------------------------------------------------------------
        if known_angle_name == target_angle_name:
            return False, [
                f"Ошибка: Известный и искомый углы совпадают ({known_angle_name}). Проверь текст задачи."
            ]

        # ------------------------------------------------------------------
        # 5. Математика и Имена
        # ------------------------------------------------------------------
        if logic_type == "find_inscribed_by_central":
            # Дано: Центр. Найти: Вписанный.
            angle_central_name = known_angle_name
            angle_central_val = known_angle_val
            angle_inscribed_name = target_angle_name
            angle_inscribed_val = angle_central_val / 2
        else:
            # Дано: Вписанный. Найти: Центр.
            angle_inscribed_name = known_angle_name
            angle_inscribed_val = known_angle_val
            angle_central_name = target_angle_name
            angle_central_val = angle_inscribed_val * 2

        calc_answer = angle_inscribed_val if logic_type == "find_inscribed_by_central" else angle_central_val

        # Форматирование ответа (int/float)
        if isinstance(calc_answer, float) and calc_answer.is_integer():
            calc_answer = int(calc_answer)

        # Обновляем значения в переменных (если они были float, стали int)
        if logic_type == "find_inscribed_by_central":
             angle_inscribed_val = calc_answer
        else:
             angle_central_val = calc_answer

        # ------------------------------------------------------------------
        # 6. Дуга (по центральному углу приоритетно, так надежнее)
        # ------------------------------------------------------------------
        # Из AOC -> AC. Из DOF -> DF.
        p1 = angle_central_name[0]
        p2 = angle_central_name[2] # Третья буква
        arc_name = "".join(sorted([p1, p2]))

        # ------------------------------------------------------------------
        # 7. Финальный task_context
        # ------------------------------------------------------------------
        # Определяем фигуру для картинки (abc или def)
        # Надежнее всего смотреть на буквы в target_angle_name
        is_abc = "A" in target_angle_name or "B" in target_angle_name or "C" in target_angle_name
        figure = "abc" if is_abc else "def"

        # Нарратив уже содержит тип геометрии (acute_inner и т.д.)
        # parts = [central, acute, inner, ...]
        geo_type = parts[1]
        geo_loc = parts[2]

        img_name = f"central_inscribed_{geo_type}_{geo_loc}_{figure}"

        task["image_file"] = f"task_{img_name}.png"
        task["help_image_file"] = f"help_{img_name}.png"

        task["task_context"] = {
            "narrative_type": raw_narrative, # Длинное имя для дебага
            "angle_central_name": angle_central_name,
            "angle_central_val": angle_central_val,
            "angle_inscribed_name": angle_inscribed_name,
            "angle_inscribed_val": angle_inscribed_val,
            "arc_name": arc_name,
        }

        task["answer"] = calc_answer
        task["narrative"] = logic_type # Короткое имя для Решателя

        # ------------------------------------------------------------------
        # 8. Проверка ответа
        # ------------------------------------------------------------------
        if answer is not None and int(answer) != -1:
            if abs(float(answer) - float(calc_answer)) > 0.01:
                return False, [f"Математическая ошибка: {answer} != {calc_answer}"]

        return True, []

    # =========================================================================
    # ПАТТЕРН 1.3: radius_chord_angles
    # =========================================================================

    def _validate_radius_chord_angles(self, task: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        text = task.get("question_text", "")
        raw_narrative = task.get("narrative")
        answer = task.get("answer")

        # ------------------------------------------------------------------
        # 1. Маппинг нарративов (8 длинных → 2 логических)
        # ------------------------------------------------------------------
        NARRATIVE_MAP = {
            # --- Ищем ЧАСТЬ (вычитание) ---
            "radius_chord_acute_abc_find_part": "find_part_angle",
            "radius_chord_obtuse_abc_find_part": "find_part_angle",
            "radius_chord_acute_mnk_find_part": "find_part_angle",
            "radius_chord_obtuse_mnk_find_part": "find_part_angle",

            # --- Ищем ЦЕЛОЕ (сложение) ---
            "radius_chord_acute_abc_find_whole": "find_whole_angle",
            "radius_chord_obtuse_abc_find_whole": "find_whole_angle",
            "radius_chord_acute_mnk_find_whole": "find_whole_angle",
            "radius_chord_obtuse_mnk_find_whole": "find_whole_angle",
        }

        logic_mode = NARRATIVE_MAP.get(raw_narrative)
        if not logic_mode:
            errors.append(f"Неизвестный или некорректный нарратив: {raw_narrative}")
            return False, errors

        # ------------------------------------------------------------------
        # 2. Парсинг известных углов
        # ------------------------------------------------------------------
        angles_found = []
        for m in self.angle_regex.finditer(text):
            name = m.group(1).upper()
            val_str = m.group(2).replace(',', '.')
            try:
                val = float(val_str)
                if val.is_integer(): val = int(val)
                angles_found.append((name, val))
            except ValueError:
                continue

        if len(angles_found) != 2:
            errors.append(f"Ожидалось 2 известных угла, найдено {len(angles_found)}: {angles_found}")
            return False, errors

        # 3. Парсинг искомого угла
        target_match = self.find_regex.search(text)
        target_name = target_match.group(1).upper() if target_match else "???"

        try:
            # 4. Выбор КАРТИНКИ (по частям длинного нарратива)
            parts = raw_narrative.split("_")
            # Ожидаем формат: radius_chord_[GEO]_[FIG]_[LOGIC]_[MODE]
            # parts: [0]radius, [1]chord, [2]acute, [3]abc, ...

            geo_type = parts[2]  # acute / obtuse
            fig_type = parts[3]  # abc / mnk

            img_name = f"radius_chord_{geo_type}_{fig_type}"
            task_image = f"task_{img_name}.png"
            help_image = f"help_{img_name}.png"

            # 5. Логика распределения ролей (Целое vs Часть)
            task_context = {}
            calc_answer = 0

            # Сортировка: угол С буквой 'O' -> Part, угол БЕЗ буквы 'O' -> Whole
            parts_found = []
            whole_found = []

            for ang in angles_found:
                if "O" in ang[0]:
                    parts_found.append(ang)
                else:
                    whole_found.append(ang)

            # --- ВЕТКА 1: ИЩЕМ ЧАСТЬ (Вычитание) ---
            if logic_mode == "find_part_angle":
                if len(whole_found) != 1 or len(parts_found) != 1:
                    errors.append(f"Для find_part нужны 1 Целый угол и 1 Часть. Найдено: Whole={whole_found}, Parts={parts_found}")
                    return False, errors

                whole = whole_found[0]
                known_part = parts_found[0]

                calc_answer = whole[1] - known_part[1]

                if calc_answer <= 0:
                    errors.append(f"Ошибка: Отрицательный или нулевой ответ ({calc_answer}). Проверь числа.")

                task_context = {
                    "narrative_type": raw_narrative, # Длинное имя для отладки
                    "angle_whole_name": whole[0],
                    "angle_whole_val": whole[1],
                    "angle_known_part_name": known_part[0],
                    "angle_known_part_val": known_part[1],
                    "angle_target_name": target_name,
                    # fig_type нужен хьюмонайзеру, чтобы определить вершину B/N если имена сложные
                    "fig_type": fig_type
                }

            # --- ВЕТКА 2: ИЩЕМ ЦЕЛОЕ (Сложение) ---
            elif logic_mode == "find_whole_angle":
                if len(parts_found) != 2:
                    errors.append(f"Для find_whole нужны 2 Части (с буквой O). Найдено: {parts_found}")
                    return False, errors

                part1 = parts_found[0]
                part2 = parts_found[1]

                calc_answer = part1[1] + part2[1]

                task_context = {
                    "narrative_type": raw_narrative,
                    "angle_part1_name": part1[0],
                    "angle_part1_val": part1[1],
                    "angle_part2_name": part2[0],
                    "angle_part2_val": part2[1],
                    "angle_target_name": target_name,
                    # ДОБАВЛЕНО: Явное указание на Целое (для симметрии архитектуры)
                    "angle_whole_name": target_name,
                    "fig_type": fig_type
                }

            # 6. Проверка ответа
            if answer is not None and int(answer) != -1:
                if abs(float(calc_answer) - float(answer)) > 0.01:
                    errors.append(f"Математическая ошибка: {calc_answer} != {answer}")

            # 7. Финализация
            task["image_file"] = task_image
            task["help_image_file"] = help_image
            task["task_context"] = task_context
            task["narrative"] = logic_mode # Короткое имя для Решателя
            task["answer"] = calc_answer

        except Exception as e:
            errors.append(f"Ошибка логики валидатора 1.3: {e}")
            return False, errors

        return True, errors

    # =========================================================================
    # ПАТТЕРН 1.4: arc_length_ratio
    # =========================================================================

    def _validate_arc_length_ratio(self, task: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        text = task.get("question_text", "")
        narrative = task.get("narrative")
        answer = task.get("answer")

        # 1. Парсинг (Локальные Regex)
        # Ищем угол: "∠DOF=21"
        match_angle = re.search(r"∠\s*([A-Z])([A-Z])([A-Z])\s*=\s*(\d+)", text)
        # Ищем длину: "равна 35"
        match_len = re.search(r"равна\s+(\d+)", text)

        if not match_angle or not match_len:
            errors.append("Не удалось распарсить угол (∠...=) или длину дуги (равна X).")
            return False, errors

        # Извлекаем точки: D, O, F из ∠DOF
        point_1 = match_angle.group(1) # D
        center = match_angle.group(2)  # O
        point_2 = match_angle.group(3) # F

        angle_val = int(match_angle.group(4))
        len_val = int(match_len.group(1))

        final_calc_answer = None
        task_context = {}
        task_image = None
        help_image = None # ⚠️ ВАЖНО: null, а не пустая строка

        try:
            if narrative == "small_to_large_arc":
                # Логическая проверка
                if angle_val <= 0 or angle_val >= 360:
                    errors.append(f"Некорректный угол: {angle_val}")
                    return False, errors

                # Математика
                large_arc_angle = 360 - angle_val

                # Расчет ответа
                val_float = len_val * (large_arc_angle / angle_val)

                if abs(val_float - round(val_float)) > 1e-9:
                    errors.append(f"Ответ не целый: {val_float}")
                    return False, errors

                final_calc_answer = int(round(val_float))

                # Картинка и Тип
                suffix = "acute" if angle_val < 90 else "obtuse"
                task_image = f"task_arc_length_ratio_{suffix}.png"

                # ⚠️ ВАЖНО: Чистый контекст без лишнего мусора
                task_context = {
                    "narrative_type": f"arc_length_ratio_{narrative}_{suffix}", # уточнение типа для аналитики
                    "center": center,
                    "arc_name": f"{point_1}{point_2}", # DF
                    "small_arc_length": len_val,
                    "small_arc_angle": angle_val,
                    "large_arc_angle": large_arc_angle
                }

            else:
                errors.append(f"Неизвестный нарратив: {narrative}")
                return False, errors

            # Проверка ответа
            if answer is not None and str(answer).strip() != "" and int(answer) != -1:
                if final_calc_answer != int(answer):
                    errors.append(f"Математическая ошибка: Расчет {final_calc_answer} != Вход {answer}")

            task["answer"] = final_calc_answer

        except Exception as e:
            errors.append(f"Exception: {str(e)}")
            return False, errors

        task["image_file"] = task_image
        task["help_image_file"] = help_image # Теперь здесь точно None
        task["task_context"] = task_context

        return len(errors) == 0, errors


    # =========================================================================
    # ПАТТЕРН 1.5: diameter_right_triangle
    # =========================================================================

    def _validate_diameter_right_triangle(self, task: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        text = task.get("question_text", "")
        narrative = task.get("narrative")
        answer = task.get("answer")

        # 1. Парсинг (Regex)

        # Ищем сторону, на которой лежит центр (Гипотенуза): "лежит на стороне AC"
        match_hypot = re.search(r"на стороне\s+([A-Z]{2})", text)

        # Ищем радиус: "Радиус OA равен 5" или "Радиус окружности равен 13"
        # Группы: 1=(OA|окружности), 2=Значение (может быть float 25.5)
        match_radius = re.search(r"Радиус\s+([A-Z]{2}|окружности).*?равен\s+(\d+(?:\.\d+)?)", text)

        # Ищем вопрос и условие: "Найдите AB, если BC = 24"
        # Группы: 1=Найти(AB), 2=Дано(BC), 3=Значение
        match_query = re.search(r"Найди(?:те)?\s+([A-Z]{2}).*?если\s+([A-Z]{2})\s*=\s*(\d+)", text)

        if not (match_hypot and match_radius and match_query):
            errors.append("Не удалось распарсить условие (сторона, радиус или вопрос).")
            return False, errors

        # Извлекаем данные из Regex
        diameter_side = match_hypot.group(1) # Например, AC

        radius_name_raw = match_radius.group(1)
        radius_val = float(match_radius.group(2)) # 13.0 или 25.5

        target_leg = match_query.group(1) # AB
        known_leg = match_query.group(2)  # BC
        known_leg_val = int(match_query.group(3)) # 24

        # Определяем точку радиуса для контекста
        # Если "OA" -> берем "A". Если "окружности" -> берем первую букву диаметра (fallback)
        if len(radius_name_raw) == 2 and "O" in radius_name_raw:
             radius_point = radius_name_raw.replace("O", "")
        else:
             radius_point = diameter_side[0]

        # Определяем вершину прямого угла
        # Это та буква треугольника, которой нет в названии диаметра.
        # (Если диаметр AC, а треугольник ABC, то вершина B).
        all_points = set(diameter_side + known_leg + target_leg)
        right_angle_vertex = list(all_points - set(diameter_side))
        right_angle_vertex = right_angle_vertex[0] if right_angle_vertex else "B"

        triangle_name = "".join(sorted(list(all_points))) # ABC

        final_calc_answer = None
        task_context = {}

        try:
            if narrative == "center_on_side":
                # Математика: b = sqrt((2R)^2 - a^2)
                diameter_val = 2 * radius_val

                # Геометрическая проверка (Гипотенуза > Катета)
                if diameter_val <= known_leg_val:
                    errors.append(f"Геометрическая ошибка: Диаметр ({diameter_val}) <= Катета ({known_leg_val})")
                    return False, errors

                hyp_sq = diameter_val ** 2
                leg_sq = known_leg_val ** 2

                res_sq = hyp_sq - leg_sq
                res = res_sq ** 0.5

                # Проверка на целочисленность (ОГЭ)
                if abs(res - round(res)) > 1e-9:
                    errors.append(f"Ответ не целый: {res}. Проверь входные данные (Пифагоровы тройки).")
                    return False, errors

                final_calc_answer = int(round(res))

                # Сборка эталонного контекста
                task_context = {
                    "narrative_type": "center_on_side",

                    "triangle": triangle_name,
                    "center": "O",
                    "diameter_side": diameter_side,

                    "radius_point": radius_point,
                    "radius_value": int(radius_val) if radius_val.is_integer() else radius_val,

                    "right_angle_vertex": right_angle_vertex,

                    "known_leg_name": known_leg,
                    "known_leg_value": known_leg_val,

                    "target_leg_name": target_leg
                }
            else:
                errors.append(f"Неизвестный нарратив: {narrative}")
                return False, errors

            # Сверка ответа с входными данными
            if answer is not None and str(answer).strip() != "" and int(answer) != -1:
                if final_calc_answer != int(answer):
                    errors.append(f"Математическая ошибка: Расчет {final_calc_answer} != Вход {answer}")

            task["answer"] = final_calc_answer

        except Exception as e:
            errors.append(f"Exception: {str(e)}")
            return False, errors

        task["image_file"] = "task_diameter_right_triangle.png"
        task["help_image_file"] = "help_diameter_right_triangle.png" # Здесь картинка-помощь НУЖНА (с квадратиком угла)
        task["task_context"] = task_context

        return len(errors) == 0, errors

    # =========================================================================
    # ПАТТЕРН 1.6: two_diameters_angles
    # =========================================================================

    def _validate_two_diameters_angles(self, task: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        text = task.get("question_text", "")
        narrative = task.get("narrative")
        answer = task.get("answer")

        # 1. Парсинг
        match_diams = re.search(r"([A-Z]{2})\s+и\s+([A-Z]{2}).*?диаметры", text)
        match_given = re.search(r"угол\s+([A-Z]{3})\s*=\s*(\d+)", text)
        match_target = re.search(r"Найди.*?угол\s+([A-Z]{3})", text)

        if not (match_diams and match_given and match_target):
            errors.append("Не удалось распарсить условие (диаметры, углы).")
            return False, errors

        d1, d2 = match_diams.group(1), match_diams.group(2)
        given_angle_name = match_given.group(1)
        given_val = int(match_given.group(2))
        target_angle_name = match_target.group(1)

        # Строим карту соответствия точек для поиска вертикальных углов
        # MK и LN -> {M:K, K:M, L:N, N:L}
        point_map = {}
        for d in [d1, d2]:
            p1, p2 = d[0], d[1]
            point_map[p1] = p2
            point_map[p2] = p1

        final_calc_answer = None
        task_context = {}
        central_angle_val_for_image = 0

        try:
            # === Сценарий 1: find_inscribed (Дано KON -> Найти LMO) ===
            if narrative == "find_inscribed":
                if given_val % 2 != 0:
                    errors.append(f"Угол {given_val} нечетный, ответ будет дробным.")
                    return False, errors

                # Математика
                res = (180 - given_val) / 2
                final_calc_answer = int(res)
                central_angle_val_for_image = given_val

                # Определяем вертикальный угол для KON
                # KON -> p1=K, center=O, p3=N -> map[K]=M, map[N]=L -> MOL (LOM)
                p1, center, p3 = list(given_angle_name)
                v1 = point_map.get(p1)
                v3 = point_map.get(p3)

                if not v1 or not v3:
                    errors.append("Ошибка определения вертикального угла (буквы не совпадают с диаметрами).")
                    return False, errors

                # Нормализуем имя (сортируем края), чтобы LOM и MOL были одним и тем же
                vertical_angle_name = f"{min(v1, v3)}{center}{max(v1, v3)}" # LOM

                # Треугольник строится на вертикальном угле
                triangle_name = vertical_angle_name

                task_context = {
                    "narrative_type": narrative,
                    "center": center,
                    "diameters": [d1, d2],

                    "central_angle_name": given_angle_name, # KON
                    "central_angle_value": given_val,

                    "vertical_pair": [given_angle_name, vertical_angle_name], # [KON, LOM]

                    "triangle_name": triangle_name, # LOM
                    "isosceles_sides": [f"{center}{v1}", f"{center}{v3}"], # OL, OM

                    "target_angle_name": target_angle_name
                }

            # === Сценарий 2: find_central (Дано LMO -> Найти KON) ===
            elif narrative == "find_central":
                # Математика
                res = 180 - (2 * given_val)
                if res <= 0:
                    errors.append(f"Геометрическая ошибка: угол <= 0")
                    return False, errors

                final_calc_answer = int(res)
                central_angle_val_for_image = res

                # В этом сценарии known (LMO) - это угол основания.
                # Нам нужно найти вершину треугольника.
                # LMO -> треугольник LOM. Вершина O. Угол LOM.
                p1, p2, p3 = list(given_angle_name) # L, M, O
                points = {p1, p2, p3}
                center = "O" if "O" in points else "O"
                base_points = sorted(list(points - {center})) # [L, M]

                triangle_vertex_angle = f"{base_points[0]}{center}{base_points[1]}" # LOM

                # Искомый угол (KON) - вертикальный к LOM
                target_vertical_name = target_angle_name # KON

                task_context = {
                    "narrative_type": narrative,
                    "center": center,
                    "diameters": [d1, d2],

                    "base_angle_name": given_angle_name, # LMO
                    "base_angle_value": given_val,

                    "triangle_name": triangle_vertex_angle, # LOM
                    "isosceles_sides": [f"{center}{base_points[0]}", f"{center}{base_points[1]}"],

                    "vertical_pair": [triangle_vertex_angle, target_vertical_name], # [LOM, KON]
                    "target_angle_name": target_angle_name # KON
                    # central_angle_value УБРАН (Солвер сам посчитает)
                }

            else:
                errors.append(f"Неизвестный нарратив: {narrative}")
                return False, errors

            # Сверка ответа
            if answer is not None and int(answer) != -1:
                if final_calc_answer != int(answer):
                    errors.append(f"Математическая ошибка: {final_calc_answer} != {answer}")

            task["answer"] = final_calc_answer

            # Выбор картинки
            suffix = "acute" if central_angle_val_for_image < 90 else "obtuse"
            task["image_file"] = f"task_two_diameters_angles_{suffix}.png"
            task["help_image_file"] = f"help_two_diameters_angles_{suffix}.png"

        except Exception as e:
            errors.append(f"Exception: {str(e)}")
            return False, errors

        task["task_context"] = task_context
        return len(errors) == 0, errors

    # =========================================================================
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ (HELPERS)
    # =========================================================================

    def _get_simple_image_version(self, angle_name: str, value: int, figure: str) -> str:
        is_acute = value < 90
        vertex = angle_name[1] if len(angle_name) == 3 else angle_name

        if figure == "ABCD":
            if vertex in ["A", "C"]:
                if vertex == "A": return "v1" if is_acute else "v2"
                if vertex == "C": return "v1" if not is_acute else "v2"
            else:
                return "v3"
        else: # KLMN
            if vertex in ["K", "M"]:
                if vertex == "K": return "v1" if is_acute else "v2"
                if vertex == "M": return "v1" if not is_acute else "v2"
            else:
                return "v3"
        return "v1"

    def _get_parasite_name(self, whole: str, target_part: str) -> str:
        s_target = set(target_part)
        s_whole = set(whole)
        vertex = whole[1]

        unique_in_target = list(s_target - s_whole)
        unique_in_whole = list(s_whole - s_target)

        if unique_in_target and unique_in_whole:
            return f"{unique_in_target[0]}{vertex}{unique_in_whole[0]}"
        return "UNK"

    def _get_arc_by_small_angles(self, angle1: str, angle2: str, figure: str) -> Optional[str]:
        p1 = angle1[0]
        p2 = angle1[2]
        arc = "".join(sorted([p1, p2])).lower()
        return arc

    def _identify_arc_and_roles(self, whole: str, part1: str, part2: str, figure: str):
        vertex = whole[1]
        p1_vertex = part1[1]
        p2_vertex = part2[1]

        part_angle = None
        alien_angle = None
        role_1 = None

        if p1_vertex == vertex:
            part_angle = part1
            alien_angle = part2
            role_1 = "part"
        elif p2_vertex == vertex:
            part_angle = part2
            alien_angle = part1
            role_1 = "alien"
        else:
            return None

        arc = self._get_arc_by_small_angles(alien_angle, alien_angle, figure)
        hidden = f"{arc[0].upper()}{vertex}{arc[1].upper()}"

        return {"arc": arc, "role_1": role_1, "hidden_part_name": hidden}
