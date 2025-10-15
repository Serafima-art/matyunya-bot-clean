from typing import Dict, Any, Optional
import math
import re
import random
from fractions import Fraction


# 🔧 Вспомогательные утилиты
from matunya_bot_final.utils import answer_utils as AC
from matunya_bot_final.gpt.verification import verification_utils as VU

# === Верификаторы ===
def _verify_and_process_point_to_root(gpt_response: Dict[str, Any], tol: float = 1e-9) -> Optional[Dict[str, Any]]:
    """
    Подтип: 'point_to_root' (обязательна картинка).
    Логика:
      1) options: 4 штуки '√n', n>1, n не идеальный квадрат, все разные (с нормализацией формата).
      2) Если image_params нет — синтезируем A.pos и (min_val,max_val) без correct_answer_value.
      3) A строго внутри (min_val; max_val).
      4) Ровно один корень лежит в том же [k; k+1).
    """
    try:
        options = gpt_response.get("options") or []
        if not (isinstance(options, list) and len(options) == 4):
            print("[DBG p2r] bad options len:", options)
            return None

        ns: list[int] = []
        sqrt_vals: list[float] = []
        cleaned_opts: list[str] = []
        for opt in options:
            opt_raw = str(opt).strip()
            opt_clean = re.sub(r'^\s*\d+[\)\.:]\s*', '', opt_raw)
            opt_clean = opt_clean.replace(' ', '')
            opt_clean = re.sub(r'^√\(([^)]+)\)$', r'√\1', opt_clean)

            n = VU.parse_sqrt_option(opt_clean)
            if n is None or n <= 1 or VU.is_perfect_square(n):
                return None

            ns.append(n)
            sqrt_vals.append(math.sqrt(n))
            cleaned_opts.append(f"√{n}")

        if not VU.unique(ns):
            return None

        img = gpt_response.get("image_params") or {}
        a_pos = VU.extract_point_pos(img, "A")
        axis = VU.validate_axis(img)

        if a_pos is None or axis is None:
            floors = [math.floor(v) for v in sqrt_vals]
            counts: dict[int, int] = {}
            for f in floors:
                counts[f] = counts.get(f, 0) + 1

            cand_idx = None
            for i, f in enumerate(floors):
                if counts.get(f, 0) == 1:
                    cand_idx = i
                    break
            if cand_idx is None:
                return None

            k = floors[cand_idx]
            a_pos = k + 0.5
            min_val = k
            max_val = k + 2
            img = {"min_val": min_val, "max_val": max_val, "points": [{"label": "A", "pos": a_pos}]}
            axis = (min_val, max_val)

        min_val, max_val = axis

        if not VU.strictly_between(a_pos, min_val, max_val, tol):
            return None

        k = math.floor(a_pos)
        if not (k >= min_val and (k + 1) <= max_val):
            return None

        inside: list[int] = []
        for idx, val in enumerate(sqrt_vals):
            if (val > k - tol) and (val < (k + 1) - tol):
                inside.append(idx)
        if len(inside) != 1:
            return None

        return {
            "answer": cleaned_opts[inside[0]],
            "answer_index": inside[0],
            "image_params": img
        }

    except Exception as e:
        print(f"[ERROR] point_to_root: {e}")
        return None

