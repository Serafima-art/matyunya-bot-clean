# math_symbols.py

SUPERSCRIPT_MAP = {
    "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
    "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹",
    "-": "⁻", "+": "⁺"
}


def to_superscript(value: int | str) -> str:
    s = str(value)
    return "".join(SUPERSCRIPT_MAP.get(ch, ch) for ch in s)


def render_power(base: str, exponent: int | str) -> str:
    return f"{base}{to_superscript(exponent)}"
