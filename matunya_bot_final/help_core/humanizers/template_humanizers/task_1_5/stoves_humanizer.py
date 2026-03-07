from typing import Dict, Any

from matunya_bot_final.utils.display.display import format_number


# ============================================================
# IDEA / STEP / TIPS templates
# ============================================================

IDEA_TEMPLATES: Dict[str, str] = {

    # ------------------------------------------------------------------
    # 🟩 ВОПРОС 1 (Задача на соответствие)
    ## Паттерн stove_match_table
    # ------------------------------------------------------------------
    "IDEA_STOVE_MATCH": (
        "<b>Идея.</b>\n"
        "Сопоставь значения из строки «{column_label}» с данными печей в таблице."
    ),

    # ------------------------------------------------------------------
    # 🟨 ВОПРОС 2 (Геометрия)
    ## Паттерн stoves_room_geometry
    # ------------------------------------------------------------------

    "find_volume": (
        "Парное отделение — это прямоугольный параллелепипед (обычная «коробка»).\n"
        "Объём такой фигуры равен произведению трёх её измерений: длины, ширины и высоты.\n"
        "Формула: \n\n"
        "👉 <b>V = Длина · Ширина · Высота</b>"
    ),

    "find_base_area": (
        "Пол и потолок парного отделения — это прямоугольники.\n"
        "Формула площади прямоугольника:\n\n"
        "👉 <b>S = Длина · Ширина</b>"
    ),

    "find_lateral_area": (
        "Стены комнаты — это 4 прямоугольника.\n"
        "Сначала найдём площадь всех стен:\n\n"
        "👉 <b>S_стен = Периметр пола · Высота</b>\n\n"
        "Затем вычтем площадь двери, так как её учитывать не нужно по условию задачи."
    ),

    # ------------------------------------------------------------------
    # 🟥 ВОПРОС 3 (Стоимость печи)
    ## Паттерн stoves_purchase_cost
    # ------------------------------------------------------------------

    "find_price_difference": (
        "Нужно сравнить затраты на покупку двух вариантов печей.\n"
        "1. Для <b>электрической</b> печи учитываем её цену и стоимость установки.\n"
        "2. Для <b>дровяной</b> печи сначала выбираем модель, подходящую по объёму парной."
    ),

    "find_wood_stove_total_cost": (
        "Нужно найти стоимость покупки дровяной печи.\n"
        "Сначала выбираем печь, которая подходит по объёму парной.\n"
        "Затем к цене этой печи прибавляем стоимость доставки."
    ),

    "find_electric_stove_total_cost": (
        "Нужно найти полную стоимость покупки электрической печи.\n"
        "Для этого складываем три величины:\n"
        "1. цену самой печи,\n"
        "2. стоимость установки,\n"
        "3. стоимость доставки."
    ),

    "find_operating_cost_difference": (
        "Нужно сравнить годовые расходы на разные виды топлива.\n"
        "1. Сначала найдём стоимость электричества: потребление умножим на цену.\n"
        "2. Затем найдём стоимость дров: объём дров умножим на цену.\n"
        "3. После этого найдём разницу между расходами."
    ),

    # ------------------------------------------------------------------
    # 🟦 ВОПРОС 5 (радиус арки кожуха)
    ## Паттерн stoves_arc_radius
    # ------------------------------------------------------------------

    "find_arc_radius": (
        "Чтобы найти радиус арки, нам нужно мысленно (или на черновике) "
        "достроить чертёж до прямоугольного треугольника.\n"
        "Искомый радиус <b>R</b> будет его гипотенузой, "
        "а катетами станут высота кожуха и половина его ширины.\n"
        "Дальше останется только применить теорему Пифагора!"
    ),
}

