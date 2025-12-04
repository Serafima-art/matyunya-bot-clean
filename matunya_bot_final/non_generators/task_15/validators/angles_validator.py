# matunya_bot_final/non_generators/task_15/validators/angles_validator.py

"""
Validator for Task 15 — Theme 1: Angles

This module validates raw input data for all angle-related patterns,
checks correctness, constructs internal normalized structures,
computes the correct answer, and builds the drawing_info block.

Patterns in this group:
    - triangle_external_angle
    - angle_bisector_find_half_angle
"""

from typing import Dict, Any


class AnglesValidator:
    """
    Main entry point. Accepts raw problem data and returns
    a fully validated, normalized JSON structure.
    """

    def __init__(self):
        # Dispatch table: pattern → handler
        self.handlers = {
            "triangle_external_angle": self._handle_triangle_external_angle,
            "angle_bisector_find_half_angle": self._handle_angle_bisector_find_half_angle,
        }

    # -----------------------------------------------------------
    # Public API
    # -----------------------------------------------------------

    def validate(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method.
        Takes raw data and returns structured validated data.
        """
        pattern = raw.get("pattern")
        if pattern not in self.handlers:
            raise ValueError(f"Unsupported angle pattern: {pattern}")

        handler = self.handlers[pattern]
        return handler(raw)

    # -----------------------------------------------------------
    # Pattern 1.1: triangle_external_angle
    # -----------------------------------------------------------

    def _handle_triangle_external_angle(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate input for pattern triangle_external_angle
        and build structured JSON.
        """
        # TODO: extract A,B
        # TODO: validate ranges
        # TODO: compute answer = A + B
        # TODO: build text
        # TODO: build drawing_info
        # TODO: return full JSON blob

        return {
            "id": None,            # filled later by build system
            "pattern": "triangle_external_angle",
            "text": None,          # TODO
            "answer": None,        # TODO
            "image_svg": None,     # filled later by svg_drawer
            "variables": {
                "given": {},
                "to_find": {},
                "humanizer_data": {},
                "drawing_info": {}
            }
        }

    # -----------------------------------------------------------
    # Pattern 1.2: angle_bisector_find_half_angle
    # -----------------------------------------------------------

    def _handle_angle_bisector_find_half_angle(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate input for pattern angle_bisector_find_half_angle
        and build structured JSON.
        """
        # TODO: extract full_angle
        # TODO: validate
        # TODO: compute answer = full_angle / 2
        # TODO: build text
        # TODO: build drawing_info

        return {
            "id": None,
            "pattern": "angle_bisector_find_half_angle",
            "text": None,
            "answer": None,
            "image_svg": None,
            "variables": {
                "given": {},
                "to_find": {},
                "humanizer_data": {},
                "drawing_info": {}
            }
        }
