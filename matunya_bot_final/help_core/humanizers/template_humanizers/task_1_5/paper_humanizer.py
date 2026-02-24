# matunya_bot_final\help_core\humanizers\template_humanizers\task_1_5\paper_humanizer.pyу

import re

from typing import Dict, Any, Callable

from matunya_bot_final.utils.display import format_number

def _format_numeric_values(context: dict) -> dict:
    formatted = {}

    for k, v in context.items():

        # bool не трогаем
        if isinstance(v, bool):
            formatted[k] = v

        # если число — форматируем напрямую
        elif isinstance(v, (int, float)):
            formatted[k] = format_number(v)

        # если строка — аккуратно форматируем числа внутри неё
        elif isinstance(v, str):
            # ищем числа вида 123.45 или 420.0
            def replace_number(match):
                return format_number(match.group())

            new_v = re.sub(r"\d+\.\d+", replace_number, v)
            formatted[k] = new_v

        else:
            formatted[k] = v

    return formatted


# =============================================================================
# 1. ШАБЛОНЫ ТЕКСТОВ (TEMPLATES) — НЕ МЕНЯЕМ ФОРМУЛИРОВКИ
# =============================================================================

IDEA_TEMPLATES: Dict[str, str] = {

    # ------------------------------------------------------------------
    # 🟩 ВОПРОС 1 (Задача на соответствие)
    ## Паттерн paper_format_match
    # ------------------------------------------------------------------

    "match_formats_to_rows":
        "В таблице указаны два столбца:\n\n"
        "<b>Длина (мм) и Ширина (мм).</b>\n\n"
        "Чтобы определить, какой лист больше, удобно сравнить длину.\n"
        "Чем больше длина — тем больше формат листа.\n\n"
        "В серии форматов <b>A</b>:\n"
        "<b>A1 → больше A2 → больше A3 → больше A4 и так далее.</b>",

    # ------------------------------------------------------------------
    # 🟨 ВОПРОС 2 (Задача на разрезание)
    ## Паттерн paper_split
    # ------------------------------------------------------------------

    "count_subformats":
        "Каждый следующий формат получается разрезанием предыдущего пополам.\n"
        "Значит, при каждом переходе к следующему номеру формата \n"
        "количество листов увеличивается в <b>2 раза</b>.\n"
        "Количество листов равно <b>2 в степени разности номеров форматов.</b>",

    # ------------------------------------------------------------------
    # 🟥 ВОПРОС 3 (Прикладная задача: найти длину, ширину, соотношения этих величин)
    ## Паттерн paper_dimensions
    # ------------------------------------------------------------------

    "find_length/width":
        "Если нужного формата нет в таблице, "
        "мы вычислим его через <b>соседний формат</b>.\n\n"
        "❗️ Чем меньше номер формата, тем больше лист.\n\n"
        "Форматы серии A получают, разрезая предыдущий лист пополам.",

    "find_ratio":
        "У всех форматов серии A одинаковое соотношение сторон.\n\n"
        "📌 Если делим бо́льшую сторону на ме́ньшую → всегда получаем примерно <b>1,4</b>.\n"
        "📌 Если делим ме́ньшую сторону на бо́льшую → всегда получаем примерно <b>0,7</b>.\n\n"
        "Нужно только определить, какой порядок деления требуется в условии.",

    "find_diagonal_ratio":
        "Все форматы серии A имеют одинаковое соотношение сторон.\n"
        "Поэтому отношение диагонали к стороне не зависит от номера формата.\n\n"
        "Оно всегда одинаковое:\n\n"
        "🔹 диагональ к ме́ньшей стороне ≈ <b>1,7</b>\n"
        "🔹 диагональ к бо́льшей стороне ≈ <b>1,2</b>",

    # ------------------------------------------------------------------
    # 🟪 ВОПРОС 4 (Прикладная задача: площадь листа)
    ## Паттерн paper_area
    # ------------------------------------------------------------------

    "area_basic":
        "Площадь прямоугольного листа (прямоугольника)\n"
        "равна <b>произведению длины на ширину</b>.\n\n"
        "Размеры в таблице даны в миллиметрах,\n"
        "а ответ требуется в квадратных сантиметрах.",

    "area_with_rounding_10":
        "Площадь прямоугольного листа (прямоугольника)\n"
        "равна <b>произведению длины на ширину</b>.\n\n"
        "Размеры в таблице даны в миллиметрах,\n"
        "а ответ нужен в квадратных сантиметрах.\n\n"
        "Поэтому:\n"
        "1️⃣ переводим миллиметры в сантиметры,\n"
        "2️⃣ вычисляем площадь,\n"
        "3️⃣ округляем результат до ближайшего числа,\n"
        "которое делится на 10.",

    "area_with_rounding_5":
        "Площадь прямоугольника равна:\n\n"
        "<b>S = длина × ширина</b>\n\n"
        "Размеры в таблице даны в миллиметрах,\n"
        "а ответ нужен в квадратных сантиметрах.\n\n"
        "Поэтому:\n"
        "1️⃣ переводим миллиметры в сантиметры,\n"
        "2️⃣ вычисляем площадь,\n"
        "3️⃣ округляем результат до ближайшего числа,\n"
        "которое делится на 5.",

    # ------------------------------------------------------------------
    # 🟫 ВОПРОС 5 (Прикладная задача: масса)
    ## Паттерн paper_pack_weight
    # ------------------------------------------------------------------

    "pack_weight":
        "1️⃣ Площадь листа формата A0 равна 1 м².\n"
        "2️⃣ Масса одного листа пропорциональна его площади.\n"
        "Сначала нужно определить, сколько листов данного формата помещается в 1 м²,\n"
        "затем найти массу одного листа и умножить на количество листов в пачке.",

    # ------------------------------------------------------------------
    # 🟧 ВОПРОС 6 (Прикладная задача: масштабирование)
    ## Паттерн paper_font_scaling
    # ------------------------------------------------------------------

    "font_scaling":
        "Листы серии A подобны друг другу.\n"
        "При переходе к соседнему формату линейные размеры меняются с коэффициентом\n\n"
        "<b>√2 ≈ 1,41</b>\n\n"
        "Правило:\n\n"
        "📈 Лист стал больше на 1 → шрифт умножаем на 1,4.\n"
        "📉 Лист стал меньше на 1 → шрифт делим на 1,4 (или умножаем на 0,7)."
}


