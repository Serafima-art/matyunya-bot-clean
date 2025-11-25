"""
Валидатор для integer_expressions (задание 8, подтип integer_expressions).

Обрабатывает строки формата:
    solution_pattern | expression | a=10, b=15

Поддерживает три паттерна:
    - alg_power_fraction
    - alg_radical_power
    - alg_radical_fraction

Архитектура:
    validate → parse_raw_line → parse_expression → build_expression_tree
    → run_validation_rules → compute_answer → format_json
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
}


def normalize_superscripts(expr: str) -> str:
    """
    Нормализует Unicode-степени (a³, b⁵, a¹⁷) в формат a^3.
    '^' добавляется, если предыдущий символ — буква или ')'.
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
    """
    Принимает строку вида:
        alg_power_fraction | ((a³)⁵ · a³) / a²⁰ | a=5

    Возвращает dict с JSON-объектом или None (если выражение невалидно).

    Args:
        raw_line: Сырая строка с паттерном, выражением и переменными

    Returns:
        Dict с полями: task_type, subtype, solution_pattern, expression_tree,
        variables, answer; или None если валидация не прошла
    """
    # Парсинг сырой строки
    parsed_data = parse_raw_line(raw_line)
    if parsed_data is None:
        return None

    solution_pattern, expression, variables = parsed_data

    # Роутер по solution_pattern
    if solution_pattern == "alg_power_fraction":
        return _validate_alg_power_fraction(expression, variables)
    elif solution_pattern == "alg_radical_power":
        return _validate_alg_radical_power(expression, variables)
    elif solution_pattern == "alg_radical_fraction":
        return _validate_alg_radical_fraction(expression, variables)
    else:
        return None


# ============================================================================
# Функции-слои (общие для всех паттернов)
# ============================================================================

def parse_raw_line(raw_line: str) -> Optional[Tuple[str, str, Dict[str, float]]]:
    """
    Парсит сырую строку формата: solution_pattern | expression | a=10, b=15

    Args:
        raw_line: Сырая строка для парсинга

    Returns:
        Кортеж (solution_pattern, expression, variables) или None при ошибке
    """
    # Разбиваем по символу |
    parts = raw_line.split("|")

    # Должно быть ровно 3 части
    if len(parts) != 3:
        return None

    # Удаляем пробелы вокруг каждой части
    solution_pattern = parts[0].strip()
    expression = parts[1].strip()
    variables_str = parts[2].strip()

    # Проверяем solution_pattern
    valid_patterns = {
        "alg_power_fraction",
        "alg_radical_power",
        "alg_radical_fraction"
    }
    if solution_pattern not in valid_patterns:
        return None

    # Парсим variables
    variables: Dict[str, float] = {}

    # Если строка переменных пустая → просто вернуть
    if not variables_str:
        return (solution_pattern, expression, variables)

    # Разбиваем строку переменных по запятой
    var_parts = [part.strip() for part in variables_str.split(",")]

    # Паттерны:
    # 1) a = 3
    # 2) b = √2
    num_pattern = re.compile(r'^([a-zA-Z])\s*=\s*(-?\d+(?:\.\d+)?)$')
    sqrt_pattern = re.compile(r'^([a-zA-Z])\s*=\s*√\s*(-?\d+(?:\.\d+)?)$')

    for var_part in var_parts:

        # Вариант 1: обычное число
        m = num_pattern.match(var_part)
        if m:
            var_name = m.group(1)
            value_str = m.group(2)
            variables[var_name] = float(value_str)
            continue

        # Вариант 2: число под корнем √N
        m = sqrt_pattern.match(var_part)
        if m:
            var_name = m.group(1)
            radicand_str = m.group(2)
            try:
                radicand = float(radicand_str)
                if radicand < 0:
                    return None
                variables[var_name] = radicand ** 0.5
            except ValueError:
                return None
            continue

        # Ни один формат не подошёл → ошибка
        return None

    return (solution_pattern, expression, variables)


def _tokenize(expression: str) -> Optional[List[Dict[str, str]]]:
    """
    Токенизирует строку выражения.

    Поддерживаемые токены:
        - VAR: a, b
        - INT: целые числа (включая отрицательные)
        - POW: "^"
        - OP: ·, *, /
        - LPAREN: (
        - RPAREN: )
        - SQRT: √

    Args:
        expression: Строка с выражением

    Returns:
        Список токенов вида [{"type": "...", "value": "..."}, ...] или None при ошибке
    """
    tokens = []
    i = 0
    length = len(expression)

    while i < length:
        char = expression[i]

        # Пробелы игнорируем
        if char.isspace():
            i += 1
            continue

        # Переменные: a, b
        if char in ('a', 'b'):
            tokens.append({"type": "VAR", "value": char})
            i += 1
            continue

        # Целые числа (включая отрицательные)
        if char.isdigit() or (char == '-' and i + 1 < length and expression[i + 1].isdigit()):
            num_str = char
            i += 1
            while i < length and expression[i].isdigit():
                num_str += expression[i]
                i += 1
            tokens.append({"type": "INT", "value": num_str})
            continue

        # Унарный минус (MINUS) - только если это не часть отрицательного числа
        if char == '-':
            tokens.append({"type": "MINUS", "value": "-"})
            i += 1
            continue

        # Степень: ^
        if char == '^':
            tokens.append({"type": "POW", "value": "^"})
            i += 1
            continue

        # Операции: ·, *, /
        if char in ('·', '*', '/'):
            tokens.append({"type": "OP", "value": char})
            i += 1
            continue

        # Скобки
        if char == '(':
            tokens.append({"type": "LPAREN", "value": "("})
            i += 1
            continue

        if char == ')':
            tokens.append({"type": "RPAREN", "value": ")"})
            i += 1
            continue

        # Корень: √
        if char == '√':
            tokens.append({"type": "SQRT", "value": "√"})
            i += 1
            continue

        # Неизвестный символ
        return None

    return tokens


