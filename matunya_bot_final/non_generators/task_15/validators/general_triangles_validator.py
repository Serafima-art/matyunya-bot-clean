# matunya_bot_final/non_generators/task_15/validators/general_triangles_validator.py
"""
General triangles validator for Task 15 (Etalon JSON).
This module parses raw text tasks and builds structured JSON without doing SVG drawing.
Math is NOT implemented yet — only structure, routing, and placeholders.
"""

from __future__ import annotations
import re
from typing import Dict, Any, Optional
import math


class GeneralTrianglesValidator:
    """
    Main dispatcher for all general-triangle patterns:
      - triangle_area_by_sin
      - triangle_area_by_dividing_point
      - triangle_area_by_parallel_line
      - triangle_area_by_midpoints
      - cosine_law_find_cos
      - triangle_by_two_angles_and_side
      - trig_identity_find_trig_func
    """

    # ============================================================
    # ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ПАРСИНГА ЧИСЕЛ ИЗ ТЕКСТА
    # ============================================================

    def _extract_number_after_label(self, text: str, label: str) -> float | None:
        """
        Ищет в тексте конструкцию вида:
        'AC = 20', 'MN=12', 'AB = 21' и т.п.

        Возвращает число (int или float), либо None, если не нашли.
        """
        pattern = rf"{label}\s*=\s*([0-9]+(?:\.[0-9]+)?)"
        m = re.search(pattern, text)
        if not m:
            return None
        value_str = m.group(1)
        # сначала пробуем int, потом float
        try:
            return int(value_str)
        except ValueError:
            try:
                return float(value_str)
            except ValueError:
                return None

    def _extract_number_after_phrase(self, text: str, phrase_regex: str) -> float | None:
        """
        Ищет число после некой фразы, например:
        phrase_regex = r"площад[ь]*\\s+треугольника\\s+ABC"

        Тогда в тексте:
        'Площадь треугольника ABC равна 150. Найдите ...'
        вернёт 150.

        phrase_regex — уже готовый кусок регэкспа без внешних /.../.
        """
        # ищем: (фраза) + любые НЕЦИФРЫ + число
        pattern = rf"{phrase_regex}[^0-9\-]*(-?[0-9]+(?:\.[0-9]+)?)"
        m = re.search(pattern, text, flags=re.IGNORECASE)
        if not m:
            return None
        value_str = m.group(1)
        try:
            return int(value_str)
        except ValueError:
            try:
                return float(value_str)
            except ValueError:
                return None

    def _parse_numeric_with_root(self, token: str) -> float:
        """
        Универсальный парсер чисел: 10, 3.5, 4/5, 10√3, √5, (2√6)/5.
        """
        cleaned = token.strip().replace(",", ".").rstrip('.')

        numerator = 1.0
        denominator = 1.0

        # Сначала разбираемся с дробью, если она есть
        if "/" in cleaned:
            num_part, den_part = cleaned.split("/", 1)
            denominator = float(den_part)
            cleaned = num_part

        # Теперь работаем с числителем (который может содержать корень)
        if "√" in cleaned:
            # Убираем скобки, если они есть
            cleaned = cleaned.strip("()")

            coef_part, root_part = cleaned.split("√", 1)
            coef = float(coef_part) if coef_part not in ("", "+", "-") else (1.0 if coef_part != "-" else -1.0)
            radicand = float(root_part) if root_part else 0.0
            numerator = coef * math.sqrt(radicand)
        else:
            numerator = float(cleaned)

        return numerator / denominator

    def _format_number(self, value: float | int | None) -> float | int | str | None:
        """
        Приводит число к int при целостности, иначе к строке с запятой и без лишних хвостов.
        """
        if value is None:
            return None
        rounded = round(float(value))
        if abs(float(value) - rounded) < 1e-9:
            return int(rounded)
        text = f"{float(value):.4f}".rstrip("0").rstrip(".")
        return text.replace(".", ",")

    def __init__(self) -> None:
        self.handlers = {
            "triangle_area_by_sin": self._handle_triangle_area_by_sin,
            "triangle_area_by_dividing_point": self._handle_triangle_area_by_dividing_point,
            "triangle_area_by_parallel_line": self._handle_triangle_area_by_parallel_line,
            "triangle_area_by_midpoints": self._handle_triangle_area_by_midpoints,
            "cosine_law_find_cos": self._handle_cosine_law_find_cos,
            "triangle_by_two_angles_and_side": self._handle_triangle_by_two_angles_and_side,
            "trig_identity_find_trig_func": self._handle_trig_identity_find_trig_func,
        }

    def _parse_to_find_parallel_line(self, text: str) -> dict:
        """
        Понимает, что нужно найти в задачах с MN || AC.
        Возвращает:
        - {"type": "area", "name": "S_ABC"|"S_MBN"}
        - {"type": "side", "name": "MN"|"AC"|...}
        - {"type": "ratio", "name": "MN/AC"|"AC/MN"}
        """
        m = re.search(
            r"найд[^\n\r]*?(?:площад[ьи]\s+)?(?:отношение\s+)?([A-Z]{2,3}(?:\s*[:/]\s*[A-Z]{2})?)",
            text,
            flags=re.IGNORECASE
        )
        if not m:
            raise ValueError("Не удалось определить, что нужно найти (ожидаю 'Найди ...').")

        target = m.group(1).strip().upper().replace(" ", "")

        # отношение
        if "/" in target or ":" in target:
            target = target.replace(":", "/")
            if target not in ("MN/AC", "AC/MN"):
                # Если встретится что-то нестандартное — лучше явно упасть
                raise ValueError(f"Неизвестное отношение в вопросе: {target}")
            return {"type": "ratio", "name": target}

        # площадь
        if target in ("ABC", "MBN"):
            return {"type": "area", "name": f"S_{target}"}

        # сторона/отрезок
        return {"type": "side", "name": target}

    # ============================================================
    # PUBLIC API
    # ============================================================

    def validate(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch validation to the correct pattern handler."""
        pattern = raw.get("pattern")
        if pattern not in self.handlers:
            raise ValueError(f"Unsupported general-triangle pattern: {pattern}")
        return self.handlers[pattern](raw)

    # ============================================================
    # PATTERN 2.1
    # triangle_area_by_sin
    # ============================================================

    def _handle_triangle_area_by_sin(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Парсит две стороны и либо sin(угла), либо сам угол.
        Вычисляет площадь и возвращает Etalon 3.0 JSON.
        ВЕРСИЯ 6 (ФИНАЛ): В given.sides сохраняются СТРОКИ, а не числа.
        """
        text = raw["text"]

        # --- 1. Извлечение сторон (с сохранением raw-строк) ---
        sides_for_calc: Dict[str, float] = {}
        sides_for_json: Dict[str, str] = {}

        def add_side(name: str, value_str: str):
            clean_name = name.upper()
            clean_value = value_str.strip().rstrip(".,")
            if clean_name not in sides_for_calc:
                sides_for_calc[clean_name] = self._parse_numeric_with_root(clean_value)
                sides_for_json[clean_name] = clean_value

        for match in re.finditer(r"\b(AB|BC|AC)\s*=\s*([0-9.,√]+)", text, flags=re.IGNORECASE):
            add_side(match.group(1), match.group(2))
        pattern_b = re.search(r"(?:стороны|сторона)\s+(AB|BC|AC)\s+и\s+(AB|BC|AC)[^=]*?(?:равны|=)\s*([0-9.,√]+)\s+и\s+([0-9.,√]+)", text, flags=re.IGNORECASE)
        if pattern_b: s1, s2, v1, v2 = pattern_b.groups(); add_side(s1, v1); add_side(s2, v2)
        pattern_c = re.search(r"\b(AB|BC|AC)\s+и\s+(AB|BC|AC)\s+(?:равны|=)\s*([0-9.,√]+)\s+и\s+([0-9.,√]+)", text, flags=re.IGNORECASE)
        if pattern_c: s1, s2, v1, v2 = pattern_c.groups(); add_side(s1, v1); add_side(s2, v2)
        pattern_d = re.search(r"(?:стороны|сторона)\s+(AB|BC|AC)\s+и\s+(AB|BC|AC)[^=]*?(?:равны|=)\s*([0-9.,√]+)(?!\s+и)", text, flags=re.IGNORECASE)
        if pattern_d: s1, s2, v = pattern_d.groups(); add_side(s1, v); add_side(s2, v)

        # --- 2. Парсинг угла (sin или градусы) ---
        angle_letter: Optional[str] = None
        sin_value_num: Optional[float] = None
        trig_info: Dict[str, str] = {}
        angle_display_name: Optional[str] = None
        found_degrees: Optional[int] = None
        angles_info: Dict[str, int] = {}

        def get_angle_letter_from_spec(spec: str) -> str: return spec[1] if len(spec) == 3 else spec[0]

        sin_match = re.search(r"sin\s*[∠]?\s*([ABC]{1,3})\s*(?:=|равен|равна)?\s*([0-9]+/[0-9]+|[0-9.,]+)", text, flags=re.IGNORECASE)
        angle_match = re.search(r"(?:угол|∠)\s*([A-Z]{1,3})\s*(?:=|равен|равна)\s*(\d+)", text, flags=re.IGNORECASE)
        between_match = re.search(r"(?:синус|sin)\s+угла\s+между\s+ними(?:=|равен|равна)?\s*([0-9]+/[0-9]+|[0-9.,]+)", text, flags=re.IGNORECASE)

        if sin_match:
            angle_spec, sin_value_raw = sin_match.groups()
            angle_spec = angle_spec.upper()
            angle_letter = get_angle_letter_from_spec(angle_spec)
            sin_value_raw = sin_value_raw.strip().replace(",", ".").rstrip(".")
            trig_info[f"sin_{angle_letter}"] = sin_value_raw
            angle_display_name = f"∠{angle_spec}"
            if "/" in sin_value_raw: sin_value_num = float(sin_value_raw.split('/')[0]) / float(sin_value_raw.split('/')[1])
            else: sin_value_num = float(sin_value_raw)

        elif angle_match:
            angle_spec, degrees_str = angle_match.groups()
            angle_spec, degrees = angle_spec.upper(), int(degrees_str)
            angle_letter = get_angle_letter_from_spec(angle_spec)
            found_degrees = degrees
            angles_info[angle_letter] = degrees
            sin_map = {30:0.5, 45:math.sqrt(2)/2, 60:math.sqrt(3)/2, 90:1.0, 120:math.sqrt(3)/2, 135:math.sqrt(2)/2, 150:0.5}
            if degrees in sin_map: sin_value_num = sin_map[degrees]; angle_display_name = f"∠{angle_spec}"

        elif between_match and len(sides_for_calc) == 2:
            s1, s2 = list(sides_for_calc.keys())
            common_vertex = list(set(s1) & set(s2))
            if common_vertex:
                angle_letter = common_vertex[0]
                sin_value_raw = between_match.group(1).strip().replace(",", ".").rstrip(".")
                trig_info[f"sin_{angle_letter}"] = sin_value_raw
                angle_display_name = f"∠{angle_letter}"
                if "/" in sin_value_raw: sin_value_num = float(sin_value_raw.split('/')[0]) / float(sin_value_raw.split('/')[1])
                else: sin_value_num = float(sin_value_raw)

        # --- 3. Вычисление площади (используем числовые значения) ---
        area: Optional[float] = None
        side_pairs = {"A": ("AB", "AC"), "B": ("AB", "BC"), "C": ("AC", "BC")}
        if angle_letter in side_pairs and sin_value_num is not None:
            side1 = sides_for_calc.get(side_pairs[angle_letter][0])
            side2 = sides_for_calc.get(side_pairs[angle_letter][1])
            if side1 is not None and side2 is not None: area = 0.5 * side1 * side2 * sin_value_num

        # --- 4. Выбор картинки ---
        image_file = "T3_acute.svg"
        if found_degrees and found_degrees > 90: image_file = f"T3_obtuse_{angle_letter}.svg"

        # --- 5. Сборка JSON строго по эталону ---
        return {
            "id": raw.get("id"), "pattern": "triangle_area_by_sin", "text": text,
            "answer": self._format_number(area), "image_file": image_file,
            "variables": {
                "given": {
                    "triangle_name": "ABC", "triangle_type": "general",
                    # ИСПРАВЛЕНО: в sides теперь всегда "красивые" СТРОКИ
                    "sides": sides_for_json,
                    "angles": angles_info, "trig": trig_info, "elements": {}, "points": {}, "relations": {},
                },
                "to_find": {"type": "area", "name": "S_ABC"},
                "humanizer_data": {
                    "side_roles": {},
                    "angle_names": {angle_letter: angle_display_name} if angle_letter else {},
                    # element_names больше не нужен, т.к. sides хранит строки
                    "element_names": {},
                },
            },
        }

    # ============================================================
    # PATTERN 2.2
    # triangle_area_by_dividing_point
    # ============================================================

    def _handle_triangle_area_by_dividing_point(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Читаем AD/DC или их отношение, площади, определяем, что искать,
        считаем ответ и собираем Etalon 3.0.
        ВЕРСИЯ 8 (ФИНАЛ): Оригинальная структура + точечные добавления.
        """
        text = raw["text"]
        text_lower = text.lower()

        # --- Исходные стабильные функции ---
        def parse_number(value: str) -> float:
            return float(value.strip().replace(",", "."))

        def extract_area(patterns: list[str]) -> float | None:
            for pattern in patterns:
                match = re.search(pattern, text, flags=re.IGNORECASE)
                if match:
                    return parse_number(match.group(1))
            return None

        def asks_for(target: str) -> bool:
            if re.search(rf"(найти|найдите|вычислите|определите)[^.]*\b{target}\b", text_lower): return True
            if re.search(rf"(найти|найдите|вычислите|определите)[^.]*площад[ьи][^.]*{target}", text_lower): return True
            if re.search(rf"найд[^\n\r]*площад[ьи][^\n\r]*{target}", text_lower): return True
            return False

        # --- 1. Считываем AD и DC (с новыми паттернами) ---
        AD, DC = None, None
        for name, value in re.findall(r"(AD|DC)\s*=\s*([0-9]+(?:[.,][0-9]+)?)", text, flags=re.IGNORECASE):
            if name.upper() == "AD": AD = parse_number(value)
            else: DC = parse_number(value)
        ratio = re.search(r"AD\s*:\s*DC\s*=\s*([0-9]+)\s*:\s*([0-9]+)", text, flags=re.IGNORECASE)
        if ratio: AD, DC = parse_number(ratio.group(1)), parse_number(ratio.group(2))
        ratio_rev = re.search(r"DC\s*:\s*AD\s*=\s*([0-9]+)\s*:\s*([0-9]+)", text, flags=re.IGNORECASE)
        if ratio_rev: DC, AD = parse_number(ratio_rev.group(1)), parse_number(ratio_rev.group(2))
        ratio_plain = re.search(r"в\s+отношени[ии]\s*([0-9]+)\s*[:]\s*([0-9]+)", text_lower)
        if ratio_plain: AD, DC = parse_number(ratio_plain.group(1)), parse_number(ratio_plain.group(2))
        mult_ratio = re.search(r"(DC|AD)\s*=\s*([0-9]+)\s*\*\s*(AD|DC)", text, flags=re.IGNORECASE)
        if mult_ratio:
            s1, val, s2 = mult_ratio.groups()
            if s1 == "DC" and s2 == "AD": AD, DC = 1.0, parse_number(val)
            elif s1 == "AD" and s2 == "DC": DC, AD = 1.0, parse_number(val)

        # --- 2. Читаем площади (с новыми паттернами) ---
        S_ABC = extract_area([r"площад[ьи](?: всего)?\s+треугольника\s+ABC[^0-9]*([0-9]+(?:[.,][0-9]+)?)", r"ABC\s+площадью\s+([0-9]+(?:[.,][0-9]+)?)"])
        S_ABD = extract_area([r"площад[ьи]\s+треугольника\s+ABD[^0-9]*([0-9]+(?:[.,][0-9]+)?)"])
        S_BCD = extract_area([r"площад[ьи]\s+треугольника\s+BCD[^0-9]*([0-9]+(?:[.,][0-9]+)?)"])
        area_mult = re.search(r"площадь\s+треугольника\s+(BCD)\s+в\s+([0-9]+)\s+раза\s+больше", text_lower)
        if area_mult and S_ABD:
            mult = parse_number(area_mult.group(2))
            S_BCD = S_ABD * mult
            if AD is None: AD, DC = 1.0, mult

        # --- 3. Определяем, какую площадь ищет задача (исходный код) ---
        to_find_name = None
        if "меньш" in text_lower: to_find_name = "S_small"
        elif "больш" in text_lower: to_find_name = "S_big"
        else:
            if asks_for("bcd"): to_find_name = "S_BCD"
            elif asks_for("abd"): to_find_name = "S_ABD"
            elif asks_for("abc"): to_find_name = "S_ABC"
            if to_find_name is None:
                m = re.search(r"найти[^.]*?(abd|bcd|abc)", text_lower)
                if m: to_find_name = f"S_{m.group(1).upper()}"
        if to_find_name is None: raise ValueError(f"Не удалось определить искомую площадь: {text}")

        # --- 4. Считаем ответ (исходный код) ---
        answer = None
        base_total = (AD + DC) if AD is not None and DC is not None else None

        if to_find_name == "S_ABC":
            if S_ABD and base_total and AD: answer = S_ABD * base_total / AD
            elif S_BCD and base_total and DC: answer = S_BCD * base_total / DC
            elif S_ABD and S_BCD: answer = S_ABD + S_BCD
        elif to_find_name == "S_ABD":
            if S_ABC and base_total and AD: answer = S_ABC * AD / base_total
            elif S_BCD and AD and DC: answer = S_BCD * AD / DC
        elif to_find_name == "S_BCD":
            if S_ABC and base_total and DC: answer = S_ABC * DC / base_total
            elif S_ABD and AD and DC: answer = S_ABD * DC / AD
        elif to_find_name in ("S_small", "S_big") and S_ABC and base_total:
            a1, a2 = S_ABC * AD / base_total, S_ABC * DC / base_total
            answer = min(a1, a2) if to_find_name == "S_small" else max(a1, a2)

        # --- 5. Сборка JSON (исходный код) ---
        image_file = None
        if AD is not None and DC is not None: image_file = "T4_AD_DC.svg" if AD > DC else "T4_DC_AD.svg"
        relations = {}
        if S_ABC is not None: relations["S_ABC"] = self._format_number(S_ABC)
        if S_ABD is not None: relations["S_ABD"] = self._format_number(S_ABD)
        if S_BCD is not None: relations["S_BCD"] = self._format_number(S_BCD)
        points_info = {"D_on_AC": {}}
        if AD is not None: points_info["D_on_AC"]["AD"] = self._format_number(AD)
        if DC is not None: points_info["D_on_AC"]["DC"] = self._format_number(DC)

        return {
            "id": raw.get("id"), "pattern": raw["pattern"], "text": text,
            "answer": self._format_number(answer), "image_file": image_file,
            "variables": {
                "given": {
                    "triangle_name": "ABC", "triangle_type": "general", "sides": {}, "angles": {},
                    "trig": {}, "elements": {}, "points": points_info, "relations": relations,
                },
                "to_find": {"type": "area", "name": to_find_name},
                "humanizer_data": {"side_roles": {}, "angle_names": {}, "element_names": {}},
            },
        }

    # ============================================================
    # PATTERN 2.3
    # triangle_area_by_parallel_line
    # ============================================================

    def _handle_triangle_area_by_parallel_line(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        text = raw["text"]

        # --- 1) СБОР ДАННЫХ ИЗ ТЕКСТА ---
        raw_s: Dict[str, str] = {}

        # 1а) длины/отрезки
        for name, val_str in re.findall(
            r"\b(AC|MN|AB|BC|AM|BM|BN|NC|CN)\b\s*=\s*([0-9.,√]+)",
            text,
            flags=re.IGNORECASE
        ):
            key = "NC" if name.upper() == "CN" else name.upper()
            if key not in raw_s:
                raw_s[key] = val_str.strip("., ")

        # 1б) площади (оба формата: "площадь ... = X" и "треугольник ... площадью X")
        for name, val_str in re.findall(
            r"площад[ьи](?:\s+треугольника|\s+трапеции)?\s+(ABC|MBN)\s*=\s*([0-9.,√]+)",
            text,
            flags=re.IGNORECASE
        ):
            key = f"S_{name.upper()}"
            if key not in raw_s:
                raw_s[key] = val_str.strip("., ")

        for name, val_str in re.findall(
            r"(?:в треугольнике|треугольник)\s+(ABC|MBN)\s+площадью\s+([0-9.,√]+)",
            text,
            flags=re.IGNORECASE
        ):
            key = f"S_{name.upper()}"
            if key not in raw_s:
                raw_s[key] = val_str.strip("., ")

        # 1в) числовая модель s (ТОЛЬКО из числовых полей, без текстового отношения!)
        s: Dict[str, float] = {}
        for k, v in raw_s.items():
            s[k] = self._parse_numeric_with_root(v)

        # --- 2) ДЕДУКЦИЯ (дополняем модель) ---
        # AB, AM, BM
        if s.get("AB") is not None and s.get("AM") is not None:
            s.setdefault("BM", s["AB"] - s["AM"])
        if s.get("AB") is not None and s.get("BM") is not None:
            s.setdefault("AM", s["AB"] - s["BM"])
        if s.get("AM") is not None and s.get("BM") is not None:
            s.setdefault("AB", s["AM"] + s["BM"])

        # BC, BN, NC (NC = CN)
        if s.get("BC") is not None and s.get("BN") is not None:
            s.setdefault("NC", s["BC"] - s["BN"])
        if s.get("BC") is not None and s.get("NC") is not None:
            s.setdefault("BN", s["BC"] - s["NC"])
        if s.get("BN") is not None and s.get("NC") is not None:
            s.setdefault("BC", s["BN"] + s["NC"])

        # --- 3) ПАРСИНГ ЦЕЛИ (что ищем) ---
        to_find = self._parse_to_find_parallel_line(text)

        # --- 4) ВЫЧИСЛЕНИЕ k ---
        # k = MN/AC = BM/AB = BN/BC = sqrt(S_MBN/S_ABC) = из текста "MN относится к AC как a к b"
        k = None

        # 4а) из текстового отношения (СРАЗУ числом)
        m_ratio_text = re.search(
            r"MN[^\d]*?относится[^\d]*?AC[^\d]*?(\d+)\s*к\s*(\d+)",
            text,
            flags=re.IGNORECASE
        )
        if m_ratio_text:
            a = float(m_ratio_text.group(1))
            b = float(m_ratio_text.group(2))
            if b == 0:
                raise ValueError("Валидатор: отношение MN:AC содержит деление на ноль.")
            k = a / b

        # 4б) иначе — по данным
        if k is None and s.get("MN") is not None and s.get("AC") is not None and s["AC"] != 0:
            k = s["MN"] / s["AC"]

        if k is None and s.get("BM") is not None and s.get("AB") is not None and s["AB"] != 0:
            k = s["BM"] / s["AB"]

        if k is None and s.get("BN") is not None and s.get("BC") is not None and s["BC"] != 0:
            k = s["BN"] / s["BC"]

        if k is None and s.get("S_MBN") is not None and s.get("S_ABC") is not None and s["S_ABC"] != 0:
            val = s["S_MBN"] / s["S_ABC"]
            if val <= 0:
                raise ValueError("Валидатор: отношение площадей не может быть <= 0.")
            k = math.sqrt(val)

        if k is None:
            raise ValueError("Валидатор: недостаточно данных для вычисления коэффициента подобия k.")

        # sanity (обычно k в (0,1), но не будем жёстко запрещать, только мягкий контроль на знак)
        if k <= 0:
            raise ValueError("Валидатор: коэффициент подобия k должен быть > 0.")

        # --- 5) ВЫЧИСЛЕНИЕ ОТВЕТА ---
        answer = None

        if to_find["type"] == "area":
            if to_find["name"] == "S_MBN":
                if s.get("S_ABC") is not None:
                    answer = s["S_ABC"] * (k ** 2)

            elif to_find["name"] == "S_ABC":
                if s.get("S_MBN") is not None:
                    answer = s["S_MBN"] / (k ** 2)

        elif to_find["type"] == "side":
            name = to_find["name"]

            if name == "MN":
                if s.get("AC") is not None:
                    answer = s["AC"] * k

            elif name == "AC":
                if s.get("MN") is not None:
                    answer = s["MN"] / k

            elif name == "BM":
                if s.get("BM") is not None:
                    answer = s["BM"]
                elif s.get("AB") is not None:
                    answer = s["AB"] * k

            elif name == "AM":
                if s.get("AM") is not None:
                    answer = s["AM"]
                elif s.get("AB") is not None:
                    answer = s["AB"] * (1 - k)

            elif name == "AB":
                if s.get("BM") is not None:
                    answer = s["BM"] / k
                elif s.get("AM") is not None:
                    answer = s["AM"] / (1 - k)

            elif name == "BN":
                if s.get("BN") is not None:
                    answer = s["BN"]
                elif s.get("BC") is not None:
                    answer = s["BC"] * k

            elif name == "NC":
                if s.get("NC") is not None:
                    answer = s["NC"]
                elif s.get("BC") is not None:
                    answer = s["BC"] * (1 - k)

            elif name == "BC":
                if s.get("BN") is not None:
                    answer = s["BN"] / k
                elif s.get("NC") is not None:
                    answer = s["NC"] / (1 - k)

        elif to_find["type"] == "ratio":
            ratio_name = to_find["name"].replace(" ", "")
            if ratio_name == "MN/AC":
                answer = k
            elif ratio_name == "AC/MN":
                answer = 1 / k

        # --- ЕДИНСТВЕННАЯ ПРОВЕРКА ---
        if answer is None:
            raise ValueError(
                f"Валидатор: недостаточно данных для вычисления {to_find['name']}."
            )

        # --- 6) СБОРКА JSON (ИЗ ЧИСЛОВОЙ МОДЕЛИ s) ---
        given_sides = {key: float(s[key]) for key in ("AB", "BC", "AC") if key in raw_s}
        given_elements = {key: float(s[key]) for key in ("MN", "AM", "BM", "BN", "NC", "CN") if key in raw_s}
        given_relations = {key: float(s[key]) for key in ("S_ABC", "S_MBN") if key in s}

        # points — оставим как раньше (минимально, чтобы не ломать общий стиль)
        points = {}
        if "AM" in s or "BM" in s:
            points["M"] = "on AB"
        if "BN" in s or "NC" in s:
            points["N"] = "on BC"

        return {
            "id": raw.get("id"),
            "pattern": raw["pattern"],
            "text": text,
            "answer": self._format_number(answer),
            "image_file": "T5_triangle_area_by_parallel_line.svg",
            "variables": {
                "given": {
                    "triangle_name": "ABC",
                    "triangle_type": "general",
                    "sides": given_sides,
                    "angles": {},
                    "trig": {},
                    "elements": given_elements,
                    "points": points,
                    "relations": given_relations,
                },
                "to_find": to_find,
                "humanizer_data": {
                    "side_roles": {},
                    "angle_names": {},
                    "element_names": {},
                },
            },
        }

    # ============================================================
    # PATTERN 2.4: triangle_area_by_midpoints
    # ============================================================
    def _handle_triangle_area_by_midpoints(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обрабатывает задачи со средней линией.
        Различает два подтипа:
        1. Нахождение длины средней линии (задача-ловушка).
        2. Нахождение площадей (S_ABC, S_MBN, S_AMNC).
        """
        text = raw["text"]
        text_lower = text.lower()

        # --- 0. Определяем, что нужно найти: длину или площадь ---
        to_find_name = None
        to_find_type = None

        m_find_side = re.search(r"(?:найд[^\n\r]*?|чему\s+равна\s+длина\s+)(MN|AC)\b", text, flags=re.IGNORECASE)
        if m_find_side:
            to_find_type = "side"
            to_find_name = m_find_side.group(1).upper()
        else:
            to_find_type = "area"
            m_target = re.search(r"найд[^\n\r]*?(?:площад[ьи]\s+)?(?:трапеции\s+|четырехугольника\s+)?(s_abc|s_mbn|s_amnc|abc|mbn|amnc)\b", text_lower)
            if m_target:
                token = m_target.group(1).upper()
                if token in {"S_ABC", "ABC"}: to_find_name = "S_ABC"
                elif token in {"S_MBN", "MBN"}: to_find_name = "S_MBN"
                elif token in {"S_AMNC", "AMNC"}: to_find_name = "S_AMNC"

        if to_find_name is None:
            raise ValueError(f"Midpoints Validator: Не удалось определить, что нужно найти в тексте: '{text}'")

        # --- ВЕТКА 1: РАБОТАЕМ С ДЛИНАМИ (ЗАДАЧА-ЛОВУШКА) ---
        if to_find_type == "side":
            sides: Dict[str, float] = {}
            # Улучшенный парсер: ищет и "AC = X", и "сторона AC равна X"
            all_sides = {"AB", "BC", "AC", "MN"}
            for side_name in all_sides:
                # Ищем "AC = 62"
                m_eq = re.search(rf"\b{side_name}\b\s*=\s*([0-9]+(?:[.,][0-9]+)?)", text, flags=re.IGNORECASE)
                if m_eq:
                    sides[side_name] = float(m_eq.group(1).replace(",", "."))
                    continue # Переходим к следующей стороне

                # Ищем "сторона AC равна 62", "длина MN равна 17", "отрезок AC равен 10"
                m_word = re.search(rf"(?:сторона|основание|длина|отрезок)\s+\b{side_name}\b\s+(?:равна?|равен)\s+([0-9]+(?:[.,][0-9]+)?)", text, flags=re.IGNORECASE)
                if m_word:
                    sides[side_name] = float(m_word.group(1).replace(",", "."))

            answer = None
            if to_find_name == "MN" and "AC" in sides:
                answer = sides["AC"] / 2
            elif to_find_name == "AC" and "MN" in sides:
                answer = sides["MN"] * 2

            if answer is None:
                raise ValueError(f"Midpoints Validator: не хватает данных для поиска длины {to_find_name}")

            return {
                "id": raw.get("id"), "pattern": raw["pattern"], "text": text,
                "answer": self._format_number(answer), "image_file": "T6_triangle_area_by_midpoints.svg",
                "variables": {
                    "given": {
                        "triangle_name": "ABC", "triangle_type": "general", "sides": sides, "angles": {},
                        "trig": {}, "elements": {},
                        "points": {"M": "midpoint of AB", "N": "midpoint of BC"},
                        "relations": {},
                    },
                    "to_find": {"type": "side", "name": to_find_name},
                    "humanizer_data": {},
                },
            }

        # --- ВЕТКА 2: РАБОТАЕМ С ПЛОЩАДЯМИ (СТАРЫЙ РАБОЧИЙ КОД) ---
        else: # to_find_type == "area"
            def parse_area(patterns: list[str]) -> float | int | None:
                for pattern in patterns:
                    m = re.search(pattern, text, flags=re.IGNORECASE)
                    if m:
                        value = float(m.group(1).replace(",", "."))
                        return int(value) if value.is_integer() else value
                return None

            S_ABC = parse_area([
                r"S\s*[_]?\s*ABC\s*=\s*([0-9]+(?:[.,][0-9]+)?)",
                r"площад[ьи]\s+треугольника\s+ABC[^0-9]*([0-9]+(?:[.,][0-9]+)?)",
                r"треугольник[е]?\s+ABC[^0-9]*площад[ьюи]\s*([0-9]+(?:[.,][0-9]+)?)",
                r"в\s+треугольнике\s+abc[^0-9]*площад[ьяи]\s+равн[аы]\s*([0-9]+(?:[.,][0-9]+)?)",
                r"ABC\s+площадью\s+([0-9]+(?:[.,][0-9]+)?)",
                r"ABC,\s+площадь\s+которого\s+([0-9]+(?:[.,][0-9]+)?)",
            ])
            S_MBN = parse_area([
                r"S\s*[_]?\s*MBN\s*=\s*([0-9]+(?:[.,][0-9]+)?)",
                r"площад[ьи]\s+треугольника\s+MBN[^0-9]*([0-9]+(?:[.,][0-9]+)?)",
                r"площадь\s+MBN\s+равна\s+([0-9]+(?:[.,][0-9]+)?)",
            ])
            S_AMNC = parse_area([
                r"S\s*[_]?\s*AMNC\s*=\s*([0-9]+(?:[.,][0-9]+)?)",
                r"площад[ьи]\s+(?:четыр[её]хугольника|трапеции)\s+AMNC[^0-9]*([0-9]+(?:[.,][0-9]+)?)",
            ])

            answer = None
            calc_abc = calc_mbn = calc_amnc = None

            if S_ABC is not None:
                calc_abc, calc_mbn, calc_amnc = S_ABC, S_ABC / 4, S_ABC * 3 / 4
            elif S_MBN is not None:
                calc_mbn, calc_abc, calc_amnc = S_MBN, S_MBN * 4, S_MBN * 3
            elif S_AMNC is not None:
                calc_amnc, calc_abc, calc_mbn = S_AMNC, S_AMNC * 4 / 3, S_AMNC / 3

            if to_find_name == "S_ABC": answer = calc_abc
            elif to_find_name == "S_MBN": answer = calc_mbn
            elif to_find_name == "S_AMNC": answer = calc_amnc

            relations = {}
            if S_ABC is not None: relations["S_ABC"] = self._format_number(S_ABC)
            if S_MBN is not None: relations["S_MBN"] = self._format_number(S_MBN)
            if S_AMNC is not None: relations["S_AMNC"] = self._format_number(S_AMNC)

            return {
                "id": raw.get("id"), "pattern": "triangle_area_by_midpoints", "text": text,
                "answer": self._format_number(answer), "image_file": "T6_triangle_area_by_midpoints.svg",
                "variables": {
                    "given": {
                        "triangle_name": "ABC", "triangle_type": "general", "sides": {}, "angles": {},
                        "trig": {}, "elements": {},
                        "points": {"M": "midpoint of AB", "N": "midpoint of BC"},
                        "relations": relations,
                    },
                    "to_find": {"type": "area", "name": to_find_name},
                    "humanizer_data": {"side_roles": {}, "angle_names": {}, "element_names": {}},
                },
            }

    # ============================================================
    # PATTERN 2.5: cosine_law_find_cos
    # ============================================================

    def _handle_cosine_law_find_cos(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Парсим три стороны, определяем угол, считаем косинус по теореме косинусов.
        """
        text = raw["text"]
        id_ = raw.get("id")

        def parse_number(value: str) -> float | int:
            cleaned = value.strip().replace(",", ".")
            number = float(cleaned)
            return int(number) if number.is_integer() else number

        sides: Dict[str, float | int] = {}
        for name, val in re.findall(r"(AB|BC|AC)\s*=\s*([0-9]+(?:[.,][0-9]+)?)", text, flags=re.IGNORECASE):
            sides[name.upper()] = parse_number(val)

        if len(sides) < 3:
            raise ValueError(f"cosine_law_find_cos: не нашли все стороны в '{text}'")

        AB = float(sides.get("AB")) if sides.get("AB") is not None else None
        BC = float(sides.get("BC")) if sides.get("BC") is not None else None
        AC = float(sides.get("AC")) if sides.get("AC") is not None else None

        angle_to_find = None
        m = re.search(r"cos\s*[∠]?\s*([ABC])", text, flags=re.IGNORECASE)
        if m:
            angle_to_find = m.group(1).upper()

        if angle_to_find not in ("A", "B", "C"):
            raise ValueError(f"cosine_law_find_cos: не удалось определить угол в '{text}'")

        answer = None
        if angle_to_find == "A" and AB and AC and BC:
            answer = (AB**2 + AC**2 - BC**2) / (2 * AB * AC)
        elif angle_to_find == "B" and AB and AC and BC:
            answer = (AB**2 + BC**2 - AC**2) / (2 * AB * BC)
        elif angle_to_find == "C" and AB and AC and BC:
            answer = (AC**2 + BC**2 - AB**2) / (2 * AC * BC)

        answer = self._format_number(answer)

        # --- Выбор картинки ---
        image_file = "T3_acute.svg"  # По умолчанию - остроугольный

        # Конвертируем ответ обратно в число для сравнения
        numeric_answer = None
        if isinstance(answer, str):
            try:
                numeric_answer = float(answer.replace(',', '.'))
            except (ValueError, TypeError):
                pass
        elif isinstance(answer, (int, float)):
            numeric_answer = answer

        if numeric_answer is not None:
            if numeric_answer < 0:
                # Если ответ отрицательный, угол тупой. Выбираем картинку с нужной буквой.
                image_file = f"T3_obtuse_{angle_to_find}.svg"
            elif numeric_answer == 0:
                # Если ответ 0, угол прямой.
                image_file = f"T3_right_{angle_to_find}.svg"

        return {
            "id": id_,
            "pattern": "cosine_law_find_cos",
            "text": text,
            "answer": answer,
            "image_file": image_file,
            "variables": {
                "given": {
                    "triangle_name": "ABC",
                    "triangle_type": "general",
                    "sides": {
                        "AB": self._format_number(sides.get("AB")),
                        "BC": self._format_number(sides.get("BC")),
                        "AC": self._format_number(sides.get("AC"))
                    },
                    "angles": {},
                    "trig": {},
                    "elements": {},
                    "points": {},
                    "relations": {},
                },
                "to_find": {
                    "type": "trig",
                    "name": f"cos_{angle_to_find}"
                },
                "humanizer_data": {
                    "side_roles": {},
                    "angle_names": {
                        angle_to_find: f"∠{angle_to_find}"
                    },
                    "element_names": {}
                }
            }
        }

    # ============================================================
    # PATTERN 2.6: triangle_by_two_angles_and_side
    # ============================================================

    def _handle_triangle_by_two_angles_and_side(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Парсит два угла, одну сторону, находит третьий угол, искомую сторону по теореме синусов и выбирает шаблон T3_*.
        """
        text = raw["text"]
        id_ = raw.get("id")

        def parse_number(value: str) -> float | int:
            cleaned = value.strip().replace(",", ".")
            number = float(cleaned)
            return int(number) if number.is_integer() else number

        angles: Dict[str, float | int] = {}
        for name, val in re.findall(r"(?:угол|∠)\s*([ABC])\s*(?:равен|=)\s*([0-9]+(?:[.,][0-9]+)?)", text, flags=re.IGNORECASE):
            angles[name.upper()] = parse_number(val)

        if len(angles) < 2:
            raise ValueError(f"triangle_by_two_angles_and_side: найдено меньше 2 углов в '{text}'")

        missing = list({"A", "B", "C"} - set(angles.keys()))
        if len(missing) != 1:
            raise ValueError(f"triangle_by_two_angles_and_side: проблема с углами '{angles}'")

        missing_angle = missing[0]
        angles[missing_angle] = 180 - sum(angles.values())

        A, B, C = angles["A"], angles["B"], angles["C"]

        # Используем универсальный парсер, который умеет работать с корнем "√"
        sides: Dict[str, str] = {}

        # Ищем "AB = 7√2" ИЛИ "сторона AB равна 7√2"
        pattern = r"(?:сторона\s*)?(AB|BC|AC)\s*(?:равна|=)\s*([0-9√.,]+)"
        for name, val in re.findall(pattern, text, flags=re.IGNORECASE):

            # Убираем точку в конце, если она не относится к числу
            cleaned_val = val.strip().rstrip(".,")

            sides[name.upper()] = cleaned_val

        # Должна быть строго одна известная сторона
        if len(sides) != 1:
            raise ValueError(
                f"triangle_by_two_angles_and_side: должна быть ровно одна известная сторона в '{text}'"
            )

        # Извлекаем имя стороны и её строковое значение
        given_side_name, given_side_str_value = list(sides.items())[0]

        # Числовое значение для формул (например, 6√3 → 10.3923...)
        numeric_given_side = self._parse_numeric_with_root(given_side_str_value)

        # Находим искомую сторону
        to_find_match = re.search(r"найд[^\n\r]*?(AB|BC|AC)", text, flags=re.IGNORECASE)
        if not to_find_match:
            raise ValueError(
                f"triangle_by_two_angles_and_side: не могу определить искомую сторону в '{text}'"
            )
        to_find = to_find_match.group(1).upper()

        sin = lambda x: math.sin(math.radians(float(x)))
        sinA, sinB, sinC = sin(A), sin(B), sin(C)

        def angle_opposite_side(side: str) -> str:
            return {"BC": "A", "AC": "B", "AB": "C"}[side]

        # Определяем угол, противолежащий известной стороне
        given_angle_letter = angle_opposite_side(given_side_name)
        sin_given = {"A": sinA, "B": sinB, "C": sinC}[given_angle_letter]

        # коэффициент k по теореме синусов
        k = numeric_given_side / sin_given

        # Искомый угол для искомой стороны
        target_angle_letter = angle_opposite_side(to_find)
        sin_target = {"A": sinA, "B": sinB, "C": sinC}[target_angle_letter]

        # Финальный числовой ответ
        answer_val = k * sin_target
        answer = int(round(answer_val))

        image_file = "T3_acute.svg"
        if A > 90:
            image_file = "T3_obtuse_A.svg"
        elif B > 90:
            image_file = "T3_obtuse_B.svg"
        elif C > 90:
            image_file = "T3_obtuse_C.svg"
        elif A == 90:
            image_file = "T3_right_A.svg"
        elif B == 90:
            image_file = "T3_right_B.svg"
        elif C == 90:
            if A == 45 and B == 45:
                image_file = "T3_right_isosceles_C.svg"
            else:
                image_file = "T3_right_C.svg"

        return {
            "id": id_,
            "pattern": "triangle_by_two_angles_and_side",
            "text": text,
            "answer": answer,
            "image_file": image_file,
            "variables": {
                "given": {
                    "triangle_name": "ABC",
                    "triangle_type": "general",
                    "sides": {given_side_name: given_side_str_value},
                    "angles": {k: v for k, v in angles.items() if k != missing_angle},
                    "trig": {},
                    "elements": {},
                    "points": {},
                    "relations": {}
                },
                "to_find": {
                    "type": "side",
                    "name": to_find
                },
                "humanizer_data": {
                    "side_roles": {},
                    "angle_names": {
                        target_angle_letter: f"∠{target_angle_letter}"
                    },
                    "element_names": {}
                }
            }
        }

    # ============================================================
    # PATTERN 2.7: trig_identity_find_trig_func
    # ============================================================
    def _handle_trig_identity_find_trig_func(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Парсит задачу на основное тригонометрическое тождество (sin <-> cos).
        """
        text = raw["text"]

        # --- 1. Парсим, что дано ---
        # Ищет "косинус ... A равен ЗНАЧЕНИЕ" или "синус ... B равен ЗНАЧЕНИЕ"
        m_given = re.search(r"(синус|косинус)\s+острого\s+угла\s+([A-Z])(?:[^=]*?)(?:равен|=)\s*([0-9.,√/]+)", text, flags=re.IGNORECASE)
        if not m_given:
            raise ValueError("TrigIdentity Validator: не удалось найти данное значение sin/cos.")

        given_func_rus, angle_letter, given_val_str = m_given.groups()

        # >>> ИСПРАВЛЕНИЕ 1: Превращаем "косинус" в "cos" <<<
        given_func_eng = "cos" if "кос" in given_func_rus.lower() else "sin"
        angle_letter = angle_letter.upper()
        # >>> ИСПРАВЛЕНИЕ 2: Убираем мусор в конце значения <<<
        given_val_str = given_val_str.strip().rstrip(".,")

        # --- 2. Парсим, что найти ---
        m_to_find = re.search(r"Найдите\s+(sin|cos)\s*[∠]?\s*([A-Z])", text, flags=re.IGNORECASE)
        if not m_to_find:
            raise ValueError("TrigIdentity Validator: не удалось определить, что нужно найти.")

        to_find_func_eng, angle_letter_to_find = m_to_find.groups()
        to_find_func_eng = to_find_func_eng.lower()

        # --- 3. Вычисляем ответ ---
        given_val_num = self._parse_numeric_with_root(given_val_str)
        if not (-1 <= given_val_num <= 1):
            raise ValueError(f"Значение {given_func_rus} не может быть {given_val_num}")
        answer_val = math.sqrt(1 - given_val_num**2)

        # --- 4. Сборка JSON ---
        # >>> ИСПРАВЛЕНИЕ 3: Используем английский ключ <<<
        given_trig = {f"{given_func_eng}_{angle_letter}": given_val_str}
        to_find = {"type": "trig", "name": f"{to_find_func_eng}_{angle_letter}"}

        return {
            "id": raw.get("id"), "pattern": "trig_identity_find_trig_func", "text": text,
            "answer": self._format_number(answer_val),
            "image_file": None,
            "variables": {
                "given": {
                    "triangle_name": "ABC", "triangle_type": "general", "sides": {}, "angles": {},
                    "trig": given_trig, "elements": {}, "points": {}, "relations": {},
                },
                "to_find": to_find,
                "humanizer_data": {
                    "angle_names": {angle_letter: f"∠{angle_letter}"}
                },
            },
        }


    def validate_one(self, raw: dict):
        """
        Универсальная точка входа для валидации одной строки сырья.
        raw — это словарь вида:
        {
            "pattern": "triangle_area_by_dividing_point",
            "text": "На стороне AC ...",
            "id": ... (может быть None)
        }

        Метод автоматически:
        1. Берёт pattern
        2. Ищет метод вида _handle_<pattern>
        3. Вызывает его и возвращает итоговый JSON
        """

        if not isinstance(raw, dict):
            raise TypeError("validate_one: raw должен быть словарём")

        pattern = raw.get("pattern")
        if not pattern:
            raise ValueError("validate_one: отсутствует ключ 'pattern' в raw-данных")

        # Пример: pattern='triangle_area_by_dividing_point'
        # → handler_name='_handle_triangle_area_by_dividing_point'
        handler_name = f"_handle_{pattern}"

        handler = getattr(self, handler_name, None)
        if handler is None:
            raise ValueError(
                f"validate_one: обработчик '{handler_name}' не найден в GeneralTrianglesValidator"
            )

        # Обрабатываем
        result = handler(raw)

        if not isinstance(result, dict):
            raise ValueError(
                f"validate_one: обработчик '{handler_name}' должен вернуть dict, "
                f"получено: {type(result)}"
            )

        return result
