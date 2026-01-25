import re
from typing import Dict, Any, Tuple, List, Optional

class CircleElementsRelationsValidator:
    """
    Валидатор для Темы 2: Касательная, хорда, секущая, радиус.
    Соответствует стандарту ГОСТ-ВАЛИДАТОР-2026.
    """

    def __init__(self):
        # Регулярка для поиска длин отрезков (AB = 5, CD=12.5)
        # Ищет 2 заглавные буквы, равно, число (int/float)
        self.segment_regex = re.compile(r"([A-Z]{2})\s*=\s*(\d+(?:[.,]\d+)?)", re.IGNORECASE)

        # Регулярка для поиска точки пересечения (для паттерна 2.1)
        self.intersect_regex = re.compile(r"пересекаются\s+в\s+точке\s+([A-Z])", re.IGNORECASE)

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

        # Маршрутизация по паттернам Темы 2
        if pattern == "secant_similarity":
            is_valid, errors = self._validate_secant_similarity(task)
        elif pattern == "tangent_trapezoid_properties":
            is_valid, errors = self._validate_tangent_trapezoid_properties(task)
        elif pattern == "tangent_quad_sum":
            is_valid, errors = self._validate_tangent_quad_sum(task)
        elif pattern == "tangent_arc_angle":
            is_valid, errors = self._validate_tangent_arc_angle(task)
        elif pattern == "angle_tangency_center":
            is_valid, errors = self._validate_angle_tangency_center(task)
        elif pattern == "sector_area":
            is_valid, errors = self._validate_sector_area(task)
        elif pattern == "power_point":
            is_valid, errors = self._validate_power_point(task)
        else:
            errors.append(f"Неизвестный паттерн для Темы 2: {pattern}")
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
    # ПАТТЕРН 2.1: secant_similarity
    # =========================================================================
    def _validate_secant_similarity(self, task: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        text = task.get("question_text", "")
        narrative = task.get("narrative")
        answer = task.get("answer")

        # 1. Парсинг точки пересечения (F, K, U...)
        match_intersect = self.intersect_regex.search(text)
        if not match_intersect:
            errors.append("Не найдена точка пересечения (Regex: пересекаются в точке X)")
            return False, errors
        intersect_point = match_intersect.group(1)

        # 2. Парсинг всех переменных (BF=8, DF=24 и т.д.)
        found_vars = {}
        for m in self.segment_regex.finditer(text):
            # Сортируем буквы (FB -> BF), чтобы порядок не влиял
            key = "".join(sorted(m.group(1).upper()))
            val = float(m.group(2).replace(',', '.'))
            if val.is_integer():
                val = int(val)
            found_vars[key] = val

        final_calc_answer = None
        task_context = {}
        task_image = ""

        try:
            # --- ЛОГИКА ДЛЯ ABCD (Точка F) ---
            if "abcd" in narrative:
                # Ищем известные значения в словаре (ключи уже отсортированы)
                bf_val = found_vars.get("BF") # BF или FB
                df_val = found_vars.get("DF") # DF или FD
                ad_val = found_vars.get("AD") # AD или DA
                bc_val = found_vars.get("BC") # BC или CB

                if not (bf_val and df_val):
                    errors.append(f"Не найдены отрезки секущих (BF, DF). Найдено: {found_vars}")
                    return False, errors

                task_image = "task_secant_similarity_abcd.png"

                # Общие данные (Якоря для Humanizer)
                common_data = {
                    "intersection_point": intersect_point,
                    "common_vertex": intersect_point, # ✅ ЯКОРЬ 1: Общий угол
                    "angle_equality_reason": "cyclic_quadrilateral_180", # ✅ ЯКОРЬ 2: Свойство
                    "triangle_small_name": f"{intersect_point}BC",
                    "triangle_large_name": f"{intersect_point}DA",
                    "vertex_angle_small": "B",
                    "vertex_angle_large": "D"
                }

                if narrative == "abcd_find_small": # Ищем BC
                    if not ad_val:
                        errors.append("Не найдено основание AD.")
                        return False, errors

                    # BC = AD * (BF / DF)
                    res = ad_val * (bf_val / df_val)
                    final_calc_answer = res

                    task_context = {
                        **common_data,
                        "narrative_type": narrative,
                        "secant_segment_short_name": "BF",
                        "secant_segment_short_val": bf_val,
                        "secant_segment_long_name": "DF",
                        "secant_segment_long_val": df_val,
                        "base_known_name": "AD",
                        "base_known_val": ad_val,
                        "base_target_name": "BC"
                    }

                elif narrative == "abcd_find_large": # Ищем AD
                    if not bc_val:
                        errors.append("Не найдено основание BC.")
                        return False, errors

                    # AD = BC * (DF / BF)
                    res = bc_val * (df_val / bf_val)
                    final_calc_answer = res

                    task_context = {
                        **common_data,
                        "narrative_type": narrative,
                        "secant_segment_short_name": "BF",
                        "secant_segment_short_val": bf_val,
                        "secant_segment_long_name": "DF",
                        "secant_segment_long_val": df_val,
                        "base_known_name": "BC",
                        "base_known_val": bc_val,
                        "base_target_name": "AD"
                    }

            # --- ЛОГИКА ДЛЯ PRST (Точка U) ---
            elif "prst" in narrative:
                # Ожидаем: UR, UT (секущие), RS, PT (основания)
                ur_val = found_vars.get("RU") or found_vars.get("UR")
                ut_val = found_vars.get("TU") or found_vars.get("UT")
                rs_val = found_vars.get("RS") or found_vars.get("SR")
                pt_val = found_vars.get("PT") or found_vars.get("TP")

                if not (ur_val and ut_val):
                    errors.append(f"Не найдены отрезки секущих (UR, UT). Найдено: {found_vars}")
                    return False, errors

                task_image = "task_secant_similarity_prst.png"

                common_data = {
                    "intersection_point": intersect_point,
                    "common_vertex": intersect_point, # ✅ ЯКОРЬ 1
                    "angle_equality_reason": "cyclic_quadrilateral_180", # ✅ ЯКОРЬ 2
                    "triangle_small_name": f"{intersect_point}RS",
                    "triangle_large_name": f"{intersect_point}TP",
                    "vertex_angle_small": "R",
                    "vertex_angle_large": "T"
                }

                if narrative == "prst_find_small": # Ищем RS
                    if not pt_val:
                        errors.append("Не найдено основание PT.")
                        return False, errors

                    # RS = PT * (UR / UT)
                    res = pt_val * (ur_val / ut_val)
                    final_calc_answer = res

                    task_context = {
                        **common_data,
                        "narrative_type": narrative,
                        "secant_segment_short_name": "UR",
                        "secant_segment_short_val": ur_val,
                        "secant_segment_long_name": "UT",
                        "secant_segment_long_val": ut_val,
                        "base_known_name": "PT",
                        "base_known_val": pt_val,
                        "base_target_name": "RS"
                    }

                elif narrative == "prst_find_large": # Ищем PT
                    if not rs_val:
                        errors.append("Не найдено основание RS.")
                        return False, errors

                    # PT = RS * (UT / UR)
                    res = rs_val * (ut_val / ur_val)
                    final_calc_answer = res

                    task_context = {
                        **common_data,
                        "narrative_type": narrative,
                        "secant_segment_short_name": "UR",
                        "secant_segment_short_val": ur_val,
                        "secant_segment_long_name": "UT",
                        "secant_segment_long_val": ut_val,
                        "base_known_name": "RS",
                        "base_known_val": rs_val,
                        "base_target_name": "PT"
                    }

            else:
                errors.append(f"Неизвестный нарратив: {narrative}")
                return False, errors

            # Финализация ответа
            if isinstance(final_calc_answer, float):
                if final_calc_answer.is_integer():
                    final_calc_answer = int(final_calc_answer)

            # Если ответ дробный, а мы ждем целое (в ОГЭ обычно целое, но бывает 0.5)
            # Если результат 6.99999 -> 7
            if isinstance(final_calc_answer, float):
                 if abs(final_calc_answer - round(final_calc_answer)) < 1e-9:
                     final_calc_answer = int(round(final_calc_answer))

            # Проверка с входным ответом
            if answer is not None and str(answer).strip() != "" and int(answer) != -1:
                if abs(float(final_calc_answer) - float(answer)) > 0.01:
                    errors.append(f"Математическая ошибка: {final_calc_answer} != {answer}")

            task["answer"] = final_calc_answer
            task["image_file"] = task_image
            task["help_image_file"] = task_image.replace("task_", "help_")
            task["task_context"] = task_context

        except Exception as e:
            errors.append(f"Exception: {str(e)}")
            return False, errors

        return len(errors) == 0, errors

    # =========================================================================
    # ПАТТЕРН 2.2: tangent_trapezoid_properties
    # =========================================================================

    def _validate_tangent_trapezoid_properties(self, task: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        text = task.get("question_text", "")
        # Исходный нарратив из файла (например, tangent_trapezoid_find_midline)
        raw_narrative = task.get("narrative")
        answer = task.get("answer")

        final_calc_answer = None
        task_context = {}
        task_image = ""
        help_image = None

        # Парсинг отрезков (KL=11, MN=15)
        found_vars = {}
        for m in self.segment_regex.finditer(text):
            key = "".join(sorted(m.group(1).upper()))
            val = float(m.group(2).replace(',', '.'))
            if val.is_integer(): val = int(val)
            found_vars[key] = val

        try:
            # -----------------------------------------------------------------
            # 1. inradius_find_height (Дано r -> Найти h)
            # -----------------------------------------------------------------
            if raw_narrative == "inradius_find_height":
                match_r = re.search(r"(?:r|радиус).*?=\s*(\d+(?:[.,]\d+)?)", text, re.IGNORECASE)
                if not match_r:
                    match_r = re.search(r"r\s*=\s*(\d+)", text)

                if not match_r:
                    errors.append("Не найден радиус (r=...)")
                    return False, errors

                r_val = float(match_r.group(1).replace(',', '.'))
                if r_val.is_integer(): r_val = int(r_val)

                h_val = r_val * 2
                final_calc_answer = h_val

                task_image = "task_inradius_find_height.png"
                help_image = "help_inradius_find_height.png"

                task_context = {
                    "narrative": raw_narrative, # Оставляем исходный
                    "radius_name": "r",
                    "radius_value": r_val,
                    "height_name": "h"
                }

            # -----------------------------------------------------------------
            # 2. tangent_trapezoid_find_midline
            # РАЗДЕЛЯЕМ НА ДВА НАРРАТИВА: via_sides / via_bases
            # -----------------------------------------------------------------
            elif raw_narrative.startswith("tangent_trapezoid_find_midline"):
                task_image = "task_tangent_trapezoid_find_midline.png"
                help_image = "help_tangent_trapezoid_find_midline.png"

                # 1. Парсим названия оснований из текста
                match_bases_text = re.search(r"основаниями\s+([A-Z]{2})\s+и\s+([A-Z]{2})", text)
                if not match_bases_text:
                    errors.append("Не удалось определить названия оснований.")
                    return False, errors

                base_names = {
                    "".join(sorted(match_bases_text.group(1))),
                    "".join(sorted(match_bases_text.group(2)))
                }

                # 2. Имя средней линии
                match_midline = re.search(r"линию.*?\s+([A-Z]{2})", text)
                midline_name = match_midline.group(1) if match_midline else "PR" # Fallback

                # 3. Определяем, что дано: Основания или Боковые?
                given_keys = set(found_vars.keys())

                # --- СЦЕНАРИЙ А: Даны основания (via_bases) ---
                if given_keys.intersection(base_names):
                    # Новый, точный нарратив
                    new_narrative = "tangent_trapezoid_find_midline_via_bases"

                    b1_name, b2_name = list(base_names)
                    b1_val = found_vars.get(b1_name)
                    b2_val = found_vars.get(b2_name)

                    if b1_val is None or b2_val is None:
                        errors.append(f"Не найдены значения оснований {base_names}.")
                        return False, errors

                    res = (b1_val + b2_val) / 2
                    final_calc_answer = res

                    task_context = {
                        "narrative": new_narrative,
                        "base_1_name": b1_name,
                        "base_1_val": b1_val,
                        "base_2_name": b2_name,
                        "base_2_val": b2_val,
                        "midline_name": midline_name
                    }

                    # ⚡ ВАЖНО: Обновляем нарратив в корне задачи
                    task["narrative"] = new_narrative

                # --- СЦЕНАРИЙ Б: Даны боковые стороны (via_sides) ---
                else:
                    # Новый, точный нарратив
                    new_narrative = "tangent_trapezoid_find_midline_via_sides"

                    if len(found_vars) < 2:
                        errors.append("Найдено меньше 2-х сторон.")
                        return False, errors

                    s1_name, s2_name = list(found_vars.keys())[:2]
                    s1_val = found_vars[s1_name]
                    s2_val = found_vars[s2_name]

                    res = (s1_val + s2_val) / 2
                    final_calc_answer = res

                    task_context = {
                        "narrative": new_narrative,
                        "side_1_name": s1_name,
                        "side_1_val": s1_val,
                        "side_2_name": s2_name,
                        "side_2_val": s2_val,
                        "midline_name": midline_name
                    }

                    # ⚡ ВАЖНО: Обновляем нарратив в корне задачи
                    task["narrative"] = new_narrative

            # -----------------------------------------------------------------
            # 3. tangent_trapezoid_find_base (Найти 4-ю сторону)
            # -----------------------------------------------------------------
            elif raw_narrative == "tangent_trapezoid_find_base":
                task_image = "task_tangent_trapezoid_find_base.png"
                help_image = None

                match_target = re.search(r"Найди(?:те)?\s+([A-Z]{2})", text)
                if not match_target:
                    errors.append("Не найдена искомая сторона.")
                    return False, errors

                target_name = "".join(sorted(match_target.group(1)))

                if target_name in found_vars:
                    del found_vars[target_name]

                if len(found_vars) != 3:
                    errors.append(f"Нужно ровно 3 известные стороны, найдено {len(found_vars)}")
                    return False, errors

                target_letters = set(target_name)
                opposite_name = None
                opposite_val = 0
                sum_pair = []

                for name, val in found_vars.items():
                    if not set(name).intersection(target_letters):
                        opposite_name = name
                        opposite_val = val
                    else:
                        sum_pair.append((name, val))

                if not opposite_name or len(sum_pair) != 2:
                    errors.append("Не удалось определить пары сторон.")
                    return False, errors

                pair_sum = sum_pair[0][1] + sum_pair[1][1]
                res = pair_sum - opposite_val

                if res <= 0:
                    errors.append(f"Ошибка: сторона <= 0 ({res}).")
                    return False, errors

                final_calc_answer = res

                task_context = {
                    "narrative": raw_narrative,
                    "side_known_1_name": sum_pair[0][0],
                    "side_known_1_val": sum_pair[0][1],
                    "side_known_2_name": sum_pair[1][0],
                    "side_known_2_val": sum_pair[1][1],
                    "side_known_3_name": opposite_name,
                    "side_known_3_val": opposite_val,
                    "side_target_name": target_name
                }

            else:
                errors.append(f"Неизвестный нарратив: {raw_narrative}")
                return False, errors

            # Финализация ответа
            if isinstance(final_calc_answer, float):
                if final_calc_answer.is_integer():
                    final_calc_answer = int(final_calc_answer)
                elif abs(final_calc_answer - round(final_calc_answer)) < 1e-9:
                     final_calc_answer = int(round(final_calc_answer))

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
    # ПАТТЕРН 2.3: tangent_quad_sum
    # =========================================================================

    def _validate_tangent_quad_sum(self, task: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        text = task.get("question_text", "")
        narrative = task.get("narrative")
        answer = task.get("answer")

        # 1. Парсим Искомую сторону (Найди AD)
        match_target = re.search(r"Найди(?:те)?\s+([A-Z]{2})", text)
        if not match_target:
            errors.append("Не найдена искомая сторона (Regex: Найди XX).")
            return False, errors

        target_name = "".join(sorted(match_target.group(1))) # Сортируем буквы (AD)

        # 2. Парсим Известные стороны
        found_vars = {}
        for m in self.segment_regex.finditer(text):
            key = "".join(sorted(m.group(1).upper()))
            val = float(m.group(2).replace(',', '.'))
            if val.is_integer(): val = int(val)
            found_vars[key] = val

        # Удаляем искомую из найденных (на случай, если она случайно попала в regex)
        if target_name in found_vars:
            del found_vars[target_name]

        if len(found_vars) != 3:
            errors.append(f"Нужно ровно 3 известные стороны, найдено {len(found_vars)}: {found_vars}")
            return False, errors

        # 3. Геометрическая логика
        # В описанном 4-угольнике противоположные стороны НЕ ИМЕЮТ общих букв.
        # Смежные стороны ИМЕЮТ общую букву (вершину).
        # Нам нужно найти ПАРУ к Целевой стороне (это та, у которой нет общих букв).

        target_letters = set(target_name)

        partner_name = None
        partner_val = 0
        complete_pair = [] # [(name, val), (name, val)]

        for name, val in found_vars.items():
            # Пересечение множеств букв
            if not set(name).intersection(target_letters):
                # Нет общих букв -> Это противоположная сторона (Партнер)
                partner_name = name
                partner_val = val
            else:
                # Есть общая буква -> Это смежная сторона (часть Полной пары)
                complete_pair.append((name, val))

        if not partner_name or len(complete_pair) != 2:
            errors.append(f"Не удалось определить пары сторон для {target_name}. Проверь буквы.")
            return False, errors

        # 4. Расчет
        # Сумма полной пары = Сумма неполной пары
        sum_complete = complete_pair[0][1] + complete_pair[1][1]

        # Target + Partner = Sum_Complete
        # Target = Sum_Complete - Partner
        calc_res = sum_complete - partner_val

        if calc_res <= 0:
            errors.append(f"Геометрическая ошибка: сторона <= 0 ({calc_res}).")
            return False, errors

        # 5. Сборка контекста по утвержденному JSON
        task_context = {
            "narrative_type": "find_missing_side",
            "figure_type": "tangent_quadrilateral",

            # Левая часть (Полная пара - смежные с целевой)
            # Хотя методически это "Противоположная пара", но для уравнения:
            # L1 + L2 = R1 + x
            "sum_left_1_name": complete_pair[0][0],
            "sum_left_1_val": complete_pair[0][1],
            "sum_left_2_name": complete_pair[1][0],
            "sum_left_2_val": complete_pair[1][1],

            # Правая часть (Неполная пара)
            "sum_right_1_name": partner_name,
            "sum_right_1_val": partner_val,
            "sum_right_2_name": target_name,
            "sum_right_2_val": None, # Это мы ищем

            "target_side_name": target_name
        }

        # Финализация ответа
        final_calc_answer = calc_res
        if isinstance(final_calc_answer, float) and final_calc_answer.is_integer():
            final_calc_answer = int(final_calc_answer)

        # Проверка с ответом в файле
        if answer is not None and str(answer).strip() != "" and int(answer) != -1:
            if abs(float(final_calc_answer) - float(answer)) > 0.01:
                errors.append(f"Математическая ошибка: {final_calc_answer} != {answer}")

        # Итог
        task["answer"] = final_calc_answer
        task["image_file"] = "task_tangent_quad_sum.png"
        task["help_image_file"] = "help_tangent_quad_sum.png"
        task["task_context"] = task_context

        return True, errors

    # =========================================================================
    # ЗАГЛУШКИ ДЛЯ БУДУЩИХ ПАТТЕРНОВ (2.2 - 2.7)
    # =========================================================================


    def _validate_tangent_arc_angle(self, task: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return False, ["Pattern 2.4 not implemented yet"]

    def _validate_angle_tangency_center(self, task: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return False, ["Pattern 2.5 not implemented yet"]

    def _validate_sector_area(self, task: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return False, ["Pattern 2.6 not implemented yet"]

    def _validate_power_point(self, task: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return False, ["Pattern 2.7 not implemented yet"]