STEP_TEMPLATES: Dict[str, str] = {

    # ------------------------------------------------------------------
    # 🟩 ВОПРОС 1 (Задача на соответствие)
    ## Паттерн paper_format_match
    # ------------------------------------------------------------------

    # --- 1️⃣ match_formats_to_rows ---
    "STEP_MATCH_COMPARE": (
        "<b>Шаг 1.</b> Сравним значения длин и определим соответствие форматов.\n"
        "Помним правило: <b>чем меньше номер формата, тем больше лист</b>.\n\n"
        "➡️ <b>строка {row_1}: длина = {len_1} — самое большое число → {format_1}</b>\n\n"
        "➡️ <b>строка {row_2}: длина = {len_2} — следующее по величине → {format_2}</b>\n\n"
        "➡️ <b>строка {row_3}: длина = {len_3} → {format_3}</b>\n\n"
        "➡️ <b>строка {row_4}: длина = {len_4} — самое маленькое число → {format_4}</b>"
    ),

    "STEP_MATCH_SEQUENCE": (
        "<b>Шаг 2.</b> Нас просят записать последовательность для \n"
        "<b>{requested_order}</b>\n\n"
        "➡️ <b>{answer_sequence}</b>"
    ),

    # ------------------------------------------------------------------
    # 🟨 ВОПРОС 2 (Задача на разрезание)
    ## Паттерн paper_split
    # ------------------------------------------------------------------

    # --- 1️⃣ count_subformats ---
    "STEP_SPLIT_DIFF": (
        "<b>Шаг 1.</b> Находим разницу номеров форматов.\n"
        "Больший лист — {from_format}, меньший — {to_format}.\n\n"
        "➡️ <b>{to_index} − {from_index} = {index_difference}</b>\n\n"
        "Значит, нужно сделать {index_difference} {transition_word}.\n\n"
        "➡️ <b>{transition_chain}</b>"
    ),

    "STEP_SPLIT_POWER": (
        "<b>Шаг 2.</b> Каждый переход увеличивает количество листов в 2 раза:\n\n"
        "➡️ <b>{doubling_chain}</b>\n\n"
        "Следовательно,\n\n"
        "➡️ <b>Количество листов = 2{sup_power}</b>\n"
        "➡️ <b>2{sup_power} = {power_value}</b>"
    ),
    # ------------------------------------------------------------------
    # 🟥 ВОПРОС 3 (Прикладная задача: найти длину, ширину, соотношения этих величин)
    ## Паттерн paper_dimensions
    # ------------------------------------------------------------------

    # --- 1️⃣ find_length ---
    "STEP_DIM_LENGTH_1": (
        "<b>Шаг 1.</b> Выберем <b>соседний формат</b>, который есть в таблице\n"
        "и выпишем нужную сторону — <b>ширину</b> этого формата.\n"
        "➡️ <b>Ширина {reference_format} = {reference_width_mm} мм</b>"
    ),
    "STEP_DIM_LENGTH_2": (
        "<b>Шаг 2.</b> Если нам нужен <b>{direction_word}</b> формат, используем правило <b>{rule_word}</b>:\n"
        "➡️ <b>{formula_line}</b>"
    ),
    "STEP_DIM_LENGTH_3": (
        "<b>Шаг 3.</b> Выполним вычисление.\n"
        "➡️ <b>{calc_line}</b>"
    ),
    "STEP_DIM_LENGTH_4_ROUND": (
        "<b>Шаг 4.</b> Округляем <b>{raw_result}</b> до ближайшего числа, кратного <b>{multiple_of}</b>.\n\n"
        "Ближайшие кратные <b>{multiple_of}</b> числа:\n"
        "➡️ <b>{lower_bound} и {upper_bound}</b>\n\n"
        "<b>{raw_result}</b> ближе к <b>{answer}</b>.\n\n"
        "➡️ <b>{raw_result} → {answer}</b>"
    ),

    # --- 2️⃣ find_width ---
    "STEP_DIM_WIDTH_1": (
        "<b>Шаг 1.</b> Выберем <b>соседний формат</b>, который есть в таблице\n"
        "и выпишем нужную сторону — <b>длину</b> этого формата.\n"
        "➡️ <b>Длина {reference_format} = {reference_length_mm} мм</b>"
    ),
    "STEP_DIM_WIDTH_2": (
        "<b>Шаг 2.</b> Если нам нужен <b>{direction_word}</b> формат, используем правило <b>{rule_word}</b>:\n"
        "➡️ <b>{formula_line}</b>"
    ),
    "STEP_DIM_WIDTH_3": (
        "<b>Шаг 3.</b> Выполним вычисление.\n"
        "➡️ <b>{calc_line}</b>"
    ),
    "STEP_DIM_WIDTH_4_ROUND": (
        "<b>Шаг 4.</b> Округляем <b>{raw_result}</b> до ближайшего числа, кратного <b>{multiple_of}</b>.\n\n"
        "Ближайшие кратные <b>{multiple_of}</b> числа:\n"
        "➡️ <b>{lower_bound} и {upper_bound}</b>\n\n"
        "<b>{raw_result}</b> ближе к <b>{answer}</b>.\n\n"
        "➡️ <b>{raw_result} → {answer}</b>"
    ),

    # --- 3️⃣ find_ratio ---
    "STEP_RATIO_ORDER": (
        "<b>Шаг 1.</b> Определяем, что требует задача:\n\n"
        "🔹 {division_order}"
    ),

    "STEP_RATIO_CALC": (
        "<b>Шаг 2.</b> Записываем готовое значение:\n\n"
        "➡️ {division_expression} ≈ <b>{raw_ratio}</b>\n\n"
        "Округляем до десятых и получаем <b>{rounded_ratio}</b>"
    ),

    # --- 4️⃣ find_diagonal_ratio ---
    "STEP_DIAG_ORDER": (
        "<b>Шаг 1.</b> Определяем, какую сторону нужно взять по условию:\n"
        "➡️ <b>{side_type}</b>"
    ),

    "STEP_DIAG_RATIO": (
        "<b>Шаг 2.</b> Используем постоянное соотношение:\n\n"
        "➡️ диагональ к {side_type} стороне = <b>{ratio_value}</b>"
    ),

    # ------------------------------------------------------------------
    # 🟪 ВОПРОС 4 (Прикладная задача: площадь листа)
    ## Паттерн paper_area
    # ------------------------------------------------------------------

    # --- 1️⃣ area_basic ---
    "STEP_AREA_BASIC_SIZES": (
        "<b>Шаг 1.</b> В таблице находим размеры формата <b>{format}</b>:\n"
        "➡️ <b>Длина — {length_mm} мм</b>\n"
        "➡️ <b>Ширина — {width_mm} мм</b>\n\n"
        "Переводим в сантиметры:\n"
        "1 см = 10 мм, значит делим на 10.\n\n"
        "➡️ <b>{length_mm} мм = {length_cm} см</b>\n"
        "➡️ <b>{width_mm} мм = {width_cm} см</b>"
    ),

    "STEP_AREA_BASIC_CALC": (
        "<b>Шаг 2.</b> Вычисляем площадь:\n"
        "➡️ <b>S = {length_cm} · {width_cm} = {area_raw} см²</b>"
    ),

    # --- 2️⃣ area_with_rounding_10 ---
    "STEP_AREA_R10_SIZES": (
        "<b>Шаг 1.</b> В таблице находим размеры листа <b>{format}</b>:\n"
        "➡️ <b>Длина — {length_mm} мм</b>\n"
        "➡️ <b>Ширина — {width_mm} мм</b>\n\n"
        "Переводим в сантиметры:\n"
        "1 см = 10 мм, значит делим на 10.\n\n"
        "➡️ <b>{length_mm} мм = {length_cm} см</b>\n"
        "➡️ <b>{width_mm} мм = {width_cm} см</b>"
    ),

    "STEP_AREA_R10_CALC": (
        "<b>Шаг 2.</b> Вычисляем площадь:\n"
        "➡️ <b>S = {length_cm} · {width_cm} = {area_raw} см²</b>"
    ),

    "STEP_AREA_R10_ROUND": (
        "<b>Шаг 3.</b> Округляем до ближайшего числа, кратного <b>{round_base}</b>.\n\n"
        "Ближайшие десятки: <b>{lower_value} и {upper_value}</b>.\n"
        "<b>{area_raw}</b> ближе к <b>{rounded_area}</b>.\n\n"
        "➡️ <b>Округлённая площадь = {rounded_area} см²</b>"
    ),

    # --- 3️⃣ area_with_rounding_5 ---
    "STEP_AREA_R5_SIZES": (
        "<b>Шаг 1.</b> В таблице находим размеры листа <b>{format}</b>:\n"
        "➡️ <b>Длина — {length_mm} мм</b>\n"
        "➡️ <b>Ширина — {width_mm} мм</b>\n\n"
        "Переводим в сантиметры:\n"
        "1 см = 10 мм, значит делим на 10.\n\n"
        "➡️ <b>{length_mm} мм = {length_cm} см</b>\n"
        "➡️ <b>{width_mm} мм = {width_cm} см</b>"
    ),

    "STEP_AREA_R5_CALC": (
        "<b>Шаг 2.</b> Вычисляем площадь:\n"
        "➡️ <b>S = {length_cm} · {width_cm} = {area_raw} см²</b>"
    ),

    "STEP_AREA_R5_ROUND": (
        "<b>Шаг 3.</b> Округляем до ближайшего числа, кратного <b>{round_base}</b>.\n\n"
        "Ближайшие кратные 5 числа: <b>{lower_value} и {upper_value}</b>.\n"
        "➡️ <b>{area_raw} ближе к {rounded_area}</b>.\n\n"
        "➡️ <b>Округлённая площадь = {rounded_area} см²</b>"
    ),

    # ------------------------------------------------------------------
    # 🟫 ВОПРОС 5 (Прикладная задача: масса)
    ## Паттерн paper_pack_weight
    # ------------------------------------------------------------------

    # --- 1️⃣ pack_weight ---
    "STEP_PACK_COUNT": (
        "<b>Шаг 1.</b> Определяем, сколько листов {to_format} получается из {from_format}.\n\n"
        "Разница номеров форматов:\n"
        "➡️ <b>{to_index} − {from_index} = {index_difference}</b>\n\n"
        "Следовательно,\n\n"
        "➡️ <b>Количество листов = 2{sup_power}</b>\n"
        "➡️ <b>2{sup_power} = {sheet_count}</b>\n\n"
        "Значит, из одного листа {from_format} получается <b>{sheet_count}</b> {sheet_word} {to_format}."
    ),

    "STEP_PACK_SINGLE_WEIGHT": (
        "<b>Шаг 2.</b> Находим массу одного листа {to_format}.\n\n"
        "Масса 1 м² бумаги равна {mass_per_m2} г.\n\n"
        "➡️ <b>масса одного листа = {mass_per_m2} : {sheet_count} = {single_weight} г</b>"
    ),

    "STEP_PACK_TOTAL": (
        "<b>Шаг 3.</b> Находим массу пачки.\n\n"
        "➡️ <b>{single_weight} · {pack_size} = {total_weight} г</b>"
    ),

    # ------------------------------------------------------------------
    # 🟧 ВОПРОС 6 (Прикладная задача: масштабирование)
    ## Паттерн paper_font_scaling
    # ------------------------------------------------------------------

    # --- 1️⃣ font_scaling ---

    # --- 1️⃣ Направление ---
    "STEP_FONT_DIRECTION": (
        "<b>Шаг 1.</b> Определим направление перехода.\n"
        "{from_format} → {to_format}.\n"
        "Номер формата изменился ({from_index} → {to_index}), "
        "значит лист стал <b>{sheet_became}</b>.\n"
        "Шрифт нужно <b>{font_action}</b>."
    ),

    # --- 2️⃣ Коэффициент (exact) ---
    "STEP_FONT_SCALE": (
        "<b>Шаг 2.</b> Находим коэффициент масштабирования.\n\n"
        "Разница форматов: <b>{step_count}</b>, "
        "значит коэффициент = <b>{scale_formula}</b>.\n"
        "Упрощаем: <b>{scale_formula} = {scale_factor}</b>\n\n"
        "➡️ <b>{original_font} · {scale_factor} = {rounded_font}</b>"
    ),

    # --- 2️⃣ Коэффициент (подробный, с √2) ---
    "STEP_FONT_SCALE_DETAILED": (
        "<b>Шаг 2.</b> Находим коэффициент масштабирования.\n\n"
        "Разница форматов: <b>{step_count}</b>, "
        "значит коэффициент = <b>{scale_formula}</b>.\n"
        "Упрощаем: <b>{scale_formula} = {scale_factor}</b>\n\n"
        "➡️ <b>{original_font} · {scale_factor} = "
        "{original_font} · {coef_approx} = {scaled_intermediate}</b>"
    ),

    # --- 3️⃣ Округление ---
    "STEP_FONT_ROUND": (
        "<b>Шаг 3.</b> Округляем до целого числа.\n\n"
        "➡️ <b>{round_source} → {rounded_font}</b>"
    ),
}


