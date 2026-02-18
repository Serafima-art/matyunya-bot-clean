# matunya_bot_final/help_core/solvers/task_1_5/paper_solver.py

from __future__ import annotations

import math

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
            }
        )

    # =========================================================
    # 🔵 ДОСТРОЙКА FACTS ДЛЯ Q3 (paper_dimensions)
    # =========================================================

    if pattern == "paper_dimensions":

        fmt = task["input_data"]["format"]

        # получаем размеры из variant.table_context
        table_context = variant["table_context"]
        formats_data = table_context["formats_data"]

        length_mm = formats_data[fmt]["length_mm"]
        width_mm = formats_data[fmt]["width_mm"]

        greater = max(length_mm, width_mm)
        smaller = min(length_mm, width_mm)

        row_number = list(formats_data.keys()).index(fmt) + 1


        # ---------------------------
        # find_length / find_width
        # ---------------------------
        if narrative in ("find_length", "find_width"):

            selected = greater if narrative == "find_length" else smaller

            variables.update({
                "format": fmt,
                "row_number": row_number,
                "length_mm": length_mm,
                "width_mm": width_mm,
                "selected_value": selected,
            })


        # ---------------------------
        # find_side
        # ---------------------------
        if narrative == "find_side":

            length = variables["length_mm"]
            width = variables["width_mm"]
            selected = variables["selected_value"]

            # определяем вторую сторону
            if selected == length:
                other_value = width
            else:
                other_value = length

            # формируем корректное сравнение
            if selected > other_value:
                comparison_expression = f"{selected} больше {other_value}"
            else:
                comparison_expression = f"{selected} меньше {other_value}"

            variables.update({
                "other_value": other_value,
                "comparison_expression": comparison_expression,
            })


        # ---------------------------
        # find_ratio
        # ---------------------------
        if narrative == "find_ratio":

            rounded_ratio = base_variables["rounded_ratio"]

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
        # find_diagonal_ratio
        # ---------------------------
        if narrative == "find_diagonal_ratio":

            ratio = base_variables["rounded_ratio"]

            text = task.get("original_text", "").lower()

            if "больш" in text:
                side_type = "большей"
            else:
                side_type = "меньшей"

            variables.update({
                "side_type": side_type,
                "ratio_value": ratio,
            })


        # ---------------------------
        # find_with_rounding (Q3)
        # ---------------------------
        if narrative == "find_with_rounding":

            original_value = int(variables["original_value"])
            rounded_value = int(variables["rounded_value"])
            round_base = int(variables["round_base"])

            exact_multiple = (original_value % round_base == 0)

            if exact_multiple:
                lower_value = original_value
                upper_value = original_value
                is_middle = False
            else:
                lower_value = (original_value // round_base) * round_base
                upper_value = lower_value + round_base

                # ровно ли посередине
                is_middle = abs(original_value - lower_value) == abs(original_value - upper_value)

            variables.update({
                "exact_multiple": exact_multiple,
                "is_middle": is_middle,
                "lower_value": int(lower_value),
                "upper_value": int(upper_value),
            })

    # =========================================================
    # 🔵 ДОСТРОЙКА FACTS ДЛЯ Q4 (paper_area)
    # =========================================================

    if pattern == "paper_area":

        fmt = task["input_data"]["format"]

        table_context = variant["table_context"]
        formats_data = table_context["formats_data"]

        length_mm = formats_data[fmt]["length_mm"]
        width_mm = formats_data[fmt]["width_mm"]

        length_cm = round(length_mm / 10, 1)
        width_cm = round(width_mm / 10, 1)

        # ---------------------------
        # area_basic
        # ---------------------------
        if narrative == "area_basic":

            area_value = base_variables["area"]

            variables.update({
                "format": fmt,
                "length_mm": length_mm,
                "width_mm": width_mm,
                "length_cm": length_cm,
                "width_cm": width_cm,
                "area_raw": area_value,
                "area_value": area_value,
            })

        # ---------------------------
        # area_with_rounding_10
        # ---------------------------
        if narrative == "area_with_rounding_10":

            area_raw = base_variables["area_raw"]
            rounded_area = base_variables["rounded_area"]

            round_base = 10

            lower_value = (int(area_raw) // round_base) * round_base
            upper_value = lower_value + round_base

            variables.update({
                "format": fmt,
                "length_mm": length_mm,
                "width_mm": width_mm,
                "length_cm": length_cm,
                "width_cm": width_cm,
                "area_raw": area_raw,
                "rounded_area": rounded_area,
                "round_base": round_base,
                "lower_value": lower_value,
                "upper_value": upper_value,
            })

        # ---------------------------
        # area_with_rounding_5
        # ---------------------------
        if narrative == "area_with_rounding_5":

            area_raw = base_variables["area_raw"]
            rounded_area = base_variables["rounded_area"]

            round_base = 5

            lower_value = (int(area_raw) // round_base) * round_base
            upper_value = lower_value + round_base

            variables.update({
                "format": fmt,
                "length_mm": length_mm,
                "width_mm": width_mm,
                "length_cm": length_cm,
                "width_cm": width_cm,
                "area_raw": area_raw,
                "rounded_area": rounded_area,
                "round_base": round_base,
                "lower_value": lower_value,
                "upper_value": upper_value,
            })

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

    return solution_core
