from __future__ import annotations

from math import pi, sqrt
from typing import Any, Dict, Tuple

from .utils import format_answer

Number = float | int


class Task12Calculator:
    @staticmethod
    def _normalize_input(
        data: Dict[str, Any],
        default_variable: str | None = None,
    ) -> Tuple[str, Dict[str, float], Dict[str, float]]:
        if "variable_to_find" in data:
            variable = data["variable_to_find"]
            params_raw = data.get("params", {}) or {}
            constants_raw = data.get("constants", {}) or {}
        else:
            if default_variable is None:
                raise ValueError("'variable_to_find' is required in the input data")
            variable = default_variable
            params_raw = {k: v for k, v in data.items() if k != "constants"}
            constants_raw = data.get("constants", {}) or {}

        params: Dict[str, float] = {}
        for key, value in params_raw.items():
            if value is None or key.startswith("_"):
                continue
            params[key] = float(value)

        constants: Dict[str, float] = {}
        if isinstance(constants_raw, dict):
            for key, value in constants_raw.items():
                if value is None:
                    continue
                constants[key] = float(value)

        return variable, params, constants

    @staticmethod
    def _require(value: float | None, name: str) -> float:
        if value is None:
            raise ValueError(f"Parameter '{name}' is required for this calculation.")
        return value

    @staticmethod
    def _get_constant(constants: Dict[str, float], name: str, default: float) -> float:
        return constants.get(name, default)

    @staticmethod
    def _finalize(
        values: Dict[str, float | None],
        variable: str,
        answer: float,
    ) -> Dict[str, float | str]:
        values[variable] = answer
        result: Dict[str, float | str] = {}
        for key, value in values.items():
            if value is not None:
                result[key] = float(value)
        result["answer_value"] = float(answer)
        result["answer"] = format_answer(answer)
        return result

    def _solve_gas_law(
        self,
        variable: str,
        params: Dict[str, float],
        constants: Dict[str, float],
    ) -> Tuple[str, float, Dict[str, float]]:
        R_value = self._get_constant(constants, "R", 8.31)
        P = params.get("P")
        V = params.get("V")
        nu = params.get("nu") if params.get("nu") is not None else params.get("n")
        T = params.get("T")

        if variable == "P":
            V_val = self._require(V, "V")
            nu_val = self._require(nu, "nu")
            T_val = self._require(T, "T")
            P = nu_val * R_value * T_val / V_val
            answer = P
        elif variable in {"V", "volume"}:
            P_val = self._require(P, "P")
            nu_val = self._require(nu, "nu")
            T_val = self._require(T, "T")
            V = nu_val * R_value * T_val / P_val
            answer = V
            variable = "V"
        elif variable in {"nu", "n"}:
            P_val = self._require(P, "P")
            V_val = self._require(V, "V")
            T_val = self._require(T, "T")
            nu = P_val * V_val / (R_value * T_val)
            answer = nu
            variable = "nu"
        elif variable == "T":
            P_val = self._require(P, "P")
            V_val = self._require(V, "V")
            nu_val = self._require(nu, "nu")
            T = P_val * V_val / (nu_val * R_value)
            answer = T
        elif variable == "R":
            P_val = self._require(P, "P")
            V_val = self._require(V, "V")
            nu_val = self._require(nu, "nu")
            T_val = self._require(T, "T")
            R_value = P_val * V_val / (nu_val * T_val)
            answer = R_value
            variable = "R"
        else:
            raise ValueError(f"Unsupported variable '{variable}' for ideal gas law.")

        values = {"P": P, "V": V, "nu": nu, "T": T, "R": R_value}
        return variable, answer, values

    def _heron_area(self, a: float, b: float, c: float) -> float:
        semi = (a + b + c) / 2.0
        area_sq = semi * (semi - a) * (semi - b) * (semi - c)
        if area_sq < 0:
            raise ValueError("Triangle sides are inconsistent for Heron's formula.")
        return sqrt(area_sq)

    def _wrap_payload(self, variable: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if 'variable_to_find' in data or 'params' in data or 'constants' in data:
            payload = dict(data)
            payload.setdefault('variable_to_find', variable)
            if 'params' not in payload:
                params = {k: v for k, v in data.items() if k not in {'variable_to_find', 'params', 'constants'}}
                payload['params'] = params
            return payload
        return {'variable_to_find': variable, 'params': dict(data)}

        semi = (a + b + c) / 2.0
        area_sq = semi * (semi - a) * (semi - b) * (semi - c)
        if area_sq < 0:
            raise ValueError("Triangle sides are inconsistent for Heron's formula.")
        return sqrt(area_sq)


    def calculate_archimedes_force(self, data: Dict[str, Any]) -> Dict[str, float]:
        variable, params, constants = self._normalize_input(data, default_variable="F")
        rho = params.get("rho")
        F = params.get("F")
        V = params.get("V")
        g = self._get_constant(constants, "g", 10.0)

        if variable == "F":
            rho_val = self._require(rho, "rho")
            V_val = self._require(V, "V")
            F = rho_val * g * V_val
            answer = F
        elif variable == "V":
            F_val = self._require(F, "F")
            rho_val = self._require(rho, "rho")
            V = F_val / (rho_val * g)
            answer = V
        elif variable == "rho":
            F_val = self._require(F, "F")
            V_val = self._require(V, "V")
            rho = F_val / (g * V_val)
            answer = rho
        elif variable == "g":
            F_val = self._require(F, "F")
            rho_val = self._require(rho, "rho")
            V_val = self._require(V, "V")
            g = F_val / (rho_val * V_val)
            answer = g
        else:
            raise ValueError(f"Unsupported variable '{variable}' for archimedes_force.")

        values = {"F": F, "rho": rho, "V": V, "g": g}
        return self._finalize(values, variable, answer)

    def calculate_area_parallelogram(self, data: Dict[str, Any]) -> Dict[str, float]:
        variable, params, _ = self._normalize_input(data, default_variable="S")
        a = params.get("a")
        b = params.get("b")
        h = params.get("h")
        sin_alpha = params.get("sin_alpha")
        S = params.get("S")

        def area_from_params() -> float:
            if a is not None and h is not None:
                return a * h
            if a is not None and b is not None and sin_alpha is not None:
                return a * b * sin_alpha
            raise ValueError("Insufficient data to compute area of parallelogram.")

        if variable == "S":
            S = area_from_params()
            answer = S
        elif variable == "a":
            S_val = self._require(S, "S")
            if h is not None:
                a = S_val / self._require(h, "h")
            elif b is not None and sin_alpha is not None:
                a = S_val / (b * sin_alpha)
            else:
                raise ValueError("Cannot determine 'a' without 'h' or ('b' and 'sin_alpha').")
            answer = a
        elif variable == "b":
            S_val = self._require(S, "S")
            if a is not None and sin_alpha is not None:
                b = S_val / (a * sin_alpha)
            else:
                raise ValueError("Cannot determine 'b' without 'a' and 'sin_alpha'.")
            answer = b
        elif variable == "h":
            S_val = self._require(S, "S")
            if a is None:
                raise ValueError("Cannot determine 'h' without 'a'.")
            h = S_val / a
            answer = h
        elif variable == "sin_alpha":
            S_val = self._require(S, "S")
            if a is None or b is None:
                raise ValueError("Cannot determine 'sin_alpha' without 'a' and 'b'.")
            sin_alpha = S_val / (a * b)
            answer = sin_alpha
        else:
            raise ValueError(f"Unsupported variable '{variable}' for area_parallelogram.")

        values = {"a": a, "b": b, "h": h, "sin_alpha": sin_alpha, "S": S}
        return self._finalize(values, variable, answer)

    def calculate_area_quadrilateral_d1d2_sin(self, data: Dict[str, Any]) -> Dict[str, float]:
        variable, params, _ = self._normalize_input(data, default_variable="S")
        d1 = params.get("d1")
        d2 = params.get("d2")
        sin_alpha = params.get("sin_alpha")
        S = params.get("S")

        if variable == "S":
            d1_val = self._require(d1, "d1")
            d2_val = self._require(d2, "d2")
            sin_val = self._require(sin_alpha, "sin_alpha")
            S = 0.5 * d1_val * d2_val * sin_val
            answer = S
        elif variable == "d1":
            S_val = self._require(S, "S")
            d2_val = self._require(d2, "d2")
            sin_val = self._require(sin_alpha, "sin_alpha")
            d1 = (2.0 * S_val) / (d2_val * sin_val)
            answer = d1
        elif variable == "d2":
            S_val = self._require(S, "S")
            d1_val = self._require(d1, "d1")
            sin_val = self._require(sin_alpha, "sin_alpha")
            d2 = (2.0 * S_val) / (d1_val * sin_val)
            answer = d2
        elif variable == "sin_alpha":
            S_val = self._require(S, "S")
            d1_val = self._require(d1, "d1")
            d2_val = self._require(d2, "d2")
            sin_alpha = (2.0 * S_val) / (d1_val * d2_val)
            answer = sin_alpha
        else:
            raise ValueError(
                f"Unsupported variable '{variable}' for area_quadrilateral_d1d2_sin."
            )

        values = {"d1": d1, "d2": d2, "sin_alpha": sin_alpha, "S": S}
        return self._finalize(values, variable, answer)

    def calculate_area_rhombus(self, data: Dict[str, Any]) -> Dict[str, float]:
        variable, params, _ = self._normalize_input(data, default_variable="d1")
        d1 = params.get("d1")
        d2 = params.get("d2")
        S = params.get("S")

        if variable == "S":
            d1_val = self._require(d1, "d1")
            d2_val = self._require(d2, "d2")
            S = 0.5 * d1_val * d2_val
            answer = S
        elif variable == "d1":
            S_val = self._require(S, "S")
            d2_val = self._require(d2, "d2")
            d1 = (2.0 * S_val) / d2_val
            answer = d1
        elif variable == "d2":
            S_val = self._require(S, "S")
            d1_val = self._require(d1, "d1")
            d2 = (2.0 * S_val) / d1_val
            answer = d2
        else:
            raise ValueError(f"Unsupported variable '{variable}' for area_rhombus.")

        values = {"d1": d1, "d2": d2, "S": S}
        return self._finalize(values, variable, answer)

    def calculate_area_trapezoid(self, data: Dict[str, Any]) -> Dict[str, float]:
        variable, params, _ = self._normalize_input(data, default_variable="S")
        a = params.get("a")
        b = params.get("b")
        h = params.get("h")
        S = params.get("S")

        if variable == "S":
            a_val = self._require(a, "a")
            b_val = self._require(b, "b")
            h_val = self._require(h, "h")
            S = (a_val + b_val) / 2.0 * h_val
            answer = S
        elif variable == "a":
            S_val = self._require(S, "S")
            b_val = self._require(b, "b")
            h_val = self._require(h, "h")
            a = (2.0 * S_val) / h_val - b_val
            answer = a
        elif variable == "b":
            S_val = self._require(S, "S")
            a_val = self._require(a, "a")
            h_val = self._require(h, "h")
            b = (2.0 * S_val) / h_val - a_val
            answer = b
        elif variable == "h":
            S_val = self._require(S, "S")
            a_val = self._require(a, "a")
            b_val = self._require(b, "b")
            h = (2.0 * S_val) / (a_val + b_val)
            answer = h
        else:
            raise ValueError(f"Unsupported variable '{variable}' for area_trapezoid.")

        values = {"a": a, "b": b, "h": h, "S": S}
        return self._finalize(values, variable, answer)

    def calculate_area_triangle(self, data: Dict[str, Any]) -> Dict[str, float]:
        variable, params, _ = self._normalize_input(data, default_variable="S")
        a = params.get("a")
        b = params.get("b")
        c = params.get("c")
        h = params.get("h")
        sin_alpha = params.get("sin_alpha")
        P = params.get("P")
        r = params.get("r")
        S = params.get("S")

        def area_from_params() -> float:
            if a is not None and h is not None:
                return 0.5 * a * h
            if b is not None and c is not None and sin_alpha is not None:
                return 0.5 * b * c * sin_alpha
            if P is not None and r is not None:
                return 0.5 * P * r
            raise ValueError("Insufficient data to determine triangle area.")

        if variable == "S":
            S = area_from_params()
            answer = S
        elif variable == "a":
            S_val = self._require(S, "S")
            h_val = self._require(h, "h")
            a = (2.0 * S_val) / h_val
            answer = a
        elif variable == "h":
            S_val = self._require(S, "S")
            a_val = self._require(a, "a")
            h = (2.0 * S_val) / a_val
            answer = h
        elif variable == "sin_alpha":
            S_val = self._require(S, "S")
            b_val = self._require(b, "b")
            c_val = self._require(c, "c")
            sin_alpha = (2.0 * S_val) / (b_val * c_val)
            answer = sin_alpha
        elif variable == "P":
            S_val = self._require(S, "S")
            r_val = self._require(r, "r")
            P = 2.0 * S_val / r_val
            answer = P
        elif variable == "r":
            S_val = self._require(S, "S")
            P_val = self._require(P, "P")
            r = 2.0 * S_val / P_val
            answer = r
        else:
            raise ValueError(f"Unsupported variable '{variable}' for area_triangle.")

        values = {"a": a, "b": b, "c": c, "h": h, "sin_alpha": sin_alpha, "P": P, "r": r, "S": S}
        return self._finalize(values, variable, answer)

    def calculate_bisector_length(self, data: Dict[str, Any]) -> Dict[str, float]:
        variable, params, _ = self._normalize_input(data, default_variable="l_a")
        if variable != "l_a":
            raise ValueError("Only 'l_a' can be calculated for bisector_length.")

        a = self._require(params.get("a"), "a")
        b = self._require(params.get("b"), "b")
        c = self._require(params.get("c"), "c")
        l_a = sqrt(b * c * (1.0 - (a / (b + c)) ** 2))

        values = {"a": a, "b": b, "c": c, "l_a": l_a}
        return self._finalize(values, variable, l_a)

    def calculate_capacitor_energy(self, data: Dict[str, Any]) -> Dict[str, float]:
        variable, params, _ = self._normalize_input(data, default_variable="W")
        C = params.get("C")
        U = params.get("U")
        q = params.get("q")
        W = params.get("W")

        def ensure_C() -> float:
            return self._require(C, "C")

        if variable == "W":
            C_val = ensure_C()
            if U is not None:
                W = 0.5 * C_val * (U ** 2)
            elif q is not None:
                W = (q ** 2) / (2.0 * C_val)
            else:
                raise ValueError("Either 'U' or 'q' is required to compute 'W'.")
            answer = W
        elif variable == "C":
            if U is not None and U != 0:
                W_val = self._require(W, "W")
                C = 2.0 * W_val / (U ** 2)
            elif q is not None:
                W_val = self._require(W, "W")
                C = (q ** 2) / (2.0 * W_val)
            elif U is not None and q is not None:
                C = q / U
            else:
                raise ValueError("Insufficient data to compute 'C'.")
            answer = C
        elif variable == "U":
            C_val = ensure_C()
            if W is not None:
                if W < 0:
                    raise ValueError("Energy cannot be negative when computing 'U'.")
                U = sqrt(2.0 * W / C_val)
            elif q is not None:
                U = q / C_val
            else:
                raise ValueError("Either 'W' or 'q' is required to compute 'U'.")
            answer = U
        elif variable == "q":
            C_val = ensure_C()
            if U is not None:
                q = C_val * U
            elif W is not None:
                if W < 0:
                    raise ValueError("Energy cannot be negative when computing 'q'.")
                q = sqrt(2.0 * C_val * W)
            else:
                raise ValueError("Either 'U' or 'W' is required to compute 'q'.")
            answer = q
        else:
            raise ValueError(f"Unsupported variable '{variable}' for capacitor_energy.")

        values = {"C": C, "U": U, "q": q, "W": W}
        return self._finalize(values, variable, answer)

    def calculate_centripetal_acceleration(self, data: Dict[str, Any]) -> Dict[str, float]:
        variable, params, _ = self._normalize_input(data, default_variable="a")
        a = params.get("a")
        omega = params.get("omega")
        R = params.get("R")

        if variable == "a":
            omega_val = self._require(omega, "omega")
            R_val = self._require(R, "R")
            a = (omega_val ** 2) * R_val
            answer = a
        elif variable == "omega":
            a_val = self._require(a, "a")
            R_val = self._require(R, "R")
            omega = sqrt(a_val / R_val)
            answer = omega
        elif variable == "R":
            a_val = self._require(a, "a")
            omega_val = self._require(omega, "omega")
            R = a_val / (omega_val ** 2)
            answer = R
        else:
            raise ValueError(f"Unsupported variable '{variable}' for centripetal_acceleration.")

        values = {"a": a, "omega": omega, "R": R}
        return self._finalize(values, variable, answer)

    def calculate_circumference_length(self, data: Dict[str, Any]) -> Dict[str, float]:
        variable, params, constants = self._normalize_input(data, default_variable="L")
        L = params.get("L")
        R = params.get("R")
        pi_value = self._get_constant(constants, "pi", pi)

        if variable == "L":
            R_val = self._require(R, "R")
            L = 2.0 * pi_value * R_val
            answer = L
        elif variable == "R":
            L_val = self._require(L, "L")
            R = L_val / (2.0 * pi_value)
            answer = R
        elif variable == "pi":
            L_val = self._require(L, "L")
            R_val = self._require(R, "R")
            pi_value = L_val / (2.0 * R_val)
            answer = pi_value
        else:
            raise ValueError(f"Unsupported variable '{variable}' for circumference_length.")

        values = {"L": L, "R": R, "pi": pi_value}
        return self._finalize(values, variable, answer)

    def calculate_circumscribed_circle_radius(self, data: Dict[str, Any]) -> Dict[str, float]:
        variable, params, _ = self._normalize_input(data, default_variable="R")
        a = params.get("a")
        b = params.get("b")
        c = params.get("c")
        sin_alpha = params.get("sin_alpha")
        R = params.get("R")
        S = params.get("S")

        if variable == "S":
            a_val = self._require(a, "a")
            b_val = self._require(b, "b")
            c_val = self._require(c, "c")
            R_val = self._require(R, "R")
            S = (a_val * b_val * c_val) / (4.0 * R_val)
            answer = S
        elif variable == "R":
            if a is not None and sin_alpha is not None:
                R = a / (2.0 * sin_alpha)
            else:
                a_val = self._require(a, "a")
                b_val = self._require(b, "b")
                c_val = self._require(c, "c")
                S_val = self._require(S, "S")
                R = (a_val * b_val * c_val) / (4.0 * S_val)
            answer = R
        elif variable in {"a", "b", "c"}:
            S_val = self._require(S, "S")
            R_val = self._require(R, "R")
            other = [name for name in ("a", "b", "c") if name != variable]
            first = self._require(params.get(other[0]), other[0])
            second = self._require(params.get(other[1]), other[1])
            value = (4.0 * S_val * R_val) / (first * second)
            if variable == "a":
                a = value
            elif variable == "b":
                b = value
            else:
                c = value
            answer = value
        elif variable == "sin_alpha":
            a_val = self._require(a, "a")
            R_val = self._require(R, "R")
            sin_alpha = a_val / (2.0 * R_val)
            answer = sin_alpha
        else:
            raise ValueError(
                f"Unsupported variable '{variable}' for circumscribed_circle_radius."
            )

        values = {"a": a, "b": b, "c": c, "sin_alpha": sin_alpha, "R": R, "S": S}
        return self._finalize(values, variable, answer)

    def calculate_coulomb_law(self, data: Dict[str, Any]) -> Dict[str, float]:
        variable, params, _ = self._normalize_input(data, default_variable="F")
        F = params.get("F")
        q1 = params.get("q1")
        q2 = params.get("q2")
        r = params.get("r")
        k_const = params.get("k")

        if variable == "F":
            k_val = self._require(k_const, "k")
            q1_val = self._require(q1, "q1")
            q2_val = self._require(q2, "q2")
            r_val = self._require(r, "r")
            F = k_val * q1_val * q2_val / (r_val ** 2)
            answer = F
        elif variable == "q1":
            F_val = self._require(F, "F")
            k_val = self._require(k_const, "k")
            q2_val = self._require(q2, "q2")
            r_val = self._require(r, "r")
            q1 = F_val * (r_val ** 2) / (k_val * q2_val)
            answer = q1
        elif variable == "q2":
            F_val = self._require(F, "F")
            k_val = self._require(k_const, "k")
            q1_val = self._require(q1, "q1")
            r_val = self._require(r, "r")
            q2 = F_val * (r_val ** 2) / (k_val * q1_val)
            answer = q2
        elif variable == "r":
            F_val = self._require(F, "F")
            k_val = self._require(k_const, "k")
            q1_val = self._require(q1, "q1")
            q2_val = self._require(q2, "q2")
            r = sqrt(k_val * q1_val * q2_val / F_val)
            answer = r
        elif variable == "k":
            F_val = self._require(F, "F")
            q1_val = self._require(q1, "q1")
            q2_val = self._require(q2, "q2")
            r_val = self._require(r, "r")
            k_const = F_val * (r_val ** 2) / (q1_val * q2_val)
            answer = k_const
        else:
            raise ValueError(f"Unsupported variable '{variable}' for coulomb_law.")

        values = {"F": F, "q1": q1, "q2": q2, "r": r, "k": k_const}
        return self._finalize(values, variable, answer)

    def calculate_gas_law(self, data: Dict[str, Any]) -> Dict[str, float]:
        variable, params, constants = self._normalize_input(data, default_variable="P")
        variable, answer, values = self._solve_gas_law(variable, params, constants)
        if values.get("nu") is not None:
            values["n"] = values["nu"]
        return self._finalize(values, variable, answer)

    def calculate_height_pyramid(self, data: Dict[str, Any]) -> Dict[str, float]:
        variable, params, _ = self._normalize_input(data, default_variable="h")
        V = params.get("V")
        S_base = params.get("S_base")
        h = params.get("h")

        if variable == "V":
            S_val = self._require(S_base, "S_base")
            h_val = self._require(h, "h")
            V = S_val * h_val / 3.0
            answer = V
        elif variable == "S_base":
            V_val = self._require(V, "V")
            h_val = self._require(h, "h")
            S_base = 3.0 * V_val / h_val
            answer = S_base
        elif variable == "h":
            V_val = self._require(V, "V")
            S_val = self._require(S_base, "S_base")
            h = 3.0 * V_val / S_val
            answer = h
        else:
            raise ValueError(f"Unsupported variable '{variable}' for height_pyramid.")

        values = {"V": V, "S_base": S_base, "h": h}
        return self._finalize(values, variable, answer)

    def calculate_inscribed_circle_radius(self, data: Dict[str, Any]) -> Dict[str, float]:
        variable, params, _ = self._normalize_input(data, default_variable="r")
        r = params.get("r")
        S = params.get("S")
        P = params.get("P")
        a = params.get("a")
        b = params.get("b")
        c = params.get("c")

        if variable == "r":
            if S is not None and P is not None:
                r = 2.0 * S / P
            elif a is not None and b is not None and c is not None:
                area = self._heron_area(a, b, c)
                perimeter = a + b + c
                r = 2.0 * area / perimeter
            else:
                raise ValueError("Insufficient data to compute inscribed circle radius.")
            answer = r
        elif variable == "S":
            if P is not None and r is not None:
                S = 0.5 * P * r
            elif a is not None and b is not None and c is not None:
                S = self._heron_area(a, b, c)
            else:
                raise ValueError("Insufficient data to compute triangle area.")
            answer = S
        elif variable == "P":
            S_val = self._require(S, "S")
            r_val = self._require(r, "r")
            P = 2.0 * S_val / r_val
            answer = P
        else:
            raise ValueError(f"Unsupported variable '{variable}' for inscribed_circle_radius.")

        values = {"r": r, "S": S, "P": P, "a": a, "b": b, "c": c}
        return self._finalize(values, variable, answer)

    def calculate_joule_lenz(self, data: Dict[str, Any]) -> Dict[str, float]:
        variable, params, _ = self._normalize_input(data, default_variable="Q")
        Q = params.get("Q")
        I = params.get("I")
        R = params.get("R")
        t = params.get("t")

        if variable == "Q":
            I_val = self._require(I, "I")
            R_val = self._require(R, "R")
            t_val = self._require(t, "t")
            Q = (I_val ** 2) * R_val * t_val
            answer = Q
        elif variable == "I":
            Q_val = self._require(Q, "Q")
            R_val = self._require(R, "R")
            t_val = self._require(t, "t")
            I = sqrt(Q_val / (R_val * t_val))
            answer = I
        elif variable == "R":
            Q_val = self._require(Q, "Q")
            I_val = self._require(I, "I")
            t_val = self._require(t, "t")
            R = Q_val / (I_val ** 2 * t_val)
            answer = R
        elif variable == "t":
            Q_val = self._require(Q, "Q")
            I_val = self._require(I, "I")
            R_val = self._require(R, "R")
            t = Q_val / (I_val ** 2 * R_val)
            answer = t
        else:
            raise ValueError(f"Unsupported variable '{variable}' for joule_lenz.")

        values = {"Q": Q, "I": I, "R": R, "t": t}
        return self._finalize(values, variable, answer)

    def calculate_kinetic_energy(self, data: Dict[str, Any]) -> Dict[str, float]:
        variable, params, _ = self._normalize_input(data, default_variable="E")
        E = params.get("E")
        m = params.get("m")
        v = params.get("v")

        if variable == "E":
            m_val = self._require(m, "m")
            v_val = self._require(v, "v")
            E = m_val * (v_val ** 2) / 2.0
            answer = E
        elif variable == "m":
            E_val = self._require(E, "E")
            v_val = self._require(v, "v")
            if v_val == 0:
                raise ValueError("Velocity must be non-zero to compute mass from kinetic energy.")
            m = 2.0 * E_val / (v_val ** 2)
            answer = m
        elif variable == "v":
            E_val = self._require(E, "E")
            m_val = self._require(m, "m")
            value = 2.0 * E_val / m_val
            if value < 0:
                raise ValueError("Computed squared velocity is negative.")
            v = sqrt(value)
            answer = v
        else:
            raise ValueError(f"Unsupported variable '{variable}' for kinetic_energy.")

        values = {"E": E, "m": m, "v": v}
        return self._finalize(values, variable, answer)

    def calculate_lightning_distance(self, data: Dict[str, Any]) -> Dict[str, float]:
        variable, params, constants = self._normalize_input(data, default_variable="s")
        t = params.get("t")
        s_km = params.get("s") or params.get("s_km")
        speed = self._get_constant(constants, "speed", 330.0)

        if variable == "s":
            t_val = self._require(t, "t")
            s_km = speed * t_val / 1000.0
            answer = s_km
        elif variable == "t":
            s_val = self._require(s_km, "s")
            t = s_val * 1000.0 / speed
            answer = t
        elif variable == "speed":
            t_val = self._require(t, "t")
            s_val = self._require(s_km, "s")
            speed = s_val * 1000.0 / t_val
            answer = speed
        else:
            raise ValueError(f"Unsupported variable '{variable}' for lightning_distance.")

        values = {"t": t, "s": s_km, "s_km": s_km, "speed": speed}
        return self._finalize(values, variable if variable != "s_km" else "s", answer)

    def calculate_mechanical_energy(self, data: Dict[str, Any]) -> Dict[str, float]:
        variable, params, constants = self._normalize_input(data, default_variable="E")
        E = params.get("E")
        m = params.get("m")
        v = params.get("v")
        h = params.get("h")
        g = self._get_constant(constants, "g", 10.0)

        if variable == "E":
            m_val = self._require(m, "m")
            v_val = self._require(v, "v")
            h_val = self._require(h, "h")
            E = m_val * (v_val ** 2) / 2.0 + m_val * g * h_val
            answer = E
        elif variable == "m":
            E_val = self._require(E, "E")
            v_val = self._require(v, "v")
            h_val = self._require(h, "h")
            denominator = (v_val ** 2) / 2.0 + g * h_val
            if denominator == 0:
                raise ValueError("Denominator becomes zero while solving for 'm'.")
            m = E_val / denominator
            answer = m
        elif variable == "v":
            E_val = self._require(E, "E")
            m_val = self._require(m, "m")
            h_val = self._require(h, "h")
            value = 2.0 * (E_val / m_val - g * h_val)
            if value < 0:
                raise ValueError("Computed squared velocity is negative.")
            v = sqrt(value)
            answer = v
        elif variable == "h":
            E_val = self._require(E, "E")
            m_val = self._require(m, "m")
            v_val = self._require(v, "v")
            h = (E_val / m_val - (v_val ** 2) / 2.0) / g
            answer = h
        elif variable == "g":
            E_val = self._require(E, "E")
            m_val = self._require(m, "m")
            v_val = self._require(v, "v")
            h_val = self._require(h, "h")
            g = (E_val / m_val - (v_val ** 2) / 2.0) / h_val
            answer = g
        else:
            raise ValueError(f"Unsupported variable '{variable}' for mechanical_energy.")

        values = {"E": E, "m": m, "v": v, "h": h, "g": g}
        return self._finalize(values, variable, answer)

    def calculate_newton_gravity(self, data: Dict[str, Any]) -> Dict[str, float]:
        variable, params, constants = self._normalize_input(data, default_variable="F")
        F = params.get("F")
        m1 = params.get("m1")
        m2 = params.get("m2")
        r = params.get("r")
        G_const = params.get("G") or self._get_constant(constants, "G", 6.67e-11)

        if variable == "F":
            G_val = self._require(G_const, "G")
            m1_val = self._require(m1, "m1")
            m2_val = self._require(m2, "m2")
            r_val = self._require(r, "r")
            F = G_val * m1_val * m2_val / (r_val ** 2)
            answer = F
        elif variable == "m1":
            F_val = self._require(F, "F")
            G_val = self._require(G_const, "G")
            m2_val = self._require(m2, "m2")
            r_val = self._require(r, "r")
            m1 = F_val * (r_val ** 2) / (G_val * m2_val)
            answer = m1
        elif variable == "m2":
            F_val = self._require(F, "F")
            G_val = self._require(G_const, "G")
            m1_val = self._require(m1, "m1")
            r_val = self._require(r, "r")
            m2 = F_val * (r_val ** 2) / (G_val * m1_val)
            answer = m2
        elif variable == "r":
            F_val = self._require(F, "F")
            G_val = self._require(G_const, "G")
            m1_val = self._require(m1, "m1")
            m2_val = self._require(m2, "m2")
            r = sqrt(G_val * m1_val * m2_val / F_val)
            answer = r
        elif variable == "G":
            F_val = self._require(F, "F")
            m1_val = self._require(m1, "m1")
            m2_val = self._require(m2, "m2")
            r_val = self._require(r, "r")
            G_const = F_val * (r_val ** 2) / (m1_val * m2_val)
            answer = G_const
        else:
            raise ValueError(f"Unsupported variable '{variable}' for newton_gravity.")

        values = {"F": F, "m1": m1, "m2": m2, "r": r, "G": G_const}
        return self._finalize(values, variable, answer)

    def calculate_ohm_power(self, data: Dict[str, Any]) -> Dict[str, float]:
        variable, params, _ = self._normalize_input(data, default_variable="P")
        P = params.get("P")
        I = params.get("I")
        R = params.get("R")

        if variable == "P":
            I_val = self._require(I, "I")
            R_val = self._require(R, "R")
            P = (I_val ** 2) * R_val
            answer = P
        elif variable == "I":
            P_val = self._require(P, "P")
            R_val = self._require(R, "R")
            I = sqrt(P_val / R_val)
            answer = I
        elif variable == "R":
            P_val = self._require(P, "P")
            I_val = self._require(I, "I")
            R = P_val / (I_val ** 2)
            answer = R
        else:
            raise ValueError(f"Unsupported variable '{variable}' for ohm_power.")

        values = {"P": P, "I": I, "R": R}
        return self._finalize(values, variable, answer)

    def calculate_pendulum_period(self, data: Dict[str, Any]) -> Dict[str, float]:
        variable, params, constants = self._normalize_input(data, default_variable="T")
        T = params.get("T")
        l = params.get("l")
        g = self._get_constant(constants, "g", 10.0)
        pi_value = self._get_constant(constants, "pi", pi)

        if variable == "T":
            l_val = self._require(l, "l")
            if l_val < 0:
                raise ValueError("Length must be non-negative.")
            T = 2.0 * pi_value * sqrt(l_val / g)
            answer = T
        elif variable == "l":
            T_val = self._require(T, "T")
            if T_val == 0:
                raise ValueError("Period must be non-zero to compute length.")
            l = g * (T_val / (2.0 * pi_value)) ** 2
            answer = l
        elif variable == "g":
            T_val = self._require(T, "T")
            l_val = self._require(l, "l")
            if T_val == 0:
                raise ValueError("Period must be non-zero to compute gravity.")
            g = (4.0 * pi_value ** 2 * l_val) / (T_val ** 2)
            answer = g
        else:
            raise ValueError(f"Unsupported variable '{variable}' for pendulum_period.")

        values = {"T": T, "l": l, "g": g}
        return self._finalize(values, variable, answer)

    def calculate_polygon_angles_sum(self, data: Dict[str, Any]) -> Dict[str, float]:
        variable, params, _ = self._normalize_input(data, default_variable="Sigma")
        Sigma = params.get("Sigma") or params.get("sum_angles")
        n = params.get("n")

        if variable in {"Sigma", "sum_angles"}:
            n_val = self._require(n, "n")
            Sigma = (n_val - 2.0) * 180.0
            answer = Sigma
            variable = "Sigma"
        elif variable == "n":
            sum_val = self._require(Sigma, "Sigma")
            n = sum_val / 180.0 + 2.0
            answer = n
        else:
            raise ValueError(f"Unsupported variable '{variable}' for polygon_angles_sum.")

        values = {"Sigma": Sigma, "sum_angles": Sigma, "n": n}
        return self._finalize(values, variable, answer)

    def calculate_potential_energy(self, data: Dict[str, Any]) -> Dict[str, float]:
        variable, params, constants = self._normalize_input(data, default_variable="E")
        E = params.get("E")
        m = params.get("m")
        h = params.get("h")
        g = self._get_constant(constants, "g", 10.0)

        if variable == "E":
            m_val = self._require(m, "m")
            h_val = self._require(h, "h")
            E = m_val * g * h_val
            answer = E
        elif variable == "m":
            E_val = self._require(E, "E")
            h_val = self._require(h, "h")
            m = E_val / (g * h_val)
            answer = m
        elif variable == "h":
            E_val = self._require(E, "E")
            m_val = self._require(m, "m")
            h = E_val / (m_val * g)
            answer = h
        elif variable == "g":
            E_val = self._require(E, "E")
            m_val = self._require(m, "m")
            h_val = self._require(h, "h")
            g = E_val / (m_val * h_val)
            answer = g
        else:
            raise ValueError(f"Unsupported variable '{variable}' for potential_energy.")

        values = {"E": E, "m": m, "h": h, "g": g}
        return self._finalize(values, variable, answer)

    def calculate_step_length_distance(self, data: Dict[str, Any]) -> Dict[str, float]:
        variable, params, _ = self._normalize_input(data, default_variable="s")
        steps = params.get("n") or params.get("steps")
        l_cm = params.get("l_cm")
        l_m = params.get("l_m")
        distance = params.get("s") or params.get("dist_km")

        if variable == "s":
            steps_val = self._require(steps, "n")
            if l_cm is not None:
                distance = steps_val * l_cm / 100000.0
            elif l_m is not None:
                distance = steps_val * l_m / 1000.0
            else:
                raise ValueError("Either 'l_cm' or 'l_m' is required to compute distance.")
            answer = distance
        elif variable in {"n", "steps"}:
            distance_val = self._require(distance, "s")
            if l_cm is not None:
                steps = distance_val * 100000.0 / l_cm
            elif l_m is not None:
                steps = distance_val * 1000.0 / l_m
            else:
                raise ValueError("Either 'l_cm' or 'l_m' is required to compute steps.")
            answer = steps
            variable = "n"
        elif variable == "l_cm":
            distance_val = self._require(distance, "s")
            steps_val = self._require(steps, "n")
            l_cm = distance_val * 100000.0 / steps_val
            answer = l_cm
        elif variable == "l_m":
            distance_val = self._require(distance, "s")
            steps_val = self._require(steps, "n")
            l_m = distance_val * 1000.0 / steps_val
            answer = l_m
        else:
            raise ValueError(f"Unsupported variable '{variable}' for step_length_distance.")

        values = {"n": steps, "steps": steps, "l_cm": l_cm, "l_m": l_m, "s": distance, "dist_km": distance}
        return self._finalize(values, variable, answer)

    def calculate_taxi_cost(self, data: Dict[str, Any]) -> Dict[str, float]:
        variable, params, _ = self._normalize_input(data, default_variable="C")
        C_value = params.get("C")
        k = params.get("k")
        t = params.get("t")
        c0 = params.get("c0")
        c1 = params.get("c1")
        free_minutes = params.get("free_minutes")

        if variable == "C":
            t_val = self._require(t, "t")
            if k is not None:
                C_value = k * t_val
            elif c0 is not None and c1 is not None and free_minutes is not None:
                C_value = c0 + c1 * max(0.0, t_val - free_minutes)
            else:
                raise ValueError("Insufficient data to compute taxi cost.")
            answer = C_value
        else:
            raise ValueError(f"Unsupported variable '{variable}' for taxi_cost.")

        values = {"C": C_value, "k": k, "t": t, "c0": c0, "c1": c1, "free_minutes": free_minutes}
        return self._finalize(values, variable, answer)

    def calculate_temperature_conversion(self, data: Dict[str, Any]) -> Dict[str, float]:
        variable, params, _ = self._normalize_input(data, default_variable="F")
        C = params.get("C")
        F_value = params.get("F")

        if variable == "F":
            C_val = self._require(C, "C")
            F_value = 1.8 * C_val + 32.0
            answer = F_value
        elif variable == "C":
            F_val = self._require(F_value, "F")
            C = (F_val - 32.0) / 1.8
            answer = C
        else:
            raise ValueError(f"Unsupported variable '{variable}' for temperature_conversion.")

        values = {"C": C, "F": F_value}
        return self._finalize(values, variable, answer)

    def calculate_well_cost(self, data: Dict[str, Any]) -> Dict[str, float]:
        variable, params, _ = self._normalize_input(data, default_variable="C")
        C_value = params.get("C")
        A = params.get("A")
        B = params.get("B")
        n = params.get("n")

        if variable == "C":
            A_val = self._require(A, "A")
            B_val = self._require(B, "B")
            n_val = self._require(n, "n")
            C_value = A_val + B_val * n_val
            answer = C_value
        else:
            raise ValueError(f"Unsupported variable '{variable}' for well_cost.")

        values = {"C": C_value, "A": A, "B": B, "n": n}
        return self._finalize(values, variable, answer)

    def calculate_work_of_current(self, data: Dict[str, Any]) -> Dict[str, float]:
        variable, params, _ = self._normalize_input(data, default_variable="A")
        A = params.get("A")
        U = params.get("U")
        t = params.get("t")
        R = params.get("R")

        if variable == "A":
            U_val = self._require(U, "U")
            t_val = self._require(t, "t")
            R_val = self._require(R, "R")
            A = (U_val ** 2) * t_val / R_val
            answer = A
        elif variable == "U":
            A_val = self._require(A, "A")
            t_val = self._require(t, "t")
            R_val = self._require(R, "R")
            U = sqrt(A_val * R_val / t_val)
            answer = U
        elif variable == "t":
            A_val = self._require(A, "A")
            U_val = self._require(U, "U")
            R_val = self._require(R, "R")
            t = A_val * R_val / (U_val ** 2)
            answer = t
        elif variable == "R":
            A_val = self._require(A, "A")
            U_val = self._require(U, "U")
            t_val = self._require(t, "t")
            R = (U_val ** 2) * t_val / A_val
            answer = R
        else:
            raise ValueError(f"Unsupported variable '{variable}' for work_of_current.")

        values = {"A": A, "U": U, "t": t, "R": R}
        return self._finalize(values, variable, answer)

    def calculate_gas_law_find_P(self, data: Dict[str, Any]) -> Dict[str, float]:
        payload = self._wrap_payload('P', data)
        return self.calculate_gas_law(payload)

    def calculate_gas_law_find_T(self, data: Dict[str, Any]) -> Dict[str, float]:
        payload = self._wrap_payload('T', data)
        return self.calculate_gas_law(payload)

    def calculate_gas_law_find_V(self, data: Dict[str, Any]) -> Dict[str, float]:
        payload = self._wrap_payload('V', data)
        return self.calculate_gas_law(payload)

    def calculate_gas_law_find_n(self, data: Dict[str, Any]) -> Dict[str, float]:
        payload = self._wrap_payload('nu', data)
        result = self.calculate_gas_law(payload)
        result['n'] = result.get('nu')
        return result

    def calculate_gravity_law(self, data: Dict[str, Any]) -> Dict[str, float]:
        payload = self._wrap_payload('F', data)
        result = self.calculate_newton_gravity(payload)
        return result

    def calculate_joul_lenz_law(self, data: Dict[str, Any]) -> Dict[str, float]:
        payload = self._wrap_payload('Q', data)
        return self.calculate_joule_lenz(payload)

    def calculate_electric_power(self, data: Dict[str, Any]) -> Dict[str, float]:
        payload = self._wrap_payload('P', data)
        return self.calculate_ohm_power(payload)

    def calculate_length_circle(self, data: Dict[str, Any]) -> Dict[str, float]:
        payload = self._wrap_payload('L', data)
        result = self.calculate_circumference_length(payload)
        if 'L' in result:
            result.setdefault('length', result['L'])
        return result

    def calculate_triangle_area_circumradius(self, data: Dict[str, Any]) -> Dict[str, float]:
        payload = self._wrap_payload('R', data)
        return self.calculate_circumscribed_circle_radius(payload)

    def calculate_steps_distance(self, data: Dict[str, Any]) -> Dict[str, float]:
        payload = self._wrap_payload('s', data)
        result = self.calculate_step_length_distance(payload)
        result.setdefault('dist_km', result.get('s'))
        return result