TIPS_TEMPLATES: Dict[str, str] = {

    # ------------------------------------------------------------------
    # 🟩 ВОПРОС 1 (Задача на соответствие)
    ## Паттерн paper_format_match
    # ------------------------------------------------------------------

    "match_formats_to_rows": (
        "📌 Чтобы определить формат, достаточно сравнить одну сторону — длину или ширину.\n\n"
        "Чем больше это число, тем больше лист.\n\n"
        "🔹 В серии форматов A:\n"
        "<b>A1 больше A2, A2 больше A3, A3 больше A4 и так далее.</b>\n\n"
        "📌 Чем меньше номер формата — тем больше сам лист."
    ),

    # ------------------------------------------------------------------
    # 🟨 ВОПРОС 2 (Задача на разрезание)
    ## Паттерн paper_split
    # ------------------------------------------------------------------

    "count_subformats": (
        "📌 Количество листов = 2 в степени (номер меньшего формата − номер большего формата).\n"
        "📌 При увеличении формата количество листов уменьшается в 2 раза на каждом шаге.\n"
        "📌 Переходы можно считать «по стрелочкам» или сразу через степень двойки."
    ),

    # ------------------------------------------------------------------
    # 🟥 ВОПРОС 3 (Прикладная задача: найти длину, ширину, соотношения этих величин)
    ## Паттерн paper_dimensions
    # ------------------------------------------------------------------

    "find_length/width": (
        "📌 Длина — бо́льшая сторона листа, ширина — ме́ньшая.\n"
        "📌 Форматы серии A получают делением листа пополам.\n"
        "📌 Округление выполняем строго по условию задачи."
    ),

    "find_width": (
        "📌 <b>Ширина</b> — это всегда ме́ньшая сторона листа.\n"
        "📌 Каждый следующий формат получают, если предыдущий лист разрезать пополам.\n"
        "📌 При таком переходе одна сторона делится на 2, а стороны меняются местами.\n\n"
        "📌 Округление выполняем только так, как указано в условии."
    ),

    "find_ratio": (
        "📌 Соотношение сторон у всех форматов серии A одинаковое.\n"
        "📌 Делим бо́льшую сторону на ме́ньшую → всегда получаем примерно 1,4.\n"
        "📌 Делим ме́ньшую сторону на бо́льшую → всегда получаем примерно 0,7.\n"
        "📌 Поэтому число не нужно каждый раз пересчитывать — \n"
        "достаточно запомнить эти два приближённых значения."
    ),

    "find_diagonal_ratio": (
        "📌 Не нужно считать большие числа по теореме Пифагора — \n"
        "достаточно знать это постоянное соотношение:\n\n"
        "👉 Диагональ к ме́ньшей стороне ≈ 1,7.\n"
        "👉 Диагональ к бо́льшей стороне ≈ 1,2."
    ),

    # ------------------------------------------------------------------
    # 🟪 ВОПРОС 4 (Прикладная задача: площадь)
    ## Паттерн paper_area
    # ------------------------------------------------------------------

    "area_basic": (
        "📌 Площадь формата A0 равна 10 000 см² (1 м²).\n"
        "📌 Каждый следующий формат в 2 раза меньше предыдущего.\n"
        "📌 Поэтому площадь A4 ❗<b>примерно</b>❗ в 16 раз меньше \n"
        "площади A0 (2⁴ = 16) — это удобно для проверки.\n\n"
        "❗ ВАЖНО: в бланк ОГЭ записывай только число без единиц измерений. "
    ),

    "area_with_rounding_10": (
        "📌 Чтобы перевести мм в см, нужно разделить на 10 \n"
        "(перенести запятую на один знак влево).\n"
        "📌 «Кратно 10» означает, что число заканчивается на 0.\n"
        "📌 Читай условие внимательно, чтобы не ошибиться при округлении.\n"
        "Иногда просят округлить просто до целого числа.\n\n"
        "❗ ВАЖНО: в бланк ОГЭ записывай только число без единиц измерений. "
    ),

    "area_with_rounding_5": (
        "📌 Сначала вычисляем точную площадь, затем округляем.\n"
        "📌 «Кратно 5» означает, что число заканчивается на 0 или 5.\n"
        "📌 Читай условие внимательно, чтобы не ошибиться при округлении.\n"
        "Иногда просят округлить просто до целого числа.\n"
        "📌 Округляем только площадь, а не длину и ширину до умножения.\n\n"
        "❗ ВАЖНО: в бланк ОГЭ записывай только число без единиц измерений. "
    ),

    # ------------------------------------------------------------------
    # 🟫 ВОПРОС 5 (Прикладная задача: масса)
    ## Паттерн paper_pack_weight
    # ------------------------------------------------------------------

    "pack_weight": (
        "📌 Площадь листа A0 равна 1 м² — это основа всей системы форматов серии A.\n"
        "📌 Каждый следующий формат в 2 раза меньше предыдущего, \n"
        "значит и масса в 2 раза меньше.\n"
        "📌 Чтобы найти массу пачки, сначала находят массу одного листа.\n"
        "📌 Масса пачки — это масса одного листа, умноженная на количество листов в пачке."
    ),

    # ------------------------------------------------------------------
    # 🟧 ВОПРОС 6 (Прикладная задача: масштаб)
    ## Паттерн paper_font_scaling
    # ------------------------------------------------------------------

    "font_scaling": (
        "📌 Запомни «магические числа» для масштабирования шрифта:\n\n"
        "🔹 Разница 1 формат:\n"
        "   (A4 ↔ A3) → умножаем шрифт на √2 ≈ 1,4\n"
        "   (A4 ↔ A5) → делим на √2 ≈ 1,4 (или умножаем на 0,7)\n\n"
        "🔹 Разница 2 формата:\n"
        "   (A4 ↔ A2) → умножаем исходный шрифт на 2 (это (√2)²)\n"
        "   (A4 ↔ A6) → делим на 2\n\n"
        "🔹 Разница 3 формата:\n"
        "   (A7 ↔ A4) → умножаем шрифт на 2,8 (это (√2)³ или 2 · 1,4)\n"
        "   (A4 ↔ A7) → делим на 2,8 (или умножаем на 0,35)\n\n"
        "📌 <b>Главное правило:</b> Степень у √2 всегда равна количеству шагов перехода между форматами.\n\n"
        "❗ ВАЖНО: Округление выполняем только в самом конце вычислений!"
    ),
}


