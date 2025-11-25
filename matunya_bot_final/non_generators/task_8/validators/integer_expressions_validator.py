"""
Валидатор для integer_expressions (задание 8, подтип integer_expressions).

Обрабатывает строки формата:
    solution_pattern | expression | a=10, b=15

Поддерживает три паттерна:
    - alg_power_fraction
    - alg_radical_power
    - alg_radical_fraction
"""

import re
from fractions import Fraction
from typing import Dict, Any, Optional, Tuple, List


SUPERSCRIPT_MAP = {
    "⁰": "0",
    "¹": "1",
    "²": "2",
    "³": "3",
    "⁴": "4",
    "⁵": "5",
    "⁶": "6",
    "⁷": "7",
    "⁸": "8",
    "⁹": "9",
    "⁻": "-",
}


def normalize_superscripts(expr: str) -> str:
    """
    Нормализует Unicode-степени (a³, a⁻²) в формат a^3, a^-2.
    """
    result = []
    for idx, ch in enumerate(expr):
        if ch in SUPERSCRIPT_MAP:
            prev = expr[idx - 1] if idx > 0 else ""
            if prev.isalpha() or prev == ")":
                result.append("^")
            result.append(SUPERSCRIPT_MAP[ch])
        else:
            result.append(ch)
    return "".join(result)


# ============================================================================
# Главная функция-валидатор
# ============================================================================

def validate(raw_line: str) -> Optional[Dict[str, Any]]:
    parsed_data = parse_raw_line(raw_line)
    if parsed_data is None:
        return None

    # Теперь мы получаем еще и variables_display
    solution_pattern, expression, variables, variables_display = parsed_data

    # Роутер по solution_pattern
    if solution_pattern == "alg_power_fraction":
        return _validate_alg_power_fraction(expression, variables, variables_display)
    elif solution_pattern == "alg_radical_power":
        return _validate_alg_radical_power(expression, variables, variables_display)
    elif solution_pattern == "alg_radical_fraction":
        return _validate_alg_radical_fraction(expression, variables, variables_display)
    else:
        return None


# ============================================================================
# Парсинг и AST
# ============================================================================

def parse_raw_line(raw_line: str) -> Optional[Tuple[str, str, Dict[str, float], Dict[str, str]]]:
    """
    Возвращает: (pattern, expression, variables_float, variables_display)
    """
    parts = raw_line.split("|")
    if len(parts) != 3:
        return None

    solution_pattern = parts[0].strip()
    expression = parts[1].strip()
    variables_str = parts[2].strip()

    valid_patterns = {
        "alg_power_fraction",
        "alg_radical_power",
        "alg_radical_fraction"
    }
    if solution_pattern not in valid_patterns:
        return None

    variables: Dict[str, float] = {}
    variables_display: Dict[str, str] = {} # Словарь для хранения "красивых" строк

    if not variables_str:
        return (solution_pattern, expression, variables, variables_display)

    var_parts = [part.strip() for part in variables_str.split(",")]

    # Паттерны: a = 3, a = -3, a = 0.4
    num_pattern = re.compile(r'^([a-zA-Z])\s*=\s*(-?\d+(?:\.\d+)?)$')
    # Паттерн: b = √2
    sqrt_pattern = re.compile(r'^([a-zA-Z])\s*=\s*√\s*(-?\d+(?:\.\d+)?)$')

    for var_part in var_parts:
        # 1. Обычное число
        m = num_pattern.match(var_part)
        if m:
            var_name = m.group(1)
            value_str = m.group(2)
            variables[var_name] = float(value_str)
            variables_display[var_name] = value_str # "5", "0.4"
            continue

        # 2. Корень
        m = sqrt_pattern.match(var_part)
        if m:
            var_name = m.group(1)
            radicand_str = m.group(2)
            try:
                radicand = float(radicand_str)
                if radicand < 0: return None
                variables[var_name] = radicand ** 0.5
                variables_display[var_name] = f"√{radicand_str}" # "√2", "√5"
            except ValueError:
                return None
            continue

        return None

    return (solution_pattern, expression, variables, variables_display)


