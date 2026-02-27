# matunya_bot_final/help_core/solvers/task_1_5/paper_solver.py

from __future__ import annotations

import math
from pathlib import Path

from typing import Any, Dict

from matunya_bot_final.utils.display import (
    to_superscript,
    format_number,
    format_power,
)

def solve_paper(task_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Facts-builder solver для блока 1–5 (Paper).

    Принцип:
    - НИЧЕГО не "решаем" как математику с нуля
    - Только достраиваем variables так, чтобы humanizer мог
      подставить все плейсхолдеры STEP_TEMPLATES без KeyError.

    Важно:
    - Q1 и Q2 не трогаем по смыслу, только аккуратно достраиваем поля.
    """

    task: Dict[str, Any] = task_context["task"]
    variant: Dict[str, Any] = task_context["variant"]

    question_id = task["q_number"]
    pattern = task["pattern"]
    narrative = task["narrative"]

    base_variables: Dict[str, Any] = (task.get("solution_data") or {}).copy()
    variables: Dict[str, Any] = base_variables.copy()

    # -----------------------------------------------------
    # Общие утилиты для "число прописью"
    # -----------------------------------------------------

    NUM_WORDS = {
        0: "ноль",
        1: "один",
        2: "два",
        3: "три",
        4: "четыре",
        5: "пять",
        6: "шесть",
        7: "семь",
        8: "восемь",
        9: "девять",
        10: "десять",
    }

    def _index_word(n: int) -> str:
        return NUM_WORDS.get(n, str(n))

    # =========================================================
    # 🔵 Q1 — paper_format_match / match_formats_to_rows
    # =========================================================
    if narrative == "match_formats_to_rows":
        table_context = variant["table_context"]
        formats_data = table_context["formats_data"]

        mapping: Dict[str, str] = base_variables["row_to_format_mapping"]  # "1"->"A0" и т.д.

        rows_data = []
        for row_str, fmt in mapping.items():
            row_num = int(row_str)
            length = int(formats_data[fmt]["length_mm"])
            rows_data.append((row_num, fmt, length))

        # сортируем по длине убыванию (самый большой лист сверху)
        rows_data.sort(key=lambda x: x[2], reverse=True)

        # Под STEP_MATCH_COMPARE: row_1..row_4, len_1..len_4, format_1..format_4
        for i, (row_num, fmt, length) in enumerate(rows_data, start=1):
            variables[f"row_{i}"] = row_num
            variables[f"format_{i}"] = fmt
            variables[f"len_{i}"] = length

        # Под STEP_MATCH_SEQUENCE: requested_order (строкой)
        requested_order = task["input_data"]["columns_order"]
        variables["requested_order"] = ", ".join(requested_order)

        # Дополнительно (полезно для следующих вопросов): формат -> номер строки
        # Это НЕ ломает humanizer, но помогает Q3/Q4/Q5 в дальнейшем
        variables["format_to_row_mapping"] = {fmt: int(row) for row, fmt in mapping.items()}

    # =========================================================
    # 🔵 Q2 — paper_split / count_subformats
    # =========================================================
    elif narrative == "count_subformats":
        from_format = task["input_data"]["from_format"]
        to_format = task["input_data"]["to_format"]

        from_index = int(from_format[1:])
        to_index = int(to_format[1:])

        index_difference = int(base_variables["index_difference"])
        variables["index_word"] = _index_word(index_difference)

        # цепочка переходов: A1 → A2 → A3 → A4
        transition_chain = " → ".join(f"A{i}" for i in range(from_index, to_index + 1))

        # цепочка удвоений: 1 → 2 → 4 → 8
        doubling = []
        value = 1
        for _ in range(index_difference + 1):
            doubling.append(str(value))
            value *= 2
        doubling_chain = " → ".join(doubling)

        variables.update(
            {
                "from_format": from_format,
                "to_format": to_format,
                "from_index": from_index,
                "to_index": to_index,
                "transition_chain": transition_chain,
                "doubling_chain": doubling_chain,
                "sup_power": to_superscript(index_difference),
                "power_value": int(base_variables.get("power_value", 2 ** index_difference)),
            }
        )

    # =========================================================
    # 🔵 ДОСТРОЙКА FACTS ДЛЯ Q3 (paper_dimensions)
    # =========================================================

    if pattern == "paper_dimensions":

        fmt = task["input_data"]["format"]
        solution_data = task["solution_data"]

        table_context = variant["table_context"]
        formats_data = table_context["formats_data"]

        length_mm = formats_data[fmt]["length_mm"]
        width_mm = formats_data[fmt]["width_mm"]

        greater = max(length_mm, width_mm)
        smaller = min(length_mm, width_mm)

        # -------------------------------------------------
        # 1️⃣ find_length
        # -------------------------------------------------
        if narrative == "find_length":

            rounding = solution_data.get("rounding")

            raw_result = float(solution_data["raw_result"])
            operation = solution_data.get("operation")

            reference_format = solution_data["reference_format"]
            ref_width = int(solution_data["reference_width_mm"])
            ref_length = int(solution_data["reference_length_mm"])

            # определяем направление перехода по индексам форматов
            format_order = ["A0","A1","A2","A3","A4","A5","A6","A7"]
            target_idx = format_order.index(fmt)
            ref_idx = format_order.index(reference_format)

            moving_to_larger = target_idx < ref_idx

            # текст формулы / вычисления — ТОЛЬКО по operation
            if operation == "multiply_by_2":
                direction_word = "бо́льший"
                rule_word = "удвоения соответствующей стороны"
                formula_line = f"Длина {fmt} = 2 · Ширина {reference_format}"
                calc_line = f"Длина {fmt} = 2 · {ref_width} = {raw_result}"
            elif operation == "take_ref_width":
                direction_word = "бо́льший" if moving_to_larger else "меньший"
                rule_word = "соответствия сторон"
                formula_line = f"Длина {fmt} = Ширина {reference_format}"
                calc_line = f"Длина {fmt} = {ref_width}"
            else:
                # safety: чтобы не падало, даже если операция неожиданная
                direction_word = ""
                rule_word = ""
                formula_line = ""
                calc_line = ""

            # округление (границы нужны только если rounding есть)
            lower_bound = None
            upper_bound = None
            multiple_of = None

            if rounding:
                multiple_of = int(rounding["multiple_of"])
                lower_bound = int((raw_result // multiple_of) * multiple_of)
                upper_bound = int(lower_bound + multiple_of)

            variables.update({
                "target_format": solution_data["target_format"],
                "reference_format": reference_format,
                "reference_width_mm": ref_width,
                "reference_length_mm": ref_length,

                "operation": operation,
                "direction_word": direction_word,
                "rule_word": rule_word,
                "formula_line": formula_line,
                "calc_line": calc_line,

                "raw_result": raw_result,
                "rounding": rounding,
                "multiple_of": multiple_of,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "answer": int(solution_data["answer"]),
            })

        # -------------------------------------------------
        # 2️⃣ find_width
        # -------------------------------------------------
        if narrative == "find_width":

            rounding = solution_data.get("rounding")

            raw_result = float(solution_data["raw_result"])
            operation = solution_data.get("operation")

            reference_format = solution_data["reference_format"]
            ref_length = int(solution_data["reference_length_mm"])
            ref_width = int(solution_data["reference_width_mm"])

            # определяем направление перехода по индексам форматов
            format_order = ["A0","A1","A2","A3","A4","A5","A6","A7"]
            target_idx = format_order.index(fmt)
            ref_idx = format_order.index(reference_format)

            moving_to_larger = target_idx < ref_idx

            # текст формулы / вычисления — ТОЛЬКО по operation
            if operation == "divide_by_2":
                direction_word = "меньший" if not moving_to_larger else "бо́льший"
                rule_word = "разрезания"
                formula_line = f"Ширина {fmt} = Длина {reference_format} : 2"
                calc_line = f"Ширина {fmt} = {ref_length} : 2 = {raw_result}"
            elif operation == "take_ref_length":
                direction_word = "бо́льший" if moving_to_larger else "меньший"
                rule_word = "соответствия сторон"
                formula_line = f"Ширина {fmt} = Длина {reference_format}"
                calc_line = f"Ширина {fmt} = {ref_length}"
            else:
                direction_word = ""
                rule_word = ""
                formula_line = ""
                calc_line = ""

            # округление (границы нужны только если rounding есть)
            lower_bound = None
            upper_bound = None
            multiple_of = None

            if rounding:
                multiple_of = int(rounding["multiple_of"])
                lower_bound = int((raw_result // multiple_of) * multiple_of)
                upper_bound = int(lower_bound + multiple_of)

            variables.update({
                "target_format": solution_data["target_format"],
                "reference_format": reference_format,
                "reference_length_mm": ref_length,
                "reference_width_mm": ref_width,

                "operation": operation,
                "direction_word": direction_word,
                "rule_word": rule_word,
                "formula_line": formula_line,
                "calc_line": calc_line,

                "raw_result": raw_result,
                "rounding": rounding,
                "multiple_of": multiple_of,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "answer": int(solution_data["answer"]),
            })

        # ---------------------------
        # 3️⃣ find_ratio (НЕ ТРОГАЕМ)
        # ---------------------------
        if narrative == "find_ratio":

            rounded_ratio = solution_data["rounded_ratio"]

            division_order = "делим бо́льшую сторону на ме́ньшую"
            division_expression = f"{greater} ÷ {smaller}"
            raw_ratio = round(greater / smaller, 2)

            variables.update({
                "division_order": division_order,
                "division_expression": division_expression,
                "raw_ratio": raw_ratio,
                "rounded_ratio": rounded_ratio,
            })

        # ---------------------------
        # 4️⃣ find_diagonal_ratio (НЕ ТРОГАЕМ)
        # ---------------------------
        if narrative == "find_diagonal_ratio":

            text = (task.get("original_text") or task.get("question_text") or "").lower()
            side_type = "большей" if "больш" in text else "меньшей"

            ratio = solution_data["rounded_ratio"]

            variables.update({
                "side_type": side_type,
                "ratio_value": ratio,
            })

    # =========================================================
    # 🔵 ДОСТРОЙКА FACTS ДЛЯ Q4 (paper_area → find_area)
    # =========================================================

    if pattern == "paper_area":

        if narrative != "find_area":
            raise ValueError("Q4 поддерживает только narrative = find_area")

        fmt = task["input_data"]["format"]

        # размеры из контекста варианта (fallback)
        formats_data = variant["table_context"]["formats_data"]
        length_mm_fallback = formats_data[fmt]["length_mm"]
        width_mm_fallback = formats_data[fmt]["width_mm"]
        length_cm_fallback = round(length_mm_fallback / 10, 1)
        width_cm_fallback = round(width_mm_fallback / 10, 1)

        # -----------------------------------------------------
        # Базовые поля из валидатора (solution_data)
        # -----------------------------------------------------

        target_format = base_variables.get("target_format") or fmt
        index_difference = int(base_variables["index_difference"])

        # -----------------------------------------------------
        # Склонение "раз"
        # -----------------------------------------------------

        def _decline_raz(n: int) -> str:
            if 11 <= n % 100 <= 14:
                return "раз"
            if n % 10 == 1:
                return "раз"
            if 2 <= n % 10 <= 4:
                return "раза"
            return "раз"

        def _decline_perehod(n: int) -> str:
            if 11 <= n % 100 <= 14:
                return "переходов"
            if n % 10 == 1:
                return "переход"
            if 2 <= n % 10 <= 4:
                return "перехода"
            return "переходов"

        raz_word = _decline_raz(index_difference)
        index_word = _index_word(index_difference)

        area_start = base_variables["area_start"]
        division_steps = base_variables["division_steps"]
        area_raw = base_variables["area_raw"]

        rounding = base_variables["rounding"]
        iso_check = base_variables["iso_check"]

        # -----------------------------------------------------
        # Цепочка форматов A0 → ... → A_k
        # -----------------------------------------------------

        format_chain = " → ".join(f"A{i}" for i in range(index_difference + 1))

        # -----------------------------------------------------
        # Форматирование чисел под эталон
        # 10000 -> "10 000", 312.5 -> "312,5"
        # -----------------------------------------------------

        def _fmt_num(x: float) -> str:
            if x is None:
                return ""

            sign = "-" if x < 0 else ""
            x = abs(x)

            integer_part = int(x)
            decimal_part = x - integer_part

            # форматируем целую часть с пробелами
            integer_str = f"{integer_part:,}".replace(",", " ")

            # если дробной части нет
            if abs(decimal_part) < 1e-9:
                return f"{sign}{integer_str}"

            # получаем дробную часть без лишних нулей
            decimal_str = f"{decimal_part:.10f}".rstrip("0").rstrip(".")[2:]

            return f"{sign}{integer_str},{decimal_str}"

        # -----------------------------------------------------
        # Линии деления (как в эталоне)
        # -----------------------------------------------------

        division_lines: list[str] = []
        current = area_start
        for value in division_steps:
            division_lines.append(f"{_fmt_num(float(current))} : 2 = {_fmt_num(float(value))}")
            current = value

        division_lines_str = "\n".join(division_lines)

        # -----------------------------------------------------
        # ISO поля (берём из iso_check, но страхуемся fallback'ом)
        # -----------------------------------------------------

        iso_length_mm = iso_check.get("length_mm", length_mm_fallback)
        iso_width_mm = iso_check.get("width_mm", width_mm_fallback)
        iso_length_cm = iso_check.get("length_cm", length_cm_fallback)
        iso_width_cm = iso_check.get("width_cm", width_cm_fallback)
        iso_area_raw = iso_check["area_iso_raw"]

        # -----------------------------------------------------
        # Достраиваем variables (и структурные, и плоские)
        # -----------------------------------------------------

        variables.update({
            # required_fields профиля (структурные)
            "target_format": target_format,
            "index_difference": index_difference,
            "area_start": area_start,
            "division_steps": division_steps,
            "area_raw": area_raw,
            "iso_check": iso_check,
            "rounding": rounding,

            # для STEP_TEMPLATES (плоские)
            "format_chain": format_chain,
            "division_lines": division_lines_str,

            "length_mm": iso_length_mm,
            "width_mm": iso_width_mm,
            "length_cm": _fmt_num(float(iso_length_cm)),
            "width_cm": _fmt_num(float(iso_width_cm)),
            "area_iso_raw": _fmt_num(float(iso_area_raw)),
            "raz_word": raz_word,
            "index_word": index_word,
            "perehod_word": _decline_perehod(index_difference),

            "rounding_required": rounding["required"],
            "area_raw_str": _fmt_num(float(area_raw)),  # удобно, если шаблоны хотят строку
        })

        # -----------------------------------------------------
        # Округление / допустимые ответы
        # -----------------------------------------------------

        if rounding["required"]:
            variables.update({
                "multiple_of": rounding["multiple_of"],
                "lower_bound": rounding["lower_bound"],
                "upper_bound": rounding["upper_bound"],
                "rounded_area": rounding["rounded_area"],
            })
        else:
            acceptable = base_variables.get("acceptable_answers")
            if acceptable:
                variables["acceptable_answers"] = acceptable
                variables["acceptable_answers_str"] = ", ".join(_fmt_num(float(x)) for x in acceptable)

    # =========================================================
    # 🔵 Q5 — paper_pack_weight
    # =========================================================

    if pattern == "paper_pack_weight" and narrative == "pack_weight":

        fmt = task["input_data"]["format"]
        density = int(task["input_data"]["density_g_per_m2"])

        idx = int(fmt[1:])  # A0=0, A5=5 и т.д.

        sheet_area_factor = int(base_variables["sheet_area_factor"])
        single_weight = float(base_variables["weight_one_sheet"])
        total_weight = int(base_variables["total_weight"])

        pack_size = int(task["input_data"]["sheet_count"])

        sup_power = to_superscript(idx)

        variables.update({
            "from_format": "A0",
            "to_format": fmt,

            "from_index": 0,
            "to_index": idx,
            "index_difference": idx,
            "index_word": _index_word(idx),

            "sup_power": sup_power,

            "sheet_count": sheet_area_factor,  # 2^idx
            "mass_per_m2": density,
            "single_weight": single_weight,
            "pack_size": pack_size,          # из условия
            "total_weight": total_weight,
        })


    # =========================================================
    # 🔵 Q6 — paper_font_scaling
    # =========================================================

    if pattern == "paper_font_scaling" and narrative == "font_scaling":

        fmt_from = task["input_data"]["from_format"]
        fmt_to = task["input_data"]["to_format"]
        original_font = int(task["input_data"]["original_font"])

        idx_from = int(fmt_from[1:])
        idx_to = int(fmt_to[1:])

        delta = idx_from - idx_to
        step_count = abs(delta)
        sup_step = to_superscript(step_count)

        # ---------------------------------------------
        # Направление
        # ---------------------------------------------
        sheet_became = "больше" if delta > 0 else "меньше"
        font_action = "увеличить" if delta > 0 else "уменьшить"

        # ---------------------------------------------
        # Коэффициент масштаба
        # ---------------------------------------------
        sqrt2_value = None
        coef_approx = None
        scaled_intermediate = None

        if step_count % 2 == 0:
            # ЧЁТНАЯ степень → точное число
            base_scale = 2 ** (step_count // 2)
            is_exact = True

            if delta > 0:
                scale = base_scale
                scale_factor_pretty = str(base_scale)
            else:
                scale = 1 / base_scale
                scale_factor_pretty = f"1/{base_scale}"

            # Для exact случаев промежуточные значения не нужны
            sqrt2_value = None
            coef_approx = None
            scaled_intermediate = None

        else:
            # НЕЧЁТНАЯ степень → остаётся √2
            is_exact = False

            sqrt2 = math.sqrt(2)
            sqrt2_value = round(sqrt2, 2)  # 1.41

            coef_power = 2 ** ((step_count - 1) // 2)

            if delta > 0:
                # Прямое увеличение
                scale = sqrt2 ** step_count

                if coef_power == 1:
                    scale_factor_pretty = "√2"
                else:
                    scale_factor_pretty = f"{coef_power}√2"

                coef_approx = round(scale, 2)

            else:
                # Уменьшение (обратная степень)
                scale = sqrt2 ** (-step_count)

                if coef_power == 1:
                    scale_factor_pretty = "1/√2"
                else:
                    scale_factor_pretty = f"1/({coef_power}√2)"

                coef_approx = round(scale, 2)

            # Промежуточное произведение (например 12 * 0.71 = 8.52)
            scaled_intermediate = round(original_font * coef_approx, 2)

        # ---------------------------------------------
        # Вычисления
        # ---------------------------------------------
        scaled_precise = original_font * scale
        rounded_font = int(round(scaled_precise))

        needs_rounding = (scaled_precise != rounded_font)

        # ---------------------------------------------
        # Формула для отображения
        # ---------------------------------------------
        if delta > 0:
            scale_formula = f"(√2){sup_step}"
        else:
            scale_formula = f"1/(√2){sup_step}"

        # ---------------------------------------------
        # Передача в humanizer
        # ---------------------------------------------
        variables.update({
            "from_format": fmt_from,
            "to_format": fmt_to,
            "from_index": idx_from,
            "to_index": idx_to,

            "sheet_became": sheet_became,
            "font_action": font_action,

            "original_font": original_font,
            "step_count": step_count,
            "sup_step": sup_step,
            "delta": step_count,
            "is_exact": is_exact,

            "scale_formula": scale_formula,
            "scale_factor": scale_factor_pretty,

            # 🔹 Для подробного режима
            "sqrt2_approx": format_number(sqrt2_value) if not is_exact else None,
            "coef_approx": format_number(coef_approx) if not is_exact else None,
            "scaled_intermediate": format_number(scaled_intermediate) if not is_exact else None,

            "rounded_font": rounded_font,
            "needs_rounding": needs_rounding,
        })


    solution_core: Dict[str, Any] = {
        "question_id": question_id,
        "pattern": pattern,
        "narrative": narrative,
        "variables": variables,
        "final_answer": task["answer"],
    }

    # ---------------------------------------------------------
    # help_image по контракту
    # ---------------------------------------------------------

    help_image_file = task.get("help_image_file")
    help_image = None

    if help_image_file:
        sd = task.get("solution_data") or {}

        target = sd.get("target_format")
        reference = sd.get("reference_format")
        operation = sd.get("operation")

        # 🔹 Добавляем абсолютный путь
        assets_dir = (
            Path(__file__).resolve().parents[4]
            / "non_generators"
            / "task_1_5"
            / "paper"
            / "assets"
        )

        full_path = assets_dir / help_image_file

        # Определяем текст операции для GPT
        if operation == "divide_by_2":
            operation_text = "меньший формат получается делением большего пополам"
        elif operation == "multiply_by_2":
            operation_text = "больший формат получается удвоением соответствующей стороны"
        elif operation in ("take_ref_length", "take_ref_width"):
            operation_text = "соответствующие стороны форматов совпадают по длине"
        else:
            operation_text = "форматы связаны стандартным правилом серии A"

        help_image = {
            "file": str(full_path),   # ← вот это главное изменение
            "schema": "paper_pair",
            "params": {
                "target_format": target,
                "reference_format": reference,
                "operation": operation,
            },
            "description_for_gpt": (
                f"На изображении показана схема форматов бумаги серии A для пары "
                f"{reference} → {target}. "
                f"В серии A каждый следующий формат получается делением предыдущего "
                f"листа пополам по длинной стороне. "
                f"В данной задаче используется правило: {operation_text}. "
                f"На схеме указаны длина и ширина каждого формата."
            )
        }

    return {
        "solution_core": solution_core,
        "help_image": help_image,
    }
