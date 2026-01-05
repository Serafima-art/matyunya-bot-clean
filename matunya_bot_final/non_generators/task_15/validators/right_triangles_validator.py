import re
from typing import Any, Dict

ANGLE_SYMBOL = "∠"

def extract_target_angle(text: str) -> str:
    """
    Строго извлекает целевой угол для sin/cos/tg.
    Возвращает 'A', 'B' или 'C'.
    Если угол не найден или найдено несколько — бросает ошибку.
    """

    patterns = [
        r"(?:sin|cos|tg)\s*([ABC])",
        r"(?:синус|косинус|тангенс)\s+(?:угла\s+)?([ABC])",
    ]

    found = []

    for pattern in patterns:
        matches = re.findall(pattern, text, re.I)
        for m in matches:
            found.append(m.upper())

    found = list(set(found))  # убираем дубли

    if len(found) == 0:
        raise ValueError("Не удалось определить целевой угол (sin/cos/tg без указания угла)")

    if len(found) > 1:
        raise ValueError(f"Найдено несколько целевых углов: {found}")

    return found[0]

class RightTrianglesValidator:
    """Валидатор для ТЕМЫ 4: Прямоугольные треугольники."""

    def __init__(self) -> None:
        self.handlers = {
            # 4.1 Сумма острых углов
            "right_triangle_angles_sum": self._handle_angles_sum,
            # 4.2 Теорема Пифагора (ищем катет)
            "pythagoras_find_leg": self._handle_pythagoras_leg,
            # 4.3 Теорема Пифагора (ищем гипотенузу)
            "pythagoras_find_hypotenuse": self._handle_pythagoras_hypotenuse,
            # 4.4 Синус, косинус, тангенс по сторонам
            "find_cos_sin_tg_from_sides": self._handle_trig_from_sides,
            # 4.5 Сторона по тригонометрическому соотношению
            "find_side_from_trig_ratio": self._handle_side_from_trig,
            # 4.6 Медиана к гипотенузе
            "right_triangle_median_to_hypotenuse": self._handle_median_to_hypotenuse,
        }

    def validate(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Основной диспетчер валидации."""
        pattern = raw.get("pattern")
        if pattern not in self.handlers:
            raise ValueError(f"Неизвестный паттерн в ТЕМЕ 4: {pattern}")
        return self.handlers[pattern](raw)

    # -----------------------------------------------------------
    # Паттерн 4.1: Сумма острых углов (right_triangle_angles_sum)
    # -----------------------------------------------------------
    def _handle_angles_sum(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        text = raw["text"]
        task_id = raw.get("id")

        # 1. Извлекаем ВСЕ числа из текста
        all_numbers = re.findall(r"(\d+)", text)

        # 2. Ищем среди них острый угол (число, которое не равно 90)
        angle_val = None
        for num_str in all_numbers:
            num = int(num_str)
            if num != 90: # Игнорируем прямой угол
                angle_val = num
                break

        if angle_val is None:
            raise ValueError(f"Острый угол (не 90°) не найден в задаче {task_id}")

        # 3. Расчет
        answer = 90 - angle_val

        # 4. Формируем "Финальный Эталон"
        return {
            "id": task_id,
            "pattern": "right_triangle_angles_sum",
            "narrative": "find_second_acute_angle",
            "text": text,
            "answer": answer,
            "image_file": None,  # Убираем картинку
            "variables": {
                "given": {
                    "triangle_type": "right",
                    "angle_alpha": angle_val
                },
                "to_find": {
                    "type": "angle",
                    "role": "second_acute"
                },
                "humanizer_data": {
                    "sum_total": 90,
                    "angle_symbol": ANGLE_SYMBOL
                }
            }
        }

    # -----------------------------------------------------------
    # Паттерн 4.2: Нахождение катета (pythagoras_find_leg)
    # -----------------------------------------------------------
    def _handle_pythagoras_leg(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        text = raw["text"]
        task_id = raw.get("id")

        # 1. Извлекаем все числа из текста
        numbers = [int(n) for n in re.findall(r"(\d+)", text)]

        # Нам нужно как минимум 2 числа
        if len(numbers) < 2:
            raise ValueError(f"Недостаточно данных для теоремы Пифагора в задаче {task_id}")

        # 2. Определяем роли: в прямоугольном треугольнике гипотенуза — самое большое число
        c = max(numbers)
        a = min(numbers)

        # 3. Расчет по теореме Пифагора: b = sqrt(c^2 - a^2)
        answer_sq = c**2 - a**2
        answer = answer_sq**0.5

        # 4. Проверка на целое число (для ОГЭ катеты обычно целые или красивые десятичные)
        if not answer.is_integer():
            answer = round(answer, 2)
        else:
            answer = int(answer)

        # 5. Сборка JSON
        return {
            "id": task_id,
            "pattern": "pythagoras_find_leg",
            "narrative": "find_leg_by_hypotenuse_and_leg",
            "text": text,
            "answer": answer,
            "image_file": None,  # Убираем картинку
            "variables": {
                "given": {
                    "triangle_type": "right",
                    "hypotenuse": c,
                    "known_leg": a
                },
                "to_find": {
                    "type": "side",
                    "role": "unknown_leg"
                },
                "humanizer_data": {
                    "formula": "b² = c² - a²",
                    "c_squared": c**2,
                    "a_squared": a**2,
                    "diff": answer_sq
                }
            }
        }

    # -----------------------------------------------------------
    # Паттерн 4.3: Нахождение гипотенузы (pythagoras_find_hypotenuse)
    # -----------------------------------------------------------
    def _handle_pythagoras_hypotenuse(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        text = raw["text"]
        task_id = raw.get("id")

        # 1. Извлекаем все числа
        numbers = [int(n) for n in re.findall(r"(\d+)", text)]

        if len(numbers) < 2:
            raise ValueError(f"Недостаточно данных для поиска гипотенузы в задаче {task_id}")

        # 2. В этом паттерне оба числа — катеты
        a, b = numbers[0], numbers[1]

        # 3. Расчет: c = sqrt(a^2 + b^2)
        sum_sq = a**2 + b**2
        answer = sum_sq**0.5

        if not answer.is_integer():
            answer = round(answer, 2)
        else:
            answer = int(answer)

        # 4. Сборка JSON (image_file теперь null)
        return {
            "id": task_id,
            "pattern": "pythagoras_find_hypotenuse",
            "narrative": "find_hypotenuse_by_legs",
            "text": text,
            "answer": answer,
            "image_file": None,  # Убираем картинку
            "variables": {
                "given": {
                    "triangle_type": "right",
                    "leg_1": a,
                    "leg_2": b
                },
                "to_find": {
                    "type": "side",
                    "role": "hypotenuse"
                },
                "humanizer_data": {
                    "formula": "c² = a² + b²",
                    "a_squared": a**2,
                    "b_squared": b**2,
                    "sum_squared": sum_sq
                }
            }
        }

    # -----------------------------------------------------------
    # Паттерн 4.4: Тригонометрия по сторонам (find_cos_sin_tg_from_sides)
    # -----------------------------------------------------------
    def _handle_trig_from_sides(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        text = raw["text"]
        task_id = raw.get("id")

        # -------------------------------------------------------
        # 1. Сбор данных о сторонах
        # -------------------------------------------------------
        side_values = {}

        found = re.findall(
            r"([A-Z]{2})\s*(?:=|:|равна|равен|равны)\s*([\d,.]+)",
            text
        )
        for name, val in found:
            side_values[frozenset(name.upper())] = float(val.replace(",", "."))

        multi = re.search(
            r"([A-Z]{2})\s+и\s+([A-Z]{2})\s+равны\s+([\d,.]+)\s+и\s+([\d,.]+)",
            text
        )
        if multi:
            n1, n2, v1, v2 = multi.groups()
            side_values[frozenset(n1.upper())] = float(v1.replace(",", "."))
            side_values[frozenset(n2.upper())] = float(v2.replace(",", "."))

        def get_v(a: str, b: str) -> float:
            return side_values.get(frozenset([a.upper(), b.upper()]), 0.0)

        # -------------------------------------------------------
        # 2. ЯВНОЕ определение прямого угла (высший приоритет)
        # -------------------------------------------------------
        def extract_explicit_right_angle(text: str) -> str | None:
            """
            Определяет вершину прямого угла по явной формулировке в тексте.

            Поддерживаемые реальные формулировки:
            - угол A = 90°, ∠B = 90°, угол C равен 90
            - угол B — прямой, угол C прямой
            - прямой угол A, прямым углом B
            - с прямым углом C, имеет прямой угол A
            - в прямоугольном треугольнике ABC угол B — прямой
            """

            t = text.replace("∠", "угол ").lower()

            patterns = [
                # угол A = 90°, угол B равен 90
                r"\bугол\s*([abc])\s*(=|равен)\s*90",

                # угол C прямой / угол B — прямой
                r"\bугол\s*([abc])\s*[—-]?\s*прям",

                # прямой угол A / прямым углом B
                r"\bпрям(ой|ым)\s*угл(ом|а)\s*([abc])",

                # с прямым углом B / имеет прямой угол C
                r"\b(с|имеет)\s*прям(ым|ой)?\s*угл(ом|а)?\s*([abc])",

                # в прямоугольном треугольнике ABC угол B — прямой
                r"\bпрямоугольн\w*\s+треугольник\w*\s+abc.*?угол\s*([abc])",
            ]

            for p in patterns:
                m = re.search(p, t, re.IGNORECASE | re.DOTALL)
                if not m:
                    continue
                for g in m.groups():
                    if g and g.upper() in ("A", "B", "C"):
                        return g.upper()

            return None


        explicit_right = extract_explicit_right_angle(text)

        if explicit_right:
            right_angle = explicit_right
        else:
            raise ValueError(
                "Не удалось определить прямой угол треугольника. "
                "Ожидается явная формулировка, например: "
                "'угол A = 90°', '∠B = 90°', 'угол C прямой', "
                "'прямой угол A', 'с прямым углом B', "
                "'в прямоугольном треугольнике ABC угол B — прямой'."
            )

        # -------------------------------------------------------
        # 3. Целевая функция
        # -------------------------------------------------------
        text_l = text.lower()
        if "tg" in text_l or "тангенс" in text_l:
            target_fn = "tg"
        elif "cos" in text_l or "косинус" in text_l:
            target_fn = "cos"
        else:
            target_fn = "sin"

        # -------------------------------------------------------
        # 4. Целевой угол
        # -------------------------------------------------------
        angle_match = re.search(
            r"(?:sin|cos|tg|синус|косинус|тангенс)\s+([ABC])",
            text,
            re.I
        )
        if not angle_match:
            angle_match = re.search(r"угла\s+([ABC])", text, re.I)

        if not angle_match:
            raise ValueError("Не удалось определить целевой угол")

        target_angle = angle_match.group(1).upper()

        # ❗ ВАЖНО: если целевой угол совпал с прямым — это ошибка задачи
        if target_angle == right_angle:
            raise ValueError(
                f"Целевой угол {target_angle} является прямым — тригонометрия невозможна"
            )

        # -------------------------------------------------------
        # 5. Определение вершин
        # -------------------------------------------------------
        other_vertex = list({"A", "B", "C"} - {right_angle, target_angle})[0]

        # -------------------------------------------------------
        # 6. Стороны (ЭТАЛОННАЯ ВЕРСИЯ)
        # -------------------------------------------------------

        hyp, adj, opp, derived = resolve_triangle_sides(
            right_angle=right_angle,
            target_angle=target_angle,
            get_v=get_v,
        )

        # -------------------------------------------------------
        # 7. Вычисление
        # -------------------------------------------------------
        if target_fn == "sin":
            ans = opp / hyp
            formula = "противолежащий катет / гипотенуза"
            ratio = f"{round(opp,1)} / {round(hyp,1)}"
        elif target_fn == "cos":
            ans = adj / hyp
            formula = "прилежащий катет / гипотенуза"
            ratio = f"{round(adj,1)} / {round(hyp,1)}"
        else:
            ans = opp / adj
            formula = "противолежащий катет / прилежащий катет"
            ratio = f"{round(opp,1)} / {round(adj,1)}"

        # -------------------------------------------------------
        # 8. JSON
        # -------------------------------------------------------
        n_opp = "".join(sorted([right_angle, other_vertex]))
        n_adj = "".join(sorted([right_angle, target_angle]))
        n_hyp = "".join(sorted([target_angle, other_vertex]))

        return {
            "id": task_id,
            "pattern": "find_cos_sin_tg_from_sides",
            "text": text,
            "answer": round(ans, 2),
            "image_file": f"T3_right_{right_angle}.png",
            "variables": {
                "given": {
                    n_opp: round(opp, 2),
                    n_adj: round(adj, 2),
                    n_hyp: round(hyp, 2),
                },
                "target": {
                    "fn": target_fn,
                    "angle": target_angle,
                    "right_angle": right_angle,
                },
                "humanizer_data": {
                    "formula_name": formula,
                    "ratio_values": ratio,
                    "opp_leg": n_opp,
                    "adj_leg": n_adj,
                    "hypotenuse": n_hyp,
                    "derived": derived,
                },
            },
        }

    # ----------------------------------------------------------
    # Паттерн 4.5: Нахождение стороны по sin, cos, tg
    # -----------------------------------------------------------
    def _handle_side_from_trig(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        text = raw["text"]
        task_id = raw.get("id")

        # -------------------------------------------------------
        # 1. Определяем прямой угол (ТОЧНО как в 4.4)
        # -------------------------------------------------------
        def extract_explicit_right_angle(text: str) -> str:
            t = text.replace("∠", "угол ").lower()

            patterns = [
                r"\bугол\s*([abc])\s*(=|равен)\s*90",
                r"\bугол\s*([abc])\s*[—-]?\s*прям",
                r"\bпрям(ой|ым)\s*угл(ом|а)\s*([abc])",
                r"\b(с|имеет)\s*прям(ым|ой)?\s*угл(ом|а)?\s*([abc])",
                r"\bпрямоугольн\w*\s+треугольник\w*\s+abc.*?угол\s*([abc])",
            ]

            for p in patterns:
                m = re.search(p, t, re.IGNORECASE | re.DOTALL)
                if not m:
                    continue
                for g in m.groups():
                    if g and g.upper() in ("A", "B", "C"):
                        return g.upper()

            raise ValueError("Не удалось определить прямой угол")

        right_angle = extract_explicit_right_angle(text)

        # -------------------------------------------------------
        # 2. Определяем тригонометрическую функцию
        # -------------------------------------------------------
        text_l = text.lower()
        if "tg" in text_l or "тангенс" in text_l:
            trig_fn = "tg"
        elif "cos" in text_l or "косинус" in text_l:
            trig_fn = "cos"
        elif "sin" in text_l or "синус" in text_l:
            trig_fn = "sin"
        else:
            raise ValueError("Не удалось определить sin / cos / tg")

        # -------------------------------------------------------
        # 3. Определяем угол, при котором задана функция
        # -------------------------------------------------------
        target_angle = extract_target_angle(text)

        if target_angle == right_angle:
            raise ValueError("Тригонометрическая функция задана при прямом угле")

        other_vertex = list({"A", "B", "C"} - {right_angle, target_angle})[0]

        # -------------------------------------------------------
        # 4. Извлекаем числовые значения
        # -------------------------------------------------------
        ratio_match = re.search(r"=\s*([\d,.]+)\s*/\s*([\d,.]+)", text)
        if not ratio_match:
            raise ValueError("Не удалось извлечь значение тригонометрического отношения")

        num = float(ratio_match.group(1).replace(",", "."))
        den = float(ratio_match.group(2).replace(",", "."))

        value = num / den

        side_match = re.search(
            r"([A-Z]{2})\s*(?:=|равен|равна)\s*([\d,.]+)",
            text
        )
        if not side_match:
            raise ValueError("Не удалось извлечь заданную сторону")

        known_side_name = side_match.group(1).upper()
        known_side_val = float(side_match.group(2).replace(",", "."))

        # -------------------------------------------------------
        # 5. Имена сторон
        # -------------------------------------------------------
        hyp_name = "".join(sorted({"A", "B", "C"} - {right_angle}))
        adj_name = "".join(sorted({right_angle, target_angle}))
        opp_name = "".join(sorted({right_angle, other_vertex}))

        # -------------------------------------------------------
        # 6. Вычисление искомой стороны
        # -------------------------------------------------------
        if trig_fn == "sin":
            # sin = opp / hyp
            if known_side_name == hyp_name:
                opp = value * known_side_val
                hyp = known_side_val
                adj = (hyp**2 - opp**2) ** 0.5
                find = opp_name
            else:
                opp = known_side_val
                hyp = opp / value
                adj = (hyp**2 - opp**2) ** 0.5
                find = hyp_name

        elif trig_fn == "cos":
            # cos = adj / hyp
            if known_side_name == hyp_name:
                adj = value * known_side_val
                hyp = known_side_val
                opp = (hyp**2 - adj**2) ** 0.5
                find = adj_name
            else:
                adj = known_side_val
                hyp = adj / value
                opp = (hyp**2 - adj**2) ** 0.5
                find = hyp_name

        else:
            # tg = opp / adj
            if known_side_name == adj_name:
                opp = value * known_side_val
                adj = known_side_val
                hyp = (opp**2 + adj**2) ** 0.5
                find = opp_name
            else:
                opp = known_side_val
                adj = opp / value
                hyp = (opp**2 + adj**2) ** 0.5
                find = adj_name

        answer = round(
            {"hyp": hyp, "adj": adj, "opp": opp}[
                "hyp" if find == hyp_name else
                "adj" if find == adj_name else
                "opp"
            ],
            2
        )

        # -------------------------------------------------------
        # 7. Финальный JSON
        # -------------------------------------------------------
        return {
            "id": task_id,
            "pattern": "find_side_from_trig_ratio",
            "text": text,
            "answer": answer,
            "image_file": f"T3_right_{right_angle}.png",
            "variables": {
                "given": {
                    "trig_fn": trig_fn,
                    "angle": target_angle,
                    known_side_name: known_side_val,
                },
                "target": {
                    "find": find,
                    "right_angle": right_angle,
                },
                "humanizer_data": {
                    "ratio": f"{num}/{den}",
                    "formula": f"{trig_fn} = {num}/{den}",
                },
            },
        }

    # -----------------------------------------------------------
    # Паттерн 4.6: Свойство медианы к гипотенузе (right_triangle_median_to_hypotenuse)
    # -----------------------------------------------------------
    def _handle_median_to_hypotenuse(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Логика: Медиана, проведенная к гипотенузе, равна её половине.
        """
        raise NotImplementedError("Паттерн 4.6 еще не реализован")


# =======================================================
# Helper: восстановление сторон прямоугольного треугольника
# Используется в тригонометрических паттернах (4.x)
# =======================================================

def resolve_triangle_sides(
    *,
    right_angle: str,
    target_angle: str,
    get_v,
):
    """
    Надёжно определяет гипотенузу, прилежащий и противолежащий катеты.
    НИКОГДА не гадает. Сначала доверяет данным, затем применяет Пифагора.
    """

    vertices = {"A", "B", "C"}
    other_vertex = list(vertices - {right_angle, target_angle})[0]

    # --- Имена сторон ---
    hyp_name = "".join(sorted(vertices - {right_angle}))       # сторона напротив прямого угла
    adj_name = "".join(sorted({right_angle, target_angle}))    # прилежащий катет
    opp_name = "".join(sorted({right_angle, other_vertex}))    # противолежащий катет

    # --- Считываем заданные значения ---
    hyp = get_v(hyp_name[0], hyp_name[1])
    adj = get_v(adj_name[0], adj_name[1])
    opp = get_v(opp_name[0], opp_name[1])

    derived = None

    # --- Если все три есть — просто проверяем ---
    if hyp and adj and opp:
        if hyp <= max(adj, opp):
            raise ValueError(
                f"Некорректные стороны: гипотенуза {hyp} "
                f"должна быть больше катетов {adj}, {opp}"
            )
        return hyp, adj, opp, derived

    # --- Восстанавливаем недостающую сторону ---
    if not hyp and adj and opp:
        hyp = (adj ** 2 + opp ** 2) ** 0.5
        derived = "hyp"

    elif not adj and hyp and opp:
        diff = hyp ** 2 - opp ** 2
        if diff <= 0:
            raise ValueError(
                f"Некорректные стороны: гипотенуза {hyp} "
                f"меньше или равна катету {opp}"
            )
        adj = diff ** 0.5
        derived = "adj"

    elif not opp and hyp and adj:
        diff = hyp ** 2 - adj ** 2
        if diff <= 0:
            raise ValueError(
                f"Некорректные стороны: гипотенуза {hyp} "
                f"меньше или равна катету {adj}"
            )
        opp = diff ** 0.5
        derived = "opp"

    else:
        raise ValueError(
            "Недостаточно данных для восстановления сторон треугольника"
        )

    return hyp, adj, opp, derived

def extract_right_angle(text: str) -> str:
    """
    Возвращает вершину прямого угла: A, B или C.
    Бросает ошибку, если определить невозможно.
    """

    text_l = text.lower()

    # Явные указания
    if re.search(r"(угол|∠)\s*a\s*(=|равен)?\s*90|a\s*=\s*90|прям.*a", text_l):
        return "A"
    if re.search(r"(угол|∠)\s*b\s*(=|равен)?\s*90|b\s*=\s*90|прям.*b", text_l):
        return "B"
    if re.search(r"(угол|∠)\s*c\s*(=|равен)?\s*90|c\s*=\s*90|прям.*c", text_l):
        return "C"

    raise ValueError("Не удалось определить прямой угол треугольника")