STEP_TEMPLATES: Dict[str, str] = {

    # ------------------------------------------------------------------
    # 🟩 ВОПРОС 1 (Задача на соответствие)
    ## Паттерн stove_match_table
    # ------------------------------------------------------------------
    "STEP_STOVE_MATCH": (
        "<b>Сопоставление:</b>\n"
        "{match_lines}"
    ),

    # ------------------------------------------------------------------
    # 🟨 ВОПРОС 2 (Геометрия)
    ## Паттерн stoves_room_geometry
    # ------------------------------------------------------------------

    #---find_volume---

    "STEP_STOVES_VOLUME_GIVEN": (
            "<b>Шаг 1.</b> Условие задачи.\n"
            "Дано: <b>Длина = {length} м; Ширина = {width} м; Высота = {height} м</b>.\n"
            "Найти: <b>Объём (V)</b>."
        ),

    "STEP_STOVES_VOLUME_FORMULA": (
        "<b>Шаг 2.</b> Используем формулу объёма.\n"
        "Перемножим все три измерения:\n"
        "➡️ <b>V = {length} · {width} · {height} = {volume}</b>"
    ),

    #---find_base_area---

    "STEP_STOVES_BASE_AREA_GIVEN": (
        "<b>Шаг 1.</b> Условие задачи.\n"
        "Дано: <b>Длина = {length} м; Ширина = {width} м</b>. (Высота не нужна).\n"
        "Найти: <b>Площадь пола (S)</b>."
    ),

    "STEP_STOVES_BASE_AREA_FORMULA": (
        "<b>Шаг 2.</b> Используем формулу площади прямоугольника.\n"
        "Перемножим длину и ширину:\n"
        "➡️ <b>S = {length} · {width} = {area}</b>"
    ),

    #---find_lateral_area---

    "STEP_STOVES_LATERAL_AREA_GIVEN": (
        "<b>Шаг 1.</b> Условие задачи.\n"
        "Дано:\n"
        "<b>Длина = {length} м</b>\n"
        "<b>Ширина = {width} м</b>\n"
        "<b>Высота = {height} м</b>\n"
        "<b>Ширина двери = {door_width_m} м</b>\n"
        "<b>Высота двери = {door_height_m} м</b>\n\n"
        "Найти: <b>Площадь стен без двери</b>."
    ),

    "STEP_STOVES_LATERAL_AREA_PERIMETER": (
        "<b>Шаг 2.</b> Найдем периметр пола.\n"
        "Периметр — это сумма длин всех сторон пола:\n"
        "P = (Длина + Ширина) · 2\n"
        "➡️ <b>P = ({length} + {width}) · 2 = {sum_length_width} · 2 = {perimeter} м</b>"
    ),

    "STEP_STOVES_LATERAL_AREA_WALLS": (
        "<b>Шаг 3.</b> Найдем общую площадь четырёх стен.\n"
        "Умножим периметр на высоту комнаты:\n"
        "S_стен = P · Высота\n"
        "➡️ <b>S = {perimeter} · {height} = {walls_area} м²</b>"
    ),

    "STEP_STOVES_LATERAL_AREA_DOOR": (
        "<b>Шаг 4.</b> Найдём площадь двери\n"
        "S_двери = Ширина двери · Высота двери\n"
        "Ширина двери = {door_width_cm} см = {door_width_m} м\n"
        "➡️ <b>S = {door_width_m} · {door_height_m} = {door_area} м²</b>"
    ),

    "STEP_STOVES_LATERAL_AREA_RESULT": (
        "<b>Шаг 5.</b> Вычтем площадь двери из общей площади стен\n"
        "➡️ <b>S = {walls_area} − {door_area} = {result_area} м²</b>"
    ),

    # ------------------------------------------------------------------
    # 🟥 ВОПРОС 3 (Стоимость печи)
    ## Паттерн stoves_purchase_cost
    # ------------------------------------------------------------------

    #---find_price_difference---
    "STEP_STOVES_PRICE_DIFF_VOLUME": (
        "<b>Шаг 1.</b> Найдём объём парной.\n"
        "➡️ <b>V = {length} · {width} · {height} = {room_volume} м³</b>"
    ),

    "STEP_STOVES_PRICE_DIFF_WOOD_SELECT": (
        "<b>Шаг 2.</b> Выберем подходящую дровяную печь.\n"
        "Объём парной: <b>{room_volume} м³</b>.\n"
        "Подходит печь №{wood_ok_no}.\n"
        "Цена этой печи: <b>{wood_ok_cost} руб.</b>"
    ),

    "STEP_STOVES_PRICE_DIFF_ELECTRIC_TOTAL": (
        "<b>Шаг 3.</b> Найдём полную стоимость электрической печи.\n"
        "Цена печи + установка:\n"
        "➡️ <b>{electric_cost} + {electric_install_cost} = {electric_total} руб.</b>"
    ),

    "STEP_STOVES_PRICE_DIFF_RESULT": (
        "<b>Шаг 4.</b> Найдём разницу.\n"
        "➡️ <b>{electric_total} − {wood_ok_cost} = {result}</b>"
    ),

    #---find_wood_stove_total_cost---
    "STEP_STOVES_WOOD_COST_VOLUME": (
        "<b>Шаг 1.</b> Найдём объём парной.\n"
        "➡️ <b>V = {length} · {width} · {height} = {room_volume} м³</b>"
    ),

    "STEP_STOVES_WOOD_COST_SELECT": (
        "<b>Шаг 2.</b> Выберем подходящую дровяную печь.\n"
        "Объём парной: <b>{room_volume} м³</b>.\n"
        "Подходит печь №{wood_ok_no}.\n"
        "Цена этой печи: <b>{wood_ok_cost} руб.</b>"
    ),

    "STEP_STOVES_WOOD_COST_TOTAL": (
        "<b>Шаг 3.</b> Найдём итоговую стоимость покупки.\n"
        "Стоимость = Цена печи + Доставка\n"
        "➡️ <b>{wood_ok_cost} + {delivery_cost} = {result} руб.</b>"
    ),

    #---find_electric_stove_total_cost---
    "STEP_STOVES_ELECTRIC_COST_GIVEN": (
        "<b>Шаг 1.</b> Найдём все нужные данные.\n"
        "Цена электрической печи: <b>{electric_cost} руб.</b>\n"
        "Установка: <b>{electric_install_cost} руб.</b>\n"
        "Доставка: <b>{delivery_cost} руб.</b>"
    ),

    "STEP_STOVES_ELECTRIC_COST_TOTAL": (
        "<b>Шаг 2.</b> Сложим все расходы.\n"
        "➡️ <b>{electric_cost} + {electric_install_cost} + {delivery_cost} = {result} руб.</b>"
    ),

    #---find_operating_cost_difference---
    "STEP_STOVES_OPERATING_ELECTRIC": (
        "<b>Шаг 1.</b> Найдём расходы на электрическую печь.\n"
        "Потребление: <b>{electric_kwh} кВт·ч</b>\n"
        "Цена: <b>{electric_price_per_kwh} руб.</b>\n"
        "➡️ <b>{electric_kwh} · {electric_price_per_kwh} = {electric_oper} руб.</b>"
    ),

    "STEP_STOVES_OPERATING_WOOD": (
        "<b>Шаг 2.</b> Найдём расходы на дровяную печь.\n"
        "Потребление: <b>{wood_volume_m3} м³</b>\n"
        "Цена: <b>{wood_price_per_m3} руб.</b>\n"
        "➡️ <b>{wood_volume_m3} · {wood_price_per_m3} = {wood_oper} руб.</b>"
    ),

    "STEP_STOVES_OPERATING_RESULT": (
        "<b>Шаг 3.</b> Найдём разницу расходов.\n"
        "➡️ <b>{electric_oper} − {wood_oper} = {result}</b>"
    ),

    # ------------------------------------------------------------------
    # 🟦 ВОПРОС 5 (радиус арки кожуха)
    ## Паттерн stoves_arc_radius
    # ------------------------------------------------------------------

    #---find_arc_radius---
    "STEP_STOVES_ARC_RADIUS_TRIANGLE": (
        "<b>Шаг 1.</b> Определим длины катетов прямоугольного треугольника.\n"
        "• Вертикальный катет равен высоте кожуха: ➡️ <b>{a}</b>\n"
        "• Горизонтальный катет — это половина ширины кожуха:\n"
        "➡️ <b>{b} : 2 = {half_width}</b>"
    ),

    "STEP_STOVES_ARC_RADIUS_PYTHAGORAS": (
        "<b>Шаг 2.</b> Применим теорему Пифагора.\n"
        "Квадрат радиуса равен сумме квадратов катетов:\n"
        "➡️ <b>R² = a² + (b/2)²</b>"
    ),

    "STEP_STOVES_ARC_RADIUS_CALC": (
        "<b>Шаг 3.</b> Выполним вычисления.\n"
        "➡️ <b>R = √({a}² + {half_width}²)</b>\n"
        "➡️ <b>R = √({a_squared} + {half_width_squared})</b>\n"
        "➡️ <b>R = √{radius_squared} = {radius}</b>"
    ),

}


