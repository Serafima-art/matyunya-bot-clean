"""
Валидатор для powers_and_roots (задание 8, подтип powers_and_roots).
Обрабатывает числовые выражения с корнями и степенями.
"""

import re
import math
from typing import Dict, Any, Optional, Tuple, List

# ============================================================================
# Константы и Хелперы
# ============================================================================

SUPERSCRIPT_MAP = {
    "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4",
    "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9",
    "⁻": "-",
}

def normalize_superscripts(expr: str) -> str:
    """
    Нормализует Unicode-степени в формат ^N.
    Исправленная логика: ставит ^ только перед началом группы верхних индексов.
    4¹⁰ -> 4^10 (а не 4^1^0)
    """
    result = []

    for idx, ch in enumerate(expr):
        if ch in SUPERSCRIPT_MAP:
            # Проверяем, был ли ПРЕДЫДУЩИЙ символ тоже верхним индексом
            is_prev_super = (idx > 0) and (expr[idx-1] in SUPERSCRIPT_MAP)

            # Если это начало серии верхних индексов — ставим галочку
            if not is_prev_super:
                 result.append("^")

            result.append(SUPERSCRIPT_MAP[ch])
        else:
            result.append(ch)

    return "".join(result)

# ============================================================================
# Токенизация и Парсинг
# ============================================================================

def _tokenize(expression: str) -> Optional[List[Dict[str, str]]]:
    tokens = []
    i = 0
    length = len(expression)

    while i < length:
        char = expression[i]

        if char.isspace():
            i += 1
            continue

        # Числа (целые)
        if char.isdigit():
            num_str = char
            i += 1
            while i < length and expression[i].isdigit():
                num_str += expression[i]
                i += 1
            tokens.append({"type": "INT", "value": num_str})
            continue

        # Операторы и спецсимволы
        # ВАЖНО: Добавлена поддержка тире (–) и математического минуса (−)
        if char in ('-', '−', '–'):
            tokens.append({"type": "MINUS", "value": "-"})
        elif char == '+':
            tokens.append({"type": "PLUS", "value": "+"})
        elif char in ('·', '*', '×'):
            tokens.append({"type": "OP_MUL", "value": "*"})
        elif char in ('/', ':'):
            tokens.append({"type": "OP_DIV", "value": "/"})
        elif char == '^':
            tokens.append({"type": "POW", "value": "^"})
        elif char == '(':
            tokens.append({"type": "LPAREN", "value": "("})
        elif char == ')':
            tokens.append({"type": "RPAREN", "value": ")"})
        elif char == '√':
            tokens.append({"type": "SQRT", "value": "√"})
        else:
            # Неизвестный символ
            return None

        i += 1

    return tokens

class _Parser:
    """
    Парсер для числовых выражений.
    """
    def __init__(self, tokens: List[Dict[str, str]]):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self):
        self.pos += 1

    def parse(self):
        if not self.tokens: return None
        res = self._expression()
        if self.pos < len(self.tokens): return None # Не всё распарсили
        return res

    def _expression(self):
        left = self._term()
        if not left: return None

        while self.current() and self.current()["type"] in ("PLUS", "MINUS"):
            op = self.current()["value"]
            self.advance()
            right = self._term()
            if not right: return None
            left = {"type": "binary_op", "op": op, "left": left, "right": right}
        return left

    def _term(self):
        left = self._power()
        if not left: return None

        while True:
            cur = self.current()
            if not cur: break

            if cur["type"] in ("OP_MUL", "OP_DIV"):
                op = cur["value"]
                self.advance()
                right = self._power()
                if not right: return None
                if op == "*":
                    left = {"type": "product", "factors": [left, right]}
                else:
                    left = {"type": "fraction", "numerator": left, "denominator": right}

            # Неявное умножение: 2√3, (a)(b)
            elif cur["type"] in ("INT", "SQRT", "LPAREN"):
                right = self._power()
                if not right: return None
                if left["type"] == "product":
                    left["factors"].append(right)
                else:
                    left = {"type": "product", "factors": [left, right]}
            else:
                break
        return left

    def _power(self):
        base = self._atom()
        if not base: return None

        while self.current() and self.current()["type"] == "POW":
            self.advance()
            exp = self._atom()
            if not exp: return None
            base = {"type": "power", "base": base, "exp": exp}
        return base

    def _atom(self):
        cur = self.current()
        if not cur: return None

        if cur["type"] == "INT":
            val = int(cur["value"])
            self.advance()
            return {"type": "integer", "value": val}

        if cur["type"] == "MINUS":
            self.advance()
            node = self._atom()
            return {"type": "product", "factors": [{"type": "integer", "value": -1}, node]}

        if cur["type"] == "SQRT":
            self.advance()
            radicand = self._atom()
            if not radicand: return None
            return {"type": "sqrt", "radicand": radicand}

        if cur["type"] == "LPAREN":
            self.advance()
            expr = self._expression()
            if not expr: return None
            if not self.current() or self.current()["type"] != "RPAREN": return None
            self.advance()
            return expr

        return None