def _tokenize(expression: str) -> Optional[List[Dict[str, str]]]:
    tokens = []
    i = 0
    length = len(expression)

    while i < length:
        char = expression[i]
        if char.isspace():
            i += 1
            continue
        if char.isalpha():
            tokens.append({"type": "VAR", "value": char})
            i += 1
            continue
        if char.isdigit() or (char == '-' and i + 1 < length and expression[i + 1].isdigit()):
            num_str = char
            i += 1
            while i < length and expression[i].isdigit():
                num_str += expression[i]
                i += 1
            tokens.append({"type": "INT", "value": num_str})
            continue
        if char == '-':
            tokens.append({"type": "MINUS", "value": "-"})
            i += 1
            continue
        if char == '^':
            tokens.append({"type": "POW", "value": "^"})
            i += 1
            continue
        if char in ('·', '*', '/'):
            tokens.append({"type": "OP", "value": char})
            i += 1
            continue
        if char == '(':
            tokens.append({"type": "LPAREN", "value": "("})
            i += 1
            continue
        if char == ')':
            tokens.append({"type": "RPAREN", "value": ")"})
            i += 1
            continue
        if char == '√':
            tokens.append({"type": "SQRT", "value": "√"})
            i += 1
            continue
        return None

    return tokens


class _Parser:
    def __init__(self, tokens: List[Dict[str, str]]):
        self.tokens = tokens
        self.pos = 0

    def current(self) -> Optional[Dict[str, str]]:
        if self.pos >= len(self.tokens): return None
        return self.tokens[self.pos]

    def advance(self):
        self.pos += 1

    def parse(self) -> Optional[Dict[str, Any]]:
        return self._parse_expression()

    def _parse_expression(self) -> Optional[Dict[str, Any]]:
        left = self._parse_product()
        if left is None: return None
        while self.current() and self.current()["type"] == "OP" and self.current()["value"] == "/":
            self.advance()
            right = self._parse_product()
            if right is None: return None
            left = {"kind": "fraction", "numerator": left, "denominator": right}
        return left

    def _parse_product(self) -> Optional[Dict[str, Any]]:
        factors = []
        factor = self._parse_power()
        if factor is None: return None
        factors.append(factor)
        while self.current():
            if self.current()["type"] == "OP" and self.current()["value"] in ("·", "*"):
                self.advance()
                factor = self._parse_power()
                if factor is None: return None
                factors.append(factor)
            elif self.current()["type"] in ("VAR", "INT", "LPAREN", "SQRT", "MINUS"):
                factor = self._parse_power()
                if factor is None: return None
                factors.append(factor)
            else:
                break
        if len(factors) == 1: return factors[0]
        return {"kind": "product", "factors": factors}

    def _parse_power(self) -> Optional[Dict[str, Any]]:
        base = self._parse_atom()
        if base is None: return None
        while True:
            if self.current() and self.current()["type"] == "POW":
                self.advance()
                exp_node = self._parse_atom()
                if exp_node is None or exp_node["kind"] != "integer": return None
                base = {"kind": "power", "base": base, "exp": exp_node}
            else:
                break
        return base

    def _parse_atom(self) -> Optional[Dict[str, Any]]:
        if not self.current(): return None
        token = self.current()
        if token["type"] == "MINUS":
            self.advance()
            atom = self._parse_atom()
            if atom is None: return None
            return {"kind": "product", "factors": [{"kind": "integer", "value": -1}, atom]}
        if token["type"] == "VAR":
            self.advance()
            return {"kind": "variable", "name": token["value"]}
        if token["type"] == "INT":
            value = int(token["value"])
            self.advance()
            return {"kind": "integer", "value": value}
        if token["type"] == "LPAREN":
            self.advance()
            expr = self._parse_expression()
            if expr is None: return None
            if not self.current() or self.current()["type"] != "RPAREN": return None
            self.advance()
            return expr
        if token["type"] == "SQRT":
            self.advance()
            has_paren = False
            if self.current() and self.current()["type"] == "LPAREN":
                self.advance(); has_paren = True
            radicand = self._parse_expression()
            if radicand is None: return None
            if has_paren:
                if not self.current() or self.current()["type"] != "RPAREN": return None
                self.advance()
            return {"kind": "sqrt", "radicand": radicand}
        return None


