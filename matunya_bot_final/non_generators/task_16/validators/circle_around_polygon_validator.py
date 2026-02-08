import re
from typing import Dict, Any, Tuple, List, Optional

class CircleAroundPolygonValidator:
    """
    Валидатор для Темы 3: Окружность, описанная вокруг многоугольника.
    Соответствует стандарту ГОСТ-ВАЛИДАТОР-2026.
    """

    def __init__(self):
        # Универсальная регулярка для поиска величин:
        # Ищет: "AB = 5", "R = 10", "r = 2.5", "сторона равна 8"
        # Группа 1: Имя (AB, R, r, сторона)
        # Группа 2: Значение
        self.value_regex = re.compile(r"([A-Z]{1,2}|R|r|сторона.*?)\s*(?:=|равна|равен)\s*(\d+(?:[.,]\d+)?)", re.IGNORECASE)

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

        # Маршрутизация по паттернам Темы 3
        if pattern == "square_incircle_circumcircle":
            is_valid, errors = self._validate_square_incircle_circumcircle(task)
        elif pattern == "eq_triangle_circles":
            is_valid, errors = self._validate_eq_triangle_circles(task)
        elif pattern == "square_radius_midpoint":
            is_valid, errors = self._validate_square_radius_midpoint(task)
        elif pattern == "right_triangle_circumradius":
            is_valid, errors = self._validate_right_triangle_circumradius(task)
        else:
            errors.append(f"Неизвестный паттерн для Темы 3: {pattern}")
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
            "id", "pattern", "narrative", "question_text", "answer",
            "image_file", "help_image_file", "task_context"
        ]

        for key in ordered_keys:
            if key in temp:
                task[key] = temp[key]

        for key, val in temp.items():
            if key not in task:
                task[key] = val

    # =========================================================================
    # ПАТТЕРН 3.1: square_incircle_circumcircle
    # =========================================================================
    def _validate_square_incircle_circumcircle(
        self, task: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        errors = []

        text = task.get("question_text", "")
        narrative = (task.get("narrative") or "").strip()
        answer = task.get("answer")

        # -------------------------------------------------
        # 1. Парсинг значения вида X√2 или √2
        # -------------------------------------------------
        match_val = re.search(r"(\d*)\s*[√v]2", text)
        if not match_val:
            errors.append("Не найдено значение с корнем (X√2).")
            return False, errors

        raw_coeff = match_val.group(1)
        coeff = int(raw_coeff) if raw_coeff else 1
        value_str = f"{coeff}√2" if coeff > 1 else "√2"

        final_answer: int | None = None
        task_image = ""
        help_image = ""
        task_context: Dict[str, Any] = {}

        try:
            # =================================================
            # circum_to_in  (R → r)
            # =================================================
            if narrative == "circum_to_in":
                final_answer = coeff

                task_image = "task_square_two_circles.png"
                help_image = "help_square_two_circles.png"

                task_context = {
                    "figure": "square",
                    "narrative": "circum_to_in",
                    "given": {
                        "element_type": "circumcircle",
                        "symbol": "R",
                        "value_str": value_str,
                        "coeff": coeff,
                    },
                    "target": {
                        "element_type": "incircle",
                        "symbol": "r",
                        "value": final_answer,
                    },
                    "relations": {
                        "radius_relation": "r = R / √2",
                    },
                    "geometry_facts": {
                        "center_relation": "same_center",
                    },
                }

            # =================================================
            # in_to_circum  (r → R)
            # =================================================
            elif narrative == "in_to_circum":
                final_answer = coeff * 2

                task_image = "task_square_two_circles.png"
                help_image = "help_square_two_circles.png"

                task_context = {
                    "figure": "square",
                    "narrative": "in_to_circum",
                    "given": {
                        "element_type": "incircle",
                        "symbol": "r",
                        "value_str": value_str,
                        "coeff": coeff,
                    },
                    "target": {
                        "element_type": "circumcircle",
                        "symbol": "R",
                        "value": final_answer,
                    },
                    "relations": {
                        "radius_relation": "R = r · √2",
                    },
                    "geometry_facts": {
                        "center_relation": "same_center",
                    },
                }

            # =================================================
            # circum_to_side  (R → a)
            # =================================================
            elif narrative == "circum_to_side":
                final_answer = coeff * 2

                task_image = "task_square_circumcircle.png"
                help_image = "help_square_circumcircle.png"

                task_context = {
                    "figure": "square",
                    "narrative": "circum_to_side",
                    "given": {
                        "element_type": "circumcircle",
                        "symbol": "R",
                        "value_str": value_str,
                        "coeff": coeff,
                    },
                    "target": {
                        "element_type": "side",
                        "symbol": "a",
                        "value": final_answer,
                    },
                    "relations": {
                        "side_relation": "a = R · √2",
                    },
                    "geometry_facts": {
                        "diagonal_relation": "d = a√2",
                    },
                }

            # =================================================
            # circum_to_perimeter  (R → P)
            # =================================================
            elif narrative == "circum_to_perimeter":
                side_val = coeff * 2
                final_answer = side_val * 4

                task_image = "task_square_circumcircle.png"
                help_image = "help_square_circumcircle.png"

                task_context = {
                    "figure": "square",
                    "narrative": "circum_to_perimeter",
                    "given": {
                        "element_type": "circumcircle",
                        "symbol": "R",
                        "value_str": value_str,
                        "coeff": coeff,
                    },
                    "intermediate": {
                        "side_value": side_val,
                    },
                    "target": {
                        "element_type": "perimeter",
                        "symbol": "P",
                        "value": final_answer,
                    },
                    "relations": {
                        "side_relation": "a = R · √2",
                        "perimeter_relation": "P = 4a",
                    },
                    "geometry_facts": {
                        "diagonal_relation": "d = a√2",
                    },
                }

            else:
                errors.append(f"Неизвестный narrative: {narrative}")
                return False, errors

            # -------------------------------------------------
            # Проверка ответа
            # -------------------------------------------------
            if answer not in (None, "", -1):
                if int(answer) != final_answer:
                    errors.append(
                        f"Математическая ошибка: {final_answer} != {answer}"
                    )

            # -------------------------------------------------
            # Запись обратно в task
            # -------------------------------------------------
            task["answer"] = final_answer
            task["image_file"] = task_image
            task["help_image_file"] = help_image
            task["task_context"] = task_context

        except Exception as e:
            errors.append(f"Exception: {type(e).__name__}: {e}")
            return False, errors

        return len(errors) == 0, errors

    # =========================================================================
    # ПАТТЕРН 3.2: eq_triangle_circles
    # =========================================================================
    def _validate_eq_triangle_circles(self, task: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        text = task.get("question_text", "")
        narrative = task.get("narrative")
        answer = task.get("answer")

        # 1. Парсинг значения с корнем (12√3 или просто √3)
        match_val = re.search(r"(\d*)\s*[√v]3", text)
        if not match_val:
            errors.append("Не найдено значение с корнем (X√3).")
            return False, errors

        raw_coeff_str = match_val.group(1)
        coeff = int(raw_coeff_str) if raw_coeff_str else 1
        raw_val_str = f"{coeff}√3" if coeff > 1 else "√3"

        final_calc_answer = None
        task_context = {}

        base_context = {
            "figure": "equilateral_triangle",
            "narrative": narrative,
            "geometry_facts": {"triangle_type": "equilateral"}
        }

        task_image = "task_eq_triangle_circumcircle.png"
        help_image = "help_eq_triangle_circumcircle.png"

        try:
            # --- ГРУППА 1: Диаметр описанной (D <-> a) ---
            if narrative == "circum_diameter_to_side":
                # D = coeff*√3. R = D/2. a = R*√3.
                # a = (coeff*√3 / 2) * √3 = coeff * 3 / 2
                res = (coeff * 3) / 2

                # Приведение к int ДО записи в контекст
                if isinstance(res, float) and res.is_integer():
                    res = int(res)

                final_calc_answer = res

                task_context = {
                    **base_context,
                    "given": {
                        "element_type": "circumcircle_diameter",
                        "symbol": "D",
                        "value_str": raw_val_str,
                        "coeff": coeff
                    },
                    "target": {
                        "element_type": "side",
                        "symbol": "a",
                        "value": final_calc_answer # Теперь здесь int (если число целое)
                    },
                    "relations": {
                        "radius_from_diameter": "R = D : 2",
                        "side_from_radius": "a = R · √3"
                    }
                    # radius_val удален
                }

            elif narrative == "side_to_circum_diameter":
                # a = coeff*√3. D = 2 * (a/√3) = 2 * coeff
                res = coeff * 2
                # coeff - int, значит res - int, но для надежности оставим проверку
                if isinstance(res, float) and res.is_integer():
                    res = int(res)
                final_calc_answer = res

                task_context = {
                    **base_context,
                    "given": {
                        "element_type": "side",
                        "symbol": "a",
                        "value_str": raw_val_str,
                        "coeff": coeff
                    },
                    "target": {
                        "element_type": "circumcircle_diameter",
                        "symbol": "D",
                        "value": final_calc_answer
                    },
                    "relations": {
                        "radius_relation": "R = a : √3",
                        "diameter_relation": "D = 2 · R"
                    }
                }

            # --- ГРУППА 2: Радиус описанной (R <-> a) ---
            elif narrative == "circum_radius_to_side":
                # R = coeff*√3. a = R*√3 = coeff*3
                res = coeff * 3
                if isinstance(res, float) and res.is_integer():
                    res = int(res)
                final_calc_answer = res

                task_context = {
                    **base_context,
                    "given": {
                        "element_type": "circumcircle_radius",
                        "symbol": "R",
                        "value_str": raw_val_str,
                        "coeff": coeff
                    },
                    "target": {
                        "element_type": "side",
                        "symbol": "a",
                        "value": final_calc_answer
                    },
                    "relations": {
                        "side_relation": "a = R · √3"
                    }
                }

            elif narrative == "side_to_circum_radius":
                # a = coeff*√3. R = a/√3 = coeff
                res = coeff
                if isinstance(res, float) and res.is_integer():
                    res = int(res)
                final_calc_answer = res

                task_context = {
                    **base_context,
                    "given": {
                        "element_type": "side",
                        "symbol": "a",
                        "value_str": raw_val_str,
                        "coeff": coeff
                    },
                    "target": {
                        "element_type": "circumcircle_radius",
                        "symbol": "R",
                        "value": final_calc_answer
                    },
                    "relations": {
                        "radius_relation": "R = a : √3"
                    }
                }

            # --- ГРУППА 3: Радиус вписанной (r <-> a) ---
            elif narrative == "inradius_to_side":
                task_image = "task_eq_triangle_incircle.png"
                help_image = "help_eq_triangle_incircle.png"

                # r = coeff*√3. a = 6r / √3 = 6*coeff
                res = coeff * 6
                if isinstance(res, float) and res.is_integer():
                    res = int(res)
                final_calc_answer = res

                task_context = {
                    **base_context,
                    "given": {
                        "element_type": "incircle_radius",
                        "symbol": "r",
                        "value_str": raw_val_str,
                        "coeff": coeff
                    },
                    "target": {
                        "element_type": "side",
                        "symbol": "a",
                        "value": final_calc_answer
                    },
                    "relations": {
                        "side_relation": "a = 6r / √3"
                    }
                }

            elif narrative == "side_to_inradius":
                task_image = "task_eq_triangle_incircle.png"
                help_image = "help_eq_triangle_incircle.png"

                # a = coeff*√3. r = a√3 / 6 = coeff*3 / 6 = coeff / 2
                res = coeff / 2

                # Здесь может быть дробь (например, 0.5), но если целое (1.0), то станет int(1)
                if isinstance(res, float) and res.is_integer():
                    res = int(res)

                final_calc_answer = res

                task_context = {
                    **base_context,
                    "given": {
                        "element_type": "side",
                        "symbol": "a",
                        "value_str": raw_val_str,
                        "coeff": coeff
                    },
                    "target": {
                        "element_type": "incircle_radius",
                        "symbol": "r",
                        "value": final_calc_answer
                    },
                    "relations": {
                        "radius_relation": "r = a√3 / 6"
                    }
                }

            else:
                errors.append(f"Неизвестный нарратив: {narrative}")
                return False, errors

            # Финальная проверка с ответом из файла
            if answer is not None and str(answer).strip() != "" and int(answer) != -1:
                if abs(float(final_calc_answer) - float(answer)) > 0.01:
                    errors.append(f"Математическая ошибка: {final_calc_answer} != {answer}")

            task["answer"] = final_calc_answer
            task["image_file"] = task_image
            task["help_image_file"] = help_image
            task["task_context"] = task_context

        except Exception as e:
            errors.append(f"Exception: {str(e)}")
            return False, errors

        return len(errors) == 0, errors

    # =========================================================================
    # ПАТТЕРН 3.3: square_radius_midpoint
    # =========================================================================
    def _validate_square_radius_midpoint(self, task: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        text = task.get("question_text", "")
        narrative = task.get("narrative")
        answer = task.get("answer")

        # 1. Парсинг геометрии
        match_side_name = re.search(r"сторон[ыа]\s+([A-Z]{2})", text, re.IGNORECASE)
        match_center = re.search(r"(?:Точка|точке)\s+([A-Z])", text, re.IGNORECASE)
        match_vertex = re.search(r"вершину\s+([A-Z])", text, re.IGNORECASE)

        if not (match_side_name and match_center and match_vertex):
            errors.append("Не удалось распарсить геометрию (сторона, центр или вершина).")
            return False, errors

        midpoint_side = match_side_name.group(1).upper()
        circle_center = match_center.group(1).upper()
        point_on_circle = match_vertex.group(1).upper()

        # 2. Парсинг чисел
        match_root = re.search(r"(\d*)\s*[√v]5", text)
        match_int = re.search(r"равен\s+(\d+)(?!\s*[√v])", text)

        final_calc_answer = None
        task_context = {}

        base_context = {
            "figure": "square",
            "narrative": narrative,
            "geometry_facts": {
                "midpoint_side": midpoint_side,
                "circle_center": circle_center,
                "point_on_circle": point_on_circle
            }
        }

        try:
            # -----------------------------------------------------------------
            # Сценарий 1: midpoint_side_to_area (Дано R -> Найти S)
            # -----------------------------------------------------------------
            if narrative == "midpoint_side_to_area":
                if "KL" in midpoint_side or "KN" in midpoint_side or "LM" in midpoint_side or "MN" in midpoint_side:
                     task_image = "task_square_radius_midpoint_klmn.png"
                     help_image = "help_square_radius_midpoint_klmn.png"
                else:
                     task_image = "task_square_radius_midpoint_prst.png"
                     help_image = "help_square_radius_midpoint_prst.png"

                if match_root:
                    raw_coeff_str = match_root.group(1)
                    coeff = int(raw_coeff_str) if raw_coeff_str else 1
                    r_val_str = f"{coeff}√5" if coeff > 1 else "√5"
                    r_sq = (coeff ** 2) * 5
                elif match_int:
                    val = int(match_int.group(1))
                    r_val_str = str(val)
                    r_sq = val ** 2
                else:
                    errors.append("Не найдено значение радиуса.")
                    return False, errors

                area = (4 * r_sq) / 5

                if abs(area - round(area)) > 1e-9:
                    errors.append(f"Площадь не целая: {area}")
                    return False, errors

                final_calc_answer = int(area)

                task_context = {
                    **base_context,
                    "given": {
                        "element_type": "circle_radius",
                        "symbol": "R",
                        "value_str": r_val_str
                    },
                    "target": {
                        "element_type": "square_area",
                        "symbol": "S",
                        "value": final_calc_answer
                    },
                    "relations": {
                        "area_relation": "S = 4R² / 5"
                    }
                }

            # -----------------------------------------------------------------
            # Сценарий 2: midpoint_side_to_radius (Дано a -> Найти R)
            # -----------------------------------------------------------------
            elif narrative == "midpoint_side_to_radius":
                task_image = "task_square_radius_midpoint_abcd.png"
                help_image = "help_square_radius_midpoint_abcd.png"

                if not match_root:
                    errors.append("В этом типе задач ожидается сторона с корнем (X√5).")
                    return False, errors

                raw_coeff_str = match_root.group(1)
                coeff = int(raw_coeff_str) if raw_coeff_str else 1
                a_val_str = f"{coeff}√5" if coeff > 1 else "√5"

                # Вычисляем половину стороны
                half_coeff = coeff // 2
                half_val_str = f"{half_coeff}√5" if half_coeff > 1 else "√5"

                # Вычисляем квадраты для подробного объяснения (Шаг 4)
                a_num_sq = coeff ** 2      # Квадрат коэффициента стороны
                half_a_num_sq = half_coeff ** 2  # Квадрат коэффициента половины

                # Итоговое подкоренное выражение R^2 = (coeff^2 * 5) + (half^2 * 5)
                # Это чисто математически то же самое, что (coeff*5)/2 в финале, но через сумму квадратов
                calc_r2_val = (a_num_sq * 5) + (half_a_num_sq * 5)

                # R = корень из R^2
                res = calc_r2_val ** 0.5

                if abs(res - round(res)) > 1e-9:
                    errors.append(f"Радиус не целый: {res}")
                    return False, errors

                final_calc_answer = int(res)

                task_context = {
                    **base_context,
                    # ✅ Добавлено поле R^2 для итогового корня
                    "calc_r2": str(calc_r2_val),

                    "given": {
                        "element_type": "side",
                        "symbol": "a",
                        "value_str": a_val_str,
                        "coeff": coeff,
                        "half_value_str": half_val_str,

                        # ✅ Добавлены строковые поля для развернутого решения
                        "a_num": str(coeff),
                        "half_a_num": str(half_coeff),
                        "a_num_sq": str(a_num_sq),
                        "half_a_num_sq": str(half_a_num_sq)
                    },
                    "target": {
                        "element_type": "circle_radius",
                        "symbol": "R",
                        "value": final_calc_answer
                    },
                    "relations": {
                        "radius_relation": "R = a√5 / 2"
                    }
                }

            else:
                errors.append(f"Неизвестный нарратив: {narrative}")
                return False, errors

            # Проверка ответа
            if answer is not None and str(answer).strip() != "" and int(answer) != -1:
                if abs(float(final_calc_answer) - float(answer)) > 0.01:
                    errors.append(f"Математическая ошибка: {final_calc_answer} != {answer}")

            task["answer"] = final_calc_answer
            task["image_file"] = task_image
            task["help_image_file"] = help_image
            task["task_context"] = task_context

        except Exception as e:
            errors.append(f"Exception: {str(e)}")
            return False, errors

        return len(errors) == 0, errors

    # =========================================================================
    # ПАТТЕРН 3.4: right_triangle_circumradius
    # =========================================================================
    def _validate_right_triangle_circumradius(self, task: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        text = task.get("question_text", "")
        narrative = task.get("narrative")
        answer = task.get("answer")

        # 1. Парсинг отрезков (BC=6, BD=8)
        found_vars = {}
        for m in self.value_regex.finditer(text):
            # Группа 1: Имя (BC), Группа 2: Значение (6)
            raw_key = m.group(1).upper().strip()
            # Игнорируем "R", "r", "D" если они вдруг попадутся (хотя regex ловит 1-2 буквы)
            if len(raw_key) == 2:
                key = "".join(sorted(raw_key)) # Сортируем буквы BC
                val = float(m.group(2).replace(',', '.'))
                if val.is_integer(): val = int(val)
                found_vars[key] = val

        final_calc_answer = None
        task_context = {}

        task_image = "task_right_triangle_circum.png"
        help_image = "help_right_triangle_circum.png"

        try:
            if narrative == "hypotenuse_half":
                # Ожидаем 2 катета. Проверяем, что их 2.
                if len(found_vars) != 2:
                    errors.append(f"Ожидалось 2 катета, найдено: {found_vars}")
                    return False, errors

                legs = list(found_vars.items()) # [('BC', 6), ('BD', 8)]
                leg1_name, leg1_val = legs[0]
                leg2_name, leg2_val = legs[1]

                # 2. Геометрическая проверка: есть ли общая вершина (прямой угол)?
                # BC и BD -> общая B.
                s1 = set(leg1_name)
                s2 = set(leg2_name)
                common = s1.intersection(s2)

                if len(common) != 1:
                    errors.append(f"Катеты {leg1_name} и {leg2_name} не имеют общей вершины.")
                    return False, errors

                right_angle_vertex = list(common)[0]

                # Гипотенуза - оставшиеся буквы
                p1 = list(s1 - common)[0]
                p2 = list(s2 - common)[0]
                hypotenuse_name = "".join(sorted([p1, p2]))

                # 3. Математика: Пифагор
                # c^2 = a^2 + b^2
                hyp_sq = leg1_val**2 + leg2_val**2
                hyp_val = hyp_sq ** 0.5

                # Радиус = Гипотенуза / 2
                res = hyp_val / 2

                # Проверка на адекватность чисел (ОГЭ обычно целые или .5)
                # Если гипотенуза не извлекается (напр sqrt(20)), это плохо для этого типа задач
                if abs(hyp_val - round(hyp_val)) > 1e-9:
                     # Можно допустить корни, но в наших задачах (3,4,5) все красиво.
                     # Если что, здесь можно добавить warning.
                     pass
                else:
                    hyp_val = int(hyp_val)

                final_calc_answer = res

                # Формируем контекст
                task_context = {
                    "figure": "right_triangle",
                    "narrative": narrative,

                    "geometry_facts": {
                        "right_angle_vertex": right_angle_vertex,
                        "legs": [leg1_name, leg2_name],
                        "hypotenuse": hypotenuse_name
                    },

                    "given": {
                        "element_type": "legs",
                        "symbols": [leg1_name, leg2_name],
                        "values": [leg1_val, leg2_val]
                    },

                    # Вычисленные данные для красивого решения
                    "hypotenuse_sq_val": hyp_sq, # 100
                    "hypotenuse_val": hyp_val,   # 10

                    "target": {
                        "element_type": "circumradius",
                        "symbol": "R",
                        "value": int(res) if res.is_integer() else res
                    },

                    "relations": {
                        "pythagoras": f"{hypotenuse_name}² = {leg1_name}² + {leg2_name}²",
                        "circumradius_rule": f"R = {hypotenuse_name} / 2"
                    }
                }

            else:
                errors.append(f"Неизвестный нарратив: {narrative}")
                return False, errors

            # Финализация ответа
            if isinstance(final_calc_answer, float) and final_calc_answer.is_integer():
                final_calc_answer = int(final_calc_answer)

            if answer is not None and str(answer).strip() != "" and int(answer) != -1:
                if abs(float(final_calc_answer) - float(answer)) > 0.01:
                    errors.append(f"Математическая ошибка: {final_calc_answer} != {answer}")

            task["answer"] = final_calc_answer
            task["image_file"] = task_image
            task["help_image_file"] = help_image
            task["task_context"] = task_context

        except Exception as e:
            errors.append(f"Exception: {str(e)}")
            return False, errors

        return len(errors) == 0, errors