def _verify_point_to_fraction_decimal(gpt_response: Dict[str, Any], tol: float = 1e-4) -> Optional[Dict[str, Any]]:
    """
    (ФИНАЛЬНАЯ ВЕРСЯ)
    Подтип: 'point_to_fraction_decimal'.
    Проверяет, что ровно одна из дробей в options соответствует точке.
    """
    try:
        options = gpt_response.get('options', [])
        img = gpt_response.get('image_params', {}) or {}
        points = img.get('points', []) or []
        correct_answer_idx_gpt = gpt_response.get('correct_answer_index')

        # Проверка базовой структуры
        if not all([options, points, len(points) == 1, correct_answer_idx_gpt is not None]):
            print(f"[DEBUG][P2FD] Базовая структура неверна.")
            return None
            
        point_pos = float(points[0].get("pos", 999))

        # Ищем, какой из вариантов ответа соответствует точке
        match_index = -1
        for i, opt_str in enumerate(options):
            # Используем наш универсальный парсер, который умеет читать дроби "a/b"
            opt_val = AC.parse_user_answer(opt_str) 
            if opt_val is not None and abs(float(opt_val) - point_pos) <= tol:
                if match_index != -1: 
                    print(f"[WARN][P2FD] Найдено несколько совпадений. Брак.")
                    return None
                match_index = i
        
        if match_index == -1:
            print(f"[DEBUG][P2FD] Совпадений: 0. Брак.")
            return None

        # Наш 100% правильный ответ (индекс)
        our_correct_index = match_index
        
        if our_correct_index != correct_answer_idx_gpt:
            print(f"[WARN] GPT ошибся в индексе. Наш: {our_correct_index}, GPT: {correct_answer_idx_gpt}. Исправляем.")

        # В ответе просят номер варианта (1, 2, 3, 4)
        final_answer = str(our_correct_index + 1)
        
        # Возвращаем только проверенный ответ и image_params
        return {
            "answer": final_answer,
            "image_params": img
        }

    except Exception as e:
        print(f"[ERROR] _verify_point_to_fraction_decimal: {e}")
        return None

def _verify_root_to_point(gpt_response: Dict[str, Any], tol: float = 1e-9) -> Optional[Dict[str, Any]]:
    """(ФИНАЛЬНАЯ ВЕРСИЯ 7.0) 'root_to_point'."""
    try:
        text = gpt_response.get('text', '')
        options = gpt_response.get('options', [])
        
        if options != ["A", "B", "C", "D"]: return None

        # --- ИСПРАВЛЕННОЕ РЕГУЛЯРНОЕ ВЫРАЖЕНИЕ ---
        # Оно будет искать:
        # -√7 | √0.2 | -0.5 | 3/4 | 5
        pattern = r'[-]?\d+/\d+|[-]?√[\d\.,]+|[-]?\d+,\d+|[-]?\d+'
        all_numbers_found = re.findall(pattern, text.replace('−', '-'))
        # --- КОНЕЦ ИСПРАВЛЕНИЯ ---
        
        if len(all_numbers_found) < 5:
            print(f"[WARN] Найдено чисел: {len(all_numbers_found)} ({all_numbers_found}), а ожидалось 5 (4+1).")
            return None
        
        numbers_str = all_numbers_found[:4]
        target_str = all_numbers_found[-1]

        if len(set(numbers_str)) != 4:
             print(f"[WARN] Числа для точек не уникальны: {numbers_str}.")
             return None

        number_values = {}
        for s in numbers_str:
            parsed_val = AC.parse_user_answer(s)
            if parsed_val is None: return None
            number_values[s] = float(parsed_val)

        sorted_numbers_str = sorted(number_values.keys(), key=lambda k: number_values[k])
        point_map = {label: num_str for label, num_str in zip(sorted(options), sorted_numbers_str)}
        
        correct_answer_label = None
        for label, number_str in point_map.items():
            if number_str == target_str:
                correct_answer_label = label
                break
        if not correct_answer_label: return None
        
        correct_answer_index = options.index(correct_answer_label)

        points_for_image = [{"label": label, "pos": number_values[num_str]} for label, num_str in point_map.items()]
        all_pos = [p['pos'] for p in points_for_image]

        return {
            "answer": str(correct_answer_index + 1),
            "image_params": {
                "min_val": math.floor(min(all_pos)) - 1,
                "max_val": math.ceil(max(all_pos)) + 1,
                "points": points_for_image
            }
        }
    except Exception as e:
        print(f"[ERROR] _verify_root_to_point: {e}")
        return None

    