def parse_expression(expression: str, solution_pattern: str) -> Optional[Any]:
    expression = normalize_superscripts(expression)
    tokens = _tokenize(expression)
    if tokens is None: return None
    parser = _Parser(tokens)
    ast = parser.parse()
    if parser.pos < len(tokens): return None
    return ast


def build_expression_tree(ast: Any, solution_pattern: str) -> Optional[Dict[str, Any]]:
    if ast is None or not isinstance(ast, dict) or "kind" not in ast: return None
    kind = ast["kind"]
    if kind == "integer": return {"type": "integer", "value": ast["value"]}
    if kind == "variable": return {"type": "variable", "name": ast["name"]}
    if kind == "power":
        base = build_expression_tree(ast["base"], solution_pattern)
        exp = build_expression_tree(ast["exp"], solution_pattern)
        if base is None or exp is None or exp.get("type") != "integer": return None
        return {"type": "power", "base": base, "exp": exp}
    if kind == "product":
        factors = [build_expression_tree(f, solution_pattern) for f in ast["factors"]]
        if any(f is None for f in factors): return None
        return {"type": "product", "factors": factors}
    if kind == "fraction":
        num = build_expression_tree(ast["numerator"], solution_pattern)
        den = build_expression_tree(ast["denominator"], solution_pattern)
        if num is None or den is None: return None
        return {"type": "fraction", "numerator": num, "denominator": den}
    if kind == "sqrt":
        rad = build_expression_tree(ast["radicand"], solution_pattern)
        if rad is None: return None
        return {"type": "sqrt", "radicand": rad}
    return None


# ============================================================================
# Вычисления (Robust Float-based)
# ============================================================================

def is_terminating_denominator(d: int) -> bool:
    d = abs(d)
    if d == 0: return False
    while d % 2 == 0: d //= 2
    while d % 5 == 0: d //= 5
    return d == 1

def _eval_node_float(node: Dict[str, Any], variables: Dict[str, float]) -> Optional[float]:
    if not isinstance(node, dict) or "type" not in node: return None
    node_type = node["type"]
    if node_type == "integer": return float(node["value"])
    if node_type == "variable":
        name = node["name"]
        return variables.get(name)
    if node_type == "power":
        base_val = _eval_node_float(node["base"], variables)
        exp_val = _eval_node_float(node["exp"], variables)
        if base_val is None or exp_val is None: return None
        try: return base_val ** int(round(exp_val))
        except: return None
    if node_type == "product":
        result = 1.0
        for factor in node["factors"]:
            val = _eval_node_float(factor, variables)
            if val is None: return None
            result *= val
        return result
    if node_type == "fraction":
        num = _eval_node_float(node["numerator"], variables)
        den = _eval_node_float(node["denominator"], variables)
        if num is None or den is None or abs(den) < 1e-15: return None
        try: return num / den
        except: return None
    if node_type == "sqrt":
        rad = _eval_node_float(node["radicand"], variables)
        if rad is None or rad < 0: return None
        try: return rad ** 0.5
        except: return None
    return None

def _fraction_to_decimal_string(frac: Fraction) -> str:
    num = frac.numerator
    den = frac.denominator
    if den == 1: return str(num)
    d = abs(den)
    c2 = c5 = 0
    while d % 2 == 0: d //= 2; c2 += 1
    while d % 5 == 0: d //= 5; c5 += 1
    k = max(c2, c5)
    scale_2 = k - c2; scale_5 = k - c5
    scaled_num = num * (2 ** scale_2) * (5 ** scale_5)
    s = str(abs(scaled_num))
    if k > 0:
        if len(s) <= k: s = "0" * (k - len(s) + 1) + s
        int_part = s[:-k]; frac_part = s[-k:]
        s = int_part + "," + frac_part
    if "," in s: s = s.rstrip("0").rstrip(",")
    sign = "-" if scaled_num < 0 else ""
    return sign + s

