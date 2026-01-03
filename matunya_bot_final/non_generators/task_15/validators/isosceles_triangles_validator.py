import re
from typing import Any, Dict

ANGLE_SYMBOL = "∠"

class IsoscelesValidator:
    """Валидатор для ТЕМЫ 3: Равнобедренные и равносторонние треугольники."""

    def __init__(self) -> None:
        self.handlers = {
            "isosceles_triangle_angles": self._handle_isosceles_angles,
            "equilateral_height_to_side": self._handle_equilateral_height,
            "equilateral_side_to_element": self._handle_equilateral_elements,
        }

    def validate(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        pattern = raw.get("pattern")
        if pattern not in self.handlers:
            raise ValueError(f"Неизвестный паттерн в ТЕМЕ 3: {pattern}")
        return self.handlers[pattern](raw)

    # -----------------------------------------------------------
    # Паттерн 3.1: Углы в равнобедренном треугольнике
    # -----------------------------------------------------------
    def _handle_isosceles_angles(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        text = raw["text"]
        task_id = raw.get("id")

        # 1. Извлекаем число
        val_match = re.search(r"(\d+)", text)
        if not val_match:
            raise ValueError(f"Число не найдено в задаче {task_id}")
        val = int(val_match.group(1))

        # 2. Детекция букв
        triangle_name = "ABC"
        tr_match = re.search(r"треугольнике\s+([A-Z]{3})", text)
        if tr_match: triangle_name = tr_match.group(1)

        vertex_letter = ""
        pair_match = re.search(r"([A-Z]{2})\s*(?:и|=)\s*([A-Z]{2})", text)
        if pair_match:
            s1, s2 = pair_match.groups()
            common = list(set(s1) & set(s2))
            if common: vertex_letter = common[0]

        # 3. УЛЬТРА-ДЕТЕКЦИЯ РОЛИ
        given_role = None

        # А) Математический фильтр: угол при основании всегда < 90
        if val >= 90:
            given_role = "vertex"

        if not given_role:
            # Ищем явные связки "роль ... равен [число]" или "[число] ... роль"
            # Проверяем контекст в обе стороны от числа
            val_start = val_match.start()
            val_end = val_match.end()

            # Берем кусок текста ДО числа и чуть-чуть ПОСЛЕ
            prefix = text[max(0, val_start-60):val_start].lower()
            suffix = text[val_end:val_end+20].lower()

            vertex_kw = ["вершин", "противолежащ", "между боков", "напротив", "вершина"]
            base_kw = ["основан"]

            # ПРИОРИТЕТ 1: Если слово "основании" совсем рядом с числом в ПРЕФИКСЕ
            if any(kw in prefix[-30:] for kw in base_kw):
                given_role = "base"
            # ПРИОРИТЕТ 2: Если слова вершины рядом в ПРЕФИКСЕ
            elif any(kw in prefix[-30:] for kw in vertex_kw):
                given_role = "vertex"
            # ПРИОРИТЕТ 3: Поиск по всему префиксу (условию)
            elif any(kw in prefix for kw in base_kw):
                given_role = "base"
            elif any(kw in prefix for kw in vertex_kw):
                given_role = "vertex"

        # 4. Фоллбэк по буквам или умолчанию
        if not given_role:
            angle_name_match = re.search(r"угол\s+([A-Z])", text[:val_match.start()])
            if angle_name_match and vertex_letter:
                given_role = "vertex" if angle_name_match.group(1) == vertex_letter else "base"
            else:
                given_role = "vertex"

        # 5. Расчет
        if given_role == "vertex":
            narrative = "find_base_angle"
            answer = (180 - val) / 2
        else:
            narrative = "find_vertex_angle"
            answer = 180 - (val * 2)

        # 6. Сбор данных для Humanizer
        all_letters = list(triangle_name)
        base_letters = sorted([c for c in all_letters if c != vertex_letter])

        find_match = re.search(r"(?:Найди|Вычисли|Определи|Чему равен).*?угол\s+([A-Z])", text, re.IGNORECASE)
        target_letter = find_match.group(1) if find_match else ""
        if not target_letter:
            target_letter = base_letters[0] if narrative == "find_base_angle" and base_letters else vertex_letter

        return {
            "id": task_id,
            "pattern": "isosceles_triangle_angles",
            "narrative": narrative,
            "text": text,
            "answer": int(answer) if float(answer).is_integer() else answer,
            "image_file": None,
            "variables": {
                "given": {
                    "triangle_name": triangle_name,
                    "angle": {"value": val, "role": given_role, "letter": vertex_letter if given_role == "vertex" else ""}
                },
                "to_find": {"role": "base" if narrative == "find_base_angle" else "vertex", "letter": target_letter},
                "humanizer_data": {
                    "vertex_letter": vertex_letter,
                    "base_letters": base_letters,
                    "angle_symbol": ANGLE_SYMBOL
                }
            }
        }

    # -----------------------------------------------------------
    # Паттерн 3.2: Сторона равностороннего треугольника по высоте
    # -----------------------------------------------------------
    def _handle_equilateral_height(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        text = raw["text"]
        task_id = raw.get("id")

        # 1. Извлекаем коэффициент перед корнем (например, "19" из "19√3")
        match = re.search(r"(\d+)\s*(?:√|корн|sqrt)", text)

        if match:
            k = int(match.group(1))
            has_root = True
        else:
            match_simple = re.search(r"(\d+)", text)
            if not match_simple:
                raise ValueError(f"Числовые данные не найдены в задаче {task_id}")
            k = int(match_simple.group(1))
            has_root = False

        # 2. Расчет: если h = k√3, то a = 2k
        if has_root:
            answer = k * 2
        else:
            answer = (2 * k) / (3**0.5)

        return {
            "id": task_id,
            "pattern": "equilateral_height_to_side",
            "narrative": "find_side_by_height",
            "text": text,
            "answer": int(answer) if float(answer).is_integer() else round(answer, 2),
            "image_file": "T1_equilateral_height_to_side.png", # Путь исправлен
            "variables": {
                "given": {
                    "triangle_type": "equilateral",
                    "element": "height",
                    "value_raw": f"{k}√3" if has_root else str(k),
                    "coefficient": k,
                    "has_root": has_root
                },
                "to_find": {
                    "element": "side"
                },
                "humanizer_data": {
                    "k": k,
                    "formula": "a = 2h / √3"
                }
            }
        }

    # -----------------------------------------------------------
    # Паттерн 3.3: Высота/медиана/биссектриса по стороне
    # -----------------------------------------------------------
    def _handle_equilateral_elements(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        text = raw["text"]
        task_id = raw.get("id")

        # 1. Извлекаем коэффициент k из "k√3"
        match = re.search(r"(\d+)\s*(?:√|корн|sqrt)", text)
        if not match:
            # Если корня нет, ищем просто число (например, "сторона 10 см")
            match_simple = re.search(r"(\d+)", text)
            if not match_simple:
                raise ValueError(f"Данные не найдены в задаче {task_id}")
            k_val = int(match_simple.group(1))
            has_root = False
        else:
            k_val = int(match.group(1))
            has_root = True

        # 2. Определяем, ЧТО ищем (для нарратива)
        if "медиан" in text:
            target = "median"
        elif "биссектрис" in text:
            target = "bisector"
        else:
            target = "height"

        # 3. Расчет: h = (a * √3) / 2. Если a = k√3, то h = 1.5 * k
        if has_root:
            answer = k_val * 1.5
        else:
            # Если сторона дана без корня: h = (k * 1.73...) / 2 -> в ОГЭ это редкость
            answer = (k_val * (3**0.5)) / 2

        return {
            "id": task_id,
            "pattern": "equilateral_side_to_element",
            "narrative": f"find_{target}_by_side",
            "text": text,
            "answer": int(answer) if float(answer).is_integer() else round(answer, 1),
            "image_file": "T1_equilateral_side_to_element.png",
            "variables": {
                "given": {
                    "side_value": f"{k_val}√3" if has_root else str(k_val),
                    "k": k_val,
                    "has_root": has_root
                },
                "to_find": {"element": target},
                "humanizer_data": {
                    "target_name": target,
                    "k": k_val
                }
            }
        }