class _Parser:
    """Рекурсивный нисходящий парсер для построения AST."""

    def __init__(self, tokens: List[Dict[str, str]]):
        self.tokens = tokens
        self.pos = 0

    def current(self) -> Optional[Dict[str, str]]:
        """Возвращает текущий токен."""
        if self.pos >= len(self.tokens):
            return None
        return self.tokens[self.pos]

    def advance(self):
        """Переходит к следующему токену."""
        self.pos += 1

    def parse(self) -> Optional[Dict[str, Any]]:
        """Главная функция парсинга - парсит выражение (дроби)."""
        return self._parse_expression()

    def _parse_expression(self) -> Optional[Dict[str, Any]]:
        """Парсит выражение (дроби)."""
        left = self._parse_product()
        if left is None:
            return None

        while self.current() and self.current()["type"] == "OP" and self.current()["value"] == "/":
            self.advance()  # пропускаем "/"
            right = self._parse_product()
            if right is None:
                return None
            left = {
                "kind": "fraction",
                "numerator": left,
                "denominator": right
            }

        return left

    def _parse_product(self) -> Optional[Dict[str, Any]]:
        """Парсит произведение (·, *)."""
        factors = []
        factor = self._parse_power()
        if factor is None:
            return None

        factors.append(factor)

        while self.current():
            if self.current()["type"] == "OP" and self.current()["value"] in ("·", "*"):
                self.advance()  # пропускаем оператор
                factor = self._parse_power()
                if factor is None:
                    return None
                factors.append(factor)
            elif self.current()["type"] in ("VAR", "INT", "LPAREN", "SQRT"):
                # Неявное умножение (например, "a b" или "2a" или "25a")
                factor = self._parse_power()
                if factor is None:
                    return None
                factors.append(factor)
            else:
                break

        if len(factors) == 1:
            return factors[0]

        return {
            "kind": "product",
            "factors": factors
        }

    def _parse_power(self) -> Optional[Dict[str, Any]]:
        """Парсит степени (^)."""
        base = self._parse_atom()
        if base is None:
            return None

        # Обрабатываем степени (башни)
        while True:
            if self.current() and self.current()["type"] == "POW":
                self.advance()  # пропускаем "^"
                exp_node = self._parse_atom()
                if exp_node is None:
                    return None
                # exp должен быть AST-узлом integer
                if exp_node["kind"] != "integer":
                    return None
                base = {
                    "kind": "power",
                    "base": base,
                    "exp": exp_node
                }
            else:
                break

        return base

    def _parse_atom(self) -> Optional[Dict[str, Any]]:
        """Парсит атомарные элементы."""
        if not self.current():
            return None

        token = self.current()

        # Унарный минус (MINUS) - обрабатываем как product(-1, atom)
        if token["type"] == "MINUS":
            self.advance()
            atom = self._parse_atom()
            if atom is None:
                return None
            return {
                "kind": "product",
                "factors": [
                    {"kind": "integer", "value": -1},
                    atom
                ]
            }

        # Переменная
        if token["type"] == "VAR":
            self.advance()
            return {"kind": "variable", "name": token["value"]}

        # Целое число
        if token["type"] == "INT":
            value = int(token["value"])
            self.advance()
            return {"kind": "integer", "value": value}

        # Скобки
        if token["type"] == "LPAREN":
            self.advance()
            expr = self._parse_expression()
            if expr is None:
                return None
            if not self.current() or self.current()["type"] != "RPAREN":
                return None
            self.advance()
            return expr

        # Корень
        if token["type"] == "SQRT":
            self.advance()
            if not self.current() or self.current()["type"] != "LPAREN":
                return None
            self.advance()  # пропускаем "("
            radicand = self._parse_expression()
            if radicand is None:
                return None
            if not self.current() or self.current()["type"] != "RPAREN":
                return None
            self.advance()  # пропускаем ")"
            return {
                "kind": "sqrt",
                "radicand": radicand
            }

        return None



def parse_expression(expression: str, solution_pattern: str) -> Optional[Any]:
    """
    Парсит выражение в строковом формате.

    Поддерживает:
        - степени: a^3
        - башни: (a^3)^5
        - произведения: a · b · c
        - дроби: (…) / (…)
        - корни: √(…)
        - отрицательные степени: a^-7
        - переменные: a, b
        - скобки любого уровня вложенности

    Args:
        expression: Строка с выражением
        solution_pattern: Паттерн решения (для выбора стратегии парсинга)

    Returns:
        Промежуточное представление (AST) или None при ошибке
    """
    expression = normalize_superscripts(expression)
    tokens = _tokenize(expression)
    if tokens is None:
        return None

    parser = _Parser(tokens)
    ast = parser.parse()

    # Проверяем, что все токены обработаны
    if parser.pos < len(tokens):
        return None

    return ast