TIPS_TEMPLATES: Dict[str, str] = {

    # ------------------------------------------------------------------
    # 🟩 ВОПРОС 1 (Задача на соответствие)
    ## Паттерн stove_match_table
    # ------------------------------------------------------------------
    "TIP_STOVE_MATCH": "📌 Ищи точное совпадение значения в таблице.",

    # ------------------------------------------------------------------
    # 🟨 ВОПРОС 2 (Геометрия)
    ## Паттерн stoves_room_geometry
    # ------------------------------------------------------------------
    "find_volume": (
        "📌 Объём измеряется в кубических метрах (м³).\n"
        "1 м³ — это объём куба со стороной 1 метр.\n\n"
        "❗ ВАЖНО: В бланке ОГЭ записывай только число без единиц измерения."
    ),

    "find_base_area": (
        "📌 В условии даны все три размера (включая высоту).\n"
        "Твоя задача — не попасться в ловушку и выбрать только те числа, "
        "которые относятся к площади: длина и ширина.\n\n"
        "❗ ВАЖНО: В бланке ОГЭ записывай только число без единиц измерения."
    ),

    "find_lateral_area": (
        "📌 Формулу <b>S = P · h</b> легко запомнить:\n"
        "мы как бы «вытягиваем» периметр пола вверх на высоту стен.\n\n"
        "Если в задаче сказано «площадь двери не учитывать», "
        "сначала находят площадь всех четырёх стен, а потом вычитают площадь дверного проёма.\n\n"
        "❗ ВАЖНО: В бланке ОГЭ записывай только число без единиц измерения."
    ),

    # ------------------------------------------------------------------
    # 🟥 ВОПРОС 3 (Стоимость печи)
    ## Паттерн stoves_purchase_cost
    # ------------------------------------------------------------------

    "find_price_difference": (
        "📌 В таблице часто есть более дешёвая печь, "
        "но она может не подходить по объёму помещения.\n"
        "Сначала проверь столбец «Объём», и только потом сравнивай цены.\n\n"
        "❗ В бланке ОГЭ записывай только число без единиц измерения."
    ),

    "find_wood_stove_total_cost": (
        "📌 В таблице может быть несколько дровяных печей.\n"
        "Сначала проверь, подходит ли печь по объёму помещения.\n\n"
        "❗ В бланке ОГЭ записывай только число без единиц измерения."
    ),

    "find_electric_stove_total_cost": (
        "📌 Электрическая печь в таблице обычно одна, поэтому выбирать не нужно.\n"
        "Главное — не забыть прибавить и установку, и доставку.\n\n"
        "❗ В бланке ОГЭ записывай только число без единиц измерения."
    ),

    "find_operating_cost_difference": (
        "📌 В этой задаче мы не учитываем стоимость самой печи.\n"
        "Нужно сравнить только расходы на топливо за год.\n\n"
        "❗ В бланке ОГЭ записывай только число без единиц измерения."
    ),

    # ------------------------------------------------------------------
    # 🟦 ВОПРОС 5 (радиус арки кожуха)
    ## Паттерн stoves_arc_radius
    # ------------------------------------------------------------------

    "find_arc_radius": (
        "❗️ <b>Главная ловушка:</b> очень часто в этой задаче забывают поделить ширину <b>b</b> пополам "
        "и берут для расчетов всё значение целиком.\n"
        "Обязательно проверяй себя: горизонтальный катет — это ровно половина ширины печи!\n\n"
        "❗ В бланке ОГЭ записывай только число без единиц измерения (никаких «см»)."
    ),

}

