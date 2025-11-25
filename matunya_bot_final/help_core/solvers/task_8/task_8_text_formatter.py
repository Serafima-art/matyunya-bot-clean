"""
task_8_text_formatter.py — Форматтер для задания №8 (Алгебра).
"""

from typing import Any, Dict

SUPERSCRIPT_REV = {
    "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
    "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹",
    "-": "⁻", "+": "⁺"
}


def to_superscript(val: int | str) -> str:
    s = str(val)
    if s.startswith("-") and "-" in SUPERSCRIPT_REV:
        s = s.replace("-", SUPERSCRIPT_REV["-"], 1)
    return "".join(SUPERSCRIPT_REV.get(ch, ch) for ch in s)


def fmt_number(val: int | float | str) -> str:
    s = str(val)
    s = s.replace(".", ",")
    s = s.replace("-", "−")
    return s


def render_node(node: Dict[str, Any]) -> str:
    if not node:
        return ""

    t = node.get("type")

    # 1. Атомарные
    if t == "integer":
        return fmt_number(node["value"])
    if t == "variable":
        return str(node["name"])

    # 2. Степень
    if t == "power":
        base = render_node(node["base"])
        exp_node = node["exp"]
        exp_str = ""
        is_simple = False

        if exp_node.get("type") == "integer":
            exp_str = to_superscript(exp_node["value"])
            is_simple = True
        elif (exp_node.get("type") == "product" and
              len(exp_node.get("factors", [])) == 2 and
              exp_node["factors"][0].get("value") == -1):
            val = render_node(exp_node["factors"][1]).replace("(", "").replace(")", "")
            exp_str = "⁻" + to_superscript(val)
            is_simple = True

        if is_simple:
            # Скобки для сложной базы
            if node["base"].get("type") in ("power", "product", "fraction", "binary_op"):
                return f"({base}){exp_str}"
            return f"{base}{exp_str}"
        else:
            return f"({base})^({render_node(exp_node)})"

    # 3. Произведение (Product) - здесь была ошибка
    if t == "product":
        raw_factors = node.get("factors", [])
        if not raw_factors: return ""

        rendered_factors = []
        for f in raw_factors:
            s = render_node(f) or "?" # Защита от None
            if f.get("type") == "binary_op":
                s = f"({s})"
            rendered_factors.append(s)

        result_parts = []
        for i in range(len(raw_factors) - 1):
            left_node = raw_factors[i]
            right_node = raw_factors[i+1]
            left_str = rendered_factors[i]  # Это строка, не None

            l_type = left_node.get("type")
            r_type = right_node.get("type")

            # Неявное умножение
            implicit = False
            if l_type == "integer" and r_type in ("sqrt", "variable"): implicit = True
            elif l_type == "variable" and r_type in ("sqrt", "variable"): implicit = True
            # Число/Переменная + Степень (если база переменная)
            elif l_type in ("integer", "variable") and r_type == "power":
                if right_node["base"].get("type") == "variable": implicit = True

            if l_type == "binary_op" or r_type == "binary_op": implicit = False

            # Прячем 1 и -1 (1a -> a)
            if l_type == "integer" and implicit:
                val = left_node.get("value")
                if val == 1: left_str = ""
                elif val == -1: left_str = "−"

            separator = "" if implicit else " · "
            result_parts.append(left_str + separator)

        result_parts.append(rendered_factors[-1])
        return "".join(result_parts)

    # 4. Дробь (Fraction) - Твоя правка здесь
    if t == "fraction":
        num = render_node(node["numerator"])
        den = render_node(node["denominator"])

        # Числитель: Product опасен -> скобки
        safe_num = ("integer", "variable", "power", "sqrt")
        if node["numerator"].get("type") not in safe_num:
            num = f"({num})"

        # Знаменатель: Sqrt безопасен -> без скобок
        safe_den = ("integer", "variable", "power", "sqrt")
        if node["denominator"].get("type") not in safe_den:
            den = f"({den})"

        return f"{num} / {den}"

    # 5. Остальное
    if t == "sqrt":
        rad = render_node(node["radicand"])
        if node["radicand"].get("type") in ("product", "fraction", "binary_op"):
            return f"√({rad})"
        return f"√{rad}"

    if t == "binary_op":
        l = render_node(node["left"])
        r = render_node(node["right"])
        op = node["op"]
        if op == "-": op = "−"
        return f"{l} {op} {r}"

    if t == "range_query":
        l = render_node(node["left"])
        r = render_node(node["right"])
        return f"{l} и {r}"

    return "?"