def build_expression_tree(ast: Any, solution_pattern: str) -> Optional[Dict[str, Any]]:
    """
    Строит expression_tree из AST.

    Узлы дерева (финальный стандарт):
        - integer: {"type": "integer", "value": int}
        - variable: {"type": "variable", "name": str}
        - power: {"type": "power", "base": {...}, "exp": {...}}
        - product: {"type": "product", "factors": [{...}, ...]}
        - fraction: {"type": "fraction", "numerator": {...}, "denominator": {...}}
        - sqrt: {"type": "sqrt", "radicand": {...}}

    Args:
        ast: Промежуточное представление (AST)
        solution_pattern: Паттерн решения

    Returns:
        Expression tree в формате словаря или None при ошибке
    """
    if ast is None:
        return None

    if not isinstance(ast, dict) or "kind" not in ast:
        return None

    kind = ast["kind"]

    # integer
    if kind == "integer":
        return {
            "type": "integer",
            "value": ast["value"]
        }

    # variable
    if kind == "variable":
        return {
            "type": "variable",
            "name": ast["name"]
        }

    # power
    if kind == "power":
        base_tree = build_expression_tree(ast["base"], solution_pattern)
        if base_tree is None:
            return None

        # exp теперь уже AST-узел integer
        exp_tree = build_expression_tree(ast["exp"], solution_pattern)
        if exp_tree is None or exp_tree.get("type") != "integer":
            return None

        return {
            "type": "power",
            "base": base_tree,
            "exp": exp_tree
        }

    # product
    if kind == "product":
        factors = []
        for factor_ast in ast["factors"]:
            factor_tree = build_expression_tree(factor_ast, solution_pattern)
            if factor_tree is None:
                return None
            factors.append(factor_tree)

        return {
            "type": "product",
            "factors": factors
        }

    # fraction
    if kind == "fraction":
        numerator_tree = build_expression_tree(ast["numerator"], solution_pattern)
        if numerator_tree is None:
            return None

        denominator_tree = build_expression_tree(ast["denominator"], solution_pattern)
        if denominator_tree is None:
            return None

        return {
            "type": "fraction",
            "numerator": numerator_tree,
            "denominator": denominator_tree
        }

    # sqrt
    if kind == "sqrt":
        radicand_tree = build_expression_tree(ast["radicand"], solution_pattern)
        if radicand_tree is None:
            return None

        return {
            "type": "sqrt",
            "radicand": radicand_tree
        }

    return None


def _is_perfect_square_int(x: int) -> bool:
    """Проверяет, является ли целое число полным квадратом."""
    if x < 0:
        return False
    if x == 0:
        return True
    root = int(x ** 0.5)
    return root * root == x


def _eval_node(node: Dict[str, Any], variables: Dict[str, float]) -> Optional[Fraction]:
    """
    Рекурсивно вычисляет значение узла дерева используя Fraction для точности.

    Args:
        node: Узел expression_tree
        variables: Словарь переменных

    Returns:
        Fraction или None при ошибке
    """
    if not isinstance(node, dict) or "type" not in node:
        return None

    node_type = node["type"]

    # integer
    if node_type == "integer":
        return Fraction(node["value"], 1)

    # variable
    if node_type == "variable":
        var_name = node["name"]
        if var_name not in variables:
            return None
        try:
            return Fraction(variables[var_name])
        except (ValueError, TypeError):
            return None

    # power
    if node_type == "power":
        base = _eval_node(node["base"], variables)
        if base is None:
            return None
        exp = _eval_node(node["exp"], variables)
        if exp is None:
            return None
        # exp обязан быть integer (exp.denominator == 1)
        if exp.denominator != 1:
            return None
        try:
            # result = base ** exp.numerator
            return base ** exp.numerator
        except (OverflowError, ValueError, ZeroDivisionError):
            return None

    # product
    if node_type == "product":
        result = Fraction(1, 1)
        for factor in node["factors"]:
            factor_value = _eval_node(factor, variables)
            if factor_value is None:
                return None
            try:
                result *= factor_value
            except (OverflowError, ValueError):
                return None
        return result

    # fraction
    if node_type == "fraction":
        numerator = _eval_node(node["numerator"], variables)
        if numerator is None:
            return None
        denominator = _eval_node(node["denominator"], variables)
        if denominator is None:
            return None
        if denominator == 0:
            return None
        try:
            return numerator / denominator
        except (OverflowError, ValueError, ZeroDivisionError):
            return None

    # sqrt
    if node_type == "sqrt":
        radicand = _eval_node(node["radicand"], variables)
        if radicand < 0:
            return None

        num = abs(radicand.numerator)
        den = abs(radicand.denominator)

        if not _is_perfect_square_int(num) or not _is_perfect_square_int(den):
            return None

        num_root = int(num ** 0.5)
        den_root = int(den ** 0.5)

        return Fraction(num_root, den_root)
        # Извлекаем корень из числителя и знаменателя
        num_root = int(abs(num) ** 0.5)
        if num < 0:
            num_root = -num_root
        den_root = int(abs(den) ** 0.5)
        try:
            result = Fraction(num_root, den_root)
            # Проверяем, что результат неотрицательный (корень из неотрицательного числа)
            if result < 0:
                return None
            return result
        except (ValueError, ZeroDivisionError):
            return None

    return None


