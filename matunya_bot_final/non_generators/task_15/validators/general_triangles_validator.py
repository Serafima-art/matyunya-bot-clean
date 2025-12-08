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
        """
        text = raw["text"]

        # --- 1. Извлечение сторон ---
        sides: Dict[str, float] = {}

        # A) Формат "AB = 10", "AC = 6√3" и т.п.
        for match in re.finditer(r"\b(AB|BC|AC)\s*=\s*([0-9.,√]+)", text, flags=re.IGNORECASE):
            name, value = match.groups()
            value = value.rstrip(".")
            sides[name.upper()] = self._parse_numeric_with_root(value)

        # B) Формат "стороны AC и BC ... равны 30 и 8 (соответственно)"
        combo_pattern_1 = re.search(
            r"(?:стороны|сторона)\s+(AB|BC|AC)\s+и\s+(AB|BC|AC)[^=]*?"
            r"(?:равны|=)\s*([0-9.,√]+)\s+и\s+([0-9.,√]+)",
            text,
            flags=re.IGNORECASE,
        )
        if combo_pattern_1:
            s1, s2, v1, v2 = combo_pattern_1.groups()
            v1 = v1.rstrip(".")
            v2 = v2.rstrip(".")
            if s1.upper() not in sides:
                sides[s1.upper()] = self._parse_numeric_with_root(v1)
            if s2.upper() not in sides:
                sides[s2.upper()] = self._parse_numeric_with_root(v2)

        # C) Формат "AC и BC равны 30 и 8" (без слова "стороны")
        combo_pattern_2 = re.search(
            r"\b(AB|BC|AC)\s+и\s+(AB|BC|AC)\s+(?:равны|=)\s*([0-9.,√]+)\s+и\s+([0-9.,√]+)",
            text,
            flags=re.IGNORECASE,
        )
        if combo_pattern_2:
            s1, s2, v1, v2 = combo_pattern_2.groups()
            v1 = v1.rstrip(".")
            v2 = v2.rstrip(".")
            if s1.upper() not in sides:
                sides[s1.upper()] = self._parse_numeric_with_root(v1)
            if s2.upper() not in sides:
                sides[s2.upper()] = self._parse_numeric_with_root(v2)

        # --- 2. Парсинг угла (sin или градусы) ---
        angle_letter = None          # A / B / C
        sin_value_num: Optional[float] = None
        trig_info: Dict[str, str] = {}
        angle_display_name: Optional[str] = None
        found_degrees: Optional[int] = None  # пока не используем, но пусть будет

        # Способ A: ищем явное "sin∠C = 5/12" или "sin C равен 0,4"
        sin_match = re.search(
            r"sin\s*[∠]?\s*([ABC]{1,3})\s*(?:=|равен|равна)\s*([0-9]+/[0-9]+|[0-9.,]+)",
            text,
            flags=re.IGNORECASE,
        )
        if sin_match:
            angle_spec = sin_match.group(1).upper()      # "C" или "ABC"
            angle_letter = angle_spec[1] if len(angle_spec) == 3 else angle_spec[0]
            sin_value_raw = sin_match.group(2).strip().replace(",", ".")
            if sin_value_raw.endswith("."):
                sin_value_raw = sin_value_raw[:-1]

            # безопасный разбор дроби/десятичного числа
            if "/" in sin_value_raw:
                num_str, den_str = sin_value_raw.split("/", 1)
                sin_value_num = float(num_str) / float(den_str)
            else:
                sin_value_num = float(sin_value_raw)

            trig_info[f"sin_{angle_letter}"] = sin_value_raw
            angle_display_name = f"∠{angle_spec}"

        else:
            # Способ Б: "угол A равен 150°"
            angle_match = re.search(
                r"(?:угол|∠)\s*([A-Z]{1,3})\s*(?:=|равен|равна)\s*(\d+)",
                text,
                flags=re.IGNORECASE,
            )
            if angle_match:
                angle_spec = angle_match.group(1).upper()
                angle_letter = angle_spec[1] if len(angle_spec) == 3 else angle_spec[0]
                degrees = int(angle_match.group(2))
                found_degrees = degrees

                # стандартные значения sin для "красивых" углов
                sin_map = {
                    30: 0.5,
                    45: math.sqrt(2) / 2,
                    60: math.sqrt(3) / 2,
                    90: 1.0,
                    120: math.sqrt(3) / 2,
                    135: math.sqrt(2) / 2,
                    150: 0.5,
                }

                if degrees in sin_map:
                    sin_value_num = sin_map[degrees]
                    angle_display_name = f"∠{angle_spec}"

        # --- 3. Вычисление площади ---
        area: Optional[float] = None
        # какому углу какие стороны "прилежат"
        side_pairs = {
            "A": ("AB", "AC"),
            "B": ("AB", "BC"),
            "C": ("AC", "BC"),
        }

        if angle_letter in side_pairs and sin_value_num is not None:
            side1_name, side2_name = side_pairs[angle_letter]
            side1 = sides.get(side1_name)
            side2 = sides.get(side2_name)
            if side1 is not None and side2 is not None:
                area = 0.5 * side1 * side2 * sin_value_num

        # --- 4. Выбор картинки ---
        # Если угол в градусах есть и > 90°, используем тупой, иначе — острый.
        image_file = "T3_acute.svg"
        if angle_letter:
            obtuse_match = re.search(
                rf"(?:угол\s*{angle_letter}|∠\s*{angle_letter})\s*(?:=|равен|равна)?\s*(\d+)",
                text,
                flags=re.IGNORECASE,
            )
            if obtuse_match and int(obtuse_match.group(1)) > 90:
                image_file = f"T3_obtuse_{angle_letter}.svg"

        # --- 5. Сборка JSON строго по эталону ---
        return {
            "id": raw.get("id"),
            "pattern": "triangle_area_by_sin",
            "text": text,
            "answer": self._format_number(area),
            "image_file": image_file,
            "variables": {
                "given": {
                    "triangle_name": "ABC",
                    "triangle_type": "general",
                    "sides": sides,
                    "angles": {},
                    "trig": trig_info,
                    "elements": {},
                    "points": {},
                    "relations": {},
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
        Читаем AD/DC или их отношение, площади, определяем, что искать,
        считаем ответ и собираем Etalon 3.0.
        """

        text = raw["text"]
        text_lower = text.lower()

        def parse_number(value: str) -> float | int:
            return self._parse_numeric_with_root(value)

        def extract_area(patterns: list[str]) -> float | int | None:
            """ Ищем площадь по нескольким возможным паттернам """
            for pattern in patterns:
                match = re.search(pattern, text, flags=re.IGNORECASE)
                if match:
                    return parse_number(match.group(1))
            return None

        def asks_for(target: str) -> bool:
            """
            Определяет, что именно ПРОСЯТ найти:
            — 'найдите площадь BCD'
            — 'найти ABD'
            — 'вычислите площадь треугольника ABC'
            Не реагирует на данные 'площадь ABC равна ...'
            """
            # 1. Прямой запрос: найти ABC/ABD/BCD
            if re.search(rf"(найти|найдите|вычислите|определите)[^.]*\b{target}\b", text_lower):
                return True

            # 2. Запрос «найдите площадь треугольника BCD»
            if re.search(
                rf"(найти|найдите|вычислите|определите)[^.]*площад[ьи][^.]*{target}",
                text_lower
            ):
                return True

            # 3. Запрос в стиле: "площадь треугольника BCD. Найди"
            if re.search(
                rf"найд[^\n\r]*площад[ьи][^\n\r]*{target}",
                text_lower
            ):
                return True

            return False

        # ------------------------------------------------------------
        # 1. Считываем AD и DC
        # ------------------------------------------------------------
        AD = None
        DC = None

        # Форматы AD=7, DC = 8
        for name, value in re.findall(r"(AD|DC)\s*=\s*([0-9]+(?:[.,][0-9]+)?)", text, flags=re.IGNORECASE):
            if name.upper() == "AD":
                AD = parse_number(value)
            else:
                DC = parse_number(value)

        # Формат AD : DC = 2 : 7
        ratio = re.search(r"AD\s*:\s*DC\s*=\s*([0-9]+)\s*:\s*([0-9]+)", text, flags=re.IGNORECASE)
        if ratio:
            AD = parse_number(ratio.group(1))
            DC = parse_number(ratio.group(2))

        # Обратное отношение
        ratio_rev = re.search(r"DC\s*:\s*AD\s*=\s*([0-9]+)\s*:\s*([0-9]+)", text, flags=re.IGNORECASE)
        if ratio_rev:
            DC = parse_number(ratio_rev.group(1))
            AD = parse_number(ratio_rev.group(2))

        # 👉 ДОБАВИТЬ ВОТ ЭТО
        ratio_plain = re.search(r"в\s+отношени[ии]\s*([0-9]+)\s*[:]\s*([0-9]+)", text_lower)
        if ratio_plain:
            AD = parse_number(ratio_plain.group(1))
            DC = parse_number(ratio_plain.group(2))

        # ------------------------------------------------------------
        # 2. Читаем площади
        # ------------------------------------------------------------

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

        # ------------------------------------------------------------
        # 3. Определяем, какую площадь ищет задача
        # ------------------------------------------------------------
        to_find_name = None

        # 3.1 "меньшую/большую площадь"
        if "меньш" in text_lower:
            to_find_name = "S_small"
        elif "больш" in text_lower:
            to_find_name = "S_big"

        else:
            # 3.2 прямой вопрос: НАЙТИ BCD/ABD/ABC
            if asks_for("bcd"):
                to_find_name = "S_BCD"
            elif asks_for("abd"):
                to_find_name = "S_ABD"
            elif asks_for("abc"):
                to_find_name = "S_ABC"

            # 3.3 fallback — ловим последнее слово после "найти" перед точкой
            if to_find_name is None:
                m = re.search(r"найти[^.]*?(abd|bcd|abc)", text_lower)
                if m:
                    token = m.group(1)
                    to_find_name = f"S_{token.upper()}"

            # 3.4 если так и не определили — ошибка данных
            if to_find_name is None:
                raise ValueError(f"Не удалось определить искомую площадь: {text}")

        # ------------------------------------------------------------
        # 4. Считаем ответ
        # ------------------------------------------------------------
        answer = None

        if to_find_name == "S_ABC":
            if S_ABC is not None:
                answer = S_ABC
            elif S_ABD is not None and AD and base_total:
                answer = float(S_ABD) * base_total / float(AD)
            elif S_BCD is not None and DC and base_total:
                answer = float(S_BCD) * base_total / float(DC)

        elif to_find_name == "S_ABD":
            if S_ABD is not None:
                answer = S_ABD
            elif S_ABC is not None and AD and base_total:
                answer = float(S_ABC) * float(AD) / base_total
            elif S_BCD is not None and AD and DC:
                answer = float(S_BCD) * float(AD) / float(DC)

        elif to_find_name == "S_BCD":
            if S_BCD is not None:
                answer = S_BCD
            elif S_ABC is not None and DC and base_total:
                answer = float(S_ABC) * float(DC) / base_total
            elif S_ABD is not None and AD and DC:
                answer = float(S_ABD) * float(DC) / float(AD)

        elif to_find_name in {"S_small", "S_big"}:
            area_abd = area_bcd = None

            if S_ABC is not None and AD and DC:
                area_abd = float(S_ABC) * float(AD) / float(base_total)
                area_bcd = float(S_ABC) * float(DC) / float(base_total)

            elif S_ABD is not None and AD and DC:
                total_area = float(S_ABD) * float(base_total) / float(AD)
                area_abd = float(S_ABD)
                area_bcd = total_area - area_abd

            elif S_BCD is not None and AD and DC:
                total_area = float(S_BCD) * float(base_total) / float(DC)
                area_bcd = float(S_BCD)
                area_abd = total_area - area_bcd

            if area_abd is not None and area_bcd is not None:
                answer = min(area_abd, area_bcd) if to_find_name == "S_small" else max(area_abd, area_bcd)

        # Финальный формат числа
        answer = self._format_number(answer)

        # ------------------------------------------------------------
        # 5. Выбор картинки T4_AD_DC или T4_DC_AD
        # ------------------------------------------------------------
        image_file = None
        if AD is not None and DC is not None:
            image_file = "T4_AD_DC.svg" if AD > DC else "T4_DC_AD.svg"

        # ------------------------------------------------------------
        # 6. Сборка JSON
        # ------------------------------------------------------------
        relations: Dict[str, float | int | str] = {}
        if S_ABC is not None:
            relations["S_ABC"] = self._format_number(S_ABC)
        if S_ABD is not None:
            relations["S_ABD"] = self._format_number(S_ABD)
        if S_BCD is not None:
            relations["S_BCD"] = self._format_number(S_BCD)

        points_info = {"D_on_AC": {}}
        if AD is not None:
            points_info["D_on_AC"]["AD"] = self._format_number(AD)
        if DC is not None:
            points_info["D_on_AC"]["DC"] = self._format_number(DC)

        return {
            "id": raw.get("id"),
            "pattern": raw["pattern"],
            "text": raw["text"],
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
                "to_find": {"type": "area", "name": to_find_name},
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
        Задачи вида: MN ∥ AC, M ∈ AB, N ∈ BC.

        Умеем:
        - находить площадь S_MBN или S_ABC;
        - находить стороны (AM, BM, AB, BN, NC, BC, AC, MN);
        - находить отношение MN : AC (как десятичное число).
        """
        text = raw["text"]
        text_lower = text.lower()

        # ---------- 0. Определение задач на отношение ----------
        relation_task = False
        relation_target = None  # 'MN/AC' или 'AC/MN', или по X:Y

        # a) Форматы "MN / AC", "MN : AC"
        m_rel = re.search(r"(MN)\s*[:/]\s*(AC)", text, flags=re.IGNORECASE)
        if not m_rel:
            m_rel = re.search(r"(AC)\s*[:/]\s*(MN)", text, flags=re.IGNORECASE)

        if m_rel:
            relation_task = True
            a, b = m_rel.group(1).upper(), m_rel.group(2).upper()
            relation_target = f"{a}/{b}"

        # b) Форматы "отношение MN к AC"
        m_rel2 = re.search(r"отношени[ея]\s+([A-Z]{2})\s+(?:к|и)\s+([A-Z]{2})", text_lower)
        if m_rel2:
            relation_task = True
            a, b = m_rel2.group(1).upper(), m_rel2.group(2).upper()
            relation_target = f"{a}/{b}"

        # c) Формат "MN относится к AC как 1 к 2"
        m_rel3 = re.search(
            r"(MN|AC)\s+относит[^\n]*?\s+(AC|MN)\s+как\s+(\d+)\s*к\s*(\d+)",
            text_lower,
        )
        ratio_value = None
        if m_rel3:
            relation_task = True
            a = m_rel3.group(1).upper()
            b = m_rel3.group(2).upper()
            x = int(m_rel3.group(3))
            y = int(m_rel3.group(4))
            relation_target = f"{a}/{b}"
            ratio_value = x / y

        # ---------- Вспомогательные парсеры ----------

        def parse_number(value: str) -> float | int:
            cleaned = value.strip().replace(",", ".")
            num = float(cleaned)
            return int(num) if num.is_integer() else num

        def extract_area(patterns: list[str]) -> float | int | None:
            """Ищем площадь по набору шаблонов."""
            for pattern in patterns:
                m = re.search(pattern, text, flags=re.IGNORECASE)
                if m:
                    return parse_number(m.group(1))
            return None

        def extract_ratio_mn_ac() -> float | None:
            """
            Ищем отношение MN : AC в формах:
            - 'MN относится к AC как 1 к 2'
            - 'отношение MN : AC равно 1 : 2'
            - 'MN : AC = 1 : 2'
            Возвращаем k = MN/AC.
            """
            # MN относится к AC как 1 к 2
            m = re.search(
                r"MN[^\n\r]*?относ[^\n\r]*?AC[^\d]*?([0-9]+)\s*к\s*([0-9]+)",
                text,
                flags=re.IGNORECASE,
            )
            if m:
                a, b = m.groups()
                if float(b) != 0:
                    return float(a) / float(b)

            # отношение MN : AC равно 1 : 2
            m = re.search(
                r"отношен[иея][^\n\r]*MN\s*[:]\s*AC[^\d]*([0-9]+)\s*[:]\s*([0-9]+)",
                text,
                flags=re.IGNORECASE,
            )
            if m:
                a, b = m.groups()
                if float(b) != 0:
                    return float(a) / float(b)

            # MN : AC = 1 : 2
            m = re.search(
                r"MN\s*[:]\s*AC[^\d]*([0-9]+)\s*[:]\s*([0-9]+)",
                text,
                flags=re.IGNORECASE,
            )
            if m:
                a, b = m.groups()
                if float(b) != 0:
                    return float(a) / float(b)

            return None

        # ---------- 1. Числа при равенствах длин ----------

        lengths: Dict[str, float | int | None] = {
            name: None for name in ("AC", "MN", "AB", "BC", "AM", "BM", "BN", "NC")
        }

        # Формат "AC = 30"
        for name, value in re.findall(
            r"\b(AC|MN|AB|BC|AM|BM|BN|NC|CN)\b\s*=\s*([0-9]+(?:[.,][0-9]+)?)",
            text,
            flags=re.IGNORECASE,
        ):
            key = name.upper()
            if key == "CN":
                key = "NC"   # <-- нормализуем
            lengths[key] = parse_number(value)

        # Формат "AC равна 30", "AB равен 16"
        for name, value in re.findall(
            r"\b(AC|MN|AB|BC|AM|BM|BN|NC|CN)\b\s+равн[аое]\s*([0-9]+(?:[.,][0-9]+)?)",
            text,
            flags=re.IGNORECASE,
        ):
            key = name.upper()
            if key == "CN":
                key = "NC"
            if lengths[key] is None:
                lengths[key] = parse_number(value)

        AC = lengths["AC"]
        MN = lengths["MN"]
        AB = lengths["AB"]
        BC = lengths["BC"]
        BN = lengths["BN"]

        # ---------- 2. Площади S_ABC и S_MBN ----------

        S_ABC = extract_area(
            [
                r"S\s*[_]?\s*ABC\s*=\s*([0-9]+(?:[.,][0-9]+)?)",
                r"площад[ьи]\s+треугольника\s+ABC[^0-9]*([0-9]+(?:[.,][0-9]+)?)",
                r"треугольник[а]?\s+ABC\s+с\s+площад[ьюи]\s*([0-9]+(?:[.,][0-9]+)?)",
            ]
        )

        S_MBN = extract_area(
            [
                r"S\s*[_]?\s*MBN\s*=\s*([0-9]+(?:[.,][0-9]+)?)",
                r"площад[ьи]\s+треугольника\s+MBN[^0-9]*([0-9]+(?:[.,][0-9]+)?)",
            ]
        )

        # ---------- 3. Коэффициент подобия k = MN / AC ----------

        k: float | None = None

        # a) Явное отношение MN:AC
        k = extract_ratio_mn_ac()

        # b) Если k не нашли, но заданы MN и AC
        if k is None and MN is not None and AC is not None and AC != 0:
            k = float(MN) / float(AC)

        # c) Если k всё ещё None, пробуем BN / BC
        if k is None and BN is not None and BC is not None and BC != 0:
            k = float(BN) / float(BC)

        def parse_to_find(text: str):
            """Определяет, что нужно найти: площадь, отношение или сторону."""

            # --- 1. ПЛОЩАДЬ ---

            # Формат: «Найди площадь треугольника MBN»
            m = re.search(
                r"найд[^\n\r]*площад[^\n\r]*треугольник[а]?\s+([A-Z]{2,3})",
                text,
                flags=re.IGNORECASE,
            )
            if m:
                tri = m.group(1).upper()
                return {"type": "area", "name": f"S_{tri}"}

            # Формат: «Найди площадь MBN»
            m = re.search(
                r"найд[^\n\r]*площад[^\n\r]*([A-Z]{2,3})",
                text,
                flags=re.IGNORECASE,
            )
            if m:
                tri = m.group(1).upper()
                return {"type": "area", "name": f"S_{tri}"}

            # --- 2. ОТНОШЕНИЕ ---

            # Формат: «Найди отношение MN : AC» или «MN / AC»
            m = re.search(
                r"найд[^\n\r]*отношен[^\n\r]*([A-Z]{2})\s*[:/]\s*([A-Z]{2})",
                text,
                flags=re.IGNORECASE,
            )
            if m:
                a = m.group(1).upper()
                b = m.group(2).upper()
                return {"type": "ratio", "name": f"{a}/{b}"}

            # Формат: «Найди отношение AC к MN»
            m = re.search(
                r"найд[^\n\r]*отношен[^\n\r]*([A-Z]{2})\s+к\s+([A-Z]{2})",
                text,
                flags=re.IGNORECASE,
            )
            if m:
                a = m.group(1).upper()
                b = m.group(2).upper()
                return {"type": "ratio", "name": f"{a}/{b}"}

            # --- 3. СТОРОНА (AM, BM, AB, AC...) ---

            m = re.search(
                r"найд[^\n\r]*\b([ABCMN]{1,2})\b",
                text,
                flags=re.IGNORECASE,
            )
            if m:
                return {"type": "side", "name": m.group(1).upper()}

            raise ValueError(f"Не удалось определить, что нужно найти: {text}")


        def compute_answer(parsed, given):
            """
            Вычисляет числовой ответ по формулам подобия.
            parsed = {"type": "...", "name": "..."}
            given = словарь relations + sides + elements
            """

            relations = given.get("relations", {})
            sides = given.get("sides", {})
            elements = given.get("elements", {})

            # Удобные обозначения:
            S_ABC = relations.get("S_ABC")
            S_MBN = relations.get("S_MBN")
            AC = sides.get("AC")
            MN = elements.get("MN")

            # -----------------------------
            # 1) ИЩЕМ ПЛОЩАДЬ S_MBN
            # -----------------------------
            if parsed["type"] == "area" and parsed["name"] == "S_MBN":
                if S_ABC is not None and AC and MN:
                    k = MN / AC
                    return S_ABC * k * k
                if S_MBN is not None:  # уже дана
                    return S_MBN

            # -----------------------------
            # 2) ИЩЕМ ПЛОЩАДЬ S_ABC
            # -----------------------------
            if parsed["type"] == "area" and parsed["name"] == "S_ABC":
                if S_MBN is not None and AC and MN:
                    k = MN / AC
                    return S_MBN / (k * k)
                if S_ABC is not None:
                    return S_ABC

            # -----------------------------
            # 3) ИЩЕМ ОТНОШЕНИЕ MN/AC
            # -----------------------------
            if parsed["type"] == "ratio" and parsed["name"] == "MN/AC":
                if S_MBN is not None and S_ABC is not None:
                    return math.sqrt(S_MBN / S_ABC)
                if MN and AC:
                    return MN / AC

            # -----------------------------
            # 4) ИЩЕМ СТОРОНУ (например, AM)
            # -----------------------------
            # Пока возвращаем None — это отдельный подтип
            if parsed["type"] == "side":
                return None

            return None

        # ---------- 6. Подготовка JSON ----------

        image_file = "T5_triangle_area_by_parallel_line.svg"

        sides = {
            key: self._format_number(val)
            for key, val in lengths.items()
            if key in ("AC", "AB", "BC") and val is not None
        }
        elements = {
            key: self._format_number(val)
            for key, val in lengths.items()
            if key not in ("AC", "AB", "BC") and val is not None
        }

        relations: Dict[str, float | int | str] = {}
        if S_ABC is not None:
            relations["S_ABC"] = self._format_number(S_ABC)
        if S_MBN is not None:
            relations["S_MBN"] = self._format_number(S_MBN)

        points: Dict[str, str] = {}
        if AB is not None:
            points["M"] = "on AB"
        if BC is not None:
            points["N"] = "on BC"

        parsed_to_find = parse_to_find(text)

        # -------------------------------------------------------------
        # ВОССТАНАВЛИВАЕМ ПЕРЕМЕННЫЕ ДЛЯ JSON (answer, area_task, to_find_name)
        # -------------------------------------------------------------

        # 1. area_task — ищем его так же, как было раньше
        area_task = ("найди площадь" in text_lower) or ("вычисли площадь" in text_lower)

        # 2. to_find_name — используем parsed_to_find
        to_find_name = parsed_to_find["name"]

        # 3. answer — вычисляем правильно
        answer = compute_answer(parsed_to_find, {
            "sides": sides,
            "elements": elements,
            "relations": relations,
        })
        answer = self._format_number(answer)

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
                "points": points,
                "relations": relations,
            },
            "to_find": {
                "type": (
                    "ratio" if relation_task
                    else ("area" if area_task else "side")
                ),
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

        S_ABC = parse_area([
        r"S\s*[_]?\s*ABC\s*=\s*([0-9]+(?:[.,][0-9]+)?)",
        r"площад[ьи]\s+треугольника\s+ABC[^0-9]*([0-9]+(?:[.,][0-9]+)?)",
        r"треугольник[е]?\s+ABC[^0-9]*площад[ьюи]\s*([0-9]+(?:[.,][0-9]+)?)",
        r"в\s+треугольнике\s+abc[^0-9]*площад[ьяи]\s+равн[аы]\s*([0-9]+(?:[.,][0-9]+)?)",
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
        m_target = re.search(
            r"найд[^\n\r]*?(?:площад[ьюи]\s+)?(s_abc|s_mbn|s_amnc|abc|mbn|amnc)",
            text_lower
        )
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
            answer = calc_abc
        elif to_find_name == "S_MBN":
            answer = calc_mbn
        elif to_find_name == "S_AMNC":
            answer = calc_amnc

        answer = self._format_number(answer)

        relations = {}
        if S_ABC is not None:
            relations["S_ABC"] = self._format_number(S_ABC)
        if S_MBN is not None:
            relations["S_MBN"] = self._format_number(S_MBN)
        if S_AMNC is not None:
            relations["S_AMNC"] = self._format_number(S_AMNC)

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
