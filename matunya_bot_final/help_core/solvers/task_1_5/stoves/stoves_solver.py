from typing import Dict, Any


def solve_stoves(task_context: Dict[str, Any]) -> Dict[str, Any]:

    task: Dict[str, Any] = task_context["task"]

    question_id = task["q_number"]
    pattern = task["pattern"]
    narrative = task["narrative"]

    input_data: Dict[str, Any] = task.get("input_data") or {}
    solution_data: Dict[str, Any] = task.get("solution_data") or {}

    base_variables: Dict[str, Any] = {**input_data, **solution_data}
    variables: Dict[str, Any] = base_variables.copy()

    # =========================================================
    # 🔵 PATTERN: stove_match_table
    # =========================================================

    if pattern == "stove_match_table":

        columns = input_data.get("columns_order")
        column_label = input_data.get("column_label")
        mapping = base_variables.get("stove_no_to_value_mapping")
        answer = base_variables.get("answer_sequence") or task.get("answer")

        required = {
            "columns_order": columns,
            "column_label": column_label,
            "mapping": mapping,
            "answer": answer,
        }

        missing = [k for k, v in required.items() if v is None]
        if missing:
            raise ValueError(f"SOLVER Q1: missing fields: {', '.join(missing)}")

        variables.update({
            "column_label": column_label,
            "columns": columns,
            "stove_no_to_value_mapping": mapping,
            "answer": answer,
        })

        if narrative == "match_volume":
            explanation_idea = "IDEA_STOVE_MATCH_VOLUME"
        elif narrative == "match_weight":
            explanation_idea = "IDEA_STOVE_MATCH_WEIGHT"
        elif narrative == "match_cost":
            explanation_idea = "IDEA_STOVE_MATCH_COST"
        else:
            raise ValueError(f"Unsupported narrative for stove_match_table: {narrative}")

    # =========================================================
    # 🟨 PATTERN: stoves_room_geometry
    # =========================================================

    elif pattern == "stoves_room_geometry":

        # -----------------------------
        # find_volume
        # -----------------------------
        if narrative == "find_volume":

            length = base_variables.get("length")
            width = base_variables.get("width")
            height = base_variables.get("height")
            volume = base_variables.get("volume")

            required = {
                "length": length,
                "width": width,
                "height": height,
                "volume": volume,
            }
            missing = [k for k, v in required.items() if v is None]
            if missing:
                raise ValueError(f"SOLVER Q2 find_volume: missing fields: {', '.join(missing)}")

            variables.update({
                "length": length,
                "width": width,
                "height": height,
                "volume": volume,
                "answer": volume,
            })

            explanation_idea = "find_volume"

        # -----------------------------
        # find_base_area
        # -----------------------------
        elif narrative == "find_base_area":

            length = base_variables.get("length")
            width = base_variables.get("width")
            area = base_variables.get("area")

            required = {
                "length": length,
                "width": width,
                "area": area,
            }
            missing = [k for k, v in required.items() if v is None]
            if missing:
                raise ValueError(f"SOLVER Q2 find_base_area: missing fields: {', '.join(missing)}")

            variables.update({
                "length": length,
                "width": width,
                "area": area,
                "answer": area,
            })

            explanation_idea = "find_base_area"

        # -----------------------------
        # find_lateral_area
        # -----------------------------
        elif narrative == "find_lateral_area":

            length = base_variables.get("length")
            width = base_variables.get("width")
            height = base_variables.get("height")

            door_width_cm = base_variables.get("door_width_cm")
            door_width_m = base_variables.get("door_width_m")
            door_height_m = base_variables.get("door_height_m")

            sum_length_width = base_variables.get("sum_length_width")
            perimeter = base_variables.get("perimeter")
            walls_area = base_variables.get("walls_area")
            door_area = base_variables.get("door_area")
            result_area = base_variables.get("result_area")

            required = {
                "length": length,
                "width": width,
                "height": height,
                "door_width_cm": door_width_cm,
                "door_width_m": door_width_m,
                "door_height_m": door_height_m,
                "sum_length_width": sum_length_width,
                "perimeter": perimeter,
                "walls_area": walls_area,
                "door_area": door_area,
                "result_area": result_area,
            }
            missing = [k for k, v in required.items() if v is None]
            if missing:
                raise ValueError(
                    f"SOLVER Q2 find_lateral_area: missing fields: {', '.join(missing)}"
                )

            variables.update({
                "length": length,
                "width": width,
                "height": height,
                "door_width_cm": door_width_cm,
                "door_width_m": door_width_m,
                "door_height_m": door_height_m,
                "sum_length_width": sum_length_width,
                "perimeter": perimeter,
                "walls_area": walls_area,
                "door_area": door_area,
                "result_area": result_area,
                "answer": result_area,
            })

            explanation_idea = "find_lateral_area"

        else:
            raise ValueError(f"Unsupported narrative for stoves_room_geometry: {narrative}")

    # =========================================================
    # 🔶 PATTERN: stoves_purchase_cost
    # =========================================================

    elif pattern == "stoves_purchase_cost":

        length = base_variables.get("length")
        width = base_variables.get("width")
        height = base_variables.get("height")
        room_volume = base_variables.get("room_volume")

        variables.update({
            "length": length,
            "width": width,
            "height": height,
            "room_volume": room_volume,
        })

        # -----------------------------------------------------
        # find_price_difference
        # -----------------------------------------------------
        if narrative == "find_price_difference":

            electric_cost = base_variables.get("electric_cost")
            electric_install_cost = base_variables.get("electric_install_cost")
            electric_total = base_variables.get("electric_total")

            wood_ok_no = base_variables.get("wood_ok_no")
            wood_ok_cost = base_variables.get("wood_ok_cost")

            result = base_variables.get("result")

            required = {
                "electric_cost": electric_cost,
                "electric_install_cost": electric_install_cost,
                "electric_total": electric_total,
                "wood_ok_no": wood_ok_no,
                "wood_ok_cost": wood_ok_cost,
                "result": result,
            }

            missing = [k for k, v in required.items() if v is None]
            if missing:
                raise ValueError(
                    f"SOLVER Q3 find_price_difference: missing fields: {', '.join(missing)}"
                )

            variables.update({
                "electric_cost": electric_cost,
                "electric_install_cost": electric_install_cost,
                "electric_total": electric_total,
                "wood_ok_no": wood_ok_no,
                "wood_ok_cost": wood_ok_cost,
                "result": result,
                "answer": result,
            })

            explanation_idea = "find_price_difference"

        # -----------------------------------------------------
        # find_wood_stove_total_cost
        # -----------------------------------------------------
        elif narrative == "find_wood_stove_total_cost":

            wood_ok_no = base_variables.get("wood_ok_no")
            wood_ok_cost = base_variables.get("wood_ok_cost")
            delivery_cost = base_variables.get("delivery_cost")
            wood_total = base_variables.get("wood_total")

            result = base_variables.get("result")

            required = {
                "wood_ok_no": wood_ok_no,
                "wood_ok_cost": wood_ok_cost,
                "delivery_cost": delivery_cost,
                "wood_total": wood_total,
                "result": result,
            }

            missing = [k for k, v in required.items() if v is None]
            if missing:
                raise ValueError(
                    f"SOLVER Q3 find_wood_stove_total_cost: missing fields: {', '.join(missing)}"
                )

            variables.update({
                "wood_ok_no": wood_ok_no,
                "wood_ok_cost": wood_ok_cost,
                "delivery_cost": delivery_cost,
                "wood_total": wood_total,
                "result": result,
                "answer": result,
            })

            explanation_idea = "find_wood_stove_total_cost"

        # -----------------------------------------------------
        # find_electric_stove_total_cost
        # -----------------------------------------------------
        elif narrative == "find_electric_stove_total_cost":

            electric_cost = base_variables.get("electric_cost")
            electric_install_cost = base_variables.get("electric_install_cost")
            delivery_cost = base_variables.get("delivery_cost")
            electric_total = base_variables.get("electric_total")

            result = base_variables.get("result")

            required = {
                "electric_cost": electric_cost,
                "electric_install_cost": electric_install_cost,
                "delivery_cost": delivery_cost,
                "electric_total": electric_total,
                "result": result,
            }

            missing = [k for k, v in required.items() if v is None]
            if missing:
                raise ValueError(
                    f"SOLVER Q3 find_electric_stove_total_cost: missing fields: {', '.join(missing)}"
                )

            variables.update({
                "electric_cost": electric_cost,
                "electric_install_cost": electric_install_cost,
                "delivery_cost": delivery_cost,
                "electric_total": electric_total,
                "result": result,
                "answer": result,
            })

            explanation_idea = "find_electric_stove_total_cost"

        # -----------------------------------------------------
        # find_operating_cost_difference
        # -----------------------------------------------------
        elif narrative == "find_operating_cost_difference":

            electric_kwh = base_variables.get("electric_kwh")
            electric_price = base_variables.get("electric_price_per_kwh")
            electric_oper = base_variables.get("electric_oper")

            wood_volume = base_variables.get("wood_volume_m3")
            wood_price = base_variables.get("wood_price_per_m3")
            wood_oper = base_variables.get("wood_oper")

            result = base_variables.get("result")

            required = {
                "electric_kwh": electric_kwh,
                "electric_price_per_kwh": electric_price,
                "electric_oper": electric_oper,
                "wood_volume_m3": wood_volume,
                "wood_price_per_m3": wood_price,
                "wood_oper": wood_oper,
                "result": result,
            }

            missing = [k for k, v in required.items() if v is None]
            if missing:
                raise ValueError(
                    f"SOLVER Q3 find_operating_cost_difference: missing fields: {', '.join(missing)}"
                )

            variables.update({
                "electric_kwh": electric_kwh,
                "electric_price_per_kwh": electric_price,
                "electric_oper": electric_oper,
                "wood_volume_m3": wood_volume,
                "wood_price_per_m3": wood_price,
                "wood_oper": wood_oper,
                "result": result,
                "answer": result,
            })

            explanation_idea = "find_operating_cost_difference"

        else:
            raise ValueError(f"Unsupported narrative for stoves_purchase_cost: {narrative}")

    # =========================================================
    # 🟩 PATTERN: stoves_arc_radius
    # =========================================================

    elif pattern == "stoves_arc_radius":

        if narrative == "find_arc_radius":

            a = base_variables.get("a")
            b = base_variables.get("b")

            half_width = base_variables.get("half_width")

            a_squared = base_variables.get("a_squared")
            half_width_squared = base_variables.get("half_width_squared")
            radius_squared = base_variables.get("radius_squared")

            radius = base_variables.get("radius")

            required = {
                "a": a,
                "b": b,
                "half_width": half_width,
                "a_squared": a_squared,
                "half_width_squared": half_width_squared,
                "radius_squared": radius_squared,
                "radius": radius,
            }

            missing = [k for k, v in required.items() if v is None]
            if missing:
                raise ValueError(
                    f"SOLVER Q5 find_arc_radius: missing fields: {', '.join(missing)}"
                )

            variables.update({
                "a": a,
                "b": b,
                "half_width": half_width,
                "a_squared": a_squared,
                "half_width_squared": half_width_squared,
                "radius_squared": radius_squared,
                "radius": radius,
                "answer": radius,
            })

            explanation_idea = "find_arc_radius"

        else:
            raise ValueError(f"Unsupported narrative for stoves_arc_radius: {narrative}")

    else:
        raise ValueError(f"Unsupported pattern for stoves solver: {pattern}")

    # =========================================================
    # 📦 Канонический solution_core
    # =========================================================

    solution_core: Dict[str, Any] = {
        "question_id": question_id,
        "pattern": pattern,
        "narrative": narrative,
        "skill_source_id": task.get("skill_source_id"),
        "explanation_idea": explanation_idea,
        "calculation_steps": [],
        "final_answer": task.get("answer"),
        "variables": variables,
        "hints": [],
    }

    return {
        "solution_core": solution_core
    }