def is_terminating_denominator(d: int) -> bool:
    """
    Проверяет, является ли знаменатель таким, что дробь будет конечной десятичной.

    Конечная десятичная дробь получается только если знаменатель после сокращения
    содержит только простые множители 2 и 5.

    Args:
        d: Знаменатель

    Returns:
        True если дробь будет конечной, False иначе
    """
    d = abs(d)
    if d == 0:
        return False
    # Убираем все множители 2
    while d % 2 == 0:
        d //= 2
    # Убираем все множители 5
    while d % 5 == 0:
        d //= 5
    # Если остался только 1, значит знаменатель содержал только 2 и 5
    return d == 1


def compute_answer(expression_tree: Dict[str, Any], variables: Dict[str, float]) -> Optional[str]:
    """
    Вычисляет ответ, подставляя переменные в дерево используя Fraction для точности.

    Дерево вычисляется рекурсивно:
        - integer → число
        - variable → подставляем переменную
        - power → eval(base)**exp
        - product → перемножаем
        - fraction → numerator/denominator
        - sqrt → radicand ** 0.5 (только если идеальный квадрат)

    Ответ приводится к строке:
        - если целое → "80"
        - если конечная дробь → "0,04"
        - никаких округлений, только точные значения
        - бесконечные дроби запрещены → return None

    Args:
        expression_tree: Дерево выражения
        variables: Словарь переменных {name: value}

    Returns:
        Строка с ответом или None при ошибке
    """
    # 1. Вычисляем значение дерева
    value = _eval_node(expression_tree, variables)
    if value is None:
        return None

    # 2. Проверяем конечную десятичную дробь
    if not is_terminating_denominator(value.denominator):
        return None

    # 3. Формирование ответа (строка)
    # Если знаменатель = 1 → вернуть str(numerator)
    if value.denominator == 1:
        return str(value.numerator)

    # Иначе → точная десятичная дробь (без округлений!)
    # Преобразуем Fraction в float, затем в строку
    s = str(float(value))
    s = s.rstrip("0").rstrip(".")

    # Обработка случая "-0"
    if s == "-0" or s == "0":
        return "0"

    # Заменяем точку на запятую
    s = s.replace(".", ",")

    return s

def _eval_node_float(node: Dict[str, Any], variables: Dict[str, float]) -> Optional[float]:
    """
    Упрощённый численный eval для alg_radical_fraction.
    Работает с float, разрешает любые радикалы, а уже потом
    мы пытаемся восстановить рациональное значение через Fraction.
    """
    if not isinstance(node, dict) or "type" not in node:
        return None

    node_type = node["type"]

    # integer
    if node_type == "integer":
        return float(node["value"])

    # variable
    if node_type == "variable":
        name = node["name"]
        if name not in variables:
            return None
        try:
            return float(variables[name])
        except (TypeError, ValueError):
            return None

    # power
    if node_type == "power":
        base_val = _eval_node_float(node["base"], variables)
        exp_val = _eval_node_float(node["exp"], variables)
        if base_val is None or exp_val is None:
            return None
        # показатель степени должен быть целым
        if abs(exp_val - int(round(exp_val))) > 1e-9:
            return None
        try:
            return base_val ** int(round(exp_val))
        except (OverflowError, ValueError, ZeroDivisionError):
            return None

    # product
    if node_type == "product":
        result = 1.0
        for factor in node["factors"]:
            val = _eval_node_float(factor, variables)
            if val is None:
                return None
            result *= val
        return result

    # fraction
    if node_type == "fraction":
        num = _eval_node_float(node["numerator"], variables)
        den = _eval_node_float(node["denominator"], variables)
        if num is None or den is None or abs(den) < 1e-15:
            return None
        try:
            return num / den
        except (OverflowError, ValueError, ZeroDivisionError):
            return None

    # sqrt
    if node_type == "sqrt":
        rad = _eval_node_float(node["radicand"], variables)
        if rad is None or rad < 0:
            return None
        try:
            return rad ** 0.5
        except (OverflowError, ValueError):
            return None

    return None


def _fraction_to_decimal_string(frac: Fraction) -> str:
    """
    Превращает Fraction с "правильным" знаменателем (только 2 и 5 в разложении)
    в десятичную запись с запятой.
    """
    num = frac.numerator
    den = frac.denominator

    if den == 1:
        return str(num)

    # разложим знаменатель на 2 и 5
    d = abs(den)
    c2 = c5 = 0
    while d % 2 == 0:
        d //= 2
        c2 += 1
    while d % 5 == 0:
        d //= 5
        c5 += 1

    k = max(c2, c5)
    scale_2 = k - c2
    scale_5 = k - c5

    scaled_num = num * (2 ** scale_2) * (5 ** scale_5)
    # знаменатель теперь ровно 10^k

    sign = "-" if scaled_num < 0 else ""
    s = str(abs(scaled_num))

    if k > 0:
        if len(s) <= k:
            s = "0" * (k - len(s) + 1) + s
        int_part = s[:-k]
        frac_part = s[-k:]
        s = int_part + "," + frac_part
    # если запятая есть — срежем хвостовые нули
    if "," in s:
        s = s.rstrip("0").rstrip(",")

    return sign + s


