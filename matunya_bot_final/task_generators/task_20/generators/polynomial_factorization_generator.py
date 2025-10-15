"""Generator for task 20 polynomial_factorization subtype."""

from __future__ import annotations

import random
import re
import uuid
from typing import Any, Callable, Dict, Iterable, List, Sequence, Tuple


SUPERSCRIPTS = {
    "0": "\u2070",
    "1": "\u00b9",
    "2": "\u00b2",
    "3": "\u00b3",
    "4": "\u2074",
    "5": "\u2075",
    "6": "\u2076",
    "7": "\u2077",
    "8": "\u2078",
    "9": "\u2079",
}

ROOT_CANDIDATES = [number for number in range(-6, 7) if number != 0]


def _poly_multiply(poly_a: Sequence[int], poly_b: Sequence[int]) -> List[int]:
    """Multiply two polynomials represented in ascending power order."""
    result = [0 for _ in range(len(poly_a) + len(poly_b) - 1)]
    for idx_a, coeff_a in enumerate(poly_a):
        for idx_b, coeff_b in enumerate(poly_b):
            result[idx_a + idx_b] += coeff_a * coeff_b
    return result


def _poly_from_roots(roots: Iterable[int]) -> List[int]:
    """Construct a monic polynomial with the provided integer roots."""
    coeffs: List[int] = [1]
    for root in roots:
        coeffs = _poly_multiply(coeffs, [-root, 1])
    return coeffs


def _format_polynomial(coeffs: Sequence[int]) -> str:
    """Convert polynomial coefficients into a readable string."""
    if not coeffs:
        return "0"

    degree = len(coeffs) - 1
    terms: List[str] = []
    for idx, coefficient in enumerate(reversed(coeffs)):
        power = degree - idx
        if coefficient == 0:
            continue

        sign = "-" if coefficient < 0 else "+"
        abs_coeff = abs(coefficient)

        if power == 0:
            body = str(abs_coeff)
        elif power == 1:
            body = "x" if abs_coeff == 1 else f"{abs_coeff}x"
        else:
            body = f"x^{power}" if abs_coeff == 1 else f"{abs_coeff}x^{power}"

        if not terms:
            terms.append(body if sign == "+" else f"-{body}")
        else:
            terms.append(f" {sign} {body}")

    return "".join(terms) if terms else "0"


def _equation_to_display(equation: str) -> str:
    """Replace powers with superscript equivalents for display purposes."""

    def _replace_known(match: re.Match[str]) -> str:
        base = match.group(1)
        exponent = match.group(2)
        superscript = "".join(SUPERSCRIPTS.get(char, char) for char in exponent)
        return f"{base}{superscript}"

    equation = re.sub(r"(x)\^([0-9]+)", _replace_known, equation)
    equation = re.sub(r"\^([0-9])", lambda match: SUPERSCRIPTS.get(match.group(1), match.group(1)), equation)
    return equation


def _prepare_question_text(equation: str) -> str:
    """Wrap equation with standard instruction and prettify powers."""
    return f"Реши уравнение:\n{_equation_to_display(equation)}"


def _generate_common_poly_task() -> Tuple[str, List[str], Dict[str, Any]]:
    """Generate task of the form (ax + b)(poly) = k * poly."""
    for _ in range(500):
        r1, r2 = random.sample(ROOT_CANDIDATES, 2)
        r3_candidates = [value for value in ROOT_CANDIDATES if value not in {r1, r2}]
        if not r3_candidates:
            continue
        r3 = random.choice(r3_candidates)

        common_poly_coeffs = _poly_from_roots((r1, r2))

        linear_coeff = random.choice([-4, -3, -2, -1, 1, 2, 3, 4])
        constant_term = random.randint(-8, 8)
        rhs_multiplier = linear_coeff * r3 + constant_term
        if rhs_multiplier in (0, 1, -1):
            continue

        rhs_coeffs = [coefficient * rhs_multiplier for coefficient in common_poly_coeffs]
        if any(abs(coeff) > 80 for coeff in rhs_coeffs):
            continue

        linear_text = _format_polynomial([constant_term, linear_coeff])
        common_poly_text = _format_polynomial(common_poly_coeffs)
        rhs_text = _format_polynomial(rhs_coeffs)

        equation = f"({linear_text})({common_poly_text}) = {rhs_text}"
        answers = sorted({r1, r2, r3})

        variables = {
            "solution_pattern": "common_poly",
            "linear_factor": {
                "a": linear_coeff,
                "b": constant_term,
                "text": linear_text,
                "root": r3,
            },
            "common_factor": {
                "coeffs": common_poly_coeffs,
                "text": common_poly_text,
                "roots": sorted([r1, r2]),
            },
            "rhs": {
                "multiplier": rhs_multiplier,
                "coeffs": rhs_coeffs,
                "text": rhs_text,
            },
        }
        return equation, [str(value) for value in answers], variables
    raise RuntimeError("Failed to generate common polynomial pattern.")


