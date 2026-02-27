import re
import math
from typing import Dict, Any, Tuple, List, Optional


class PaperSheetsValidator:
    """
    Валидатор non_generators для практико-ориентированного блока "Форматы бумаги A0–A7" (задания 1–5).

    Контракт контейнера (эталон):
    {
      "id": "paper_2026_var_18",
      "image_file": "task_paper_formats.png",
      "table_context": {
        "table_order": ["A3", "A1", "A6", "A7"],
        "formats_data": {...}
      },
      "questions": [
        { "q_number": 1, ... },
        ...
        { "q_number": 5, ... }
      ]
    }

    Минималистичный solution_data:
    - Q1: mapping + answer_sequence
    - Q2: index_difference + power_value
    - Q3:
        - линейные: length_mm, width_mm, selected_value (+ original/rounded для rounding)
        - ratio/diagonal_ratio: rounded_ratio
    - Q4:
        - area_basic: length_cm, width_cm, area
        - rounding: area_raw, rounded_area
    - Q5:
        - pack_weight: index_difference, sheet_area_factor, weight_one_sheet, total_weight
        - font_scaling: index_difference, rounded_font
    """

    PAPER_SIZES = {
        "A0": (1189, 841),
        "A1": (841, 594),
        "A2": (594, 420),
        "A3": (420, 297),
        "A4": (297, 210),
        "A5": (210, 148),
        "A6": (148, 105),
        "A7": (105, 74),
    }

    PAPER_ORDER = ["A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7"]

    # ================================================================
    # PUBLIC
    # ================================================================

    def validate(self, raw_variant: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
        errors: List[str] = []
        text_block = raw_variant.get("question_text", "") or ""

        parsed = self._parse_monolith(text_block)

        variant_id = parsed.get("VARIANT_CODE")
        image_file = parsed.get("IMAGE")
        table_order = parsed.get("TABLE_ORDER")

        if not variant_id or not table_order:
            return False, {}, ["Не найден VARIANT_CODE или TABLE_ORDER"]

        formats_data = self._build_formats_data()

        container: Dict[str, Any] = {
            "id": variant_id,
            "image_file": image_file,
            "table_context": {
                "table_order": table_order,
                "formats_data": formats_data,
            },
            "questions": [],
        }

        for q_num in range(1, 6):
            q_key = f"Q{q_num}"
            q_data = parsed.get(q_key)
            if not q_data:
                errors.append(f"Не найден {q_key}")
                continue

            try:
                question = self._build_question(q_num, q_data, table_order, formats_data)
                container["questions"].append(question)
            except Exception as e:
                errors.append(f"Ошибка в Q{q_num}: {str(e)}")

        return len(errors) == 0, container, errors

    # ================================================================
    # QUESTION BUILDER
    # ================================================================

    def _build_question(
        self,
        q_number: int,
        q_data: Dict[str, Any],
        table_order: List[str],
        formats_data: Dict[str, Any],
    ) -> Dict[str, Any]:

        pattern = q_data.get("PATTERN")
        narrative = q_data.get("NARRATIVE")
        text = (q_data.get("TEXT") or "").strip()

        if pattern == "paper_format_match":
            return self._build_q1(q_number, q_data, table_order, text)

        if pattern == "paper_split":
            return self._build_q2(q_number, text)

        if pattern == "paper_dimensions":
            return self._build_q3(q_number, narrative, text, table_order, formats_data)

        if pattern == "paper_area":
            return self._build_q4(q_number, narrative, text)

        if pattern in ("paper_pack_weight", "paper_font_scaling"):
            return self._build_q5(q_number, pattern, narrative, text)

        raise ValueError(f"Неизвестный pattern: {pattern}")

    # ================================================================
    # Q1 — paper_format_match
    # ================================================================

    def _build_q1(
        self,
        q_number: int,
        q_data: Dict[str, Any],
        table_order: List[str],
        text: str
    ) -> Dict[str, Any]:

        raw_cols = q_data.get("COLUMNS", "")
        if not raw_cols:
            raise ValueError("Q1: не найдено поле COLUMNS")

        columns = [x.strip() for x in raw_cols.split("|") if x.strip()]
        if len(columns) != 4:
            raise ValueError("Q1: COLUMNS должен содержать 4 формата")

        mapping = {str(i + 1): fmt for i, fmt in enumerate(table_order)}

        # ответ: для каждого формата из columns найти номер строки
        answer_digits: List[str] = []
        for fmt in columns:
            found = None
            for row, row_fmt in mapping.items():
                if row_fmt == fmt:
                    found = row
                    break
            if not found:
                raise ValueError(f"Q1: формат {fmt} не найден в TABLE_ORDER")
            answer_digits.append(found)

        answer = "".join(answer_digits)

        return {
            "q_number": q_number,
            "pattern": "paper_format_match",
            "narrative": "match_formats_to_rows",
            "question_text": text,
            "input_data": {"columns_order": columns},
            "solution_data": {
                "row_to_format_mapping": mapping,
                "answer_sequence": answer,
            },
            "answer": answer,
        }

    # ================================================================
    # Q2 — paper_split (count_subformats)
    # ================================================================

    def _build_q2(self, q_number: int, text: str) -> Dict[str, Any]:
        # Пример: "Сколько листов формата A7 можно получить из одного листа формата A3?"
        formats = re.findall(r"\b(A[0-7])\b", text)
        if len(formats) < 2:
            raise ValueError("Q2: не удалось извлечь форматы (ожидаются два A-формата)")

        # Обычно: первый — 'to', второй — 'from'
        fmt_to = formats[0]
        fmt_from = formats[1]

        idx_from = int(fmt_from[1:])
        idx_to = int(fmt_to[1:])

        # Делим больший формат на меньший: A3 -> A7 (3 -> 7) ОК
        if idx_from > idx_to:
            raise ValueError(f"Q2 логическая ошибка: нельзя получить {fmt_to} из {fmt_from}")

        index_difference = idx_to - idx_from
        power_value = 2 ** index_difference

        return {
            "q_number": q_number,
            "pattern": "paper_split",
            "narrative": "count_subformats",
            "question_text": text,
            "input_data": {"from_format": fmt_from, "to_format": fmt_to},
            "solution_data": {
                "index_difference": index_difference,
                "power_value": power_value,
            },
            "answer": power_value,
        }

    # ================================================================
    # Q3 — paper_dimensions (Новая логика)
    # ================================================================

    def _build_q3(
        self,
        q_number: int,
        narrative: str,
        text: str,
        table_order: List[str],
        formats_data: Dict[str, Dict[str, int]],
    ) -> Dict[str, Any]:

        fmt = self._extract_format(text, err_prefix="Q3")

        if fmt not in formats_data:
            raise ValueError(f"Q3: формат {fmt} отсутствует в formats_data")

        # ------------------------------------------------------------
        # find_ratio — без изменений (источник истины: formats_data)
        # ------------------------------------------------------------
        if narrative == "find_ratio":
            length_mm = formats_data[fmt]["length_mm"]
            width_mm = formats_data[fmt]["width_mm"]

            greater = max(length_mm, width_mm)
            smaller = min(length_mm, width_mm)

            raw_ratio = (greater / smaller) if ("больш" in text.lower()) else (smaller / greater)
            rounded_ratio = self._round_to_1(raw_ratio)

            return {
                "q_number": q_number,
                "pattern": "paper_dimensions",
                "narrative": "find_ratio",
                "question_text": text,
                "input_data": {"format": fmt},
                "solution_data": {
                    "format": fmt,
                    "rounded_ratio": rounded_ratio,
                },
                "answer": rounded_ratio,
            }

        # ------------------------------------------------------------
        # find_diagonal_ratio — без изменений (источник истины: formats_data)
        # ------------------------------------------------------------
        if narrative == "find_diagonal_ratio":
            length_mm = formats_data[fmt]["length_mm"]
            width_mm = formats_data[fmt]["width_mm"]

            diagonal = math.sqrt(length_mm ** 2 + width_mm ** 2)

            ratio = diagonal / max(length_mm, width_mm) if ("больш" in text.lower()) else diagonal / min(length_mm, width_mm)
            rounded_ratio = self._round_to_1(ratio)

            return {
                "q_number": q_number,
                "pattern": "paper_dimensions",
                "narrative": "find_diagonal_ratio",
                "question_text": text,
                "input_data": {"format": fmt},
                "solution_data": {
                    "format": fmt,
                    "rounded_ratio": rounded_ratio,
                },
                "answer": rounded_ratio,
            }

        # ------------------------------------------------------------
        # find_length / find_width — новая логика (двусторонний reference)
        # ------------------------------------------------------------
        if narrative in ("find_length", "find_width"):
            target_length = formats_data[fmt]["length_mm"]
            target_width = formats_data[fmt]["width_mm"]

            target_index = int(fmt[1:])  # A0 -> 0, A7 -> 7

            reference_format: Optional[str] = None
            strategy = "primary"

            # ---------- выбор reference_format ----------
            target_index = int(fmt[1:])
            reference_format = None
            strategy = "primary"

            if narrative == "find_width":
                # PRIMARY: ищем соседний вверх (ref_index == target_index - 1)
                candidates = [
                    f for f in table_order
                    if int(f[1:]) == target_index - 1
                ]
                if candidates:
                    reference_format = candidates[0]
                else:
                    # FALLBACK: ищем соседний вниз (ref_index == target_index + 1)
                    strategy = "fallback"
                    candidates = [
                        f for f in table_order
                        if int(f[1:]) == target_index + 1
                    ]
                    if not candidates:
                        raise ValueError(
                            f"Q3: для {fmt} нет соседнего формата (разница должна быть 1)"
                        )
                    reference_format = candidates[0]

            elif narrative == "find_length":
                # PRIMARY: ищем соседний вниз (ref_index == target_index + 1)
                candidates = [
                    f for f in table_order
                    if int(f[1:]) == target_index + 1
                ]
                if candidates:
                    reference_format = candidates[0]
                else:
                    # FALLBACK: ищем соседний вверх (ref_index == target_index - 1)
                    strategy = "fallback"
                    candidates = [
                        f for f in table_order
                        if int(f[1:]) == target_index - 1
                    ]
                    if not candidates:
                        raise ValueError(
                            f"Q3: для {fmt} нет соседнего формата (разница должна быть 1)"
                        )
                    reference_format = candidates[0]

            if reference_format is None:
                raise ValueError(f"Q3: reference_format не определён для {fmt}")

            ref_length = formats_data[reference_format]["length_mm"]
            ref_width = formats_data[reference_format]["width_mm"]

            # ---------- операция + raw_result (для объяснения) ----------

            format_order = ["A0","A1","A2","A3","A4","A5","A6","A7"]

            target_idx = format_order.index(fmt)
            ref_idx = format_order.index(reference_format)

            moving_to_smaller = target_idx > ref_idx
            moving_to_larger = target_idx < ref_idx


            if narrative == "find_width":
                target_value = target_width

                if moving_to_smaller:
                    # width_new = length_old / 2
                    raw_result = ref_length / 2
                    operation = "divide_by_2"
                    value_used = "length"
                else:
                    # width_new = length_old
                    raw_result = ref_length
                    operation = "take_ref_length"
                    value_used = "length"

            else:  # find_length
                target_value = target_length

                if moving_to_larger:
                    # length_new = width_old * 2
                    raw_result = ref_width * 2
                    operation = "multiply_by_2"
                    value_used = "width"
                else:
                    # length_new = width_old
                    raw_result = ref_width
                    operation = "take_ref_width"
                    value_used = "width"

            # ---------- округление (округляем стандартное target_value) ----------
            rounding_to = self._extract_rounding_to(text)

            if rounding_to is not None:
                answer = int(self._round_to_multiple(target_value, rounding_to))
                rounding_block = {"mode": "nearest", "multiple_of": int(rounding_to)}
            else:
                answer = int(target_value)
                rounding_block = None

            return {
                "q_number": q_number,
                "pattern": "paper_dimensions",
                "narrative": narrative,
                "question_text": text,
                "input_data": {"format": fmt},
                "solution_data": {
                    "target_format": fmt,
                    "reference_format": reference_format,
                    "reference_length_mm": int(ref_length),
                    "reference_width_mm": int(ref_width),
                    "target_length_mm": int(target_length),
                    "target_width_mm": int(target_width),
                    "operation": operation,
                    "value_used": value_used,
                    "raw_result": float(raw_result),
                    "rounding": rounding_block,
                    "answer": int(answer),
                },
                "answer": int(answer),
            }

        raise ValueError("Неизвестный нарратив Q3")

    # ================================================================
    # Q4 — paper_area (find_area)
    # ================================================================

    def _build_q4(self, q_number: int, narrative: str, text: str) -> Dict[str, Any]:

        if narrative != "find_area":
            raise ValueError("Q4 поддерживает только narrative = find_area")

        fmt = self._extract_format(text, err_prefix="Q4")
        target_index = int(fmt[1:])

        # ------------------------------------------------------------
        # 1. Идеальная модель (через A0)
        # ------------------------------------------------------------

        area_start = 10000  # A0 = 10 000 см²
        index_difference = target_index  # A0 → A_k = k переходов

        area_raw = area_start / (2 ** index_difference)

        # список промежуточных делений
        division_steps = []
        current = area_start
        for _ in range(index_difference):
            current = current / 2
            division_steps.append(round(current, 5))

        # ------------------------------------------------------------
        # 2. ISO-проверка (через реальные размеры)
        # ------------------------------------------------------------

        length_mm, width_mm = self.PAPER_SIZES[fmt]

        length_cm = length_mm / 10.0
        width_cm = width_mm / 10.0
        area_iso_raw = round(length_cm * width_cm, 5)

        # ------------------------------------------------------------
        # 3. Проверяем, требуется ли округление
        # ------------------------------------------------------------

        rounding_required = "кратного" in text

        rounding_data = None
        final_answer = None
        acceptable_answers = None

        if rounding_required:

            if "кратного 10" in text:
                multiple = 10
            elif "кратного 5" in text:
                multiple = 5
            else:
                raise ValueError("Q4: не удалось определить кратность округления")

            rounded_area = int(self._round_to_multiple(area_raw, multiple))

            lower_bound = (int(area_raw) // multiple) * multiple
            upper_bound = lower_bound + multiple

            rounding_data = {
                "required": True,
                "multiple_of": multiple,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "rounded_area": rounded_area
            }

            final_answer = rounded_area

        else:
            # ------------------------------------------------------------
            # без округления — допустимы оба способа
            # ------------------------------------------------------------

            rounding_data = {
                "required": False
            }

            area_raw_norm = round(area_raw, 5)
            area_iso_norm = round(area_iso_raw, 5)

            # если совпали — не дублируем
            if abs(area_raw_norm - area_iso_norm) < 1e-6:
                acceptable_answers = [area_raw_norm]
            else:
                acceptable_answers = [area_raw_norm, area_iso_norm]

            final_answer = area_raw_norm

        # ------------------------------------------------------------
        # 4. Возвращаем JSON
        # ------------------------------------------------------------

        return {
            "q_number": q_number,
            "pattern": "paper_area",
            "narrative": "find_area",
            "question_text": text,
            "input_data": {
                "format": fmt
            },
            "solution_data": {
                "target_format": fmt,
                "index_difference": index_difference,
                "area_start": area_start,
                "division_steps": division_steps,
                "area_raw": round(area_raw, 5),
                "iso_check": {
                    "length_mm": length_mm,
                    "width_mm": width_mm,
                    "length_cm": length_cm,
                    "width_cm": width_cm,
                    "area_iso_raw": area_iso_raw
                },
                "rounding": rounding_data,
                "acceptable_answers": acceptable_answers if not rounding_required else None,
            },
            "answer": final_answer
        }

    # ================================================================
    # Q5 — paper_pack_weight / paper_font_scaling
    # ================================================================

    def _build_q5(self, q_number: int, pattern: str, narrative: str, text: str) -> Dict[str, Any]:
        if pattern == "paper_pack_weight":
            # Пример: "В пачке 400 листов бумаги формата A3... масса 1 м² = 125 грамм..."
            fmt = self._extract_format(text, err_prefix="Q5 pack_weight")
            sheet_count = self._extract_int(r"(\d+)\s*лист", text, "Q5 pack_weight: не найдено количество листов")
            density = self._extract_int(r"(\d+)\s*г", text, "Q5 pack_weight: не найдена плотность (г/м²)")

            idx = int(fmt[1:])  # A0=0, A3=3...
            # Сколько листов данного формата в 1 м² (то есть в A0): 2^idx
            sheet_area_factor = 2 ** idx  # например A5: 2^5=32
            weight_one_sheet = density / sheet_area_factor
            total_weight = weight_one_sheet * sheet_count

            # по эталону: ответ в граммах, обычно целое (в твоих вариантах так)
            total_weight_int = int(round(total_weight))

            return {
                "q_number": q_number,
                "pattern": "paper_pack_weight",
                "narrative": "pack_weight",
                "question_text": text,
                "input_data": {
                    "format": fmt,
                    "sheet_count": sheet_count,
                    "density_g_per_m2": density,
                },
                "solution_data": {
                    "index_difference": idx,  # A? относительно A0
                    "sheet_area_factor": sheet_area_factor,
                    "weight_one_sheet": self._pretty_float(weight_one_sheet, 3),
                    "total_weight": total_weight_int,
                },
                "answer": total_weight_int,
            }

        if pattern == "paper_font_scaling":
            # Пример: "... 30 пунктов на A1 -> разместить на A3 ... округли ..."
            formats = re.findall(r"\b(A[0-7])\b", text)
            if len(formats) < 2:
                raise ValueError("Q5 font_scaling: не удалось извлечь from/to форматы")

            fmt_from, fmt_to = formats[0], formats[1]

            original_font = self._extract_int(
                r"(\d+)\s*пункт",
                text,
                "Q5 font_scaling: не найден размер шрифта (пунктов)"
            )

            idx_from = int(fmt_from[1:])
            idx_to = int(fmt_to[1:])

            # Количество шагов между форматами
            step_count = abs(idx_to - idx_from)

            # Если лист становится меньше → уменьшаем шрифт
            # Если лист становится больше → увеличиваем шрифт
            if idx_to > idx_from:
                scale = (math.sqrt(2) ** (-step_count))
            else:
                scale = (math.sqrt(2) ** step_count)

            scaled_font = original_font * scale
            rounded_font = int(round(scaled_font))

            return {
                "q_number": q_number,
                "pattern": "paper_font_scaling",
                "narrative": "font_scaling",
                "question_text": text,
                "input_data": {
                    "from_format": fmt_from,
                    "to_format": fmt_to,
                    "original_font": original_font,
                },
                "solution_data": {
                    "step_count": step_count,
                    "rounded_font": rounded_font,
                },
                "answer": rounded_font,
            }

        raise ValueError("Неизвестный pattern в Q5")

    # ================================================================
    # HELPERS
    # ================================================================

    def _build_formats_data(self) -> Dict[str, Dict[str, int]]:
        return {
            k: {"length_mm": v[0], "width_mm": v[1]}
            for k, v in self.PAPER_SIZES.items()
        }

    def _extract_format(self, text: str, err_prefix: str) -> str:
        m = re.search(r"\b(A[0-7])\b", text)
        if not m:
            raise ValueError(f"{err_prefix}: формат не найден")
        fmt = m.group(1)
        if fmt not in self.PAPER_SIZES:
            raise ValueError(f"{err_prefix}: неизвестный формат {fmt}")
        return fmt

    def _extract_rounding_to(self, text: str) -> Optional[int]:
        low = text.lower()
        if "кратного 10" in low or "кратного десяти" in low:
            return 10
        if "кратного 5" in low or "кратного пяти" in low:
            return 5
        if "до ближайшего числа" in text.lower() or "до ближайшего целого" in text.lower():
            return 1
        # fallback: если просто встречается "10" или "5" — но это риск.
        # Оставим только явные формулировки.
        return None

    def _extract_int(self, pattern: str, text: str, err: str) -> int:
        m = re.search(pattern, text, flags=re.IGNORECASE)
        if not m:
            raise ValueError(err)
        return int(m.group(1))

    def _round_to_multiple(self, value: float, multiple: int) -> int:
        """
        Школьное округление до ближайшего кратного multiple.
        0.5 всегда округляется вверх.
        """
        return int((value + multiple / 2) // multiple * multiple)

    def _round_to_1(self, value: float) -> float:
        return float(f"{value:.1f}")

    def _pretty_float(self, value: float, digits: int) -> float:
        # убираем хвосты двоичной арифметики
        return float(f"{value:.{digits}f}")

    # ================================================================
    # PARSER
    # ================================================================

    def _parse_monolith(self, text: str) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        lines = text.replace("\xa0", " ").split("\n")

        current_q: Optional[str] = None

        for raw_line in lines:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("VARIANT_CODE:"):
                data["VARIANT_CODE"] = line.split(":", 1)[1].strip()
                continue

            if line.startswith("IMAGE:"):
                data["IMAGE"] = line.split(":", 1)[1].strip()
                continue

            if line.startswith("TABLE_ORDER:"):
                raw = line.split(":", 1)[1].strip()
                data["TABLE_ORDER"] = [x.strip() for x in raw.split("|") if x.strip()]
                continue

            # строки вида: Q1.PATTERN: ..., Q3.TEXT:
            m = re.match(r"^(Q\d)\.([A-Z_]+)\s*:\s*(.*)$", line)
            if m:
                q_num, field, val = m.groups()
                if q_num not in data:
                    data[q_num] = {}

                if field == "TEXT":
                    data[q_num]["TEXT"] = (val or "").strip()
                else:
                    data[q_num][field] = (val or "").strip()

                current_q = q_num
                continue

            # продолжение текста (многострочный TEXT)
            if current_q and "TEXT" in data.get(current_q, {}):
                data[current_q]["TEXT"] = (data[current_q]["TEXT"] + " " + line).strip()

        return data