def _verify_point_to_fraction(gpt_response: Dict[str, Any], tol: float = 1e-9) -> Optional[Dict[str, Any]]:
    """
    Подтип: 'point_to_fraction'.
    Пример: "Одна из точек ... соответствует числу 65/8. Какая это точка?"
    """
    try:
        text = gpt_response.get('text', '')
        options = gpt_response.get('options', [])
        img = gpt_response.get('image_params', {}) or {}
        points = img.get('points', [])
        correct_answer_idx_gpt = gpt_response.get('correct_answer_index')

        # 1. Базовые проверки
        if not all([options, points, len(points) == 4, correct_answer_idx_gpt is not None]):
            return None

        # 2. Извлекаем целевую дробь из текста
        target_fraction_match = re.search(r'числу\s+([-]?\d+/\d+)', text)
        if not target_fraction_match: return None
        target_fraction_str = target_fraction_match.group(1)
        target_val = float(AC.parse_user_answer(target_fraction_str))

        # 3. Находим точку, которая ближе всего к значению дроби
        point_positions = {p.get("label"): p.get("pos") for p in points}
        closest_point_label = min(point_positions, key=lambda p: abs(point_positions[p] - target_val))

        # 4. Формируем наш 100% правильный ответ
        our_correct_option_text = f"точка {closest_point_label}"
        if our_correct_option_text not in options: return None
        
        our_correct_index = options.index(our_correct_option_text)
        
        if our_correct_index != correct_answer_idx_gpt:
            print(f"[WARN] GPT ошибся в индексе. Наш: {our_correct_index}, GPT: {correct_answer_idx_gpt}. Исправляем.")

        final_answer = str(our_correct_index + 1)
        
        return {
            "answer": final_answer,
            "image_params": img
        }
    except Exception as e:
        print(f"[ERROR] _verify_point_to_fraction: {e}")
        return None 
    
def _verify_decimal_to_point(gpt_response: Dict[str, Any], tol: float = 1e-9) -> Optional[Dict[str, Any]]:
    """(ТВОЯ ЛОГИКА) 'decimal_to_point'."""
    try:
        text = gpt_response.get('text', '')
        options = gpt_response.get('options', [])
        
        if options != ["A", "B", "C", "D"]: return None

        # --- ТВОЙ УМНЫЙ ПОИСК v7.0 ---
        all_numbers_found = re.findall(r'[-]?\d+,\d+', text)
        if len(all_numbers_found) < 5:
            print(f"[WARN] Найдено чисел: {len(all_numbers_found)}, а ожидалось 5 (4+1).")
            return None
        
        numbers_str = all_numbers_found[:4]  # Первые 4 - это числа для точек
        target_str = all_numbers_found[-1]   # Последнее - это целевое число
        # --- КОНЕЦ УМНОГО ПОИСКА ---
        
        if len(set(numbers_str)) != 4:
             print(f"[WARN] Числа для точек не уникальны: {numbers_str}.")
             return None
        
        number_values = {s: float(AC.parse_user_answer(s)) for s in numbers_str}
        sorted_numbers_str = sorted(number_values.keys(), key=lambda k: number_values[k])

        point_map = {label: num_str for label, num_str in zip(sorted(options), sorted_numbers_str)}
        
        correct_answer_label = None
        for label, number_str in point_map.items():
            if number_str == target_str:
                correct_answer_label = label
                break
        if not correct_answer_label: return None
        
        correct_answer_index = options.index(correct_answer_label)

        points_for_image = [{"label": label, "pos": number_values[num_str]} for label, num_str in point_map.items()]
        all_pos = [p['pos'] for p in points_for_image]

        return {
            "answer": str(correct_answer_index + 1),
            "image_params": {
                "min_val": math.floor(min(all_pos)) - 1,
                "max_val": math.ceil(max(all_pos)) + 1,
                "points": points_for_image
            }
        }
    except Exception as e:
        print(f"[ERROR] _verify_decimal_to_point: {e}")
        return None
    