def compute_answer(expression_tree: Dict[str, Any], variables: Dict[str, float]) -> Optional[str]:
    value = _eval_node_float(expression_tree, variables)
    if value is None: return None

    try:
        frac = Fraction(value).limit_denominator(10**7)
    except (ValueError, OverflowError):
        return None

    if abs(float(frac) - value) > 1e-9:
        return None

    if not is_terminating_denominator(frac.denominator):
        return None

    return _fraction_to_decimal_string(frac)


# ============================================================================
# Вспомогательные функции (Анализ дерева)
# ============================================================================

def _find_all_nodes(tree: Dict[str, Any], type_name: str) -> List[Dict[str, Any]]:
    result = []
    if not isinstance(tree, dict) or "type" not in tree: return result
    if tree["type"] == type_name: result.append(tree)
    node_type = tree["type"]
    if node_type == "power":
        result.extend(_find_all_nodes(tree["base"], type_name))
        result.extend(_find_all_nodes(tree["exp"], type_name))
    elif node_type == "product":
        for factor in tree["factors"]: result.extend(_find_all_nodes(factor, type_name))
    elif node_type == "fraction":
        result.extend(_find_all_nodes(tree["numerator"], type_name))
        result.extend(_find_all_nodes(tree["denominator"], type_name))
    elif node_type == "sqrt":
        result.extend(_find_all_nodes(tree["radicand"], type_name))
    return result

def _extract_numeric_coeff(tree: Dict[str, Any]) -> List[int]:
    result = []
    if not isinstance(tree, dict) or "type" not in tree: return result
    if tree["type"] == "integer": result.append(tree["value"])
    node_type = tree["type"]
    if node_type == "power":
        result.extend(_extract_numeric_coeff(tree["base"]))
    elif node_type == "product":
        for factor in tree["factors"]: result.extend(_extract_numeric_coeff(factor))
    elif node_type == "fraction":
        result.extend(_extract_numeric_coeff(tree["numerator"]))
        result.extend(_extract_numeric_coeff(tree["denominator"]))
    elif node_type == "sqrt":
        result.extend(_extract_numeric_coeff(tree["radicand"]))
    return result

def _extract_variable_powers(tree: Dict[str, Any]) -> Dict[str, int]:
    result: Dict[str, int] = {}
    def add_power(var: str, power: int):
        result[var] = result.get(var, 0) + power

    def traverse(node: Dict[str, Any], multiplier: int = 1):
        if not isinstance(node, dict) or "type" not in node: return
        node_type = node["type"]
        if node_type == "variable":
            add_power(node["name"], multiplier)
        elif node_type == "power":
            exp_val = node["exp"]["value"]
            traverse(node["base"], multiplier * exp_val)
        elif node_type == "product":
            for factor in node["factors"]: traverse(factor, multiplier)
        elif node_type == "fraction":
            traverse(node["numerator"], multiplier)
            traverse(node["denominator"], -multiplier)
        elif node_type == "sqrt":
            traverse(node["radicand"], multiplier)

    traverse(tree)
    return result

def _has_sqrt_in_subtree(tree: Dict[str, Any]) -> bool:
    if not isinstance(tree, dict) or "type" not in tree: return False
    if tree["type"] == "sqrt": return True
    node_type = tree["type"]
    if node_type == "power": return _has_sqrt_in_subtree(tree["base"]) or _has_sqrt_in_subtree(tree["exp"])
    elif node_type == "product": return any(_has_sqrt_in_subtree(f) for f in tree["factors"])
    elif node_type == "fraction": return _has_sqrt_in_subtree(tree["numerator"]) or _has_sqrt_in_subtree(tree["denominator"])
    return False

def _count_sqrt_nodes(tree: Dict[str, Any]) -> int:
    count = 0
    if not isinstance(tree, dict) or "type" not in tree: return count
    if tree["type"] == "sqrt": count = 1
    node_type = tree["type"]
    if node_type == "sqrt": count += _count_sqrt_nodes(tree["radicand"])
    elif node_type == "power": count += _count_sqrt_nodes(tree["base"]) + _count_sqrt_nodes(tree["exp"])
    elif node_type == "product": count += sum(_count_sqrt_nodes(f) for f in tree["factors"])
    elif node_type == "fraction": count += _count_sqrt_nodes(tree["numerator"]) + _count_sqrt_nodes(tree["denominator"])
    return count

