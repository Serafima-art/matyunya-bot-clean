# matunya_bot_final/non_generators/task_15/validators/general_triangles_validator.py
"""
General triangles validator for Task 15 (Etalon JSON).
This module parses raw text tasks and builds structured JSON without doing SVG drawing.
Math is NOT implemented yet — only structure, routing, and placeholders.
"""

from __future__ import annotations
import re
from typing import Dict, Any
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
        Parse two sides and sin of the included angle, compute area and build Etalon 3.0 JSON.
        """
        text = raw["text"]

        # --- Вспомогательные функции ---
        def parse_numeric(value: str) -> float:
            # Универсальный парсер чисел, включая 10√3
            cleaned = value.strip().replace(",", ".")
            if "√" in cleaned:
                parts = cleaned.split("√")
                coeff = float(parts[0]) if parts[0] else 1.0
                radicand = float(parts[1])
                return coeff * math.sqrt(radicand)
            return float(cleaned)

        def parse_sin_value(value: str) -> float:
            cleaned = value.strip().replace(",", ".")
            if "/" in cleaned:
                numerator, denominator = cleaned.split("/", 1)
                return float(numerator) / float(denominator)
            return float(cleaned)

        # --- 1. Извлечение сторон ---
        sides: Dict[str, float] = {}
        # Ищем AB=10, BC=8√2 и т.д.
        for match in re.finditer(r"(AB|BC|AC)\s*=\s*([0-9.,√]+)", text):
            side_name, value_str = match.groups()
            sides[side_name] = parse_numeric(value_str)

        # Доп. случай: "стороны AB и BC ... равны 20"
        equal_sides_match = re.search(
            r"стороны\s+(AB)\s+и\s+(BC)\s+[^\d]*([0-9]+(?:[.,][0-9]+)?)",
            text,
            flags=re.IGNORECASE,
        )
        if equal_sides_match:
            s1, s2, val = equal_sides_match.groups()
            num = parse_numeric(val)
            sides.setdefault(s1, num)
            sides.setdefault(s2, num)

        # --- 2. Извлечение синуса ---
        sin_match = re.search(
            r"sin\s*[∠]?\s*([ABC]{1,3})\s*(?:=|равен|равна)\s*([0-9]+/[0-9]+|[0-9.,]+)",
            text,
            flags=re.IGNORECASE,
        )

        angle_letter = None
        trig_info: Dict[str, str] = {}
        sin_value_num = None
        angle_display_name = None

        if sin_match:
            angle_spec = sin_match.group(1).upper()
            angle_letter = angle_spec[-1] # Берем последнюю букву (из ABC -> C)
            sin_value_raw = sin_match.group(2).strip().rstrip(".,;:")
            trig_info[f"sin_{angle_letter}"] = sin_value_raw
            sin_value_num = parse_sin_value(sin_value_raw)
            angle_display_name = f"∠{angle_spec}"

        # --- 3. Вычисление площади ---
        area = None
        side_pairs = {"A": ("AB", "AC"), "B": ("AB", "BC"), "C": ("AC", "BC")}

        if angle_letter in side_pairs and sin_value_num is not None:
            first_side, second_side = side_pairs[angle_letter]
            side1 = sides.get(first_side)
            side2 = sides.get(second_side)
            if side1 is not None and side2 is not None:
                calc_area = 0.5 * float(side1) * float(side2) * sin_value_num
                # Округляем до целого, если очень близко
                area = int(calc_area) if abs(calc_area - round(calc_area)) < 1e-9 else round(calc_area, 3)

        # --- 4. Выбор картинки ---
        image_file = "T3_acute.svg"
        if angle_letter:
            # Ищем явное указание тупого угла, например "угол A равен 150"
            obtuse_match = re.search(
                rf"(?:∠\s*{angle_letter}|угол\s*{angle_letter})\s*(?:=|равен|равна)?\s*(\d+)",
                text,
                flags=re.IGNORECASE,
            )
            if obtuse_match:
                if int(obtuse_match.group(1)) > 90:
                    image_file = f"T3_obtuse_{angle_letter}.svg"

        # --- 5. Сборка JSON ---
        return {
            "id": None, # Будет заполнено в build.py
            "pattern": "triangle_area_by_sin",
            "text": text,
            "answer": area,
            "image_file": image_file,
            "variables": {
                "given": {
                    "triangle_name": "ABC",
                    "triangle_type": "general",
                    "sides": sides,
                    "angles": {},
                    "trig": trig_info,
                    "elements": {}, "points": {}, "relations": {},
                },
                "to_find": {
                    "type": "area",
                    "name": "S_ABC",
                },
                "humanizer_data": {
                    "side_roles": {},
                    "angle_names": {angle_letter: angle_display_name} if angle_letter else {},
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
        Читаем AD/DC или их отношение, площади, определяем что искать, считаем ответ и собираем Etalon 3.0.
        """
        text = raw["text"]
        text_lower = text.lower()

        def parse_number(value: str) -> float | int:
            cleaned = value.strip().replace(",", ".")
            number = float(cleaned)
            return int(number) if number.is_integer() else number

        def normalize(value: float | None) -> float | int | None:
            if value is None:
                return None
            rounded = round(value)
            if abs(value - rounded) < 1e-9:
                return int(rounded)
            return value

        def extract_area(patterns: list[str]) -> float | int | None:
            for pattern in patterns:
                match = re.search(pattern, text, flags=re.IGNORECASE)
                if match:
                    return parse_number(match.group(1))
            return None

        def wants(target: str) -> bool:
            return bool(re.search(rf"(найти|найдите|вычислите|определите)[^.]*{target}", text_lower)) or bool(
                re.search(rf"площад[ьи][^.]*{target}", text_lower)
            )

        AD = None
        DC = None

        for name, value in re.findall(r"(AD|DC)\s*=\s*([0-9]+(?:[.,][0-9]+)?)", text, flags=re.IGNORECASE):
            if name.upper() == "AD":
                AD = parse_number(value)
            else:
                DC = parse_number(value)

        ratio = re.search(r"AD\s*:\s*DC\s*=\s*([0-9]+)\s*:\s*([0-9]+)", text, flags=re.IGNORECASE)
        if ratio:
            AD = parse_number(ratio.group(1))
            DC = parse_number(ratio.group(2))

        ratio_rev = re.search(r"DC\s*:\s*AD\s*=\s*([0-9]+)\s*:\s*([0-9]+)", text, flags=re.IGNORECASE)
        if ratio_rev:
            DC = parse_number(ratio_rev.group(1))
            AD = parse_number(ratio_rev.group(2))

        S_ABC = extract_area([
            r"S\s*[_]?\s*ABC\s*=\s*([0-9]+(?:[.,][0-9]+)?)",
            r"площад[ьи]\s+треугольника\s+ABC[^0-9]*([0-9]+(?:[.,][0-9]+)?)",
            r"ABC[^0-9]*площад[ьюи]\s*([0-9]+(?:[.,][0-9]+)?)",
        ])
        S_ABD = extract_area([
            r"S\s*[_]?\s*ABD\s*=\s*([0-9]+(?:[.,][0-9]+)?)",
            r"площад[ьи]\s+треугольника\s+ABD[^0-9]*([0-9]+(?:[.,][0-9]+)?)",
        ])
        S_BCD = extract_area([
            r"S\s*[_]?\s*BCD\s*=\s*([0-9]+(?:[.,][0-9]+)?)",
            r"площад[ьи]\s+треугольника\s+BCD[^0-9]*([0-9]+(?:[.,][0-9]+)?)",
        ])

        base_total = float(AD) + float(DC) if AD is not None and DC is not None else None

        to_find_name = None
        if "меньш" in text_lower:
            to_find_name = "S_small"
        elif "больш" in text_lower:
            to_find_name = "S_big"
        elif wants("bcd"):
            to_find_name = "S_BCD"
        elif wants("abd"):
            to_find_name = "S_ABD"
        elif wants("abc"):
            to_find_name = "S_ABC"

        answer = None

        if to_find_name == "S_ABC":
            if S_ABC is not None:
                answer = S_ABC
            elif S_ABD is not None and base_total and AD:
                answer = normalize(float(S_ABD) * base_total / float(AD))
            elif S_BCD is not None and base_total and DC:
                answer = normalize(float(S_BCD) * base_total / float(DC))

        elif to_find_name == "S_ABD":
            if S_ABC is not None and base_total and AD:
                answer = normalize(float(S_ABC) * float(AD) / base_total)
            elif S_BCD is not None and AD and DC:
                answer = normalize(float(S_BCD) * float(AD) / float(DC))
            elif S_ABD is not None:
                answer = S_ABD

        elif to_find_name == "S_BCD":
            if S_ABC is not None and base_total and DC:
                answer = normalize(float(S_ABC) * float(DC) / base_total)
            elif S_ABD is not None and AD and DC:
                answer = normalize(float(S_ABD) * float(DC) / float(AD))
            elif S_BCD is not None:
                answer = S_BCD

        elif to_find_name in {"S_small", "S_big"}:
            area_abd = area_bcd = None

            if S_ABC is not None and base_total and AD is not None and DC is not None:
                area_abd = float(S_ABC) * float(AD) / base_total
                area_bcd = float(S_ABC) * float(DC) / base_total
            elif S_ABD is not None and base_total and AD is not None:
                total_area = float(S_ABD) * base_total / float(AD)
                area_abd = float(S_ABD)
                area_bcd = total_area - area_abd
            elif S_BCD is not None and base_total and DC is not None:
                total_area = float(S_BCD) * base_total / float(DC)
                area_bcd = float(S_BCD)
                area_abd = total_area - area_bcd

            if area_abd is not None and area_bcd is not None:
                answer = normalize(min(area_abd, area_bcd) if to_find_name == "S_small" else max(area_abd, area_bcd))

        image_file = None
        if AD is not None and DC is not None:
            if AD > DC:
                image_file = "T4_AD_DC.svg"
            else:# Включает и AD < DC, и AD == DC (используем один шаблон для обоих)
                image_file = "T4_DC_AD.svg"

        relations: Dict[str, float | int] = {}
        if S_ABC is not None:
            relations["S_ABC"] = S_ABC
        if S_ABD is not None:
            relations["S_ABD"] = S_ABD
        if S_BCD is not None:
            relations["S_BCD"] = S_BCD

        points_info: Dict[str, Dict[str, float | int]] = {"D_on_AC": {}}
        if AD is not None:
            points_info["D_on_AC"]["AD"] = AD
        if DC is not None:
            points_info["D_on_AC"]["DC"] = DC

        return {
            "id": raw.get("id"),
            "pattern": "triangle_area_by_dividing_point",
            "text": text,
            "answer": answer,
            "image_file": image_file,
            "variables": {
                "given": {
                    "triangle_name": "ABC",
                    "triangle_type": "general",
                    "sides": {},
                    "angles": {},
                    "trig": {},
                    "elements": {},
                    "points": points_info,
                    "relations": relations,
                },
                "to_find": {
                    "type": "area",
                    "name": to_find_name,
                },
                "humanizer_data": {
                    "side_roles": {},
                    "angle_names": {},
                    "element_names": {},
                },
            },
        }

    # ============================================================
    # PATTERN 2.3
    # triangle_area_by_parallel_line
    # ============================================================

    def _handle_triangle_area_by_parallel_line(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Универсальная обработка: задачи на площадь или сторону при MN ∥ AC (M∈AB, N∈BC).
        """
        text = raw["text"]
        text_lower = text.lower()

        def parse_number(value: str) -> float | int:
            cleaned = value.strip().replace(",", ".")
            number = float(cleaned)
            return int(number) if number.is_integer() else number

        def normalize(value: float | None) -> float | int | None:
            if value is None:
                return None
            rounded = round(value)
            if abs(value - rounded) < 1e-9:
                return int(rounded)
            return value

        def extract_area(patterns: list[str]) -> float | int | None:
            for pattern in patterns:
                match = re.search(pattern, text, flags=re.IGNORECASE)
                if match:
                    return parse_number(match.group(1))
            return None

        lengths: Dict[str, float | int | None] = {name: None for name in ("AC", "MN", "AB", "BC", "AM", "BM", "BN", "NC")}
        for name, value in re.findall(r"(AC|MN|AB|BC|AM|BM|BN|NC)\s*=\s*([0-9]+(?:[.,][0-9]+)?)", text, flags=re.IGNORECASE):
            lengths[name.upper()] = parse_number(value)

        AC = lengths["AC"]
        MN = lengths["MN"]
        AB = lengths["AB"]
        BC = lengths["BC"]

        S_ABC = extract_area([
            r"S\s*[_]?\s*ABC\s*=\s*([0-9]+(?:[.,][0-9]+)?)",
            r"площад[ьи]\s+треугольника\s+ABC[^0-9]*([0-9]+(?:[.,][0-9]+)?)",
        ])
        S_MBN = extract_area([
            r"S\s*[_]?\s*MBN\s*=\s*([0-9]+(?:[.,][0-9]+)?)",
            r"площад[ьи]\s+треугольника\s+MBN[^0-9]*([0-9]+(?:[.,][0-9]+)?)",
        ])

        area_task = "площад" in text_lower
        to_find_name = None
        if area_task:
            if "mbn" in text_lower:
                to_find_name = "S_MBN"
            elif "abc" in text_lower:
                to_find_name = "S_ABC"
        else:
            m = re.search(r"найд[^\n\r]*?(AM|BM|AB|BC|BN|NC|AC|MN)", text, flags=re.IGNORECASE)
            if m:
                to_find_name = m.group(1).upper()

        k = (MN / AC) if (MN is not None and AC is not None and AC != 0) else None

        answer = None
        if area_task:
            if to_find_name == "S_MBN" and S_ABC is not None and k is not None:
                answer = normalize(float(S_ABC) * (k ** 2))
            elif to_find_name == "S_ABC" and S_MBN is not None and k is not None:
                answer = normalize(float(S_MBN) / (k ** 2))
        else:
            if k is not None and to_find_name:
                if to_find_name == "BM" and AB is not None:
                    answer = normalize(float(AB) * k)
                elif to_find_name == "AM" and AB is not None:
                    answer = normalize(float(AB) * (1 - k))
                elif to_find_name == "AB":
                    if lengths["BM"] is not None and k != 0:
                        answer = normalize(float(lengths["BM"]) / k)
                    elif lengths["AM"] is not None and (1 - k) != 0:
                        answer = normalize(float(lengths["AM"]) / (1 - k))
                elif to_find_name == "BN" and BC is not None:
                    answer = normalize(float(BC) * k)
                elif to_find_name == "NC" and BC is not None:
                    answer = normalize(float(BC) * (1 - k))
                elif to_find_name == "BC":
                    if lengths["BN"] is not None and k != 0:
                        answer = normalize(float(lengths["BN"]) / k)
                    elif lengths["NC"] is not None and (1 - k) != 0:
                        answer = normalize(float(lengths["NC"]) / (1 - k))
                elif to_find_name == "MN" and AC is not None:
                    answer = normalize(float(AC) * k)
                elif to_find_name == "AC" and MN is not None and k != 0:
                    answer = normalize(float(MN) / k)
                elif to_find_name == "MN":
                    bm_val = lengths.get("BM")
                    if bm_val is None and AB is not None and lengths.get("AM") is not None:
                        bm_val = float(AB) - float(lengths["AM"])
                    if bm_val is not None and AB is not None and AC is not None:
                        k_local = bm_val / float(AB)
                        answer = normalize(float(AC) * k_local)

        image_file = "T5_triangle_area_by_parallel_line.svg"

        sides = {key: val for key, val in lengths.items() if key in ("AC", "AB", "BC") and val is not None}
        elements = {key: val for key, val in lengths.items() if key not in ("AC", "AB", "BC") and val is not None}
        relations = {}
        if S_ABC is not None:
            relations["S_ABC"] = S_ABC
        if S_MBN is not None:
            relations["S_MBN"] = S_MBN

        return {
            "id": raw.get("id"),
            "pattern": "triangle_area_by_parallel_line",
            "text": text,
            "answer": answer,
            "image_file": image_file,
            "variables": {
                "given": {
                    "triangle_name": "ABC",
                    "triangle_type": "general",
                    "sides": sides,
                    "angles": {},
                    "trig": {},
                    "elements": elements,
                    "points": {
                        "M": "on AB" if AB is not None else None,
                        "N": "on BC" if BC is not None else None,
                    },
                    "relations": relations,
                },
                "to_find": {
                    "type": "area" if area_task else "side",
                    "name": to_find_name,
                },
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
        Частный случай подобия: M, N — середины AB и BC, k = 1/2, площади соотносятся как 1 : 1/4 : 3/4.
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

        def normalize(value: float | None) -> float | int | None:
            if value is None:
                return None
            rounded = round(value)
            if abs(value - rounded) < 1e-9:
                return int(rounded)
            return value

        S_ABC = parse_area([
            r"S\s*[_]?\s*ABC\s*=\s*([0-9]+(?:[.,][0-9]+)?)",
            r"площад[ьи]\s+треугольника\s+ABC[^0-9]*([0-9]+(?:[.,][0-9]+)?)",
        ])
        S_MBN = parse_area([
            r"S\s*[_]?\s*MBN\s*=\s*([0-9]+(?:[.,][0-9]+)?)",
            r"площад[ьи]\s+треугольника\s+MBN[^0-9]*([0-9]+(?:[.,][0-9]+)?)",
        ])
        S_AMNC = parse_area([
            r"S\s*[_]?\s*AMNC\s*=\s*([0-9]+(?:[.,][0-9]+)?)",
            r"площад[ьи]\s+четыр[её]хугольника\s+AMNC[^0-9]*([0-9]+(?:[.,][0-9]+)?)",
        ])

        to_find_name = None
        m_target = re.search(r"найд[^\n\r]*?(s_abc|s_mbn|s_amnc|abc|mbn|amnc)", text_lower)
        if m_target:
            token = m_target.group(1).upper()
            if token in {"S_ABC", "ABC"}:
                to_find_name = "S_ABC"
            elif token in {"S_MBN", "MBN"}:
                to_find_name = "S_MBN"
            elif token in {"S_AMNC", "AMNC"}:
                to_find_name = "S_AMNC"
        else:
            if "mbn" in text_lower:
                to_find_name = "S_MBN"
            elif "amnc" in text_lower:
                to_find_name = "S_AMNC"
            elif "abc" in text_lower:
                to_find_name = "S_ABC"

        answer = None
        calc_abc = calc_mbn = calc_amnc = None

        if S_ABC is not None:
            calc_abc = S_ABC
            calc_mbn = S_ABC / 4
            calc_amnc = S_ABC * 3 / 4
        elif S_MBN is not None:
            calc_mbn = S_MBN
            calc_abc = S_MBN * 4
            calc_amnc = S_MBN * 3
        elif S_AMNC is not None:
            calc_amnc = S_AMNC
            calc_abc = S_AMNC * 4 / 3
            calc_mbn = S_AMNC / 3

        if to_find_name == "S_ABC":
            answer = normalize(calc_abc)
        elif to_find_name == "S_MBN":
            answer = normalize(calc_mbn)
        elif to_find_name == "S_AMNC":
            answer = normalize(calc_amnc)

        relations = {}
        if S_ABC is not None:
            relations["S_ABC"] = S_ABC
        if S_MBN is not None:
            relations["S_MBN"] = S_MBN
        if S_AMNC is not None:
            relations["S_AMNC"] = S_AMNC

        return {
            "id": raw.get("id"),
            "pattern": "triangle_area_by_midpoints",
            "text": text,
            "answer": answer,
            "image_file": "T6_triangle_area_by_midpoints.svg",
            "variables": {
                "given": {
                    "triangle_name": "ABC",
                    "triangle_type": "general",
                    "sides": {},
                    "angles": {},
                    "trig": {},
                    "elements": {},
                    "points": {
                        "M": "midpoint of AB",
                        "N": "midpoint of BC",
                    },
                    "relations": relations,
                },
                "to_find": {
                    "type": "area",
                    "name": to_find_name,
                },
                "humanizer_data": {
                    "side_roles": {},
                    "angle_names": {},
                    "element_names": {},
                },
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

        if answer is not None:
            rounded = round(answer, 3)
            if abs(rounded - round(rounded)) < 1e-9:
                answer = int(round(rounded))
            else:
                answer = rounded

        image_file = "T3_obtuse_A.svg" if (answer is not None and answer < 0) else "T3_acute.svg"

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
                        "AB": sides.get("AB"),
                        "BC": sides.get("BC"),
                        "AC": sides.get("AC")
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

        sides: Dict[str, float | int] = {}
        for name, val in re.findall(r"(AB|BC|AC)\s*=\s*([0-9]+(?:[.,][0-9]+)?)", text, flags=re.IGNORECASE):
            sides[name.upper()] = parse_number(val)

        if len(sides) != 1:
            raise ValueError(f"triangle_by_two_angles_and_side: должна быть ровно одна известная сторона в '{text}'")

        given_side_name, given_side_value = list(sides.items())[0]

        to_find_match = re.search(r"найд[^\n\r]*?(AB|BC|AC)", text, flags=re.IGNORECASE)
        if not to_find_match:
            raise ValueError(f"triangle_by_two_angles_and_side: не могу определить искомую сторону в '{text}'")
        to_find = to_find_match.group(1).upper()

        import math
        sin = lambda x: math.sin(math.radians(float(x)))
        sinA, sinB, sinC = sin(A), sin(B), sin(C)

        def angle_opposite_side(side: str) -> str:
            return {"BC": "A", "AC": "B", "AB": "C"}[side]

        given_angle_letter = angle_opposite_side(given_side_name)
        sin_given = {"A": sinA, "B": sinB, "C": sinC}[given_angle_letter]
        k = float(given_side_value) / sin_given

        target_angle_letter = angle_opposite_side(to_find)
        sin_target = {"A": sinA, "B": sinB, "C": sinC}[target_angle_letter]
        answer = k * sin_target

        if abs(answer - round(answer)) < 1e-9:
            answer = int(round(answer))
        else:
            answer = round(answer, 3)

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
                    "sides": {given_side_name: given_side_value},
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