def compute_answer_alg_radical_fraction(
    expression_tree: Dict[str, Any],
    variables: Dict[str, float]
) -> Optional[str]:
    """
    Численно вычисляет ответ для alg_radical_fraction:
    1) считаем всё в float, разрешая любые радикалы;
    2) приближаем результат рациональной дробью;
    3) убеждаемся, что знаменатель даёт конечную десятичную дробь;
    4) форматируем ответ в строку с запятой.
    """
    value = _eval_node_float(expression_tree, variables)
    if value is None:
        return None

    # восстанавливаем дробь из float
    frac = Fraction(value).limit_denominator(10**6)

    # проверяем, что Fraction действительно хорошо аппроксимирует исходное значение
    if abs(float(frac) - value) > 1e-9:
        return None

    if not is_terminating_denominator(frac.denominator):
        return None

    return _fraction_to_decimal_string(frac)


# ============================================================================
# Вспомогательные функции для валидации
# ============================================================================

def _find_all_nodes(tree: Dict[str, Any], type_name: str) -> List[Dict[str, Any]]:
    """Находит все узлы заданного типа в дереве."""
    result = []
    if not isinstance(tree, dict) or "type" not in tree:
        return result

    if tree["type"] == type_name:
        result.append(tree)

    node_type = tree["type"]

    if node_type == "power":
        result.extend(_find_all_nodes(tree["base"], type_name))
        result.extend(_find_all_nodes(tree["exp"], type_name))
    elif node_type == "product":
        for factor in tree["factors"]:
            result.extend(_find_all_nodes(factor, type_name))
    elif node_type == "fraction":
        result.extend(_find_all_nodes(tree["numerator"], type_name))
        result.extend(_find_all_nodes(tree["denominator"], type_name))
    elif node_type == "sqrt":
        result.extend(_find_all_nodes(tree["radicand"], type_name))

    return result


def _extract_numeric_coeff(tree: Dict[str, Any]) -> List[int]:
    """Извлекает все числовые коэффициенты (integer узлы) из дерева."""
    result = []
    if not isinstance(tree, dict) or "type" not in tree:
        return result

    if tree["type"] == "integer":
        result.append(tree["value"])

    node_type = tree["type"]

    if node_type == "power":
        result.extend(_extract_numeric_coeff(tree["base"]))
        result.extend(_extract_numeric_coeff(tree["exp"]))
    elif node_type == "product":
        for factor in tree["factors"]:
            result.extend(_extract_numeric_coeff(factor))
    elif node_type == "fraction":
        result.extend(_extract_numeric_coeff(tree["numerator"]))
        result.extend(_extract_numeric_coeff(tree["denominator"]))
    elif node_type == "sqrt":
        result.extend(_extract_numeric_coeff(tree["radicand"]))

    return result


def _extract_variable_powers(tree: Dict[str, Any]) -> Dict[str, int]:
    """
    Извлекает степени переменных из поддерева.
    Работает строго по математическим правилам:
        - power: степень умножается: (b^7)^2 → 14
        - product: степени складываются
        - fraction: знаменатель вычитает степени
        - sqrt: степени внутри делятся на 2 (только для анализа радикандов)
    Возвращает dict вида {"a": total_power, "b": total_power}.
    """

    result: Dict[str, int] = {}

    def add_power(var: str, power: int):
        result[var] = result.get(var, 0) + power

    def traverse(node: Dict[str, Any], multiplier: float = 1.0):
        """
        multiplier:
            numerator = +1
            denominator = -1
            внутри sqrt → степень делится на 2
        """
        if not isinstance(node, dict) or "type" not in node:
            return

        node_type = node["type"]

        # variable
        if node_type == "variable":
            add_power(node["name"], int(multiplier))
            return

        # integer → нет переменной
        if node_type == "integer":
            return

        # power
        if node_type == "power":
            # вычисляем exponent — он integer внутри дерева
            if node["exp"]["type"] != "integer":
                return  # такого не должно быть, но безопасно

            exp_val = node["exp"]["value"]

            # база может быть переменной, продуктом, дробью
            # multiplier умножаем на exp_val
            traverse(node["base"], multiplier * exp_val)
            return

        # product
        if node_type == "product":
            for factor in node["factors"]:
                traverse(factor, multiplier)
            return

        # fraction (числитель +multiplier, знаменатель -multiplier)
        if node_type == "fraction":
            traverse(node["numerator"], multiplier)
            traverse(node["denominator"], -multiplier)
            return

        # sqrt — степень внутри делится на 2
        if node_type == "sqrt":
            traverse(node["radicand"], multiplier * 0.5)
            return

    traverse(tree)
    return result


def _is_perfect_square(x: int) -> bool:
    """Проверяет, является ли число полным квадратом."""
    if x < 0:
        return False
    if x == 0:
        return True
    root = int(x ** 0.5)
    return root * root == x


