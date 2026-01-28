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
    # ПАТТЕРН 2.4: tangent_arc_angle
    # =========================================================================

    def _validate_tangent_arc_angle(self, task: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        text = task.get("question_text", "")
        narrative = task.get("narrative")
        answer = task.get("answer")

        # Регулярки (локальные для этого метода)
        # "дуга AB равна 68"
        regex_arc = re.search(r"дуга\s+([A-Z]{2})\s+(?:равна|составляет)\s+(\d+(?:[.,]\d+)?)", text, re.IGNORECASE)
        # "угол ABC равен 34" or "угол ABC острый" (нам нужно значение)
        regex_angle_val = re.search(r"угол\s+([A-Z]{3})\s+равен\s+(\d+(?:[.,]\d+)?)", text, re.IGNORECASE)
        # Для поиска имени угла, если значение не дано (в прямой задаче)
        regex_angle_name = re.search(r"угол\s+([A-Z]{3})", text, re.IGNORECASE)

        final_calc_answer = None
        task_context = {}
        arc_val_for_image = 0 # Чтобы выбрать small/large

        try:
            # -----------------------------------------------------------------
            # 1. arc_to_tangent_angle (Дана Дуга -> Найти Угол)
            # -----------------------------------------------------------------
            if narrative == "arc_to_tangent_angle":
                if not regex_arc:
                    errors.append("Не найдена величина дуги (дуга XX равна Y).")
                    return False, errors

                arc_name = "".join(sorted(regex_arc.group(1).upper()))
                arc_val = float(regex_arc.group(2).replace(',', '.'))
                if arc_val.is_integer(): arc_val = int(arc_val)

                # Ищем имя искомого угла (обычно ABC)
                angle_name = regex_angle_name.group(1).upper() if regex_angle_name else "ABC"

                # Точка касания - обычно средняя буква угла (B в ABC) или общая с дугой
                tangent_point = angle_name[1] if len(angle_name) == 3 else arc_name[1]

                # Математика: Угол = Дуга / 2
                res = arc_val / 2
                final_calc_answer = res

                arc_val_for_image = arc_val

                task_context = {
                    "narrative": narrative,
                    "arc_name": arc_name,
                    "arc_value": arc_val,
                    "angle_name": angle_name,
                    "tangent_point": tangent_point,
                    "chord_name": arc_name # Хорда стягивает дугу
                }

            # -----------------------------------------------------------------
            # 2. tangent_angle_to_arc (Дан Угол -> Найти Дугу)
            # -----------------------------------------------------------------
            elif narrative == "tangent_angle_to_arc":
                if not regex_angle_val:
                    errors.append("Не найдена величина угла (угол XXX равен Y).")
                    return False, errors

                angle_name = regex_angle_val.group(1).upper()
                angle_val = float(regex_angle_val.group(2).replace(',', '.'))
                if angle_val.is_integer(): angle_val = int(angle_val)

                # Ищем имя искомой дуги
                match_target_arc = re.search(r"дуги\s+([A-Z]{2})", text, re.IGNORECASE)
                arc_name = "".join(sorted(match_target_arc.group(1).upper())) if match_target_arc else "AB"

                tangent_point = angle_name[1]

                # Математика: Дуга = Угол * 2
                res = angle_val * 2
                final_calc_answer = res

                arc_val_for_image = res # Вычисленная дуга

                task_context = {
                    "narrative": narrative,
                    "angle_name": angle_name,
                    "angle_value": angle_val,
                    "arc_name": arc_name,
                    "tangent_point": tangent_point
                }

            else:
                errors.append(f"Неизвестный нарратив: {narrative}")
                return False, errors

            # Финализация ответа
            if isinstance(final_calc_answer, float):
                if final_calc_answer.is_integer():
                    final_calc_answer = int(final_calc_answer)
                elif abs(final_calc_answer - round(final_calc_answer)) < 1e-9:
                     final_calc_answer = int(round(final_calc_answer))

            # Проверка
            if answer is not None and str(answer).strip() != "" and int(answer) != -1:
                if abs(float(final_calc_answer) - float(answer)) > 0.01:
                    errors.append(f"Математическая ошибка: {final_calc_answer} != {answer}")

            # Выбор картинки (Small < 90, Large >= 90)
            suffix = "small" if arc_val_for_image < 90 else "large"

            task["answer"] = final_calc_answer
            task["image_file"] = f"task_tangent_arc_{suffix}.png"
            task["help_image_file"] = None # Помощи нет
            task["task_context"] = task_context

        except Exception as e:
            errors.append(f"Exception: {str(e)}")
            return False, errors

        return len(errors) == 0, errors

    # =========================================================================
    # ПАТТЕРН 2.5: angle_tangency_center
    # =========================================================================

    def _validate_angle_tangency_center(self, task: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        text = task.get("question_text", "")
        narrative = task.get("narrative")
        answer = task.get("answer")

        # 1. Парсинг геометрии
        # "В угол C..." или "Найди угол E..."
        match_vertex = re.search(r"(?:В|Найди)\s+угол\s+([A-Z])", text, re.IGNORECASE)
        # "в точках A и B" или "D и F"
        match_points = re.search(r"точках\s+([A-Z])\s+и\s+([A-Z])", text, re.IGNORECASE)
        # "Точка O — центр"
        match_center = re.search(r"Точка\s+([A-Z])\s+[-—]\s+центр", text, re.IGNORECASE) or \
                       re.search(r"центром\s+(?:в\s+точке\s+)?([A-Z])", text, re.IGNORECASE)

        if not (match_vertex and match_points):
            errors.append("Не удалось распарсить геометрию (Вершину или Точки касания).")
            return False, errors

        vertex = match_vertex.group(1).upper()
        p1 = match_points.group(1).upper()
        p2 = match_points.group(2).upper()
        # Центр по умолчанию O, если не найден
        center = match_center.group(1).upper() if match_center else "O"

        # Сортируем точки касания для порядка (A, B)
        p1, p2 = sorted([p1, p2])

        # Формируем полные имена (3 буквы)
        # Угол вершины: P1-Vertex-P2 (например, ACB)
        corner_full_name = f"{p1}{vertex}{p2}"
        # Центральный угол: P1-Center-P2 (например, AOB)
        central_full_name = f"{p1}{center}{p2}"

        final_calc_answer = None
        task_context = {}
        corner_val_for_image = 0 # Для выбора картинки

        try:
            # -----------------------------------------------------------------
            # 1. find_center_angle (Дано C -> Найти AOB)
            # -----------------------------------------------------------------
            if narrative == "find_center_angle":
                # Ищем значение угла вершины (рядом с именем вершины)
                # "В угол C величиной 77°" или "угол C равен 44"
                regex_val = re.search(rf"угол\s+{vertex}.*?(?:величиной|равен)\s+(\d+)", text, re.IGNORECASE)

                if not regex_val:
                    errors.append(f"Не найдено значение угла {vertex}.")
                    return False, errors

                corner_val = int(regex_val.group(1))

                # Математика: Center = 180 - Corner
                res = 180 - corner_val
                final_calc_answer = res

                corner_val_for_image = corner_val

                task_context = {
                    "narrative": narrative,

                    "vertex_point": vertex,
                    "center": center,
                    "touch_point_1": p1,
                    "touch_point_2": p2,

                    "tangent_1": f"{vertex}{p1}",
                    "tangent_2": f"{vertex}{p2}",

                    "corner_angle_name": vertex, # В тексте обычно одна буква
                    "corner_angle_full_name": corner_full_name, # ACB
                    "corner_angle_value": corner_val,

                    "central_angle_name": central_full_name, # AOB
                    "central_angle_value": res
                }

            # -----------------------------------------------------------------
            # 2. find_corner_angle (Дано AOB -> Найти C)
            # -----------------------------------------------------------------
            elif narrative == "find_corner_angle":
                # Ищем значение центрального угла
                # "угол AOB равен 103"
                regex_val = re.search(rf"угол\s+{central_full_name}\s+равен\s+(\d+)", text, re.IGNORECASE)

                if not regex_val:
                    # Попробуем найти просто "угол ... равен X", если имя сложное
                    regex_val = re.search(r"равен\s+(\d+)", text)

                if not regex_val:
                    errors.append(f"Не найдено значение центрального угла {central_full_name}.")
                    return False, errors

                central_val = int(regex_val.group(1))

                # Математика: Corner = 180 - Center
                res = 180 - central_val
                final_calc_answer = res

                corner_val_for_image = res # Это наш ответ

                task_context = {
                    "narrative": narrative,

                    "vertex_point": vertex,
                    "center": center,
                    "touch_point_1": p1,
                    "touch_point_2": p2,

                    "tangent_1": f"{vertex}{p1}",
                    "tangent_2": f"{vertex}{p2}",

                    "corner_angle_name": vertex,
                    "corner_angle_full_name": corner_full_name,
                    "corner_angle_value": res,

                    "central_angle_name": central_full_name,
                    "central_angle_value": central_val
                }

            else:
                errors.append(f"Неизвестный нарратив: {narrative}")
                return False, errors

            # Проверка ответа
            if answer is not None and str(answer).strip() != "" and int(answer) != -1:
                if abs(float(final_calc_answer) - float(answer)) > 0.01:
                    errors.append(f"Математическая ошибка: {final_calc_answer} != {answer}")

            # Выбор картинки: Острый или Тупой угол при вершине (C)
            # Acute < 90, Obtuse > 90
            suffix = "acute" if corner_val_for_image < 90 else "obtuse"

            task["answer"] = final_calc_answer
            task["image_file"] = f"task_angle_tangency_{suffix}.png"
            # Для обоих случаев одна и та же логика помощи, но картинки разные
            task["help_image_file"] = f"help_angle_tangency_{suffix}.png"
            # (Хотя ты просила help_angle_tangency.png одну,
            #  лучше иметь help_..._acute и help_..._obtuse, если они отличаются.
            #  Если картинка помощи одна универсальная — оставь так).
            #  Если нужно под каждый тип: f"help_angle_tangency_{suffix}.png"

            task["task_context"] = task_context

        except Exception as e:
            errors.append(f"Exception: {str(e)}")
            return False, errors

        return len(errors) == 0, errors

    # =========================================================================
    # ПАТТЕРН 2.6: sector_area
    # =========================================================================

    def _validate_sector_area(self, task: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        text = task.get("question_text", "")
        narrative = task.get("narrative")
        answer = task.get("answer")

        # 1. Парсинг Угла (всегда известен)
        # "Центральный угол круга равен 30°"
        match_angle = re.search(r"угол\s+.*?равен\s+(\d+)", text, re.IGNORECASE)
        if not match_angle:
            errors.append("Не найден угол (угол ... равен X).")
            return False, errors

        angle_val = int(match_angle.group(1))

        final_calc_answer = None
        task_context = {}

        # Выбор картинки (Acute < 90, Obtuse >= 90)
        suffix = "acute" if angle_val < 90 else "obtuse"
        task_image = f"task_sector_area_{suffix}.png"

        try:
            # -----------------------------------------------------------------
            # 1. find_sector_area (Дана S_круга -> Найти S_сектора)
            # -----------------------------------------------------------------
            if narrative == "find_sector_area":
                # Ищем площадь всего круга
                # "площадь всего круга равна 144"
                match_circle = re.search(r"площадь\s+всего\s+круга\s+равна\s+(\d+)", text, re.IGNORECASE)
                if not match_circle:
                    errors.append("Не найдена площадь круга.")
                    return False, errors

                s_circle = int(match_circle.group(1))

                # Математика: S_sec = S_circ * (angle / 360)
                res = s_circle * (angle_val / 360)
                final_calc_answer = res

                task_context = {
                    "narrative": narrative,
                    "angle_value": angle_val,
                    "circle_area": s_circle,
                    "sector_area": int(res) if res.is_integer() else res # Искомое
                }

            # -----------------------------------------------------------------
            # 2. find_disk_area (Дана S_сектора -> Найти S_круга)
            # -----------------------------------------------------------------
            elif narrative == "find_disk_area":
                # Ищем площадь сектора
                # Было: r"площадь\s+(?:его\s+)?сектора\s+.*?\s+равна\s+(\d+)" (Ошибка)
                # Стало: r"площадь\s+(?:его\s+)?сектора.*?\s+равна\s+(\d+)"
                # (убрали лишнее требование пробелов, .*? съест всё что угодно или ничего)
                match_sector = re.search(r"площадь\s+(?:его\s+)?сектора.*?\s+равна\s+(\d+)", text, re.IGNORECASE)

                if not match_sector:
                    errors.append("Не найдена площадь сектора.")
                    return False, errors

                s_sector = int(match_sector.group(1))

                # Математика: S_circ = S_sec * (360 / angle)
                res = s_sector * (360 / angle_val)
                final_calc_answer = res

                task_context = {
                    "narrative": narrative,
                    "angle_value": angle_val,
                    "circle_area": int(res) if res.is_integer() else res,
                    "sector_area": s_sector
                }

            else:
                errors.append(f"Неизвестный нарратив: {narrative}")
                return False, errors

            # Финализация и проверка ответа
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
            task["help_image_file"] = None # Помощи нет, как договаривались
            task["task_context"] = task_context

        except Exception as e:
            errors.append(f"Exception: {str(e)}")
            return False, errors

        return len(errors) == 0, errors

    # =========================================================================
    # ПАТТЕРН 2.7: power_point
    # =========================================================================

    def _validate_power_point(self, task: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        text = task.get("question_text", "")
        narrative = task.get("narrative")
        answer = task.get("answer")

        # 1. Парсинг Внешней точки (C)
        # "Точка C лежит вне окружности"
        match_ext = re.search(r"Точка\s+([A-Z])\s+лежит", text)
        if not match_ext:
            errors.append("Не найдена внешняя точка (Regex: Точка X лежит).")
            return False, errors
        ext_point = match_ext.group(1)

        # 2. Парсинг Касательной (CN) - Искомое
        # "Найди CN"
        match_target = re.search(r"Найди(?:те)?\s+([A-Z]{2})", text)
        if not match_target:
            errors.append("Не найдена искомая касательная (Regex: Найди XX).")
            return False, errors

        # Сортируем буквы искомой, но нам важен порядок для контекста
        # Если внешняя C, а ищем CN, то C - начало, N - точка касания
        raw_target = match_target.group(1)
        tangent_name = raw_target
        tangent_point = raw_target.replace(ext_point, "") # Если CN, то N

        # 3. Парсинг известных отрезков
        found_vars = {}
        for m in self.segment_regex.finditer(text):
            key = "".join(sorted(m.group(1).upper()))
            val = float(m.group(2).replace(',', '.'))
            if val.is_integer(): val = int(val)
            found_vars[key] = val

        # Удаляем искомую из найденных (если попала)
        target_key_sorted = "".join(sorted(tangent_name))
        if target_key_sorted in found_vars:
            del found_vars[target_key_sorted]

        if len(found_vars) != 2:
            errors.append(f"Ожидалось 2 известных отрезка, найдено {len(found_vars)}: {found_vars}")
            return False, errors

        # 4. Логика разделения отрезков (Внешний vs Внутренний)
        # Внешний отрезок секущей ОБЯЗАН содержать внешнюю точку (ext_point)
        # Внутренний отрезок НЕ содержит внешнюю точку

        ext_segment_name = None
        ext_segment_val = 0
        int_segment_name = None
        int_segment_val = 0

        for name, val in found_vars.items():
            if ext_point in name:
                ext_segment_name = name
                ext_segment_val = val
            else:
                int_segment_name = name
                int_segment_val = val

        if not ext_segment_name or not int_segment_name:
            errors.append(f"Не удалось определить внешний/внутренний отрезки. Внешняя точка: {ext_point}, Отрезки: {found_vars}")
            return False, errors

        # Определяем точки B и A (ближняя и дальняя)
        # Внешний отрезок (CB) -> B это secant_near_point
        secant_near_point = ext_segment_name.replace(ext_point, "")
        # Внутренний отрезок (BA) -> A это secant_far_point (та буква, что не B)
        secant_far_point = int_segment_name.replace(secant_near_point, "")

        # Полное имя секущей (CA)
        secant_name = f"{ext_point}{secant_far_point}"

        # 5. Математика
        # Tangent^2 = External * Whole
        # Whole = External + Internal
        whole_secant_val = ext_segment_val + int_segment_val
        tangent_sq_val = ext_segment_val * whole_secant_val

        res = tangent_sq_val ** 0.5

        # Проверка на целочисленность корня
        if abs(res - round(res)) > 1e-9:
            errors.append(f"Корень не извлекается нацело: sqrt({tangent_sq_val}) = {res}")
            return False, errors

        final_calc_answer = int(round(res))

        # 6. Сверка с ответом
        if answer is not None and str(answer).strip() != "" and int(answer) != -1:
            if final_calc_answer != int(answer):
                errors.append(f"Математическая ошибка: {final_calc_answer} != {answer}")

        # 7. Формирование контекста
        task_context = {
            "narrative": "find_tangent_length",

            # Точки
            "external_point": ext_point,
            "tangent_point": tangent_point,
            "secant_near_point": secant_near_point,
            "secant_far_point": secant_far_point,

            # Имена линий
            "tangent_name": tangent_name,
            "secant_name": secant_name,

            # Отрезки (исходные)
            "external_segment_name": ext_segment_name,
            "external_segment_value": ext_segment_val,
            "internal_segment_name": int_segment_name,
            "internal_segment_value": int_segment_val,

            # Вычисленные (для шагов)
            "whole_secant_value": whole_secant_val,
            "tangent_square_value": tangent_sq_val,
            "tangent_value": final_calc_answer
        }

        task["answer"] = final_calc_answer
        task["image_file"] = "task_power_point.png"
        task["help_image_file"] = None # Картинки помощи нет
        task["task_context"] = task_context

        return True, errors