# ============================================================================
# Вычисление (Eval)
# ============================================================================

def _eval_node(node: Dict[str, Any]) -> float:
    if node["type"] == "integer":
        return float(node["value"])

    if node["type"] == "binary_op":
        l = _eval_node(node["left"])
        r = _eval_node(node["right"])
        if node["op"] == "+": return l + r
        if node["op"] == "-": return l - r

    if node["type"] == "product":
        res = 1.0
        for f in node["factors"]:
            res *= _eval_node(f)
        return res

    if node["type"] == "fraction":
        num = _eval_node(node["numerator"])
        den = _eval_node(node["denominator"])
        if abs(den) < 1e-15: raise ZeroDivisionError
        return num / den

    if node["type"] == "power":
        base = _eval_node(node["base"])
        exp = _eval_node(node["exp"])
        if base < 0 and abs(exp % 1) > 1e-9:
            raise ValueError("Negative base fractional power")
        return base ** exp

    if node["type"] == "sqrt":
        val = _eval_node(node["radicand"])
        if val < -1e-9: raise ValueError("Sqrt of negative")
        return math.sqrt(abs(val))

    raise ValueError(f"Unknown node type: {node.get('type')}")

def format_answer(val: float) -> Optional[str]:
    """Форматирует float в 'красивую' строку."""
    if not math.isfinite(val): return None

    rounded = round(val, 9)
    if abs(rounded - round(rounded)) < 1e-9:
        return str(int(round(rounded)))

    s = f"{rounded:.9f}".rstrip("0").rstrip(".")
    if len(s) > 15: return None

    return s.replace(".", ",")

# ============================================================================
# Логика Валидации
# ============================================================================

def validate(raw_line: str) -> Optional[Dict[str, Any]]:
    parts = raw_line.split("|")
    if len(parts) < 2: return None

    pattern = parts[0].strip()
    expr_str = parts[1].strip()

    if pattern == "count_integers_between_radicals":
        return _validate_count_integers(pattern, expr_str)
    else:
        return _validate_standard_math(pattern, expr_str)


def _validate_standard_math(pattern: str, expr_str: str) -> Optional[Dict[str, Any]]:
    try:
        norm_expr = normalize_superscripts(expr_str)
        tokens = _tokenize(norm_expr)
        if not tokens: return None

        parser = _Parser(tokens)
        tree = parser.parse()
        if not tree: return None

        val = _eval_node(tree)
        ans_str = format_answer(val)

        if ans_str is None: return None

        return {
            "solution_pattern": pattern,
            "expression_tree": tree,
            "variables": {},
            "variables_display": {},
            "answer": ans_str
        }

    except Exception:
        return None


def _validate_count_integers(pattern: str, expr_str: str) -> Optional[Dict[str, Any]]:
    parts = re.split(r'\s+и\s+|\s+,\s+', expr_str)
    if len(parts) != 2: return None

    left_str, right_str = parts[0], parts[1]

    try:
        t1 = _tokenize(normalize_superscripts(left_str))
        tree1 = _Parser(t1).parse()
        val1 = _eval_node(tree1)

        t2 = _tokenize(normalize_superscripts(right_str))
        tree2 = _Parser(t2).parse()
        val2 = _eval_node(tree2)

        min_val = min(val1, val2)
        max_val = max(val1, val2)

        start_int = math.floor(min_val)
        end_int = math.ceil(max_val)
        count = 0
        for k in range(start_int, end_int + 1):
            if min_val < k < max_val:
                count += 1

        return {
            "solution_pattern": pattern,
            "expression_tree": {
                "type": "range_query",
                "left": tree1,
                "right": tree2
            },
            "variables": {},
            "variables_display": {},
            "answer": str(count)
        }

    except Exception:
        return None