# ============================================================
# Narrative profiles (источник истины: variables)
# ============================================================

NARRATIVE_PROFILES: Dict[str, Dict[str, Any]] = {
    # -------------------------
    # Q1: stove_match_table
    # -------------------------
    "match_volume": {
        "pattern": "stove_match_table",
        "idea": "IDEA_STOVE_MATCH",
        "step": "STEP_STOVE_MATCH",
        "tip": "TIP_STOVE_MATCH",
    },
    "match_weight": {
        "pattern": "stove_match_table",
        "idea": "IDEA_STOVE_MATCH",
        "step": "STEP_STOVE_MATCH",
        "tip": "TIP_STOVE_MATCH",
    },
    "match_cost": {
        "pattern": "stove_match_table",
        "idea": "IDEA_STOVE_MATCH",
        "step": "STEP_STOVE_MATCH",
        "tip": "TIP_STOVE_MATCH",
    },

    # -------------------------
    # Q2: stoves_room_geometry
    # narratives будут отличаться по идеям и шагам, но паттерн один
    # -------------------------

    "find_volume": {
        "pattern": "stoves_room_geometry",
        "idea": "find_volume",
        "steps": [
            "STEP_STOVES_VOLUME_GIVEN",
            "STEP_STOVES_VOLUME_FORMULA",
        ],
        "tip": "find_volume",
    },

    "find_base_area": {
        "pattern": "stoves_room_geometry",
        "idea": "find_base_area",
        "steps": [
            "STEP_STOVES_BASE_AREA_GIVEN",
            "STEP_STOVES_BASE_AREA_FORMULA",
        ],
        "tip": "find_base_area",
    },

    "find_lateral_area": {
        "pattern": "stoves_room_geometry",
        "idea": "find_lateral_area",
        "steps": [
            "STEP_STOVES_LATERAL_AREA_GIVEN",
            "STEP_STOVES_LATERAL_AREA_PERIMETER",
            "STEP_STOVES_LATERAL_AREA_WALLS",
            "STEP_STOVES_LATERAL_AREA_DOOR",
            "STEP_STOVES_LATERAL_AREA_RESULT",
        ],
        "tip": "find_lateral_area",
    },

    # -------------------------
    # Q3: stoves_purchase_cost
    # narratives будут отличаться по идеям и шагам, но паттерн один
    # -------------------------
    "find_price_difference": {
        "pattern": "stoves_purchase_cost",
        "idea": "find_price_difference",
        "steps": [
            "STEP_STOVES_PRICE_DIFF_VOLUME",
            "STEP_STOVES_PRICE_DIFF_WOOD_SELECT",
            "STEP_STOVES_PRICE_DIFF_ELECTRIC_TOTAL",
            "STEP_STOVES_PRICE_DIFF_RESULT",
        ],
        "tip": "find_price_difference",
    },

    "find_wood_stove_total_cost": {
        "pattern": "stoves_purchase_cost",
        "idea": "find_wood_stove_total_cost",
        "steps": [
            "STEP_STOVES_WOOD_COST_VOLUME",
            "STEP_STOVES_WOOD_COST_SELECT",
            "STEP_STOVES_WOOD_COST_TOTAL",
        ],
        "tip": "find_wood_stove_total_cost",
    },

    "find_electric_stove_total_cost": {
        "pattern": "stoves_purchase_cost",
        "idea": "find_electric_stove_total_cost",
        "steps": [
            "STEP_STOVES_ELECTRIC_COST_GIVEN",
            "STEP_STOVES_ELECTRIC_COST_TOTAL",
        ],
        "tip": "find_electric_stove_total_cost",
    },

    "find_operating_cost_difference": {
        "pattern": "stoves_purchase_cost",
        "idea": "find_operating_cost_difference",
        "steps": [
            "STEP_STOVES_OPERATING_ELECTRIC",
            "STEP_STOVES_OPERATING_WOOD",
            "STEP_STOVES_OPERATING_RESULT",
        ],
        "tip": "find_operating_cost_difference",
    },

    # -------------------------
    # Q5 stoves_arc_radius
    # narrative будет один, так как паттерн один
    # -------------------------

    "find_arc_radius": {
        "pattern": "stoves_arc_radius",
        "idea": "find_arc_radius",
        "steps": [
            "STEP_STOVES_ARC_RADIUS_TRIANGLE",
            "STEP_STOVES_ARC_RADIUS_PYTHAGORAS",
            "STEP_STOVES_ARC_RADIUS_CALC",
        ],
        "tip": "find_arc_radius",
    },

    # -------------------------
    # Q4 добавим позже
    # narratives будут здесь же
    # -------------------------

}