def _verify_variable_on_line(gpt_response: Dict[str, Any], tol: float = 1e-9) -> Optional[Dict[str, Any]]:
    """(ИСПРАВЛЕННАЯ ГЕНЕРИРУЮЩАЯ ВЕРСЯ)"""
    try:
        text = gpt_response.get('text', '')
        
        variable_label_match = re.search(r'число\s+([a-z])', text)
        if not variable_label_match: return None
        variable_label = variable_label_match.group(1)

        min_val = random.randint(-5, 5)
        max_val = min_val + 4
        a_pos = round(random.uniform(min_val + 0.5, max_val - 0.5), 1)

        image_params = {
            "min_val": min_val, "max_val": max_val,
            "points": [{"label": variable_label, "pos": a_pos}]
        }

        m_values = list(range(math.floor(a_pos) - 1, math.ceil(a_pos) + 2))
        
        potential_options = []
        for m in m_values:
            potential_options.append(f"{variable_label} - {m} > 0")
            potential_options.append(f"{variable_label} - {m} < 0")
            potential_options.append(f"{m} - {variable_label} > 0")
            potential_options.append(f"{m} - {variable_label} < 0")
        
        true_options = []
        false_options = []
        for opt in potential_options:
            eval_str = opt.replace(variable_label, str(a_pos)).replace('--', '+')
            if eval(eval_str):
                true_options.append(opt)
            else:
                false_options.append(opt)
        
        if not true_options or len(false_options) < 3: return None

        # --- ИСПРАВЛЕНИЕ ЗДЕСЬ ---
        # Сначала выбираем ОДИН правильный ответ
        our_correct_answer = random.choice(true_options)
        # Потом выбираем ТРИ неправильных
        final_false_options = random.sample(false_options, 3)
        
        # Собираем финальный список и перемешиваем
        final_options = [our_correct_answer] + final_false_options
        random.shuffle(final_options)
        
        # И только ТЕПЕРЬ ищем индекс
        our_correct_index = final_options.index(our_correct_answer)
        final_answer = str(our_correct_index + 1)
        # --- КОНЕЦ ИСПРАВЛЕНИЯ ---
        
        # Перезаписываем 'options' в gpt_response, чтобы они соответствовали
        gpt_response['options'] = final_options

        return {
            "answer": final_answer,
            "image_params": image_params,
            "options": final_options # Возвращаем новые options
        }
    except Exception as e:
        print(f"[ERROR] _verify_variable_on_line: {e}")
        return None
    
def _verify_root_in_integer_interval(gpt_response: Dict[str, Any], tol: float = 1e-9) -> Optional[Dict[str, Any]]:
    """
    (ГЕНЕРИРУЮЩАЯ ВЕРСИЯ)
    Берет ТОЛЬКО текст от GPT. САМ генерирует options и answer.
    """
    try:
        text = gpt_response.get('text', '')
        
        # 1. Извлекаем промежуток из текста, например [7;8]
        interval_match = re.search(r'промежутку\s*([(\[])\s*(\d+)\s*;\s*(\d+)\s*([)\]])', text)
        if not interval_match: return None
        
        left_bracket, min_val_str, max_val_str, right_bracket = interval_match.groups()
        min_val = int(min_val_str)
        max_val = int(max_val_str)

        # 2. САМИ ГЕНЕРИРУЕМ КОРРЕКТНЫЕ ВАРИАНТЫ
        min_sq = min_val**2
        max_sq = max_val**2
        
        # Генерируем ОДИН правильный ответ
        # (с небольшими отступами от границ, чтобы было честно)
        correct_n = random.randint(min_sq + (1 if left_bracket == '(' else 0), max_sq - (1 if right_bracket == ')' else 0))
        
        # Генерируем ТРИ неправильных
        false_options_n = []
        # Один левее
        false_options_n.append(random.randint(min_sq - 5, min_sq - (1 if left_bracket == '(' else 0)))
        # Два правее
        false_options_n.append(random.randint(max_sq + (1 if right_bracket == ')' else 0), max_sq + 5))
        false_options_n.append(random.randint(max_sq + 6, max_sq + 10))
        
        # 3. Собираем и перемешиваем
        final_options_n = [correct_n] + false_options_n
        random.shuffle(final_options_n)
        
        final_options_str = [f"√{n}" for n in final_options_n]
        our_correct_answer_str = f"√{correct_n}"
        our_correct_index = final_options_str.index(our_correct_answer_str)
        final_answer = str(our_correct_index + 1)
        
        # Перезаписываем options в ответе от GPT
        gpt_response['options'] = final_options_str

        return { "answer": final_answer }

    except Exception as e:
        print(f"[ERROR] _verify_root_in_integer_interval: {e}")
        return None
    
