# -*- coding: utf-8 -*-
from __future__ import annotations

import re
from typing import Dict, Any, Tuple, List, Optional


class StovesValidator:
    """
    Валидатор non_generators для подтипа "Печи" (задания 1–5).

    Архитектура (канон):
      TXT (монолит) → parse → validate → questions[] (solution_data) → solver (facts-only) → humanizer

    Реализовано:
      ✅ Q1 stove_match_table (match_volume / match_weight / match_cost)
      ✅ Q2 stoves_room_geometry (find_volume / find_base_area / find_lateral_area)
      ✅ Q3 stoves_purchase_cost
            - find_price_difference
            - find_wood_stove_total_cost
            - find_electric_stove_total_cost
            - find_operating_cost_difference
      ✅ Q4 stoves_discounts
            - find_past_price
            - find_discounted_price
            - conditional_discount
            - discount_and_setup
      ✅ Q5 stoves_arc_radius (find_arc_radius)
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
        room_context = self._build_room_context(parsed, errors)
        if errors:
            return False, {}, errors

        # ------------------------------------------------------------
        # STOVES TABLE
        # ------------------------------------------------------------
        stoves = self._build_and_validate_stoves_table(parsed, errors)
        if errors:
            return False, {}, errors

        # ------------------------------------------------------------
        # CONTAINER
        # ------------------------------------------------------------
        container: Dict[str, Any] = {
            "id": variant_id,
            "room_context": room_context,
            "table_context": {"stoves": stoves},
            "questions": [],
        }

        # ------------------------------------------------------------
        # Q1
        # ------------------------------------------------------------
        q1_data = parsed.get("Q1")
        if not q1_data:
            return False, {}, ["Не найден Q1"]

        try:
            q1 = self._build_q1(q_data=q1_data, stoves=stoves)
            self._validate_question_structure(q1)
            container["questions"].append(q1)
        except Exception as e:
            errors.append(f"Ошибка в Q1: {str(e)}")

        # ------------------------------------------------------------
        # Q2
        # ------------------------------------------------------------
        q2_data = parsed.get("Q2")
        if q2_data:
            try:
                q2 = self._build_q2(q_data=q2_data, room=room_context)
                self._validate_question_structure(q2)
                container["questions"].append(q2)
            except Exception as e:
                errors.append(f"Ошибка в Q2: {str(e)}")
        # Если Q2 пока отсутствует в txt — это НЕ ошибка. Будет добавляться постепенно.

        # ------------------------------------------------------------
        # Q3
        # ------------------------------------------------------------
        q3_data = parsed.get("Q3")
        if q3_data:
            try:
                q3 = self._build_q3(
                    q_data=q3_data,
                    room=room_context,
                    stoves=stoves
                )
                self._validate_question_structure(q3)
                container["questions"].append(q3)
            except Exception as e:
                errors.append(f"Ошибка в Q3: {str(e)}")

        # ------------------------------------------------------------
        # Q4
        # ------------------------------------------------------------
        q4_data = parsed.get("Q4")
        if q4_data:
            try:
                q4 = self._build_q4(
                    q_data=q4_data,
                    room=room_context,
                    stoves=stoves
                )
                self._validate_question_structure(q4)
                container["questions"].append(q4)
            except Exception as e:
                errors.append(f"Ошибка в Q4: {str(e)}")

        # ------------------------------------------------------------
        # Q5
        # ------------------------------------------------------------
        q5_data = parsed.get("Q5")
        if q5_data:
            try:
                q5 = self._build_q5(q_data=q5_data)
                self._validate_question_structure(q5)
                container["questions"].append(q5)
            except Exception as e:
                errors.append(f"Ошибка в Q5: {str(e)}")

        return len(errors) == 0, container, errors

    # ================================================================
    # ROOM
    # ================================================================

    def _build_room_context(self, parsed: Dict[str, Any], errors: List[str]) -> Dict[str, Any]:
        room_raw = parsed.get("ROOM") or {}
        if not room_raw:
            errors.append("Не найден ROOM-блок")
            return {}

        try:
            return {
                "length": float(room_raw.get("LENGTH")),
                "width": float(room_raw.get("WIDTH")),
                "height": float(room_raw.get("HEIGHT")),
                "door_width_cm": float(room_raw.get("DOOR_WIDTH")),
                "door_height_m": float(room_raw.get("DOOR_HEIGHT")),
                "electric_install_cost": int(room_raw.get("ELECTRIC_INSTALL_COST")),
            }
        except Exception:
            errors.append("Ошибка в ROOM-блоке: некорректные числовые значения")
            return {}

    # ================================================================
    # TABLE
    # ================================================================

    def _build_and_validate_stoves_table(self, parsed: Dict[str, Any], errors: List[str]) -> List[Dict[str, Any]]:
        stoves_raw = parsed.get("STOVES") or {}
        if not stoves_raw:
            errors.append("Не найден блок печей STOVE_1..STOVE_3")
            return []

        try:
            stoves = self._build_stoves_table(stoves_raw)
            self._validate_stoves_types(stoves)
            return stoves
        except Exception as e:
            errors.append(f"Ошибка в таблице печей: {str(e)}")
            return []

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
                "volume_max": volume_max,  # float (поддержка 15,5)
                "mass": mass,              # int
                "cost": cost,              # int
            })

        return stoves

    def _validate_stoves_types(self, stoves: List[Dict[str, Any]]) -> None:
        types = [s["type"] for s in stoves]
        if types.count("wood") != 2 or types.count("electric") != 1:
            raise ValueError("Должно быть 2 wood и 1 electric")

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

        # В ОГЭ в объёмах встречаются десятичные (15,5) — поэтому для Q1 читаем числа как float
        try:
            columns = [float(x.replace(",", ".")) for x in cols]
        except Exception:
            raise ValueError("Q1: COLUMNS должен содержать числовые значения")

        stove_no_to_value: Dict[str, Any] = {}

        for s in stoves:
            no = str(s["stove_no"])

            if narrative == "match_volume":
                stove_no_to_value[no] = s["volume_max"]  # float
            elif narrative == "match_weight":
                stove_no_to_value[no] = s["mass"]        # int
            else:
                stove_no_to_value[no] = s["cost"]        # int

        values = list(stove_no_to_value.values())
        if len(set(values)) != len(values):
            raise ValueError(f"Q1: неоднозначные значения для {narrative}")

        answer_digits: List[str] = []

        for value in columns:
            found = None
            for no, v in stove_no_to_value.items():
                if abs(float(v) - float(value)) < 1e-6:
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
    # Q2
    # ================================================================

    def _build_q2(self, q_data: Dict[str, Any], room: Dict[str, Any]) -> Dict[str, Any]:
        pattern = q_data.get("PATTERN")
        narrative = q_data.get("NARRATIVE")
        text = (q_data.get("TEXT") or "").strip()

        if pattern != "stoves_room_geometry":
            raise ValueError(f"Q2: неизвестный pattern: {pattern}")

        length = room["length"]
        width = room["width"]
        height = room["height"]

        # 1) find_volume
        if narrative == "find_volume":
            volume = float(f"{length * width * height:.10g}")
            return {
                "q_number": 2,
                "pattern": pattern,
                "narrative": narrative,
                "question_text": text,
                "input_data": {"length": length, "width": width, "height": height},
                "solution_data": {
                    "formula": "V = a · b · h",
                    "calculation": f"{length} · {width} · {height}",
                    "volume": volume,
                },
                "answer": str(volume),
                "help_image_file": "help_stoves_room_geometry.png",
                "skill_source_id": "stoves_q2",
            }

        # 2) find_base_area (пол или потолок — логика одна)
        if narrative == "find_base_area":
            area = self._clean_float(length * width)
            return {
                "q_number": 2,
                "pattern": pattern,
                "narrative": narrative,
                "question_text": text,
                "input_data": {"length": length, "width": width},
                "solution_data": {
                    "formula": "S = a · b",
                    "calculation": f"{length} · {width}",
                    "area": area,
                },
                "answer": str(area),
                "help_image_file": "help_stoves_room_geometry.png",
                "skill_source_id": "stoves_q2",
            }

        # 3) find_lateral_area (площадь стен без двери)
        if narrative == "find_lateral_area":

            door_width_cm = room["door_width_cm"]
            door_height_m = room["door_height_m"]

            door_width_m = self._clean_float(door_width_cm / 100)

            sum_length_width = self._clean_float(length + width)
            perimeter = self._clean_float(2 * sum_length_width)

            walls_area = self._clean_float(perimeter * height)
            door_area = self._clean_float(door_width_m * door_height_m)

            result_area = self._clean_float(walls_area - door_area)

            return {
                "q_number": 2,
                "pattern": pattern,
                "narrative": narrative,
                "question_text": text,
                "input_data": {
                    "length": length,
                    "width": width,
                    "height": height,
                    "door_width_cm": door_width_cm,
                    "door_height_m": door_height_m,
                },
                "solution_data": {
                    "formula": "S_стен = P · h − S_двери",

                    "door_width_m": door_width_m,
                    "sum_length_width": sum_length_width,

                    "perimeter": perimeter,
                    "walls_area": walls_area,
                    "door_area": door_area,
                    "result_area": result_area,
                },
                "answer": str(result_area),
                "help_image_file": "help_stoves_room_geometry.png",
                "skill_source_id": "stoves_q2",
            }

        raise ValueError(f"Q2: неизвестный narrative: {narrative}")

    # ================================================================
    # Q3
    # ================================================================
    def _build_q3(
        self,
        q_data: Dict[str, Any],
        room: Dict[str, Any],
        stoves: List[Dict[str, Any]],
    ) -> Dict[str, Any]:

        pattern = q_data.get("PATTERN")
        narrative = q_data.get("NARRATIVE")
        question_text = (q_data.get("TEXT") or "").strip()

        if not pattern:
            raise ValueError("Q3: missing PATTERN")

        if not narrative:
            raise ValueError("Q3: missing NARRATIVE")

        # ---------------------------------------------------------
        # параметры комнаты
        # ---------------------------------------------------------

        length = float(room["length"])
        width = float(room["width"])
        height = float(room["height"])

        room_volume = self._clean_float(length * width * height)

        electric_install_cost = int(room["electric_install_cost"])

        # ---------------------------------------------------------
        # печи
        # ---------------------------------------------------------

        electric = next(s for s in stoves if s["type"] == "electric")
        wood = [s for s in stoves if s["type"] == "wood"]

        suitable_wood_list = [
            s for s in wood
            if room_volume <= s["volume_max"]
        ]

        if not suitable_wood_list:
            raise ValueError("Q3: suitable wood stove not found")

        suitable_wood = min(suitable_wood_list, key=lambda s: s["cost"])

        # ---------------------------------------------------------
        # доставка
        # ---------------------------------------------------------

        delivery_cost = 0

        m = re.search(r"доставк[аи][^\d]*(\d+)", question_text.lower())
        if m:
            delivery_cost = int(m.group(1))

        # ---------------------------------------------------------
        # параметры эксплуатации (если есть)
        # ---------------------------------------------------------

        electric_kwh = None
        electric_price = None
        wood_volume = None
        wood_price = None

        electric_oper = None
        wood_oper = None

        if narrative == "find_operating_cost_difference":

            m1 = re.search(r"(\d+)\s*киловатт", question_text)
            m2 = re.search(r"(\d+(?:\.\d+)?)\s*руб.*1\s*кВт", question_text)
            m3 = re.search(r"(\d+(?:\.\d+)?)\s*куб", question_text)
            m4 = re.search(r"(\d+)\s*руб[^\d]*1\s*куб", question_text.lower())

            if m1:
                electric_kwh = int(m1.group(1))

            if m2:
                electric_price = float(m2.group(1))

            if m3:
                wood_volume = float(m3.group(1))

            if m4:
                wood_price = int(m4.group(1))

        # ---------------------------------------------------------
        # вычисление стоимости покупки
        # ---------------------------------------------------------

        electric_total = electric["cost"] + electric_install_cost + delivery_cost
        wood_total = suitable_wood["cost"] + delivery_cost

        # ---------------------------------------------------------
        # вычисление ответа
        # ---------------------------------------------------------

        if narrative == "find_price_difference":

            result = electric_total - wood_total

        elif narrative == "find_wood_stove_total_cost":

            result = wood_total

        elif narrative == "find_electric_stove_total_cost":

            result = electric_total

        elif narrative == "find_operating_cost_difference":

            electric_oper = electric_kwh * electric_price
            wood_oper = wood_volume * wood_price

            result = self._clean_float(electric_oper - wood_oper)

            if isinstance(result, float) and result.is_integer():
                result = int(result)

        else:
            raise ValueError(f"Unsupported Q3 narrative: {narrative}")

        # ---------------------------------------------------------
        # solution_data
        # ---------------------------------------------------------

        solution_data = {

            "room_volume": room_volume,

            "electric_stove_no": electric["stove_no"],
            "electric_cost": electric["cost"],

            "wood_ok_no": suitable_wood["stove_no"],
            "wood_ok_cost": suitable_wood["cost"],

            "electric_install_cost": electric_install_cost,
            "delivery_cost": delivery_cost,

            "electric_total": electric_total,
            "wood_total": wood_total,

            "electric_kwh": electric_kwh,
            "electric_price_per_kwh": electric_price,
            "wood_volume_m3": wood_volume,
            "wood_price_per_m3": wood_price,

            "electric_oper": electric_oper,
            "wood_oper": wood_oper,

            "result": result,
        }

        # ---------------------------------------------------------
        # return
        # ---------------------------------------------------------

        return {
            "q_number": 3,
            "pattern": pattern,
            "narrative": narrative,
            "question_text": question_text,
            "input_data": {
                "length": length,
                "width": width,
                "height": height,
            },
            "solution_data": solution_data,
            "answer": str(result),
            "skill_source_id": "stoves_q3",
        }

    # ================================================================
    # Q4
    # ================================================================
    def _build_q4(
        self,
        q_data: Dict[str, Any],
        room: Dict[str, Any],
        stoves: List[Dict[str, Any]],
    ) -> Dict[str, Any]:

        pattern = q_data.get("PATTERN")
        narrative = q_data.get("NARRATIVE")
        question_text = (q_data.get("TEXT") or "").strip()

        solution_data: Dict[str, Any] | None = None
        answer: Any | None = None

        if pattern != "stoves_discounts":
            raise ValueError(f"Q4: неизвестный pattern: {pattern}")

        # ---------------------------------------------------------
        # печи
        # ---------------------------------------------------------

        stove_map = {s["stove_no"]: s for s in stoves}

        electric = next((s for s in stoves if s["type"] == "electric"), None)
        if electric is None:
            raise ValueError("Q4: электрическая печь не найдена")

        # ---------------------------------------------------------
        # find_past_price
        # ---------------------------------------------------------

        if narrative == "find_past_price":

            stove_no_raw = q_data.get("STOVE")
            d1_raw = q_data.get("DISCOUNT_STOVE_1")
            d2_raw = q_data.get("DISCOUNT_STOVE_2")
            d3_raw = q_data.get("DISCOUNT_STOVE_3")

            required = {
                "STOVE": stove_no_raw,
                "DISCOUNT_STOVE_1": d1_raw,
                "DISCOUNT_STOVE_2": d2_raw,
                "DISCOUNT_STOVE_3": d3_raw,
            }
            missing = [k for k, v in required.items() if v is None]
            if missing:
                raise ValueError(
                    f"Q4 find_past_price: отсутствуют поля: {', '.join(missing)}"
                )

            stove_no = int(stove_no_raw)
            stove = stove_map.get(stove_no)

            if stove is None:
                raise ValueError(f"Q4: печь №{stove_no} не найдена")

            price_after_discount = stove["cost"]

            d1 = int(d1_raw)
            d2 = int(d2_raw)
            d3 = int(d3_raw)

            discount_map = {
                1: d1,
                2: d2,
                3: d3,
            }

            discount_percent = discount_map[stove_no]
            discount_fraction = discount_percent / 100

            remaining_percent = 100 - discount_percent
            remaining_fraction = remaining_percent / 100

            original_price = self._clean_float(price_after_discount / remaining_fraction)

            if isinstance(original_price, float) and original_price.is_integer():
                original_price = int(original_price)

            solution_data = {
                "stove_no": stove_no,
                "price_after_discount": price_after_discount,

                "discount_stove_1": d1,
                "discount_stove_2": d2,
                "discount_stove_3": d3,

                "discount_percent": discount_percent,
                "discount_fraction": discount_fraction,

                "remaining_percent": remaining_percent,
                "remaining_fraction": remaining_fraction,

                "original_price": original_price,
            }

            answer = original_price

        # ---------------------------------------------------------
        # find_discounted_price
        # ---------------------------------------------------------

        elif narrative == "find_discounted_price":

            stove_no_raw = q_data.get("STOVE")
            discount_percent_raw = q_data.get("DISCOUNT_PERCENT")

            required = {
                "STOVE": stove_no_raw,
                "DISCOUNT_PERCENT": discount_percent_raw,
            }
            missing = [k for k, v in required.items() if v is None]
            if missing:
                raise ValueError(
                    f"Q4 find_discounted_price: отсутствуют поля: {', '.join(missing)}"
                )

            stove_no = int(stove_no_raw)
            stove = stove_map.get(stove_no)

            if stove is None:
                raise ValueError(f"Q4: печь №{stove_no} не найдена")

            original_price = stove["cost"]

            discount_percent = int(discount_percent_raw)
            discount_fraction = discount_percent / 100

            remaining_percent = 100 - discount_percent
            remaining_fraction = remaining_percent / 100

            discount_amount = self._clean_float(original_price * discount_fraction)
            price_after_discount = self._clean_float(original_price * remaining_fraction)

            if isinstance(discount_amount, float) and discount_amount.is_integer():
                discount_amount = int(discount_amount)

            if isinstance(price_after_discount, float) and price_after_discount.is_integer():
                price_after_discount = int(price_after_discount)

            solution_data = {
                "stove_no": stove_no,
                "original_price": original_price,

                "discount_percent": discount_percent,
                "discount_fraction": discount_fraction,

                "remaining_percent": remaining_percent,
                "remaining_fraction": remaining_fraction,

                "discount_amount": discount_amount,
                "price_after_discount": price_after_discount,
            }

            answer = price_after_discount

        # ---------------------------------------------------------
        # conditional_discount
        # ---------------------------------------------------------

        elif narrative == "conditional_discount":

            stove_no_raw = q_data.get("STOVE")
            threshold_raw = q_data.get("THRESHOLD")
            delivery_cost_raw = q_data.get("DELIVERY_COST")
            stove_discount_raw = q_data.get("STOVE_DISCOUNT")
            delivery_discount_raw = q_data.get("DELIVERY_DISCOUNT")

            required = {
                "STOVE": stove_no_raw,
                "THRESHOLD": threshold_raw,
                "DELIVERY_COST": delivery_cost_raw,
                "STOVE_DISCOUNT": stove_discount_raw,
                "DELIVERY_DISCOUNT": delivery_discount_raw,
            }
            missing = [k for k, v in required.items() if v is None]
            if missing:
                raise ValueError(
                    f"Q4 conditional_discount: отсутствуют поля: {', '.join(missing)}"
                )

            stove_no = int(stove_no_raw)
            stove = stove_map.get(stove_no)

            if stove is None:
                raise ValueError(f"Q4: печь №{stove_no} не найдена")

            original_price = stove["cost"]

            threshold = int(threshold_raw)
            delivery_cost = int(delivery_cost_raw)

            stove_discount_percent = int(stove_discount_raw)
            delivery_discount_percent = int(delivery_discount_raw)

            threshold_passed = original_price > threshold

            remaining_percent = 100 - stove_discount_percent
            remaining_fraction = remaining_percent / 100

            delivery_remaining_percent = 100 - delivery_discount_percent
            delivery_remaining_fraction = delivery_remaining_percent / 100

            if threshold_passed:
                stove_price_after_discount = self._clean_float(
                    original_price * remaining_fraction
                )
                delivery_price_after_discount = self._clean_float(
                    delivery_cost * delivery_remaining_fraction
                )
            else:
                stove_price_after_discount = original_price
                delivery_price_after_discount = delivery_cost

            if isinstance(stove_price_after_discount, float) and stove_price_after_discount.is_integer():
                stove_price_after_discount = int(stove_price_after_discount)

            if isinstance(delivery_price_after_discount, float) and delivery_price_after_discount.is_integer():
                delivery_price_after_discount = int(delivery_price_after_discount)

            total_price = stove_price_after_discount + delivery_price_after_discount

            if isinstance(total_price, float) and total_price.is_integer():
                total_price = int(total_price)

            solution_data = {
                "stove_no": stove_no,
                "original_price": original_price,

                "threshold": threshold,
                "threshold_passed": threshold_passed,

                "stove_discount_percent": stove_discount_percent,
                "remaining_percent": remaining_percent,
                "remaining_fraction": remaining_fraction,
                "stove_price_after_discount": stove_price_after_discount,

                "delivery_cost": delivery_cost,
                "delivery_discount_percent": delivery_discount_percent,
                "delivery_remaining_percent": delivery_remaining_percent,
                "delivery_remaining_fraction": delivery_remaining_fraction,
                "delivery_price_after_discount": delivery_price_after_discount,

                "total_price": total_price,
            }

            answer = total_price

        # ---------------------------------------------------------
        # discount_and_setup
        # ---------------------------------------------------------

        elif narrative == "discount_and_setup":

            discount_percent_raw = q_data.get("DISCOUNT_PERCENT")
            delivery_cost_raw = q_data.get("DELIVERY_COST")

            required = {
                "DISCOUNT_PERCENT": discount_percent_raw,
                "DELIVERY_COST": delivery_cost_raw,
            }
            missing = [k for k, v in required.items() if v is None]
            if missing:
                raise ValueError(
                    f"Q4 discount_and_setup: отсутствуют поля: {', '.join(missing)}"
                )

            original_price = electric["cost"]
            stove_no = electric["stove_no"]

            discount_percent = int(discount_percent_raw)
            delivery_cost = int(delivery_cost_raw)

            install_cost = int(room["electric_install_cost"])

            discount_fraction = discount_percent / 100

            remaining_percent = 100 - discount_percent
            remaining_fraction = remaining_percent / 100

            price_after_discount = self._clean_float(
                original_price * remaining_fraction
            )

            if isinstance(price_after_discount, float) and price_after_discount.is_integer():
                price_after_discount = int(price_after_discount)

            total_price = price_after_discount + delivery_cost + install_cost

            if isinstance(total_price, float) and total_price.is_integer():
                total_price = int(total_price)

            solution_data = {
                "stove_no": stove_no,
                "original_price": original_price,

                "discount_percent": discount_percent,
                "discount_fraction": discount_fraction,
                "remaining_percent": remaining_percent,
                "remaining_fraction": remaining_fraction,

                "price_after_discount": price_after_discount,

                "delivery_cost": delivery_cost,
                "install_cost": install_cost,

                "total_price": total_price,
            }

            answer = total_price

        else:
            raise ValueError(f"Q4: неизвестный narrative: {narrative}")

        return {
            "q_number": 4,
            "pattern": pattern,
            "narrative": narrative,
            "question_text": question_text,
            "input_data": {},
            "solution_data": solution_data,
            "answer": str(answer),
            "skill_source_id": "stoves_q4",
        }

    # ================================================================
    # Q5
    # ================================================================

    def _build_q5(self, q_data: Dict[str, Any]) -> Dict[str, Any]:

        pattern = q_data.get("PATTERN")
        narrative = q_data.get("NARRATIVE")
        text = (q_data.get("TEXT") or "").strip()

        if pattern != "stoves_arc_radius":
            raise ValueError(f"Q5: неизвестный pattern: {pattern}")

        if narrative != "find_arc_radius":
            raise ValueError(f"Q5: неизвестный narrative: {narrative}")

        try:
            a = float(q_data.get("A"))
            b = float(q_data.get("B"))
        except Exception:
            raise ValueError("Q5: A и B должны быть числами")

        if a <= 0 or b <= 0:
            raise ValueError("Q5: A и B должны быть положительными")

        # ---------------------------------------------------------
        # геометрия
        # ---------------------------------------------------------

        half_width = self._clean_float(b / 2)

        a_squared = self._clean_float(a * a)
        half_width_squared = self._clean_float(half_width * half_width)

        radius_squared = self._clean_float(a_squared + half_width_squared)

        radius = radius_squared ** 0.5

        # радиус должен быть целым
        if abs(radius - round(radius)) > 1e-6:
            raise ValueError(
                f"Q5: радиус получается нецелым (a={a}, b={b})"
            )

        radius = int(round(radius))

        # ---------------------------------------------------------
        # solution_data (истина для solver)
        # ---------------------------------------------------------

        solution_data = {
            "a": a,
            "b": b,
            "half_width": half_width,

            "a_squared": a_squared,
            "half_width_squared": half_width_squared,
            "radius_squared": radius_squared,

            "radius": radius,
        }

        # ---------------------------------------------------------
        # return
        # ---------------------------------------------------------

        return {
            "q_number": 5,
            "pattern": pattern,
            "narrative": narrative,
            "question_text": text,
            "input_data": {
                "a": a,
                "b": b,
            },
            "solution_data": solution_data,
            "answer": str(radius),
            "skill_source_id": "stoves_q5",

            # картинки
            "image_file": "task_stoves_arc_radius.png",
            "help_image_file": "help_stoves_arc_radius.png",
        }

    # ================================================================
    # HELPERS
    # ================================================================

    def _parse_volume_max(self, s: str) -> float:
        """
        Поддержка десятичных дробей в диапазонах объёма (как в ОГЭ):
          10–15,5
          10-15.5
        """
        cleaned = (
            s.replace(" ", "")
             .replace("—", "-")
             .replace("–", "-")
             .replace(",", ".")
        )

        m = re.match(r"^(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)$", cleaned)
        if not m:
            raise ValueError(f"Некорректный диапазон объёма: {s}")

        low = float(m.group(1))
        high = float(m.group(2))

        if low <= 0 or high <= 0 or low >= high:
            raise ValueError(f"Некорректный диапазон объёма: {s}")

        return high

    def _clean_float(self, value: float) -> float:
        """
        Убирает артефакты плавающей точки Python.
        Пример:
            5.670000000000001 → 5.67
        """
        return float(f"{value:.10g}")

    def _validate_question_structure(self, q: Dict[str, Any]) -> None:
        """
        Базовая проверка структуры вопроса перед записью в JSON.
        Ловит типичные ошибки генерации.
        """

        required_fields = [
            "q_number",
            "pattern",
            "narrative",
            "question_text",
            "solution_data",
            "answer",
        ]

        for field in required_fields:
            if field not in q:
                raise ValueError(f"Вопрос {q.get('q_number')}: отсутствует поле {field}")

        if not isinstance(q["solution_data"], dict):
            raise ValueError(f"Вопрос {q['q_number']}: solution_data должен быть dict")

        if not q["solution_data"]:
            raise ValueError(f"Вопрос {q['q_number']}: solution_data пустой")

        if q["answer"] in ("", None):
            raise ValueError(f"Вопрос {q['q_number']}: отсутствует answer")

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

            # --------------------------------------------------------
            # пропускаем пустые строки и комментарии
            # --------------------------------------------------------
            if not stripped or stripped.startswith("#"):
                continue

            # --------------------------------------------------------
            # пропускаем служебные разделители
            # --------------------------------------------------------
            if set(stripped) == {"-"}:
                continue

            # --------------------------------------------------------
            # IMAGE (если есть в txt — просто сохраняем, не мешаем парсеру)
            # --------------------------------------------------------
            if stripped.startswith("IMAGE:"):
                data["IMAGE"] = stripped.split(":", 1)[1].strip()
                continue

            # --------------------------------------------------------
            # VARIANT
            # --------------------------------------------------------
            if stripped.startswith("VARIANT_CODE:"):
                data["VARIANT_CODE"] = stripped.split(":", 1)[1].strip()
                continue

            # --------------------------------------------------------
            # ROOM
            # --------------------------------------------------------
            m_room = re.match(r"^ROOM\.([A-Z_]+)\s*:\s*(.*)$", stripped)
            if m_room:
                field, val = m_room.groups()

                if "ROOM" not in data:
                    data["ROOM"] = {}

                data["ROOM"][field] = val.strip()
                continue

            # --------------------------------------------------------
            # STOVE BLOCK START
            # --------------------------------------------------------
            m_stove = re.match(r"^(STOVE_\d+)\s*:\s*$", stripped)
            if m_stove:
                current_stove = m_stove.group(1)
                stoves[current_stove] = {}
                continue

            # --------------------------------------------------------
            # STOVE BLOCK FIELDS
            # --------------------------------------------------------
            if current_stove and re.match(r"^[a-zA-Z_]+\s*:\s*.*$", stripped):
                k, v = stripped.split(":", 1)
                stoves[current_stove][k.strip()] = v.strip()
                continue

            # --------------------------------------------------------
            # Q BLOCK
            # --------------------------------------------------------
            m_q = re.match(r"^(Q\d)\.([A-Z0-9_]+)\s*:\s*(.*)$", stripped)
            if m_q:
                current_stove = None  # выходим из блока печей
                q_num, field, val = m_q.groups()

                if q_num not in data:
                    data[q_num] = {}

                data[q_num][field] = val.strip()
                current_q = q_num
                continue

            # --------------------------------------------------------
            # методические заголовки "ВОПРОС 3 ..."
            # --------------------------------------------------------
            if stripped.upper().startswith("ВОПРОС"):
                current_stove = None
                continue

            # --------------------------------------------------------
            # продолжение текста вопроса
            # --------------------------------------------------------
            if current_q and "TEXT" in data.get(current_q, {}):
                data[current_q]["TEXT"] += " " + stripped
                continue

        # ------------------------------------------------------------
        # сохраняем таблицу печей после завершения цикла
        # ------------------------------------------------------------
        if stoves:
            data["STOVES"] = stoves

        return data
