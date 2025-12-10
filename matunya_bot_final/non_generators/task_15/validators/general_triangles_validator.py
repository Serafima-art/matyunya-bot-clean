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
        Универсальный парсер чисел с возможным корнем: 10√3, √5, 3.5.
        """
        cleaned = token.strip().replace(",", ".")
        if "√" in cleaned:
            coef_part, root_part = cleaned.split("√", 1)
            coef = float(coef_part) if coef_part not in ("", "+", "-") else (1.0 if coef_part != "-" else -1.0)
            radicand = float(root_part) if root_part else 0.0
            return coef * math.sqrt(radicand)
        return float(cleaned)

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
        }

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
        """
        Задачи вида: MN ∥ AC, M ∈ AB, N ∈ BC.
        ФИНАЛЬНАЯ ВЕРСИЯ: Точный парсер площадей, дедукция длин, расчет всех форм.
        """
        text = raw["text"]

        # === ШАГ 1: УНИВЕРСАЛЬНЫЙ ПАРСИНГ ДАННЫХ ===

        # 1.1. Парсинг всех длин отрезков
        lengths: Dict[str, float | int] = {}
        pattern = r"(?:сторона\s*)?\b(AC|MN|AB|BC|AM|BM|BN|NC|CN)\b\s*(?:равна|равен|=)\s*([0-9]+(?:[.,][0-9]+)?)"
        for name, value_str in re.findall(pattern, text, flags=re.IGNORECASE):
            key = "NC" if name.upper() == "CN" else name.upper()
            lengths[key] = self._parse_numeric_with_root(value_str)

        # 1.1a. Дедукция недостающих длин
        if lengths.get("AB") and lengths.get("AM") and not lengths.get("BM"):
            lengths["BM"] = lengths["AB"] - lengths["AM"]
        if lengths.get("AB") and lengths.get("BM") and not lengths.get("AM"):
            lengths["AM"] = lengths["AB"] - lengths["BM"]
        if lengths.get("AM") and lengths.get("BM") and not lengths.get("AB"):
            lengths["AB"] = lengths["AM"] + lengths["BM"]
        if lengths.get("BC") and lengths.get("BN") and not lengths.get("NC"):
            lengths["NC"] = lengths["BC"] - lengths["BN"]
        if lengths.get("BC") and lengths.get("NC") and not lengths.get("BN"):
            lengths["BN"] = lengths["BC"] - lengths["NC"]
        if lengths.get("BN") and lengths.get("NC") and not lengths.get("BC"):
            lengths["BC"] = lengths["BN"] + lengths["NC"]

        # 1.2. Точный парсинг всех площадей (не жадный)
        areas: Dict[str, float | int] = {}
        area_patterns = [
            r"площад[ьи](?:\s+треугольника)?\s+(ABC|MBN)\s*равна\s*([0-9]+(?:[.,][0-9]+)?)",
            r"треугольник[а]?\s+(ABC|MBN)\s+с\s+площад[ьюи]\s*([0-9]+(?:[.,][0-9]+)?)",
            r"S\s*[_]?\s*(ABC|MBN)\s*=\s*([0-9]+(?:[.,][0-9]+)?)"
        ]
        for p in area_patterns:
            for name, value_str in re.findall(p, text, flags=re.IGNORECASE):
                key = f"S_{name.upper()}"
                if key not in areas:
                    areas[key] = self._parse_numeric_with_root(value_str)

        # 1.3. Парсинг явного отношения (коэффициента k)
        k_ratio: float | None = None
        ratio_pattern = r"([A-Z]{2})[^\n\r]*?относ[^\n\r]*?([A-Z]{2})[^\d]*?([0-9]+)\s*к\s*([0-9]+)"
        m_ratio_text = re.search(ratio_pattern, text, flags=re.IGNORECASE)
        if m_ratio_text:
            side1, side2, num, den = m_ratio_text.groups()
            if float(den) != 0:
                if side1.upper() == "MN" and side2.upper() == "AC":
                    k_ratio = float(num) / float(den)
                elif side1.upper() == "AC" and side2.upper() == "MN":
                    k_ratio = float(den) / float(num)

        # === ШАГ 2: ОПРЕДЕЛЕНИЕ ТОГО, ЧТО НУЖНО НАЙТИ ===

        def _parse_to_find(text_to_scan: str) -> Dict[str, str]:
            m_ratio = re.search(r"найд[^\n\r]*?отношен[^\n\r]*?([A-Z]{2})\s*(?:к|[:/])\s*([A-Z]{2})", text, flags=re.IGNORECASE)
            if m_ratio:
                a, b = m_ratio.group(1).upper(), m_ratio.group(2).upper()
                return {"type": "ratio", "name": f"{a}/{b}"}
            m_area = re.search(r"найд[^\n\r]*?площад[ьи](?:\s+треугольника)?\s+([A-Z]{3})", text, flags=re.IGNORECASE)
            if m_area:
                return {"type": "area", "name": f"S_{m_area.group(1).upper()}"}
            m_side = re.search(r"найд[^\n\r]*?(?:\bдлину\b|\bстороны\b|\bсторону\b)?\s*([A-Z]{2,3})", text, flags=re.IGNORECASE)
            if m_side:
                name = m_side.group(1).upper()
                return {"type": "area" if name in ("ABC", "MBN") else "side", "name": f"S_{name}" if name in ("ABC", "MBN") else name}
            raise ValueError(f"Не удалось определить, что нужно найти: {text}")

        to_find = _parse_to_find(text)

        # === ШАГ 3: ВЫЗОВ СПЕЦИАЛИЗИРОВАННОЙ ФУНКЦИИ ("СБОРОЧНОЙ ЛИНИИ") ===

        k: float | None = k_ratio
        if k is None:
            if lengths.get("MN") is not None and lengths.get("AC") is not None and lengths.get("AC") != 0:
                k = lengths["MN"] / lengths["AC"]
            elif lengths.get("BM") is not None and lengths.get("AB") is not None and lengths.get("AB") != 0:
                k = lengths["BM"] / lengths["AB"]
            elif lengths.get("BN") is not None and lengths.get("BC") is not None and lengths.get("BC") != 0:
                k = lengths["BN"] / lengths["BC"]
            elif areas.get("S_MBN") is not None and areas.get("S_ABC") is not None and areas.get("S_ABC") != 0:
                k = math.sqrt(areas["S_MBN"] / areas["S_ABC"])

        def _compute_area_answer(target_name: str, given_areas: dict, main_k: float | None) -> float | None:
            if main_k is None: return None
            k_squared = main_k ** 2
            if target_name == "S_MBN": return given_areas.get("S_ABC") * k_squared if given_areas.get("S_ABC") is not None else None
            if target_name == "S_ABC": return given_areas.get("S_MBN") / k_squared if given_areas.get("S_MBN") is not None else None
            return None

        def _compute_ratio_answer(target_name: str, main_k: float | None) -> float | None:
            if main_k is None: return None
            if target_name == "MN/AC": return main_k
            if target_name == "AC/MN" and main_k != 0: return 1 / main_k
            return None

        def _compute_side_answer(target_name: str, given_lengths: dict, main_k: float | None) -> float | None:
            if main_k is None: return None
            AC, MN = given_lengths.get("AC"), given_lengths.get("MN")
            AB, AM, BM = given_lengths.get("AB"), given_lengths.get("AM"), given_lengths.get("BM")
            BC, BN, NC = given_lengths.get("BC"), given_lengths.get("BN"), given_lengths.get("NC")

            if target_name == "AC": return MN / main_k if MN is not None else None
            if target_name == "MN": return AC * main_k if AC is not None else None
            if target_name == "AB":
                if BM is not None: return BM / main_k
                if AM is not None and main_k != 1: return AM / (1 - main_k)
            if target_name == "BM": return AB * main_k if AB is not None else None
            if target_name == "AM": return AB * (1 - main_k) if AB is not None else None
            if target_name == "BC":
                if BN is not None: return BN / main_k
                if NC is not None and main_k != 1: return NC / (1 - main_k)
            if target_name == "BN": return BC * main_k if BC is not None else None
            if target_name == "NC": return BC * (1 - main_k) if BC is not None else None
            return None

        answer = None
        if to_find["type"] == "area": answer = _compute_area_answer(to_find["name"], areas, k)
        elif to_find["type"] == "ratio": answer = _compute_ratio_answer(to_find["name"], k)
        elif to_find["type"] == "side": answer = _compute_side_answer(to_find["name"], lengths, k)

        # === ШАГ 4: ФОРМИРОВАНИЕ ИТОГОВОГО JSON ===
        image_file = "T5_triangle_area_by_parallel_line.svg"
        sides = {k: v for k, v in lengths.items() if k in ("AC", "AB", "BC")}
        elements = {k: v for k, v in lengths.items() if k not in ("AC", "AB", "BC")}
        points: Dict[str, str] = {}
        if lengths.get("AB") or lengths.get("AM") or lengths.get("BM"): points["M"] = "on AB"
        if lengths.get("BC") or lengths.get("BN") or lengths.get("NC"): points["N"] = "on BC"

        return {
            "id": raw.get("id"), "pattern": "triangle_area_by_parallel_line", "text": text,
            "answer": self._format_number(answer), "image_file": image_file,
            "variables": {
                "given": {
                    "triangle_name": "ABC", "triangle_type": "general", "sides": sides,
                    "angles": {}, "trig": {}, "elements": elements, "points": points, "relations": areas,
                },
                "to_find": to_find, "humanizer_data": {"side_roles": {}, "angle_names": {}, "element_names": {}},
            },
        }

    # ============================================================
    # PATTERN 2.4: triangle_area_by_midpoints
    # ============================================================

    def _handle_triangle_area_by_midpoints(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Частный случай подобия: M, N — середины AB и BC, k = 1/2, площади соотносятся как 1 : 1/4 : 3/4.
        ВЕРСИЯ 4 (ФИНАЛ): Исправлены последние ошибки парсинга площадей.
        """
        text = raw["text"]
        text_lower = text.lower()

        def parse_area(patterns: list[str]) -> float | int | None:
            for pattern in patterns:
                m = re.search(pattern, text, flags=re.IGNORECASE)
                if m:
                    value = float(m.group(1).replace(",", "."))
                    return int(value) if value.is_integer() else value
            return None

        # ИСПРАВЛЕНИЕ: Паттерны сделаны более гибкими, чтобы не зависеть от начала предложения.
        S_ABC = parse_area([
            r"S\s*[_]?\s*ABC\s*=\s*([0-9]+(?:[.,][0-9]+)?)",
            r"площад[ьи]\s+треугольника\s+ABC[^0-9]*([0-9]+(?:[.,][0-9]+)?)",
            r"треугольник[е]?\s+ABC[^0-9]*площад[ьюи]\s*([0-9]+(?:[.,][0-9]+)?)",
            r"в\s+треугольнике\s+abc[^0-9]*площад[ьяи]\s+равн[аы]\s*([0-9]+(?:[.,][0-9]+)?)",
            r"ABC\s+площадью\s+([0-9]+(?:[.,][0-9]+)?)", # <-- Убрано "треугольник" в начале
            r"ABC,\s+площадь\s+которого\s+([0-9]+(?:[.,][0-9]+)?)", # <-- Убрано "треугольник" в начале
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

        to_find_name = None
        m_target = re.search(r"найд[^\n\r]*?(?:площад[ьи]\s+)?(?:трапеции\s+|четырехугольника\s+)?(s_abc|s_mbn|s_amnc|abc|mbn|amnc)\b", text_lower)
        if m_target:
            token = m_target.group(1).upper()
            if token in {"S_ABC", "ABC"}: to_find_name = "S_ABC"
            elif token in {"S_MBN", "MBN"}: to_find_name = "S_MBN"
            elif token in {"S_AMNC", "AMNC"}: to_find_name = "S_AMNC"

        if to_find_name is None:
            if "mbn" in text_lower and "найди" in text_lower: to_find_name = "S_MBN"
            elif "amnc" in text_lower and "найди" in text_lower: to_find_name = "S_AMNC"
            elif "abc" in text_lower and "найди" in text_lower: to_find_name = "S_ABC"

        if to_find_name is None: raise ValueError(f"Не удалось определить, что нужно найти: {text}")

        # Блок вычислений и сборки JSON остается БЕЗ ИЗМЕНЕНИЙ.
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
            cleaned_val = val.strip()
            if cleaned_val.endswith(".") and not re.search(r"\d\.\d", cleaned_val):
                cleaned_val = cleaned_val[:-1]

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