def _verify_fraction_in_decimal_interval(gpt_response: Dict[str, Any], tol: float = 1e-9) -> Optional[Dict[str, Any]]:
    """
    Подтип: 'fraction_in_decimal_interval'.
    Пример: "Какому из промежутков принадлежит число 7/11?"
    """
    try:
        text = gpt_response.get('text', '')
        options = gpt_response.get('options', [])
        correct_answer_idx_gpt = gpt_response.get('correct_answer_index')

        # 1. Извлекаем целевое число (дробь или десятичное) из текста
        target_match = re.search(r'число\s+([-]?[\d,./]+)', text)
        if not target_match: return None
        target_val = float(AC.parse_user_answer(target_match.group(1)))

        # 2. Ищем единственного кандидата-промежутка, который подходит
        match_index = -1
        for i, opt_str in enumerate(options):
            # Парсим промежуток, например "[0,6; 0,7]"
            interval_match = re.search(r'([(\[])\s*([-]?\d+,\d+)\s*;\s*([-]?\d+,\d+)\s*([)\]])', opt_str)
            if not interval_match: continue

            left_bracket, min_str, max_str, right_bracket = interval_match.groups()
            min_val = float(min_str.replace(',', '.'))
            max_val = float(max_str.replace(',', '.'))
            
            # Проверяем вхождение
            left_ok = (target_val > min_val + tol) if left_bracket == '(' else (target_val >= min_val - tol)
            right_ok = (target_val < max_val - tol) if right_bracket == ')' else (target_val <= max_val + tol)

            if left_ok and right_ok:
                if match_index != -1: return None # Нашли второе совпадение - брак
                match_index = i
        
        if match_index == -1: return None # Не нашли ни одного

        # 3. Проверяем и исправляем ответ GPT
        our_correct_index = match_index
        if our_correct_index != correct_answer_idx_gpt:
            print(f"[WARN] GPT ошибся в индексе. Наш: {our_correct_index}, GPT: {correct_answer_idx_gpt}. Исправляем.")

        final_answer = str(our_correct_index + 1)
        
        return { "answer": final_answer }

    except Exception as e:
        print(f"[ERROR] _verify_fraction_in_decimal_interval: {e}")
        return None
    
