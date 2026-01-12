import re
from typing import Dict, Any, Tuple, List, Optional

class CentralAndInscribedAnglesValidator:
    """
    Валидатор для Темы 1: Центральные и вписанные углы.
    Соответствует стандарту ГОСТ-ВАЛИДАТОР-2026.

    UPD: Использует task_context вместо solution_vars.
    """

    def __init__(self):
        self.angle_regex = re.compile(r"(?:угол|∠)\s*([A-Z]{1,3})[^0-9=]*?(?:равен|=)\s*(\d+)", re.IGNORECASE)
        self.find_regex = re.compile(r"(?:найди(?:те)?|чему\s+равен)\s*(?:угол|∠)?\s*([A-Z]{1,3})", re.IGNORECASE)

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
    # ЗАГЛУШКИ ДЛЯ ОСТАЛЬНЫХ ПАТТЕРНОВ
    # =========================================================================

    def _validate_central_inscribed(self, task: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return True, []

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