# ============================================================
# Public
# ============================================================

def humanize(solution_core: Dict[str, Any]) -> str:
    """
    Единый humanizer для stoves (вопросы 1–5).
    Humanizer ничего не вычисляет и не анализирует question_text.
    Всё берём из solution_core["variables"].
    """

    pattern = solution_core.get("pattern")
    narrative = solution_core.get("narrative")
    variables = solution_core.get("variables") or {}

    # --------------------------------------------------------
    # Display-формат чисел (единый стандарт Матюни)
    # --------------------------------------------------------
    variables = {
        k: format_number(v) if isinstance(v, (int, float)) or str(v).replace('.', '', 1).isdigit() else v
        for k, v in variables.items()
    }

    if not pattern or not narrative:
        raise ValueError("HUMANIZER: missing pattern/narrative")

    profile = NARRATIVE_PROFILES.get(narrative)
    if not profile:
        raise ValueError(f"HUMANIZER: unknown narrative: {narrative}")

    # защита: narrative должен соответствовать pattern
    expected_pattern = profile.get("pattern")
    if expected_pattern and expected_pattern != pattern:
        raise ValueError(f"HUMANIZER: narrative {narrative} does not match pattern {pattern}")

    # --------------------------------------------------------
    # stove_match_table
    # --------------------------------------------------------
    if pattern == "stove_match_table":
        return _humanize_stove_match(profile, variables)

    # --------------------------------------------------------
    # stoves_room_geometry
    # --------------------------------------------------------
    if pattern == "stoves_room_geometry":
        return _humanize_stoves_geometry(profile, variables)

    # --------------------------------------------------------
    # stoves_purchase_cost
    # --------------------------------------------------------
    if pattern == "stoves_purchase_cost":
        return _humanize_stoves_geometry(profile, variables)

    # --------------------------------------------------------
    # stoves_arc_radius
    # --------------------------------------------------------
    if pattern == "stoves_arc_radius":
        return _humanize_stoves_geometry(profile, variables)

    raise ValueError(f"HUMANIZER: unsupported pattern: {pattern}")