def _verify_decimal_between_fractions(gpt_response: Dict[str, Any], tol: float = 1e-9) -> Optional[Dict[str, Any]]:
    """
    Подтип: 'decimal_between_fractions'.
    Пример: "Какое из чисел ... заключено между 2/13 и 4/15?"
    """
    try:
        text = gpt_response.get('text', '')
        options = gpt_response.get('options', [])
        correct_answer_idx_gpt = gpt_response.get('correct_answer_index')

        # 1. Извлекаем две дроби-границы из текста
        fractions_str = re.findall(r'[-]?\d+/\d+', text)
        
        if len(fractions_str) != 2: return None
        
        border1 = float(AC.parse_user_answer(fractions_str[0]))
        border2 = float(AC.parse_user_answer(fractions_str[1]))
        
        min_border = min(border1, border2)
        max_border = max(border1, border2)

        # 2. Ищем единственного кандидата, который подходит
        match_index = -1
        for i, opt_str in enumerate(options):
            opt_val = AC.parse_user_answer(opt_str)
            if opt_val is None: continue # Пропускаем, если не удалось распознать
            opt_val = float(opt_val)
            
            if (opt_val > min_border + tol) and (opt_val < max_border - tol):
                if match_index != -1: return None # Нашли второе совпадение - брак
                match_index = i
        
        if match_index == -1: return None # Не нашли ни одного

        # 3. Проверяем и исправляем ответ GPT
        our_correct_index = match_index
        if our_correct_index != correct_answer_idx_gpt:
            print(f"[WARN] GPT ошибся в индексе. Наш: {our_correct_index}, GPT: {correct_answer_idx_gpt}. Исправляем.")

        final_answer = str(our_correct_index + 1)
        
        return { "answer": final_answer }

    except Exception as e:
        print(f"[ERROR] _verify_decimal_between_fractions: {e}")
        return None
    
def _verify_integer_between_roots(gpt_response: Dict[str, Any], tol: float = 1e-9) -> Optional[Dict[str, Any]]:
    """
    Подтип: 'integer_between_roots'.
    Пример: "Какое из чисел ... заключено между 3√2 и 2√3?"
    """
    try:
        text = gpt_response.get('text', '')
        options = gpt_response.get('options', [])
        correct_answer_idx_gpt = gpt_response.get('correct_answer_index')

        # 1. Извлекаем два корня-границы из текста
        roots_str = re.findall(r'[-]?\d*√\d+', text)
        if len(roots_str) != 2: return None
        
        border1 = float(AC.parse_user_answer(roots_str[0]))
        border2 = float(AC.parse_user_answer(roots_str[1]))
        
        min_border = min(border1, border2)
        max_border = max(border1, border2)

        # 2. Ищем единственного кандидата-целое, который подходит
        match_index = -1
        for i, opt_str in enumerate(options):
            opt_val = AC.parse_user_answer(opt_str)
            if opt_val is None or not isinstance(opt_val, (int, float)) or opt_val != int(opt_val):
                continue # Пропускаем, если вариант - не целое число
            
            opt_val = int(opt_val)
            
            if (opt_val > min_border + tol) and (opt_val < max_border - tol):
                if match_index != -1: return None # Нашли второе совпадение - брак
                match_index = i
        
        if match_index == -1: return None # Не нашли ни одного

        # 3. Проверяем и исправляем ответ GPT
        our_correct_index = match_index
        if our_correct_index != correct_answer_idx_gpt:
            print(f"[WARN] GPT ошибся в индексе. Наш: {our_correct_index}, GPT: {correct_answer_idx_gpt}. Исправляем.")

        final_answer = str(our_correct_index + 1)
        
        return { "answer": final_answer }

    except Exception as e:
        print(f"[ERROR] _verify_integer_between_roots: {e}")
        return None
    
