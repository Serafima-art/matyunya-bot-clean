"""Validators for task 15 angle patterns."""

from __future__ import annotations

import re
from typing import Any, Dict

ANGLE_SYMBOL = "\u2220"


class AnglesValidator:
    """Entry point for angle tasks validation."""

    def __init__(self) -> None:
        self.handlers = {
            "triangle_external_angle": self._handle_triangle_external_angle,
            "angle_bisector_find_half_angle": self._handle_angle_bisector_find_half_angle,
        }

    def validate(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch validation to a pattern-specific handler."""
        pattern = raw.get("pattern")
        if pattern not in self.handlers:
            raise ValueError(f"Unsupported angle pattern: {pattern}")
        return self.handlers[pattern](raw)

    # -----------------------------------------------------------
    # Pattern 1.1: triangle_external_angle
    # -----------------------------------------------------------

    def _handle_triangle_external_angle(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Parse two interior angles and return Etalon 3.0 JSON."""
        text = raw["text"]
        numbers = [int(n) for n in re.findall(r"\d+", text)]
        if len(numbers) < 2:
            raise ValueError(
                f"triangle_external_angle: expected at least 2 numbers in text: {text!r}"
            )

        angle_a, angle_b = numbers[0], numbers[1]
        answer = angle_a + angle_b
        internal_c = 180 - answer

        if internal_c < 90:
            image_file = "T9_ext_acute.png"
        elif internal_c == 90:
            image_file = "T9_ext_right.png"
        else:
            image_file = "T9_ext_obtuse.png"

        return {
            "id": raw.get("id"),
            "pattern": "triangle_external_angle",
            "text": text,
            "answer": answer,
            "image_file": image_file,
            "variables": {
                "given": {
                    "triangle_name": "ABC",
                    "triangle_type": "general",
                    "angles": {"A": angle_a, "B": angle_b},
                },
                "to_find": {"type": "angle", "name": "external_C"},
                "humanizer_data": {
                    "angle_names": {
                        "A": f"{ANGLE_SYMBOL}A",
                        "B": f"{ANGLE_SYMBOL}B",
                        "C": f"{ANGLE_SYMBOL}C",
                    },
                },
            },
        }

    # -----------------------------------------------------------
    # Pattern 1.2: angle_bisector_find_half_angle
    # -----------------------------------------------------------

    def _handle_angle_bisector_find_half_angle(
        self, raw: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse the full angle with a bisector and return Etalon 3.0 JSON."""
        text = raw["text"]
        target_half_name = "CAD" if "CAD" in text else "BAD"
        numbers = [int(n) for n in re.findall(r"\d+", text)]
        if not numbers:
            raise ValueError(
                f"angle_bisector_find_half_angle: expected a number in text: {text!r}"
            )

        full_angle = numbers[0]
        half_angle = full_angle / 2
        answer = int(half_angle) if float(half_angle).is_integer() else half_angle

        if full_angle < 90:
            image_file = "T8_acute.png"
        elif full_angle == 90:
            image_file = "T8_right.png"
        else:
            image_file = "T8_obtuse.png"

        return {
            "id": raw.get("id"),
            "pattern": "angle_bisector_find_half_angle",
            "text": text,
            "answer": answer,
            "image_file": image_file,
            "variables": {
                "given": {
                    "triangle_name": "ABC",
                    "triangle_type": "general",
                    "angles": {"full_angle": full_angle},
                },
                "to_find": {"type": "angle", "name": target_half_name},
                "humanizer_data": {
                    "angle_names": {
                        "full": f"{ANGLE_SYMBOL}BAC",
                        "half": f"{ANGLE_SYMBOL}{target_half_name}",
                    },
                    "element_names": {"bisector": "AD"},
                },
            },
        }