# =============================================================================
# 2. ПРОФИЛИ НАРРАТИВОВ (канон)
# =============================================================================

NARRATIVE_PROFILES: Dict[str, Dict[str, Any]] = {

    # ===============================
    # Q1 — paper_format_match
    # ===============================
    "match_formats_to_rows": {
        "idea_key": "match_formats_to_rows",
        "steps": [
            "STEP_MATCH_COMPARE",
            "STEP_MATCH_SEQUENCE",
        ],
        "tips_key": "match_formats_to_rows",
        "required_fields": [
            # из JSON
            "row_to_format_mapping",
            "answer_sequence",

            # вычисляется solver'ом для STEP_MATCH_COMPARE
            "row_1", "row_2", "row_3", "row_4",
            "len_1", "len_2", "len_3", "len_4",
            "format_1", "format_2", "format_3", "format_4",

            # вычисляется solver'ом для STEP_MATCH_SEQUENCE
            "requested_order",
        ],
    },

    # ===============================
    # Q2 — paper_split
    # ===============================
    "count_subformats": {
        "idea_key": "count_subformats",
        "steps": [
            "STEP_SPLIT_DIFF",
            "STEP_SPLIT_POWER",
        ],
        "tips_key": "count_subformats",
        "required_fields": [
            "from_format",
            "to_format",
            "from_index",
            "to_index",
            "index_difference",
            "transition_chain",
            "doubling_chain",
            "sup_power",
            "power_value",
        ],
    },

    # ===============================
    # Q3 — paper_dimensions
    # ===============================
    "find_length": {
        "idea_key": "find_length/width",
        "steps": [
            "STEP_DIM_LENGTH_1",
            "STEP_DIM_LENGTH_2",
            "STEP_DIM_LENGTH_3",
            "STEP_DIM_LENGTH_4_ROUND",
        ],
        "tips_key": "find_length/width",
        "required_fields": [
            "target_format",
            "reference_format",
            "reference_width_mm",
            "raw_result",
            "answer",
            "rounding",
            "multiple_of",
            "lower_bound",
            "upper_bound",
        ],
    },

    "find_width": {
        "idea_key": "find_length/width",
        "steps": [
            "STEP_DIM_WIDTH_1",
            "STEP_DIM_WIDTH_2",
            "STEP_DIM_WIDTH_3",
            "STEP_DIM_WIDTH_4_ROUND",
        ],
        "tips_key": "find_length/width",
        "required_fields": [
            "target_format",
            "reference_format",
            "reference_length_mm",
            "raw_result",
            "answer",
            "rounding",
            "multiple_of",
            "lower_bound",
            "upper_bound",
        ],
    },

    "find_ratio": {
        "idea_key": "find_ratio",
        "steps": [
            "STEP_RATIO_ORDER",
            "STEP_RATIO_CALC",
        ],
        "tips_key": "find_ratio",
        "required_fields": [
            "division_order",
            "division_expression",
            "raw_ratio",
            "rounded_ratio",
        ],
    },

    "find_diagonal_ratio": {
        "idea_key": "find_diagonal_ratio",
        "steps": [
            "STEP_DIAG_ORDER",
            "STEP_DIAG_RATIO",
        ],
        "tips_key": "find_diagonal_ratio",
        "required_fields": [
            "side_type",
            "ratio_value",
        ],
    },

    # ===============================
    # Q4 — paper_area
    # ===============================
    "area_basic": {
        "idea_key": "area_basic",
        "steps": [
            "STEP_AREA_BASIC_SIZES",
            "STEP_AREA_BASIC_CALC",
        ],
        "tips_key": "area_basic",
        "required_fields": [
            "format",
            "length_mm",
            "width_mm",
            "length_cm",
            "width_cm",
            "area_raw",
        ],
    },

    "area_with_rounding_10": {
        "idea_key": "area_with_rounding_10",
        "steps": [
            "STEP_AREA_R10_SIZES",
            "STEP_AREA_R10_CALC",
            "STEP_AREA_R10_ROUND",
        ],
        "tips_key": "area_with_rounding_10",
        "required_fields": [
            "format",
            "length_mm",
            "width_mm",
            "length_cm",
            "width_cm",
            "area_raw",
            "rounded_area",
            "round_base",
            "lower_value",
            "upper_value",
        ],
    },

    "area_with_rounding_5": {
        "idea_key": "area_with_rounding_5",
        "steps": [
            "STEP_AREA_R5_SIZES",
            "STEP_AREA_R5_CALC",
            "STEP_AREA_R5_ROUND",
        ],
        "tips_key": "area_with_rounding_5",
        "required_fields": [
            "format",
            "length_mm",
            "width_mm",
            "length_cm",
            "width_cm",
            "area_raw",
            "rounded_area",
            "round_base",
            "lower_value",
            "upper_value",
        ],
    },

    # ===============================
    # Q5 — pack_weight
    # ===============================
    "pack_weight": {
        "idea_key": "pack_weight",
        "steps": [
            "STEP_PACK_COUNT",
            "STEP_PACK_SINGLE_WEIGHT",
            "STEP_PACK_TOTAL",
        ],
        "tips_key": "pack_weight",
        "required_fields": [
            "from_format",
            "to_format",
            "from_index",
            "to_index",
            "index_difference",
            "sheet_count",
            "mass_per_m2",
            "single_weight",
            "pack_size",
            "total_weight",
        ],
    },

    # ===============================
    # Q6 — font_scaling
    # ===============================
    "font_scaling": {
        "idea_key": "font_scaling",
        "steps": [
            "STEP_FONT_DIRECTION",
            "STEP_FONT_SCALE",
            "STEP_FONT_ROUND",
        ],
        "tips_key": "font_scaling",
        "required_fields": [
            "from_format",
            "to_format",
            "from_index",
            "to_index",
            "original_font",
            "step_count",
            "scale_formula",
            "scale_factor",
            "rounded_font",
        ],
    },
}