def _verify_expression_analysis_on_line(gpt_response: Dict[str, Any], tol: float = 1e-9) -> Optional[Dict[str, Any]]:
    """(ИСПРАВЛЕННАЯ ГЕНЕРИРУЮЩАЯ ВЕРСИЯ)"""
    try:
        text = gpt_response.get('text', '')
        img = gpt_response.get('image_params', {}) or {}
        points = img.get('points', [])
        
        if not points: return None
        
        var_values = {p.get("label"): p.get("pos") for p in points if p.get("label")}
        if not var_values: return None
        
        question_is_about_false = "неверно?" in text.lower()
        
        variables = list(var_values.keys())
        potential_options = []
        if len(variables) >= 1:
            v1 = variables[0]
            potential_options.extend([f"{v1} > 0", f"{v1} < 0", f"{v1}**2 > 0"])
        if len(variables) >= 2:
            v1, v2 = variables[0], variables[1]
            potential_options.extend([f"{v1} + {v2} > 0", f"{v1} + {v2} < 0", f"{v1} - {v2} > 0", f"{v1} - {v2} < 0", f"{v1} * {v2} > 0", f"{v1} * {v2} < 0"])
        
        true_options = []
        false_options = []
        for opt in potential_options:
            # --- ИСПРАВЛЕНИЕ ЗДЕСЬ ---
            # Создаем "безопасный" словарь для eval
            eval_globals = {"__builtins__": None}
            eval_globals.update(var_values)

            # Разделяем на выражение и проверку
            left_expr, sign, right_val = re.split(r'\s*([<>])\s*', opt)
            
            # Безопасно вычисляем левую часть
            result = eval(left_expr, eval_globals)
            
            # --- КОНЕЦ ИСПРАВЛЕНИЯ ---
            if (sign == '>' and result > 0) or (sign == '<' and result < 0):
                true_options.append(opt)
            else:
                false_options.append(opt)
        
        if question_is_about_false:
            if not false_options or len(true_options) < 3: return None
            our_correct_answer = random.choice(false_options)
            final_false_options = random.sample(true_options, 3)
        else:
            if not true_options or len(false_options) < 3: return None
            our_correct_answer = random.choice(true_options)
            final_false_options = random.sample(false_options, 3)
            
        final_options = [our_correct_answer] + final_false_options
        random.shuffle(final_options)
        
        our_correct_index = final_options.index(our_correct_answer)
        final_answer = str(our_correct_index + 1)
        
        gpt_response['options'] = final_options
        
        return {
            "answer": final_answer,
            "image_params": img,
            "options": final_options
        }
    except Exception as e:
        print(f"[ERROR] _verify_expression_analysis_on_line: {e}")
        return None
    
def _verify_number_in_set(gpt_response: Dict[str, Any], tol: float = 1e-9) -> Optional[Dict[str, Any]]:
    """
    Подтип: 'number_in_set'.
    Пример: "Какое из чисел ... принадлежит отрезку [8; 9]?"
    """
    try:
        text = gpt_response.get('text', '')
        options = gpt_response.get('options', [])
        correct_answer_idx_gpt = gpt_response.get('correct_answer_index')

        # 1. Извлекаем промежуток из текста, например [8; 9]
        interval_match = re.search(r'отрезку\s*\[\s*(\d+)\s*;\s*(\d+)\s*\]', text)
        if not interval_match: return None
        
        min_val = int(interval_match.group(1))
        max_val = int(interval_match.group(2))

        # 2. Ищем единственного кандидата-дробь, который подходит
        match_index = -1
        for i, opt_str in enumerate(options):
            opt_val = AC.parse_user_answer(opt_str)
            if opt_val is None: continue
            
            # Проверяем вхождение в отрезок [min; max]
            if (float(opt_val) >= min_val - tol) and (float(opt_val) <= max_val + tol):
                if match_index != -1: return None # Нашли второе совпадение - брак
                match_index = i
        
        if match_index == -1: return None # Не нашли ни одного

        # 3. Проверяем и исправляем ответ GPT
        our_correct_index = match_index
        if our_correct_index != correct_answer_idx_gpt:
            print(f"[WARN] GPT ошибся в индексе. Наш: {our_correct_index}, GPT: {correct_answer_idx_gpt}. Исправляем.")

        final_answer = str(our_correct_index + 1)
        
        return { "answer": final_answer }

    except Exception as e:
        print(f"[ERROR] _verify_number_in_set: {e}")
        return None
    
