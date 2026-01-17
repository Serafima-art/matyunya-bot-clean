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
    # ЗАГЛУШКИ ДЛЯ ОСТАЛЬНЫХ ПАТТЕРНОВ
    # =========================================================================

    def _validate_radius_chord_angles(self, task: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return True, []

    def _validate_arc_length_ratio(self, task: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return True, []

    def _validate_two_diameters_angles(self, task: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return True, []

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
