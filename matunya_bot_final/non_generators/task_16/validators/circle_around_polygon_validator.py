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
        return False, ["Pattern 3.3 not implemented yet"]

    # =========================================================================
    # ПАТТЕРН 3.4: right_triangle_circumradius
    # =========================================================================
    def _validate_right_triangle_circumradius(self, task: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return False, ["Pattern 3.4 not implemented yet"]