def _generate_diff_squares_task() -> Tuple[str, List[str], Dict[str, Any]]:
    """Generate task based on transforming (poly1)(poly2) = 0 into A² = B²."""
    full_range = list(range(-6, 7))
    for _ in range(500):
        r_minus = random.sample(full_range, 2)
        r_plus = random.sample(full_range, 2)

        sum_minus = sum(r_minus)
        sum_plus = sum(r_plus)
        prod_minus = r_minus[0] * r_minus[1]
        prod_plus = r_plus[0] * r_plus[1]

        if (sum_minus + sum_plus) % 2 != 0:
            continue
        if (sum_minus - sum_plus) % 2 != 0:
            continue
        if (prod_minus + prod_plus) % 2 != 0:
            continue
        if (prod_plus - prod_minus) % 2 != 0:
            continue

        poly_minus_coeffs = [prod_minus, -sum_minus, 1]
        poly_plus_coeffs = [prod_plus, -sum_plus, 1]
        if poly_minus_coeffs == poly_plus_coeffs:
            continue

        a_coeffs = [
            (prod_minus + prod_plus) // 2,
            -(sum_minus + sum_plus) // 2,
            1,
        ]
        b_coeffs = [
            (prod_plus - prod_minus) // 2,
            (sum_minus - sum_plus) // 2,
        ]

        if b_coeffs[0] == 0 and b_coeffs[1] == 0:
            continue

        a_text = _format_polynomial(a_coeffs)
        b_text = _format_polynomial(b_coeffs)
        poly_minus_text = _format_polynomial(poly_minus_coeffs)
        poly_plus_text = _format_polynomial(poly_plus_coeffs)

        equation = f"({a_text})^2 = ({b_text})^2"
        answers = sorted(set(r_minus + r_plus))

        variables = {
            "solution_pattern": "diff_squares",
            "factored_form": {
                "poly_minus": {
                    "coeffs": poly_minus_coeffs,
                    "text": poly_minus_text,
                    "roots": sorted(r_minus),
                },
                "poly_plus": {
                    "coeffs": poly_plus_coeffs,
                    "text": poly_plus_text,
                    "roots": sorted(r_plus),
                },
            },
            "difference_of_squares": {
                "A": {"coeffs": a_coeffs, "text": a_text},
                "B": {"coeffs": b_coeffs, "text": b_text},
            },
        }
        return equation, [str(value) for value in answers], variables
    raise RuntimeError("Failed to generate difference of squares pattern.")


def _generate_grouping_task() -> Tuple[str, List[str], Dict[str, Any]]:
    """Generate task solvable via grouping (ax + b is a common factor)."""
    for _ in range(500):
        roots = random.sample(ROOT_CANDIDATES, 3)
        total = sum(roots)
        if total == 0:
            continue

        sum_pairs = roots[0] * roots[1] + roots[0] * roots[2] + roots[1] * roots[2]
        product = roots[0] * roots[1] * roots[2]

        if product != total * sum_pairs:
            continue

        scale = random.choice([1, 2, 3])
        a_coeff = scale
        b_coeff = -scale * total
        c_coeff = scale * sum_pairs
        d_coeff = -scale * product

        if c_coeff % a_coeff != 0:
            continue

        polynomial_coeffs = [d_coeff, c_coeff, b_coeff, a_coeff]
        linear_factor_text = _format_polynomial([b_coeff, a_coeff])
        equation = f"{_format_polynomial(polynomial_coeffs)} = 0"

        linear_root_value = total
        variables = {
            "solution_pattern": "grouping",
            "coefficients": {
                "a": a_coeff,
                "b": b_coeff,
                "c": c_coeff,
                "d": d_coeff,
                "as_list": polynomial_coeffs,
            },
            "roots": sorted(roots),
            "grouping": {
                "group1_multiplier": "x^2",
                "group2_multiplier": c_coeff // a_coeff,
                "common_factor": {
                    "coeffs": [b_coeff, a_coeff],
                    "text": linear_factor_text,
                },
            },
        }
        return equation, [str(value) for value in sorted(roots)], variables
    raise RuntimeError("Failed to generate grouping pattern.")


PATTERN_GENERATORS: Dict[str, Callable[[], Tuple[str, List[str], Dict[str, Any]]]] = {
    "common_poly": _generate_common_poly_task,
    "diff_squares": _generate_diff_squares_task,
    "grouping": _generate_grouping_task,
}


def generate_task_20_polynomial_factorization() -> Dict[str, Any]:
    """Generate a task payload following the unified data contract."""
    pattern_key = random.choice(list(PATTERN_GENERATORS))
    generator = PATTERN_GENERATORS[pattern_key]
    equation, answers, variables = generator()

    # Ensure the chosen pattern is reflected in variables even if the generator added it already.
    variables.setdefault("solution_pattern", pattern_key)

    return {
        "id": f"20_polynomial_factorization_{uuid.uuid4().hex[:6]}",
        "task_number": 20,
        "topic": "algebraic_expressions",
        "subtype": "polynomial_factorization",
        "question_text": _prepare_question_text(equation),
        "answer": answers,
        "variables": variables,
    }


__all__ = ["generate_task_20_polynomial_factorization"]

