# task_generators/task_12/validators_common.py
import re
import math
from typing import Iterable, Optional

# Число: 12 | 12,5 | .5 | 0.5 | +3 | -2,75
NUM = r"[-+]?(?:\d+(?:[.,]\d+)?|\d*(?:[.,]\d+))"

def to_float(s: str) -> float:
    """Вещественное: запятая→точка, отрезаем хвост-пунктуацию."""
    s = s.strip()
    # убираем случайный хвост типа ';' '.' ',' 'см' 'кг' и т.п. (если не попали регэкспом)
    s = re.sub(r"[^\d,.\-+]+$", "", s)
    return float(s.replace(",", "."))

def _join_alts(xs: Iterable[str]) -> str:
    """Экранируем и склеиваем альтернативы для регэкспа."""
    return "|".join(re.escape(x) for x in xs)

def grab_labeled_number(text: str,
                        labels: Iterable[str],
                        units: Iterable[str] = (),
                        allow_words_equal: bool = True) -> Optional[float]:
    """
    Ищем число по меткам (labels), допускаем ':' или '=' или 'равно/равна'.
    Пример labels: ["F", "сила тяготения", "сила притяжения"]
            units: ["Н"]  (необязательны; если даны — игнорируем их при парсинге)
    Возвращаем float или None.
    """
    lbl = _join_alts(labels)
    unit = _join_alts(units) if units else None

    patterns = [
        rf"(?:{lbl})\s*[:=]\s*({NUM})(?:\s*(?:{unit}))?\b" if unit
        else rf"(?:{lbl})\s*[:=]\s*({NUM})\b",
    ]
    if allow_words_equal:
        patterns.append(
            rf"(?:{lbl})\s*(?:равн[ао]|равно)\s*({NUM})(?:\s*(?:{unit}))?\b" if unit
            else rf"(?:{lbl})\s*(?:равн[ао]|равно)\s*({NUM})\b"
        )

    for p in patterns:
        m = re.search(p, text, flags=re.IGNORECASE)
        if m:
            return to_float(m.group(1))
    return None

def grab_plain_number_after_phrase(text: str, phrase: str, units: Iterable[str] = ()) -> Optional[float]:
    """Вспомогательное: 'масса второго тела = 500 кг' (фраза фиксирована)."""
    unit = _join_alts(units) if units else None
    p = rf"{re.escape(phrase)}\s*[:=]\s*({NUM})(?:\s*(?:{unit}))?\b" if unit \
        else rf"{re.escape(phrase)}\s*[:=]\s*({NUM})\b"
    m = re.search(p, text, flags=re.IGNORECASE)
    return to_float(m.group(1)) if m else None

def grab_any_number_with_unit(text: str, unit: str) -> Optional[float]:
    """Берём первое число, за которым стоит данный юнит (например, '… 12 см …')."""
    m = re.search(rf"({NUM})\s*{re.escape(unit)}\b", text, flags=re.IGNORECASE)
    return to_float(m.group(1)) if m else None

def grab_m_index(text: str, idx_labels: Iterable[str] = ("m₂", "m2", "m 2", "m-2", "m_2")) -> Optional[float]:
    """Поймать массу по обозначению m₂/m2 (с необязательной 'кг')."""
    lbl = _join_alts(idx_labels)
    m = re.search(rf"(?:{lbl})\s*[:=]\s*({NUM})(?:\s*кг)?\b", text, flags=re.IGNORECASE)
    return to_float(m.group(1)) if m else None

def grab_sin_alpha(text: str) -> Optional[float]:
    """
    Ищем sin = ...; поддерживаем школьные '0,5' → 1/2 и '0,866' → √3/2.
    Также понимаем символическую запись '√3/2'.
    """
    # символическая запись
    if re.search(r"sin\s*=\s*√\s*3\s*/\s*2", text):
        return math.sqrt(3) / 2

    m = re.search(r"sin\s*=\s*({NUM})".format(NUM=NUM), text, flags=re.IGNORECASE)
    if not m:
        return None
    raw = m.group(1).replace(",", ".").strip()

    if raw in ("0.5", ".5", "0,5"):
        return 0.5
    if raw in ("0.866", ".866", "0,866"):
        return math.sqrt(3) / 2

    return float(raw)