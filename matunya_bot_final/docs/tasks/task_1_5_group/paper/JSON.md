{
  "id": "paper_2026_var_01",

  "image_file": "task_paper_formats.png",

  "table_context": {
    "table_order": ["A1", "A3", "A0", "A2"],

    "formats_data": {
      "A0": { "length_mm": 1189, "width_mm": 841 },
      "A1": { "length_mm": 841,  "width_mm": 594 },
      "A2": { "length_mm": 594,  "width_mm": 420 },
      "A3": { "length_mm": 420,  "width_mm": 297 },
      "A4": { "length_mm": 297,  "width_mm": 210 },
      "A5": { "length_mm": 210,  "width_mm": 148 },
      "A6": { "length_mm": 148,  "width_mm": 105 },
      "A7": { "length_mm": 105,  "width_mm": 74 }
    }
  },

  "questions": [

    {
      "q_number": 1,
      "pattern": "paper_format_match",
      "narrative": "match_formats_to_rows",

      "input_data": {
        "columns_order": ["A0", "A3", "A2", "A1"]
      },

      "solution_data": {
        "row_to_format_mapping": {
          "1": "A1",
          "2": "A3",
          "3": "A0",
          "4": "A2"
        },
        "answer_sequence": "3241"
      },

      "answer": "3241"
    },

    {
      "q_number": 2,
      "pattern": "paper_split",
      "narrative": "count_subformats",

      "input_data": {
        "from_format": "A0",
        "to_format": "A3"
      },

      "solution_data": {
        "index_from": 0,
        "index_to": 3,
        "index_difference": 3,
        "power_expression": "2^3",
        "power_value": 8
      },

      "answer": 8
    },

    {
      "q_number": 3,
      "pattern": "paper_dimensions",
      "narrative": "find_width",

      "input_data": {
        "format": "A3",
        "dimension_type": "width"
      },

      "solution_data": {
        "length_mm": 420,
        "width_mm": 297,
        "selected_value": 297
      },

      "answer": 297
    },

    {
      "q_number": 4,
      "pattern": "paper_area",
      "narrative": "area_with_rounding_10",

      "input_data": {
        "format": "A3",
        "rounding_to": 10
      },

      "solution_data": {
        "length_mm": 420,
        "width_mm": 297,
        "length_cm": 42.0,
        "width_cm": 29.7,
        "raw_area_cm2": 1247.4,
        "rounding_to": 10,
        "rounded_area_cm2": 1250
      },

      "answer": 1250
    },

    {
      "q_number": 5,
      "pattern": "paper_pack_weight",
      "narrative": "pack_weight",

      "input_data": {
        "format": "A3",
        "sheet_count": 400,
        "density_g_per_m2": 125
      },

      "solution_data": {
        "format_index": 3,
        "area_m2": 0.125,
        "sheet_count": 400,
        "density_g_per_m2": 125,
        "raw_weight_g": 6250,
        "rounded_weight_g": 6250
      },

      "answer": 6250
    }

  ]
}