# ============================================================
# Internal: Q1 stove_match_table
# ============================================================

def _humanize_stove_match(profile: Dict[str, Any], variables: Dict[str, Any]) -> str:

    required = ["column_label", "columns", "stove_no_to_value_mapping", "answer"]
    missing = [k for k in required if k not in variables]
    if missing:
        raise ValueError(f"HUMANIZER Q1: missing variables: {', '.join(missing)}")

    column_label = variables["column_label"]
    columns = variables["columns"]
    mapping = variables["stove_no_to_value_mapping"]
    answer = variables["answer"]

    match_lines = []

    for value in columns:

        found_no = None
        for no, v in mapping.items():
            if v == value:
                found_no = no
                break

        if found_no is None:
            raise ValueError(f"HUMANIZER Q1: value {value} not found in mapping")

        value_display = format_number(value)

        match_lines.append(f"{value_display} → печь №{found_no}")

    idea_text = IDEA_TEMPLATES[profile["idea"]].format(column_label=column_label)
    step_text = STEP_TEMPLATES[profile["step"]].format(match_lines="\n".join(match_lines))
    tip_text = TIPS_TEMPLATES[profile["tip"]]

    return (
        f"{idea_text}\n\n"
        f"{step_text}\n\n"
        f"{tip_text}\n"
        f"\n<b>Ответ:</b> {answer}"
    )


# ============================================================
# Internal: Q2 stoves_room_geometry
# ============================================================

def _humanize_stoves_geometry(profile: Dict[str, Any], variables: Dict[str, Any]) -> str:
    """
    Humanizer для stoves_room_geometry (Q2–Q5).
    Ничего не вычисляет — только форматирует данные из variables.
    """

    idea_key = profile.get("idea")
    step_keys = profile.get("steps")
    tip_key = profile.get("tip")

    if not idea_key or not step_keys or not tip_key:
        raise ValueError("HUMANIZER: invalid profile structure")

    # ---------------------------
    # Display-формат чисел
    # ---------------------------
    variables = {
        k: format_number(v) if isinstance(v, (int, float)) else v
        for k, v in variables.items()
    }

    # ---------------------------
    # IDEA
    # ---------------------------
    idea_text = IDEA_TEMPLATES[idea_key]

    # ---------------------------
    # STEPS
    # ---------------------------
    step_texts = []

    for step_key in step_keys:
        template = STEP_TEMPLATES[step_key]
        step_texts.append(template.format(**variables))

    steps_block = "\n\n".join(step_texts)

    # ---------------------------
    # TIPS
    # ---------------------------
    tip_text = TIPS_TEMPLATES[tip_key]

    # ---------------------------
    # ANSWER
    # ---------------------------
    answer = variables.get("answer")

    if answer is None:
        raise ValueError("HUMANIZER: missing answer in variables")

    return (
        f"💡 <b>Идея решения</b>\n{idea_text}\n\n"
        f"🪜 <b>Пошаговое решение</b>\n\n"
        f"{steps_block}\n\n"
        f"🎯 Ответ: <b>{answer}</b>\n\n"
        f"✨ <b>Полезно знать</b>\n"
        f"{tip_text}\n\n"
    )