# =============================================================================
# 3. HELPERS
# =============================================================================

def _render_block(title: str, text: str) -> str:
    return f"{title}\n{text}"


# =========================================================
# 4. ЛОКАЛЬНЫЕ УТИЛИТЫ (только для блока 1–5)
# =========================================================

def _pluralize_sheet(count: int) -> str:
    """
    Склонение слова 'лист' по количеству.
    Используется только в pack_weight.
    """
    if 11 <= count % 100 <= 14:
        return "листов"
    if count % 10 == 1:
        return "лист"
    if 2 <= count % 10 <= 4:
        return "листа"
    return "листов"

def _pluralize_transition(n: int) -> str:
    if 11 <= n % 100 <= 14:
        return "переходов"
    if n % 10 == 1:
        return "переход"
    if 2 <= n % 10 <= 4:
        return "перехода"
    return "переходов"


# =============================================================================
# 5. КОНТЕКСТ-БИЛДЕРЫ (facts -> context)
# =============================================================================

def _default_context_builder(variables: Dict[str, Any]) -> Dict[str, Any]:
    return variables

def _font_scaling_context_builder(variables: Dict[str, Any]) -> Dict[str, Any]:
    context = variables.copy()

    # 🔹 Знак для упрощения формулы
    if context.get("is_exact"):
        context["approx_sign"] = "="
    else:
        context["approx_sign"] = "="  # В подробном режиме тоже "="

    # 🔹 Источник для шага округления
    if context.get("is_exact"):
        # exact → округлять нечего, но на всякий случай
        context["round_source"] = context.get("scaled_intermediate") or context.get("rounded_font")
    else:
        # non-exact → округляем промежуточное значение
        context["round_source"] = context.get("scaled_intermediate")

    return context


