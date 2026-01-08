from typing import Dict, Any, List
import math

from matunya_bot_final.help_core.solvers.task_15.task_15_text_formatter import format_number

# ============================================================
# ПАТТЕРН 4.1: right_triangle_angles_sum
# Сумма острых углов прямоугольного треугольника
# ============================================================
def _solve_right_triangle_angles_sum(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Решает задачи на нахождение острого угла, если дан другой острый угол.
    Свойство: Сумма острых углов прямоугольного треугольника равна 90°.
    """
    variables = task.get("variables", {})
    given = variables.get("given", {})

    # 1. Извлечение данных (angle_alpha или angle)
    known_angle = given.get("angle_alpha")

    if known_angle is None:
        angle_obj = given.get("angle")
        if isinstance(angle_obj, (int, float)):
            known_angle = angle_obj
        elif isinstance(angle_obj, dict):
            known_angle = angle_obj.get("value")

    if known_angle is None:
        raise ValueError(f"right_triangle_angles_sum: не указано значение известного угла. Данные given: {given}")

    # 2. Математика
    result_val = 90 - known_angle

    if result_val <= 0:
        raise ValueError(f"right_triangle_angles_sum: некорректный угол {known_angle}, результат {result_val}")

    # 3. Форматирование
    def fmt(num):
        return int(num) if float(num).is_integer() else num

    # 4. Контекст
    context = {
        "known_angle": fmt(known_angle),
        "res": fmt(result_val)
    }

    # ВАЖНО: Принудительно ставим default, чтобы хьюмонайзер увидел "Идею решения"
    narrative = "default"

    return [{
        "action": f"{task['pattern']}:{narrative}",
        "data": context
    }]

# ============================================================
# ПАТТЕРН 4.2: pythagoras_find_leg
# Нахождение катета по гипотенузе и другому катету
# ============================================================
def _solve_pythagoras_find_leg(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    variables = task.get("variables", {})
    given = variables.get("given", {})

    c = given.get("hypotenuse")
    b = given.get("known_leg")

    if c is None or b is None:
        raise ValueError(f"pythagoras_find_leg: отсутствуют данные. given={given}")

    c_sq = c ** 2
    b_sq = b ** 2
    diff = c_sq - b_sq

    if diff <= 0:
        raise ValueError(f"pythagoras_find_leg: гипотенуза ({c}) должна быть больше катета ({b})")

    res = math.sqrt(diff)

    def fmt(num):
        return int(num) if float(num).is_integer() else num

    c_fmt = fmt(c)
    b_fmt = fmt(b)
    res_fmt = fmt(res)

    # Логика троек
    base_triples = [
        [3, 4, 5], [5, 12, 13], [8, 15, 17], [7, 24, 25],
        [20, 21, 29], [9, 40, 41], [11, 60, 61], [12, 35, 37]
    ]

    # Сортируем: [меньший_катет, больший_катет, гипотенуза]
    current_sides_sorted = sorted([int(b_fmt), int(res_fmt), int(c_fmt)])

    k_factor = math.gcd(current_sides_sorted[0], math.gcd(current_sides_sorted[1], current_sides_sorted[2]))

    triple_name = None
    base_unknown_leg = None

    if k_factor >= 1:
        reduced = [s // k_factor for s in current_sides_sorted]

        for t in base_triples:
            # t тоже отсортирован: [3, 4, 5]
            if reduced == sorted(t):
                triple_name = f"{t[0]}-{t[1]}-{t[2]}"

                # Нам нужно понять, какой из катетов в БАЗОВОЙ тройке неизвестен
                # reduced = [5, 12, 13] (базовая). Реальный res = 36 -> reduced_res = 12
                # Значит base_unknown_leg = 12
                base_unknown_leg = int(res_fmt) // k_factor
                break

    context = {
        "c": c_fmt,
        "b": b_fmt,
        "c_sq": fmt(c_sq),
        "b_sq": fmt(b_sq),
        "diff": fmt(diff),
        "res": res_fmt,
        "triple_name": triple_name,
        "k_factor": k_factor,
        # Доп переменные для шаблона
        "base_hypotenuse_calc": int(c_fmt) // k_factor,
        "base_leg_calc": int(b_fmt) // k_factor,
        "base_unknown_leg": base_unknown_leg,
        "is_scaled": k_factor > 1
    }

    return [{
        "action": f"{task['pattern']}:default",
        "data": context
    }]

# ============================================================
# ПАТТЕРН 4.3: pythagoras_find_hypotenuse
# Нахождение гипотенузы по двум катетам
# ============================================================
def _solve_pythagoras_find_hypotenuse(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Формула: c² = a² + b²
    """
    variables = task.get("variables", {})
    given = variables.get("given", {})

    # 1. Извлечение данных
    # В JSON приходят leg_1 и leg_2
    a = given.get("leg_1")
    b = given.get("leg_2")

    if a is None or b is None:
        raise ValueError(f"pythagoras_find_hypotenuse: отсутствуют данные. given={given}")

    # 2. Математика
    a_sq = a ** 2
    b_sq = b ** 2
    sum_sq = a_sq + b_sq
    res = math.sqrt(sum_sq)

    # 3. Форматирование
    def fmt(num):
        return int(num) if float(num).is_integer() else num

    a_fmt = fmt(a)
    b_fmt = fmt(b)
    res_fmt = fmt(res)

    # 4. Проверка на Пифагоровы тройки
    base_triples = [
        [3, 4, 5], [5, 12, 13], [8, 15, 17], [7, 24, 25],
        [20, 21, 29], [9, 40, 41], [11, 60, 61], [12, 35, 37]
    ]

    # Сортируем стороны: [катет1, катет2, гипотенуза]
    # res_fmt (гипотенуза) всегда будет последней после сортировки, но для порядка сортируем всё
    current_sides_sorted = sorted([int(a_fmt), int(b_fmt), int(res_fmt)])

    # Находим НОД
    k_factor = math.gcd(current_sides_sorted[0], math.gcd(current_sides_sorted[1], current_sides_sorted[2]))

    triple_name = None
    base_hyp_calc = None # Базовая гипотенуза (которую мы "вспоминаем")

    if k_factor >= 1:
        reduced = [s // k_factor for s in current_sides_sorted]

        for t in base_triples:
            if reduced == sorted(t):
                triple_name = f"{t[0]}-{t[1]}-{t[2]}"
                # В базовой тройке гипотенуза всегда самая большая (последний элемент)
                base_hyp_calc = t[-1]
                break

    # 5. Контекст
    context = {
        "a": a_fmt,
        "b": b_fmt,
        "a_sq": fmt(a_sq),
        "b_sq": fmt(b_sq),
        "sum_sq": fmt(sum_sq),
        "res": res_fmt,

        # Данные для Способа 2
        "triple_name": triple_name,
        "k_factor": k_factor,
        "is_scaled": k_factor > 1,

        # Переменные для шаблона (деление текущих катетов на к)
        "calc_leg1_base": int(a_fmt) // k_factor,
        "calc_leg2_base": int(b_fmt) // k_factor,
        "base_hyp_calc": base_hyp_calc
    }

    return [{
        "action": f"{task['pattern']}:default",
        "data": context
    }]


# ============================================================
# ПАТТЕРН 4.4: find_cos_sin_tg_from_sides
# Нахождение тригонометрических функций (sin, cos, tg) по сторонам
# ============================================================
def _solve_find_cos_sin_tg_from_sides(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    variables = task.get("variables", {})
    given = variables.get("given", {})
    target = variables.get("target", {})

    # 1. Берем нарратив из JSON (валидатор уже всё решил)
    narrative = task.get("narrative", "direct")

    # 2. Геометрия
    right_angle = target.get("right_angle")
    target_angle = target.get("angle")
    func_name = target.get("fn")

    vertex_set = {"A", "B", "C"}
    hyp_name = "".join(sorted(list(vertex_set - {right_angle})))
    opp_name = "".join(sorted(list(vertex_set - {target_angle})))
    adj_name = "".join(sorted([target_angle, right_angle]))

    def get_val(name):
        return given.get(name) or given.get(name[::-1])

    # Получаем все значения (даже если они вычислены валидатором)
    full_hyp = get_val(hyp_name)
    full_opp = get_val(opp_name)
    full_adj = get_val(adj_name)

    # 3. Настройка отображения (Что показывать в "Дано"?)
    show_hyp = False
    show_opp = False
    show_adj = False
    calc_step = None

    if narrative == "direct":
        # Показываем ТОЛЬКО то, что нужно для формулы
        if func_name == "sin":
            show_opp, show_hyp = True, True
        elif func_name == "cos":
            show_adj, show_hyp = True, True
        elif func_name == "tg":
            show_opp, show_adj = True, True

    elif narrative == "calc_hyp":
        # Даны два катета, ищем гипотенузу
        show_opp, show_adj = True, True

        calc_step = {
            "type": "find_hyp", # Для шаблона (если нужно условие)
            "formula": f"{hyp_name}² = {opp_name}² + {adj_name}²",
            "calc_str": f"{int(full_opp)}² + {int(full_adj)}² = {int(full_opp**2)} + {int(full_adj**2)} = {int(full_hyp**2)}",
            "res": int(full_hyp),
            "target_name": hyp_name
        }

    elif narrative == "calc_leg":
        # Дана гипотенуза и один катет
        show_hyp = True

        # Определяем, какой катет нам ИЗВЕСТЕН, а какой ИЩЕМ.
        # Логика:
        # Если нужен sin (opp/hyp) -> значит не хватало opp -> известен adj.
        # Если нужен cos (adj/hyp) -> значит не хватало adj -> известен opp.
        # Если нужен tg (opp/adj) -> тут сложнее. Валидатор мог решить по-разному.
        # Но для tg нам всё равно нужно показать один катет и найти другой.

        target_leg_name = None
        known_leg_name = None

        if func_name == "sin":
            known_leg_name = adj_name
            target_leg_name = opp_name
            show_adj = True
        elif func_name == "cos":
            known_leg_name = opp_name
            target_leg_name = adj_name
            show_opp = True
        else: # tg
            # Эвристика: считаем известным тот, который "красивый" (целый) или просто adj по дефолту
            # Но проще довериться валидатору: если в JSON есть opp и hyp, значит искали adj.
            # Но у нас в given есть ВСЁ.
            # Давай просто покажем ПРИЛЕЖАЩИЙ, а найдем ПРОТИВОЛЕЖАЩИЙ (или наоборот).
            # Для единообразия: пусть известен adj.
            known_leg_name = adj_name
            target_leg_name = opp_name
            show_adj = True

        known_val = get_val(known_leg_name)
        target_val = get_val(target_leg_name)

        calc_step = {
            "type": "find_leg",
            "formula": f"{target_leg_name}² = {hyp_name}² - {known_leg_name}²",
            "calc_str": f"{int(full_hyp)}² - {int(known_val)}² = {int(full_hyp**2)} - {int(known_val**2)} = {int(target_val**2)}",
            "res": int(target_val),
            "target_name": target_leg_name
        }

    # 4. Сборка ответа
    needed_map = {
        "sin": ("opp", "hyp"),
        "cos": ("adj", "hyp"),
        "tg": ("opp", "adj")
    }
    num_type, den_type = needed_map[func_name]
    vals = {"opp": full_opp, "adj": full_adj, "hyp": full_hyp}
    names = {"opp": opp_name, "adj": adj_name, "hyp": hyp_name}

    res_val = vals[num_type] / vals[den_type]

    def fmt(num):
        if num is None: return "?"
        return int(num) if float(num).is_integer() else num

    context = {
        "func_name": func_name,
        "angle": target_angle,
        "right_angle": right_angle,

        "is_sin": func_name == "sin",
        "is_cos": func_name == "cos",
        "is_tg": func_name == "tg",

        "num_name": names[num_type],
        "den_name": names[den_type],
        "num_val": fmt(vals[num_type]),
        "den_val": fmt(vals[den_type]),
        "res": res_val,

        "calc_step": calc_step,

        # ВАЖНО: Передаем только те переменные, которые разрешили флаги
        "given_hyp": fmt(full_hyp) if show_hyp else None,
        "given_opp": fmt(full_opp) if show_opp else None,
        "given_adj": fmt(full_adj) if show_adj else None,

        "hyp_name": hyp_name,
        "opp_name": opp_name,
        "adj_name": adj_name
    }

    return [{
        "action": f"{task['pattern']}:{narrative}",
        "data": context
    }]


# ============================================================
# ПАТТЕРН 4.5: find_side_from_trig_ratio
# Нахождение стороны по sin, cos, tg
# ЭТАЛОННЫЕ ШАГИ: роли -> подстановка сторон -> подстановка чисел -> крест-накрест
# ============================================================
def _solve_find_side_from_trig_ratio(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    variables = task.get("variables", {})
    given = variables.get("given", {})
    target = variables.get("target", {})

    trig_fn = given.get("trig_fn")            # "sin" / "cos" / "tg"
    angle = given.get("angle")                # "A" / "B" / "C"
    right_angle = target.get("right_angle")   # "A" / "B" / "C"
    find_side = target.get("find")            # "AB" / "BC" / "AC"

    vertex_set = {"A", "B", "C"}

    # Названия сторон
    hyp_name = "".join(sorted(vertex_set - {right_angle}))
    opp_name = "".join(sorted(vertex_set - {angle}))
    adj_name = "".join(sorted([angle, right_angle]))

    def _get_val(side: str):
        # важно: не использовать "or", чтобы не ломать 0
        v = given.get(side)
        if v is not None:
            return v
        return given.get(side[::-1])

    def _num(x: float) -> int | float:
        """Число для хранения: int, если целое; иначе float."""
        if abs(x - round(x)) < 1e-9:
            return int(round(x))
        return float(x)

    def _snum(x: float) -> str:
        """Число для печати в шагах (запятая, без .0)."""
        return format_number(float(x))

    # -----------------------------
    # 1) Определяем известную сторону (в задаче она всегда одна)
    # -----------------------------
    known_name = None
    known_val: int | float | None = None

    for side_name in (hyp_name, opp_name, adj_name):
        v = _get_val(side_name)
        if v is not None:
            known_name = side_name
            known_val = _num(float(v))
            break

    if known_val is None or known_name is None:
        raise ValueError(
            f"Не удалось определить заданную сторону в find_side_from_trig_ratio (id={task.get('id')})"
        )

    # -----------------------------
    # 2) Разбираем отношение (в humanizer_data лежит строка вида "12/13")
    # -----------------------------
    ratio_raw = variables.get("humanizer_data", {}).get("ratio", "")
    if not ratio_raw or "/" not in ratio_raw:
        raise ValueError(
            f"Не удалось прочитать ratio для find_side_from_trig_ratio (id={task.get('id')}): {ratio_raw!r}"
        )

    num_str, den_str = ratio_raw.split("/", 1)

    try:
        num = float(num_str)
        den = float(den_str)
    except ValueError:
        raise ValueError(
            f"Некорректное ratio для find_side_from_trig_ratio (id={task.get('id')}): {ratio_raw!r}"
        )

    if abs(num) < 1e-12 or abs(den) < 1e-12:
        raise ValueError(
            f"Некорректное ratio (деление на ноль) для find_side_from_trig_ratio (id={task.get('id')}): {ratio_raw!r}"
        )

    ratio_pretty = f"{_snum(num)}/{_snum(den)}"  # ✅ "6/5", без .0

    # -----------------------------
    # 3) Определяем роли по trig: trig = X / Y
    # -----------------------------
    trig_fn_rus = {"sin": "синуса", "cos": "косинуса", "tg": "тангенса"}.get(trig_fn, str(trig_fn))

    if trig_fn == "sin":
        role_num_rus = "противолежащий катет"
        role_den_rus = "гипотенуза"
        X = opp_name  # числитель
        Y = hyp_name  # знаменатель
    elif trig_fn == "cos":
        role_num_rus = "прилежащий катет"
        role_den_rus = "гипотенуза"
        X = adj_name
        Y = hyp_name
    elif trig_fn == "tg":
        role_num_rus = "противолежащий катет"
        role_den_rus = "прилежащий катет"
        X = opp_name
        Y = adj_name
    else:
        raise ValueError(f"Неизвестная trig_fn={trig_fn!r} (id={task.get('id')})")

    # Искомая сторона должна быть X или Y
    if find_side not in (X, Y):
        raise ValueError(
            f"Искомая сторона {find_side} не участвует в формуле {trig_fn} ({X}/{Y}) "
            f"(id={task.get('id')})"
        )

    # В корректных задачах известная сторона — это как раз одна из X или Y
    if known_name not in (X, Y):
        raise ValueError(
            f"Заданная сторона {known_name} не совпала с формульными сторонами {X} и {Y} "
            f"(id={task.get('id')})"
        )

    # -----------------------------
    # 4) Решаем пропорцию num/den = X/Y
    # -----------------------------
    # Сценарии:
    #   если ищем X -> должна быть известна Y
    #   если ищем Y -> должна быть известна X
    if find_side == X:
        # X искомая -> известна должна быть Y
        if known_name != Y:
            raise ValueError(f"Недостаточно данных: чтобы найти {X}, должна быть задана {Y} (id={task.get('id')})")
        res_val = (num / den) * float(known_val)
        unknown = X
        known_for_eq_side = Y
        known_for_eq_val = float(known_val)
    else:
        # Y искомая -> известна должна быть X
        if known_name != X:
            raise ValueError(f"Недостаточно данных: чтобы найти {Y}, должна быть задана {X} (id={task.get('id')})")
        res_val = (den / num) * float(known_val)
        unknown = Y
        known_for_eq_side = X
        known_for_eq_val = float(known_val)

    # ✅ храним результат как int, если целое
    res: int | float = _num(res_val)
    res_pretty = _snum(float(res))

    # -----------------------------
    # 5) Готовим эталонные строки (только текст)
    # -----------------------------
    equation_left = f"{_snum(num)}/{_snum(den)}"

    # Всегда строим правую часть так, чтобы там были "число" и "неизвестная сторона"
    # Если неизвестная в знаменателе:  num/den = known/unknown
    # Если неизвестная в числителе:   num/den = unknown/known
    if unknown == Y:
        # unknown в знаменателе
        equation_right = f"{_snum(known_for_eq_val)}/{unknown}"
        cross1 = f"{_snum(num)} · {unknown} = {_snum(den)} · {_snum(known_for_eq_val)}"
        cross2 = f"{unknown} = {_snum(den * known_for_eq_val)}/{_snum(num)} = {_snum(float(res))}"
    else:
        # unknown в числителе
        equation_right = f"{unknown}/{_snum(known_for_eq_val)}"
        cross1 = f"{_snum(num)} · {_snum(known_for_eq_val)} = {_snum(den)} · {unknown}"
        cross2 = f"{unknown} = {_snum(num * known_for_eq_val)}/{_snum(den)} = {_snum(float(res))}"

    # -----------------------------
    # 6) Контекст для humanizer
    # -----------------------------
    context = {
        "trig_fn": trig_fn,
        "trig_fn_rus": trig_fn_rus,
        "angle": angle,
        "right_angle": right_angle,

        "hyp_name": hyp_name,
        "opp_name": opp_name,
        "adj_name": adj_name,

        "known_name": known_name,
        "known_val": known_val,          # ✅ int/float без .0
        "ratio": ratio_pretty,           # ✅ "6/5"

        # роли/стороны
        "role_num_rus": role_num_rus,
        "role_den_rus": role_den_rus,
        "role_num_side": X,
        "role_den_side": Y,

        # эталонные строки
        "equation_left": equation_left,
        "equation_right": equation_right,
        "cross1": cross1,
        "cross2": cross2,

        # результат
        "res": res,                      # ✅ int/float без .0
        "res_pretty": res_pretty,        # ✅ строка для шаблонов humanizer
        "target_side": find_side,
    }

    return [{
        "action": task["pattern"],
        "data": context
    }]

# ============================================================
# ПАТТЕРН 4.6: right_triangle_median_to_hypotenuse
# Свойство медианы, проведённой к гипотенузе
# ============================================================
def _solve_right_triangle_median_to_hypotenuse(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Свойство:
    В прямоугольном треугольнике медиана,
    проведённая к гипотенузе, равна половине гипотенузы.

    Сценарии (через narrative):
    - find_median_by_hypotenuse
    - find_hypotenuse_by_median
    """

    variables = task.get("variables", {})
    given = variables.get("given", {})

    narrative = task.get("narrative")
    right_angle = given.get("right_angle")          # A / B / C
    hypotenuse = given.get("hypotenuse")            # AB / BC / AC
    median_point = given.get("median_point", "M")  # M

    # Ответ уже вычислен валидатором
    res = task.get("answer")
    if res is None:
        raise ValueError(
            f"В задаче отсутствует answer "
            f"для right_triangle_median_to_hypotenuse (id={task.get('id')})"
        )

    # Название медианы: AM / BM / CM
    median_name = f"{right_angle}{median_point}"

    # --------------------------------------------------------
    # ЛОГИКА ЧЕРЕЗ NARRATIVE
    # --------------------------------------------------------
    if narrative == "find_median_by_hypotenuse":
        target = "median"
        formula = f"{median_name} = {hypotenuse} / 2"

    elif narrative == "find_hypotenuse_by_median":
        target = "hypotenuse"
        formula = f"{hypotenuse} = 2 · {median_name}"

    else:
        raise ValueError(
            f"Неизвестный narrative {narrative!r} "
            f"в right_triangle_median_to_hypotenuse (id={task.get('id')})"
        )

    # --------------------------------------------------------
    # КОНТЕКСТ ДЛЯ HUMANIZER
    # --------------------------------------------------------
    context = {
        "right_angle": right_angle,
        "hyp_name": hypotenuse,
        "median_name": median_name,

        "narrative": narrative,
        "target": target,
        "formula": formula,

        # ⬇️ ВАЖНО
        "given_hyp": None,
        "given_med": None,

        "res": res,
    }

    if narrative == "find_median_by_hypotenuse":
        context["given_hyp"] = context["hyp_name"]

    elif narrative == "find_hypotenuse_by_median":
        context["given_med"] = context["median_name"]

    return [{
        "action": f"{task['pattern']}:{narrative}",
        "narrative": narrative,   # ← ВОТ ЭТО КРИТИЧНО
        "data": context
    }]


# ============================================================================
# ДИСПЕТЧЕР ТЕМЫ 4
# ============================================================================
HANDLERS = {
    "right_triangle_angles_sum": _solve_right_triangle_angles_sum,
    "pythagoras_find_leg": _solve_pythagoras_find_leg,
    "pythagoras_find_hypotenuse": _solve_pythagoras_find_hypotenuse,
    "find_cos_sin_tg_from_sides": _solve_find_cos_sin_tg_from_sides,
    "find_side_from_trig_ratio": _solve_find_side_from_trig_ratio,
    "right_triangle_median_to_hypotenuse": _solve_right_triangle_median_to_hypotenuse,
}


def solve(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Универсальный вход для ТЕМЫ 4 (Прямоугольные треугольники)
    """
    pattern = task.get("pattern")
    handler = HANDLERS.get(pattern)

    if not handler:
        raise ValueError(
            f"[Task 15 | Theme 4] Решатель для паттерна '{pattern}' не найден."
        )

    return handler(task)