def _evaluate_for_zero_check(tree: Dict[str, Any], variables: Dict[str, float]) -> Optional[float]:
    """
    Мини-eval для проверки, что знаменатель не равен нулю.
    Использует ту же логику, что и _eval_node, но возвращает float для проверки.
    """
    result = _eval_node(tree, variables)
    if result is None:
        return None
    # Преобразуем Fraction в float для проверки на ноль
    try:
        return float(result)
    except (OverflowError, ValueError):
        return None


def _has_sqrt_in_subtree(tree: Dict[str, Any]) -> bool:
    """Проверяет, есть ли в поддереве узлы sqrt."""
    if not isinstance(tree, dict) or "type" not in tree:
        return False

    if tree["type"] == "sqrt":
        return True

    node_type = tree["type"]

    if node_type == "power":
        return _has_sqrt_in_subtree(tree["base"]) or _has_sqrt_in_subtree(tree["exp"])
    elif node_type == "product":
        return any(_has_sqrt_in_subtree(factor) for factor in tree["factors"])
    elif node_type == "fraction":
        return _has_sqrt_in_subtree(tree["numerator"]) or _has_sqrt_in_subtree(tree["denominator"])
    elif node_type == "sqrt":
        return True

    return False


def _count_sqrt_nodes(tree: Dict[str, Any]) -> int:
    """Подсчитывает количество узлов sqrt в дереве."""
    count = 0
    if not isinstance(tree, dict) or "type" not in tree:
        return count

    if tree["type"] == "sqrt":
        count += 1
        count += _count_sqrt_nodes(tree["radicand"])
    elif tree["type"] == "power":
        count += _count_sqrt_nodes(tree["base"])
        count += _count_sqrt_nodes(tree["exp"])
    elif tree["type"] == "product":
        for factor in tree["factors"]:
            count += _count_sqrt_nodes(factor)
    elif tree["type"] == "fraction":
        count += _count_sqrt_nodes(tree["numerator"])
        count += _count_sqrt_nodes(tree["denominator"])

    return count


def _collect_all_powers_from_radicand(tree: Dict[str, Any]) -> List[int]:
    """Собирает все показатели степеней из radicand."""
    powers = []

    def _traverse(node: Dict[str, Any]):
        if not isinstance(node, dict) or "type" not in node:
            return

        node_type = node["type"]

        if node_type == "power":
            if node["exp"]["type"] == "integer":
                powers.append(node["exp"]["value"])
            _traverse(node["base"])
            _traverse(node["exp"])
        elif node_type == "product":
            for factor in node["factors"]:
                _traverse(factor)
        elif node_type == "fraction":
            _traverse(node["numerator"])
            _traverse(node["denominator"])
        elif node_type == "sqrt":
            _traverse(node["radicand"])

    _traverse(tree)
    return powers


# ============================================================================
# Основная функция валидации
# ============================================================================

def run_validation_rules(
    expression_tree: Dict[str, Any],
    solution_pattern: str,
    variables: Dict[str, float]
) -> bool:
    """
    Запускает правила валидации в зависимости от solution_pattern.

    Для alg_power_fraction:
        - степени внутри power должны быть целыми
        - знаменатель не может быть 0
        - дерево должно содержать fraction
        - в числителе/знаменателе нет корней
        - допускаются большие степени до 30
        - ответ должен быть конечной дробью или целым числом

    Для alg_radical_power:
        - верхний узел — sqrt
        - radicand должен быть fraction или product
        - коэффициент под корнем должен быть полным квадратом
        - (m − n) должен быть чётным
        - после упрощения корня оцениваем результат по дереву

    Для alg_radical_fraction:
        - должно быть 1 или 2 корня сверху
        - denominator может содержать sqrt или product из sqrt
        - после объединения всех radicand степень каждой переменной чётная
        - radicand должен быть полностью извлекаемым
        - подставленный ответ должен быть целым или конечной дробью

    Args:
        expression_tree: Дерево выражения
        solution_pattern: Паттерн решения
        variables: Словарь переменных

    Returns:
        True если все правила пройдены, False иначе
    """
    if not isinstance(expression_tree, dict) or "type" not in expression_tree:
        return False

    if solution_pattern == "alg_power_fraction":
        return _validate_alg_power_fraction_rules(expression_tree, variables)
    elif solution_pattern == "alg_radical_power":
        return _validate_alg_radical_power_rules(expression_tree, variables)
    elif solution_pattern == "alg_radical_fraction":
        return _validate_alg_radical_fraction_rules(expression_tree, variables)

    return False