def _pack_weight_context_builder(variables: Dict[str, Any]) -> Dict[str, Any]:
    context = variables.copy()

    sheet_count = context.get("sheet_count", 0)
    context["sheet_word"] = _pluralize_sheet(sheet_count)

    return context

def _count_subformats_context_builder(variables: Dict[str, Any]) -> Dict[str, Any]:
    context = variables.copy()

    context["transition_word"] = _pluralize_transition(context["index_difference"])

    return context

# =========================================================
# 6. CONTEXT BUILDERS
# =========================================================

_CONTEXT_BUILDERS: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
    key: _default_context_builder for key in NARRATIVE_PROFILES.keys()
}

# 🔵 Специальная логика округления
#_CONTEXT_BUILDERS["find_with_rounding"] = _rounding_context_builder

# 🔵 Масштабирование шрифта
_CONTEXT_BUILDERS["font_scaling"] = _font_scaling_context_builder

# 🔵 Вес пачки бумаги
_CONTEXT_BUILDERS["pack_weight"] = _pack_weight_context_builder

_CONTEXT_BUILDERS["count_subformats"] = _count_subformats_context_builder


# =============================================================================
# 7. ГЛАВНАЯ ФУНКЦИЯ (humanize)
# =============================================================================

def humanize(solution_core: Dict[str, Any]) -> str:

    narrative = solution_core["narrative"]

    # ⚠️ ВАЖНО: делаем copy, чтобы не менять solution_core напрямую
    variables = solution_core["variables"].copy()

    # 🔵 Добавляем final_answer в variables,
    # чтобы он прошёл через numeric formatter
    variables["final_answer"] = solution_core["final_answer"]

    profile = NARRATIVE_PROFILES[narrative]

    # 1️⃣ Строим контекст (facts -> context)
    builder = _CONTEXT_BUILDERS.get(narrative, _default_context_builder)
    context = builder(variables)

    # 2️⃣ Форматируем числа (для вывода)
    context = _format_numeric_values(context)

    # ✅ Проверка required_fields делается ПОСЛЕ builder (важно!)
    required_fields = profile["required_fields"]
    for field in required_fields:
        if field not in context:
            raise KeyError(f"Missing required field: {field}")

    # 💎 ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА ДЛЯ ПОДРОБНОГО font_scaling
    # (в подробном режиме должны быть числа для строки вида: 12 · 1,41 = 16,92)
    if narrative == "font_scaling" and not variables.get("is_exact", True):
        for f in ("coef_approx", "scaled_intermediate"):
            if f not in variables or variables[f] is None:
                raise KeyError(f"Missing required field: {f}")

    # 3️⃣ Рендерим блоки
    parts = []

    # IDEA
    idea_key = profile.get("idea_key")
    if idea_key and idea_key in IDEA_TEMPLATES:
        idea_text = IDEA_TEMPLATES[idea_key].format(**context)
        parts.append(_render_block("💡 <b>Идея решения</b>", idea_text))

    # STEPS
    step_texts = []

    # 💎 Флаги берём из solver-контракта (variables), но использовать будем в context
    is_exact = bool(variables.get("is_exact", False))
    needs_rounding = bool(variables.get("needs_rounding", False))

    for step_key in profile["steps"]:

        original_step_key = step_key  # для чистоты логики

        # 🔵 Условие для find_length / find_width
        if narrative in ("find_length", "find_width") and step_key.endswith("_ROUND") and not context.get("rounding"):
            continue

        # 💎 Для font_scaling: если НЕ точный случай — используем подробный шаблон
        if narrative == "font_scaling" and original_step_key == "STEP_FONT_SCALE" and not is_exact:
            step_key = "STEP_FONT_SCALE_DETAILED"

        # 💎 Если округление не требуется — шаг 3 не показываем
        if narrative == "font_scaling" and original_step_key == "STEP_FONT_ROUND" and not needs_rounding:
            continue

        # 🔵 Специальная логика для find_with_rounding (оставляем как есть)
        if step_key == "STEP_ROUND_PROCESS":

            if context.get("exact_multiple"):
                step_key = "STEP_ROUND_PROCESS_EXACT"

            elif context.get("is_middle"):
                step_key = "STEP_ROUND_PROCESS_MIDDLE"

            else:
                step_key = "STEP_ROUND_PROCESS_NORMAL"

        step_template = STEP_TEMPLATES[step_key]
        step_texts.append(step_template.format(**context))

    if step_texts:
        steps_block = "\n\n".join(step_texts)
        parts.append(_render_block("🪜 <b>Пошаговое решение</b>", steps_block))

    # ANSWER
    parts.append(f"🎯 Ответ: <b>{context['final_answer']}</b>.")

    # TIPS
    tips_key = profile.get("tips_key")
    if tips_key and tips_key in TIPS_TEMPLATES:
        tips_text = TIPS_TEMPLATES[tips_key]
        parts.append(_render_block("✨ <b>Полезно знать</b>", tips_text))

    return "\n\n".join(parts)