def _is_perfect_square_int(x: int) -> bool:
    if x < 0: return False
    if x == 0: return True
    root = int(x ** 0.5)
    return root * root == x


# ============================================================================
# ПРАВИЛА ВАЛИДАЦИИ
# ============================================================================

def _validate_alg_power_fraction_rules(expression_tree: Dict[str, Any], variables: Dict[str, float]) -> bool:
    if expression_tree["type"] != "fraction": return False
    if _has_sqrt_in_subtree(expression_tree["denominator"]): return False

    all_powers = _find_all_nodes(expression_tree, "power")
    for power_node in all_powers:
        if power_node["exp"]["type"] != "integer": return False

        base = power_node.get("base", {})
        if isinstance(base, dict) and base.get("type") == "power":
             if base["exp"].get("type") != "integer": return False

    answer = compute_answer(expression_tree, variables)
    if answer is None: return False
    return True


def _validate_alg_radical_power_rules(expression_tree: Dict[str, Any], variables: Dict[str, float]) -> bool:
    if expression_tree["type"] != "sqrt": return False
    radicand = expression_tree["radicand"]

    numeric_coeffs = _extract_numeric_coeff(radicand)
    positive_coeffs = [c for c in numeric_coeffs if c > 0]
    if positive_coeffs:
        has_perfect_square = any(_is_perfect_square_int(c) for c in positive_coeffs)
        if not has_perfect_square: return False

    var_powers = _extract_variable_powers(radicand)
    for var, power in var_powers.items():
        if power % 2 != 0:
            return False

    answer = compute_answer(expression_tree, variables)
    if answer is None: return False
    return True


def _validate_alg_radical_fraction_rules(expression_tree: Dict[str, Any], variables: Dict[str, float]) -> bool:
    if expression_tree["type"] != "fraction": return False
    numerator = expression_tree["numerator"]
    denominator = expression_tree["denominator"]
    if _count_sqrt_nodes(numerator) not in (1, 2): return False
    if denominator["type"] == "integer": return False

    answer = compute_answer(expression_tree, variables)
    if answer is None: return False
    return True


# ============================================================================
# Сборка
# ============================================================================

def format_json(solution_pattern, tree, vars, vars_disp, ans):
    return {
        "task_type": "8",
        "subtype": "integer_expressions",
        "solution_pattern": solution_pattern,
        "expression_tree": tree,
        "variables": vars,
        "variables_display": vars_disp, # Добавлено новое поле
        "answer": ans
    }

def _validate_alg_power_fraction(expression: str, variables: Dict[str, float], variables_display: Dict[str, str]) -> Optional[Dict[str, Any]]:
    ast = parse_expression(expression, "alg_power_fraction")
    tree = build_expression_tree(ast, "alg_power_fraction")
    if tree is None: return None
    if not _validate_alg_power_fraction_rules(tree, variables): return None
    answer = compute_answer(tree, variables)
    if answer is None: return None
    return format_json("alg_power_fraction", tree, variables, variables_display, answer)

def _validate_alg_radical_power(expression: str, variables: Dict[str, float], variables_display: Dict[str, str]) -> Optional[Dict[str, Any]]:
    ast = parse_expression(expression, "alg_radical_power")
    tree = build_expression_tree(ast, "alg_radical_power")
    if tree is None: return None
    if not _validate_alg_radical_power_rules(tree, variables): return None
    answer = compute_answer(tree, variables)
    if answer is None: return None
    return format_json("alg_radical_power", tree, variables, variables_display, answer)

def _validate_alg_radical_fraction(expression: str, variables: Dict[str, float], variables_display: Dict[str, str]) -> Optional[Dict[str, Any]]:
    ast = parse_expression(expression, "alg_radical_fraction")
    tree = build_expression_tree(ast, "alg_radical_fraction")
    if tree is None: return None
    if not _validate_alg_radical_fraction_rules(tree, variables): return None
    answer = compute_answer(tree, variables)
    if answer is None: return None
    return format_json("alg_radical_fraction", tree, variables, variables_display, answer)