def _validate_alg_power_fraction_rules(
    expression_tree: Dict[str, Any],
    variables: Dict[str, float]
) -> bool:
    """Правила валидации для alg_power_fraction."""
    # 1. Верхний узел должен быть fraction
    if expression_tree["type"] != "fraction":
        return False

    # 2. В знаменателе не должно быть корней
    denominator = expression_tree["denominator"]
    if _has_sqrt_in_subtree(denominator):
        return False

    # 3. Все узлы power должны иметь целый показатель
    all_powers = _find_all_nodes(expression_tree, "power")
    for power_node in all_powers:
        if power_node["exp"]["type"] != "integer":
            return False
        exp_value = power_node["exp"]["value"]
        if not isinstance(exp_value, int):
            return False

    # 4. Нет отрицательных или нулевых знаменателей после подстановки
    denom_value = _evaluate_for_zero_check(denominator, variables)
    if denom_value is None or denom_value == 0:
        return False

    # 5. Степени по модулю ≤ 30
    for power_node in all_powers:
        exp_value = power_node["exp"]["value"]
        if abs(exp_value) > 30:
            return False

    # ----------------------------------------------------------
    # Разрешаем вложенную степень вида (b^n)^r в alg_power_fraction
    # ----------------------------------------------------------
    for power_node in all_powers:
        base = power_node.get("base", {})

        # Случай: степень применяется к степенному выражению
        # Например: (b^7)^2
        if isinstance(base, dict) and base.get("type") == "power":

            inner_base = base["base"]
            inner_exp = base["exp"]

            # Разрешаем только:
            # 1) база — переменная b
            # 2) внутренняя степень — integer
            # 3) внешняя степень — integer
            if (
                isinstance(inner_base, dict)
                and inner_base.get("type") == "variable"
                and inner_base.get("name") == "b"
                and isinstance(inner_exp, dict)
                and inner_exp.get("type") == "integer"
                and power_node["exp"].get("type") == "integer"
            ):
                continue  # всё хорошо

            # Если вложенная степень есть, но это не (b^n)^r → БРАК
            return False

    # 6. Проверяем, что ответ конечный и корректный
    answer = compute_answer(expression_tree, variables)
    if answer is None:
        return False

    return True


def _validate_alg_radical_power_rules(
    expression_tree: Dict[str, Any],
    variables: Dict[str, float]
) -> bool:
    """Правила валидации для alg_radical_power."""
    # 1. Верхний узел — sqrt
    if expression_tree["type"] != "sqrt":
        return False

    radicand = expression_tree["radicand"]

    # 2. radicand — либо product, либо fraction
    if radicand["type"] not in ("product", "fraction"):
        return False

    # 3. Коэффициент под корнем — полный квадрат
    numeric_coeffs = _extract_numeric_coeff(radicand)
    # Ищем положительные коэффициенты
    positive_coeffs = [c for c in numeric_coeffs if c > 0]
    if not positive_coeffs:
        # Если нет явных коэффициентов, проверяем неявные (например, 1)
        # Но по логике задачи должен быть коэффициент
        pass
    else:
        # Проверяем, что хотя бы один коэффициент - полный квадрат
        has_perfect_square = any(_is_perfect_square(c) for c in positive_coeffs)
        if not has_perfect_square:
            return False

    # 4. Разность степеней должна быть чётной
    # Для fraction: (m - n) должна быть чётной
    if radicand["type"] == "fraction":
        num_powers = _collect_all_powers_from_radicand(radicand["numerator"])
        den_powers = _collect_all_powers_from_radicand(radicand["denominator"])
        # Суммируем степени в числителе и вычитаем из знаменателя
        total_power = sum(num_powers) - sum(den_powers)
        if total_power % 2 != 0:
            return False
    else:
        # Для product: все степени должны быть чётными
        powers = _collect_all_powers_from_radicand(radicand)
        if any(p % 2 != 0 for p in powers if p != 0):
            return False

    # 5. После упрощения корня значение должно быть конечным
    answer = compute_answer(expression_tree, variables)
    if answer is None:
        return False

    return True


def _validate_alg_radical_fraction_rules(
    expression_tree: Dict[str, Any],
    variables: Dict[str, float]
) -> bool:
    """Правила валидации для alg_radical_fraction."""
    # 1. В выражении сверху должно быть 1 или 2 корня
    if expression_tree["type"] != "fraction":
        return False

    numerator = expression_tree["numerator"]
    denominator = expression_tree["denominator"]

    # Подсчитываем sqrt в числителе
    sqrt_count_in_num = _count_sqrt_nodes(numerator)
    if sqrt_count_in_num < 1 or sqrt_count_in_num > 2:
        return False

    # 2. В знаменателе может быть sqrt, product из sqrt или обычное произведение
    # Но denominator НЕ должен быть plain integer без корней
    if denominator["type"] == "integer":
        return False

    # 3. Объединённый radicand должен быть извлекаемым
    # Собираем radicand отдельно из числителя и знаменателя
    num_radicands = []
    den_radicands = []

    def _collect_radicands_from_node(node: Dict[str, Any], target_list: List):
        if not isinstance(node, dict) or "type" not in node:
            return
        if node["type"] == "sqrt":
            target_list.append(node["radicand"])
        elif node["type"] == "power":
            _collect_radicands_from_node(node["base"], target_list)
            _collect_radicands_from_node(node["exp"], target_list)
        elif node["type"] == "product":
            for factor in node["factors"]:
                _collect_radicands_from_node(factor, target_list)
        elif node["type"] == "fraction":
            _collect_radicands_from_node(node["numerator"], target_list)
            _collect_radicands_from_node(node["denominator"], target_list)

    _collect_radicands_from_node(numerator, num_radicands)
    _collect_radicands_from_node(denominator, den_radicands)

    # Извлекаем степени переменных из всех radicand
    # В числителе - складываем, в знаменателе - вычитаем
    variable_powers = {}
    for radicand in num_radicands:
        powers = _extract_variable_powers(radicand)
        for var, power in powers.items():
            variable_powers[var] = variable_powers.get(var, 0) + power
    for radicand in den_radicands:
        powers = _extract_variable_powers(radicand)
        for var, power in powers.items():
            variable_powers[var] = variable_powers.get(var, 0) - power

    # Проверяем, что все степени чётные
    for var, power in variable_powers.items():
        if power % 2 != 0:
            return False

    # Проверяем числовой коэффициент
    all_coeffs = []
    for radicand in num_radicands:
        all_coeffs.extend(_extract_numeric_coeff(radicand))
    for radicand in den_radicands:
        all_coeffs.extend(_extract_numeric_coeff(radicand))

    positive_coeffs = [c for c in all_coeffs if c > 0]
    if positive_coeffs:
        # Хотя бы один коэффициент должен быть полным квадратом
        has_perfect_square = any(_is_perfect_square(c) for c in positive_coeffs)
        if not has_perfect_square:
            return False

    # На этом этапе мы проверили только "структуру" подкоренных выражений.
    # Само численное вычисление ответа для alg_radical_fraction
    # выполняется отдельной функцией compute_answer_alg_radical_fraction.
    return True