def _verify_difference_analysis_on_line(gpt_response: Dict[str, Any], tol: float = 1e-9) -> Optional[Dict[str, Any]]:
    """(ГЕНЕРИРУЮЩАЯ ВЕРСИЯ) 'difference_analysis_on_line'."""
    try:
        text = gpt_response.get('text', '')
        options = gpt_response.get('options', [])
        correct_answer_idx_gpt = gpt_response.get('correct_answer_index')

        # 1. Извлекаем переменные из текста (x, y, z)
        variables = re.findall(r'\b([a-z])\b', text)
        unique_vars = sorted(list(set(v for v in variables if v in "xyzmnkstuabcdef")))
        if len(unique_vars) < 2: return None

        # 2. САМИ ГЕНЕРИРУЕМ для них случайные позиции
        positions = sorted(random.sample(range(-5, 6), len(unique_vars)))
        var_values = {var: pos for var, pos in zip(unique_vars, positions)}
        
        question_is_positive = "положительна?" in text.lower()
        
        # 3. Находим правильный ответ
        match_index = -1
        # ... (здесь будет та же логика проверки, что и раньше)
        for i, opt_str in enumerate(options):
            if "ни одна" in opt_str.lower(): continue
            parts = re.split(r'\s*-\s*', opt_str.strip())
            if len(parts) != 2: continue
            var1, var2 = parts
            if var1 in var_values and var2 in var_values:
                result = var_values[var1] - var_values[var2]
                if (question_is_positive and result > 0) or (not question_is_positive and result < 0):
                    if match_index != -1: return None
                    match_index = i
        
        if match_index == -1:
            for i, opt_str in enumerate(options):
                if "ни одна" in opt_str.lower():
                    match_index = i; break
        if match_index == -1: return None
        
        our_correct_index = match_index
        if our_correct_index != correct_answer_idx_gpt:
            print(f"[WARN] GPT ошибся в индексе. Наш: {our_correct_index}, GPT: {correct_answer_idx_gpt}. Исправляем.")

        final_answer = str(our_correct_index + 1)
        
        # 4. Собираем image_params
        points = [{"label": var, "pos": pos} for var, pos in var_values.items()]
        all_pos = list(var_values.values())
        image_params = {
            "min_val": min(all_pos) - 1,
            "max_val": max(all_pos) + 1,
            "points": points
        }
        
        return { "answer": final_answer, "image_params": image_params }

    except Exception as e:
        print(f"[ERROR] _verify_difference_analysis_on_line: {e}")
        return None
    
# 📌 Здесь будут другие верификаторы по мере добавления
# Примеры:
# def _verify_and_process_root_to_point(...): ...
# def _verify_and_process_point_to_fraction(...): ...
# def _verify_and_process_variable_on_line(...): ...
# и т.д.
# === Реестр ===
REGISTRY = {
    "point_to_root": {
        "fn": _verify_and_process_point_to_root,
        "needs_image": True,
    },
    "point_to_fraction_decimal": {
        "fn": _verify_point_to_fraction_decimal,
        "needs_image": True,
    },
    "root_to_point": {
        "fn": _verify_root_to_point,
        "needs_image": True,
    },
    "point_to_fraction": {
        "fn": _verify_point_to_fraction,
        "needs_image": True,
    },
    "decimal_to_point": {
        "fn": _verify_decimal_to_point,
        "needs_image": True,
    },
    "variable_on_line": {
        "fn": _verify_variable_on_line,
        "needs_image": True,
    },
    "root_in_integer_interval": {
        "fn": _verify_root_in_integer_interval,
        "needs_image": False,
    },
    "fraction_in_decimal_interval": {
        "fn": _verify_fraction_in_decimal_interval,
        "needs_image": False,
    },
    "decimal_between_fractions": {
        "fn": _verify_decimal_between_fractions,
        "needs_image": False,
    },
    "integer_between_roots": {
        "fn": _verify_integer_between_roots,
        "needs_image": False,
    },
    "expression_analysis_on_line": {
        "fn": _verify_expression_analysis_on_line,
        "needs_image": True,
    },
    "number_in_set": {
        "fn": _verify_number_in_set,
        "needs_image": False,
    },
    "difference_analysis_on_line": {
        "fn": _verify_difference_analysis_on_line,
        "needs_image": True,
    }
}