import re
from typing import Dict, Any, Tuple, List, Optional


class StovesValidator:
    """
    Валидатор non_generators для подтипа "Печи" (задания 1–5).

    Сейчас реализовано:
      - Q1 stove_match_table (match_volume / match_weight / match_cost)
      - Поддержка ROOM-блока (для intro и будущих Q2–Q5)
    """

    # ================================================================
    # PUBLIC
    # ================================================================

    def validate(self, raw_variant: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
        errors: List[str] = []

        text_block = raw_variant.get("question_text", "") or ""
        parsed = self._parse_monolith(text_block)

        variant_id = parsed.get("VARIANT_CODE")
        if not variant_id:
            return False, {}, ["Не найден VARIANT_CODE"]

        # ------------------------------------------------------------
        # ROOM
        # ------------------------------------------------------------

        room_raw = parsed.get("ROOM") or {}
        room_context = None

        if room_raw:
            try:
                room_context = {
                    "length": float(room_raw.get("LENGTH")),
                    "width": float(room_raw.get("WIDTH")),
                    "height": float(room_raw.get("HEIGHT")),
                    "door_width_cm": float(room_raw.get("DOOR_WIDTH")),
                    "door_height_m": float(room_raw.get("DOOR_HEIGHT")),
                    "electric_install_cost": int(room_raw.get("ELECTRIC_INSTALL_COST")),
                }
            except Exception:
                return False, {}, ["Ошибка в ROOM-блоке: некорректные числовые значения"]

        # ------------------------------------------------------------
        # STOVES TABLE
        # ------------------------------------------------------------

        stoves_raw = parsed.get("STOVES") or {}
        if not stoves_raw:
            return False, {}, ["Не найден блок печей STOVE_1..STOVE_3"]

        try:
            stoves = self._build_stoves_table(stoves_raw)
            self._validate_stoves_types(stoves)
        except Exception as e:
            return False, {}, [f"Ошибка в таблице печей: {str(e)}"]

        container: Dict[str, Any] = {
            "id": variant_id,
            "room_context": room_context,
            "table_context": {"stoves": stoves},
            "questions": [],
        }

        # ------------------------------------------------------------
        # Q1
        # ------------------------------------------------------------

        q_data = parsed.get("Q1")
        if not q_data:
            return False, {}, ["Не найден Q1"]

        try:
            question = self._build_q1(q_data=q_data, stoves=stoves)
            container["questions"].append(question)
        except Exception as e:
            errors.append(f"Ошибка в Q1: {str(e)}")

        return len(errors) == 0, container, errors

    # ================================================================
    # Q1
    # ================================================================

    def _build_q1(self, q_data: Dict[str, Any], stoves: List[Dict[str, Any]]) -> Dict[str, Any]:
        pattern = q_data.get("PATTERN")
        narrative = q_data.get("NARRATIVE")
        text = (q_data.get("TEXT") or "").strip()

        if pattern != "stove_match_table":
            raise ValueError(f"Q1: неизвестный pattern: {pattern}")

        if narrative not in ("match_volume", "match_weight", "match_cost"):
            raise ValueError(f"Q1: неизвестный narrative: {narrative}")

        return self._build_match_table(
            q_number=1,
            q_data=q_data,
            narrative=narrative,
            text=text,
            stoves=stoves,
        )

    def _build_match_table(
        self,
        q_number: int,
        q_data: Dict[str, Any],
        narrative: str,
        text: str,
        stoves: List[Dict[str, Any]],
    ) -> Dict[str, Any]:

        raw_cols = q_data.get("COLUMNS", "")
        if not raw_cols:
            raise ValueError("Q1: не найдено поле COLUMNS")

        cols = [x.strip() for x in raw_cols.split("|") if x.strip()]
        if len(cols) != 3:
            raise ValueError("Q1: COLUMNS должен содержать 3 значения")

        try:
            columns = [int(x) for x in cols]
        except Exception:
            raise ValueError("Q1: COLUMNS должен содержать только целые числа")

        stove_no_to_value: Dict[str, int] = {}

        for s in stoves:
            no = str(s["stove_no"])

            if narrative == "match_volume":
                stove_no_to_value[no] = s["volume_max"]
            elif narrative == "match_weight":
                stove_no_to_value[no] = s["mass"]
            else:
                stove_no_to_value[no] = s["cost"]

        values = list(stove_no_to_value.values())
        if len(set(values)) != len(values):
            raise ValueError(f"Q1: неоднозначные значения для {narrative}")

        answer_digits: List[str] = []

        for value in columns:
            found = None
            for no, v in stove_no_to_value.items():
                if v == value:
                    found = no
                    break
            if not found:
                raise ValueError(f"Q1: значение {value} не найдено в таблице")
            answer_digits.append(found)

        answer = "".join(answer_digits)

        column_label_map = {
            "match_volume": "Объём помещения, м³",
            "match_weight": "Масса печи, кг",
            "match_cost": "Цена, руб.",
        }

        return {
            "q_number": q_number,
            "pattern": "stove_match_table",
            "narrative": narrative,
            "question_text": text,
            "input_data": {
                "columns_order": columns,
                "column_label": column_label_map[narrative],
            },
            "solution_data": {
                "stove_no_to_value_mapping": stove_no_to_value,
                "answer_sequence": answer,
            },
            "answer": answer,
            "skill_source_id": "stoves_q1",
        }

    # ================================================================
    # TABLE
    # ================================================================

    def _build_stoves_table(self, stoves_raw: Dict[str, Dict[str, str]]) -> List[Dict[str, Any]]:
        stoves: List[Dict[str, Any]] = []

        for i in range(1, 4):
            key = f"STOVE_{i}"
            block = stoves_raw.get(key)
            if not block:
                raise ValueError(f"Не найден {key}")

            stove_type = (block.get("type") or "").strip().lower()
            volume_range = (block.get("volume") or "").strip()
            mass_raw = (block.get("mass") or "").strip()
            cost_raw = (block.get("cost") or "").strip()

            if stove_type not in ("wood", "electric"):
                raise ValueError(f"{key}: type должен быть wood или electric")

            volume_max = self._parse_volume_max(volume_range)

            try:
                mass = int(mass_raw)
                cost = int(cost_raw)
            except Exception:
                raise ValueError(f"{key}: mass/cost должны быть числами")

            stoves.append({
                "stove_no": i,
                "type": stove_type,
                "volume_range": volume_range,
                "volume_max": volume_max,
                "mass": mass,
                "cost": cost,
            })

        return stoves

    def _validate_stoves_types(self, stoves: List[Dict[str, Any]]) -> None:
        types = [s["type"] for s in stoves]
        if types.count("wood") != 2 or types.count("electric") != 1:
            raise ValueError("Должно быть 2 wood и 1 electric")

    # ================================================================
    # HELPERS
    # ================================================================

    def _parse_volume_max(self, s: str) -> int:
        cleaned = s.replace(" ", "").replace("—", "-").replace("–", "-")
        m = re.match(r"^(\d+)-(\d+)$", cleaned)
        if not m:
            raise ValueError(f"Некорректный диапазон объёма: {s}")
        low = int(m.group(1))
        high = int(m.group(2))
        if low <= 0 or high <= 0 or low >= high:
            raise ValueError(f"Некорректный диапазон объёма: {s}")
        return high

    # ================================================================
    # PARSER
    # ================================================================

    def _parse_monolith(self, text: str) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        lines = text.replace("\xa0", " ").split("\n")

        current_q: Optional[str] = None
        current_stove: Optional[str] = None
        stoves: Dict[str, Dict[str, str]] = {}

        for raw_line in lines:
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            # VARIANT
            if stripped.startswith("VARIANT_CODE:"):
                data["VARIANT_CODE"] = stripped.split(":", 1)[1].strip()
                continue

            # ROOM
            m_room = re.match(r"^ROOM\.([A-Z_]+)\s*:\s*(.*)$", stripped)
            if m_room:
                field, val = m_room.groups()
                if "ROOM" not in data:
                    data["ROOM"] = {}
                data["ROOM"][field] = val.strip()
                continue

            # STOVE BLOCK
            m_stove = re.match(r"^(STOVE_\d+)\s*:\s*$", stripped)
            if m_stove:
                current_stove = m_stove.group(1)
                stoves[current_stove] = {}
                continue

            if current_stove and re.match(r"^[a-zA-Z_]+\s*:\s*.*$", stripped):
                k, v = stripped.split(":", 1)
                stoves[current_stove][k.strip()] = v.strip()
                continue

            # Q BLOCK
            m_q = re.match(r"^(Q\d)\.([A-Z_]+)\s*:\s*(.*)$", stripped)
            if m_q:
                q_num, field, val = m_q.groups()
                if q_num not in data:
                    data[q_num] = {}
                data[q_num][field] = val.strip()
                current_q = q_num
                continue

            if current_q and "TEXT" in data.get(current_q, {}):
                data[current_q]["TEXT"] += " " + stripped

        if stoves:
            data["STOVES"] = stoves

        return data