def format_json(
    solution_pattern: str,
    expression_tree: Dict[str, Any],
    variables: Dict[str, float],
    answer: str
) -> Dict[str, Any]:
    """
    Формирует финальный JSON-объект для БД.

    Args:
        solution_pattern: Паттерн решения
        expression_tree: Дерево выражения
        variables: Словарь переменных
        answer: Строка с ответом

    Returns:
        Словарь с полями:
            - task_type: "8"
            - subtype: "integer_expressions"
            - solution_pattern: str
            - expression_tree: dict
            - variables: dict
            - answer: str
    """
    return {
        "task_type": "8",
        "subtype": "integer_expressions",
        "solution_pattern": solution_pattern,
        "expression_tree": expression_tree,
        "variables": variables,
        "answer": answer
    }


# ============================================================================
# Внутренние валидаторы для каждого паттерна
# ============================================================================

def _validate_alg_power_fraction(
    expression: str,
    variables: Dict[str, float]
) -> Optional[Dict[str, Any]]:
    """
    Валидатор для паттерна alg_power_fraction.

    Примеры:
        ((a³)⁵ · a³) / a²⁰
        (a^m · (b^n)^r) / (a·b)^s

    Args:
        expression: Строка с выражением
        variables: Словарь переменных

    Returns:
        JSON-объект или None
    """
    # Парсинг выражения
    ast = parse_expression(expression, "alg_power_fraction")
    if ast is None:
        return None

    # Построение дерева
    expression_tree = build_expression_tree(ast, "alg_power_fraction")
    if expression_tree is None:
        return None

    # Валидация правил
    if not run_validation_rules(expression_tree, "alg_power_fraction", variables):
        return None

    # Вычисление ответа
    answer = compute_answer(expression_tree, variables)
    if answer is None:
        return None

    # Формирование JSON
    return format_json("alg_power_fraction", expression_tree, variables, answer)


def _validate_alg_radical_power(
    expression: str,
    variables: Dict[str, float]
) -> Optional[Dict[str, Any]]:
    """
    Валидатор для паттерна alg_radical_power.

    Примеры:
        √(100 · a²¹ / a¹⁹)
        √(25 · a²)
        √((-a)⁶ · a¹⁰)

    Args:
        expression: Строка с выражением
        variables: Словарь переменных

    Returns:
        JSON-объект или None
    """
    # Парсинг выражения
    ast = parse_expression(expression, "alg_radical_power")
    if ast is None:
        return None

    # Построение дерева
    expression_tree = build_expression_tree(ast, "alg_radical_power")
    if expression_tree is None:
        return None

    # Валидация правил
    if not run_validation_rules(expression_tree, "alg_radical_power", variables):
        return None

    # Вычисление ответа
    answer = compute_answer(expression_tree, variables)
    if answer is None:
        return None

    # Формирование JSON
    return format_json("alg_radical_power", expression_tree, variables, answer)


def _validate_alg_radical_fraction(
    expression: str,
    variables: Dict[str, float]
) -> Optional[Dict[str, Any]]:
    """
    Валидатор для паттерна alg_radical_fraction.

    Примеры:
        ( √(25a) · √(4b³) ) / √(ab)
        √(ab) / (√(9a²) · √(16b))
    """
    # Парсинг выражения
    ast = parse_expression(expression, "alg_radical_fraction")
    if ast is None:
        return None

    # Построение дерева
    expression_tree = build_expression_tree(ast, "alg_radical_fraction")
    if expression_tree is None:
        return None

    # Валидация правил структуры
    if not run_validation_rules(expression_tree, "alg_radical_fraction", variables):
        return None

    # Численное вычисление ответа по спец-правилам для радикальной дроби
    answer = compute_answer_alg_radical_fraction(expression_tree, variables)
    if answer is None:
        return None

    # Формирование JSON
    return format_json("alg_radical_fraction", expression_tree, variables, answer)
