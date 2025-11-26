"""
Solver for Task 8: Integer Expressions.
Implements step-by-step logic for:
- alg_power_fraction
- alg_radical_power
- alg_radical_fraction
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Any, Dict, List, Tuple, Optional

from matunya_bot_final.help_core.solvers.task_8.task_8_text_formatter import (
    render_node,
    to_superscript,
    fmt_number
)


def solve(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Главная точка входа."""
    if not isinstance(task_data, dict):
        raise ValueError("task_data должен быть словарём")

    pattern = task_data.get("solution_pattern") or task_data.get("pattern")

    if pattern == "alg_power_fraction":
        return _solve_power_fraction(task_data)

    if pattern == "alg_radical_power":
        return _solve_radical_power(task_data)

    if pattern == "alg_radical_fraction":
        return _solve_radical_fraction(task_data)

    return _solve_placeholder(task_data, pattern or "unknown")


def _solve_placeholder(task_data: Dict[str, Any], pattern: str) -> Dict[str, Any]:
    return {
        "question_id": f"task8_{pattern}",
        "question_group": "task_8_integer_expressions",
        "explanation_idea": "Решение в разработке.",
        "calculation_steps": [],
        "final_answer": {"value_display": task_data.get("answer", "???")},
    }


# ============================================================================
# 1. ALG_POWER_FRACTION
# ============================================================================
def _solve_power_fraction(task_data: Dict[str, Any]) -> Dict[str, Any]:
    steps = _build_steps_for_power_fraction(task_data)
    return {
        "question_id": "task8_alg_power_fraction",
        "question_group": "task_8_integer_expressions",
        "explanation_idea_key": "IDEA_ALG_POWER_FRACTION",
        "knowledge_tips_key": "KNOWLEDGE_ALG_POWER_FRACTION",
        "calculation_steps": steps,
        "final_answer": {
            "value_display": task_data["answer"],
        },
    }

def _build_steps_for_power_fraction(task_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    tree = task_data["expression_tree"]
    variables = task_data["variables"]
    vars_disp = task_data.get("variables_display") or {k: fmt_number(v) for k, v in variables.items()}

    steps = []
    step_num = 1

    # --- ШАГ 1. Исходное выражение ---
    expr_str = render_node(tree)
    vars_str = ", ".join([f"<b>{k} = {v}</b>" for k, v in vars_disp.items()])

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_INITIAL",
        "description_params": {"expr": expr_str, "vars": vars_str}
    })
    step_num += 1

    # --- ШАГ 2. Числитель ---
    numerator = tree["numerator"]
    factors = numerator.get("factors", [numerator]) if numerator.get("type") == "product" else [numerator]

    num_actions = []
    num_powers = {} # {var: total_power}

    # Логика упрощения числителя (a^n)^m -> a^nm
    for f in factors:
        if f.get("type") == "power" and f["base"].get("type") == "power":
            var = f["base"]["base"]["name"]
            inn = f["base"]["exp"]["value"]
            out = f["exp"]["value"]
            res = inn * out
            line = f"({var}{to_superscript(inn)}){to_superscript(out)} = {var}{to_superscript(res)}"
            num_actions.append(f"<b>{line}</b> (по свойству (aᵐ)ⁿ = aᵐⁿ)")
            num_powers[var] = num_powers.get(var, 0) + res
        elif f.get("type") == "power" and f["base"].get("type") == "variable":
            var = f["base"]["name"]
            num_powers[var] = num_powers.get(var, 0) + f["exp"]["value"]
        elif f.get("type") == "variable":
            var = f["name"]
            num_powers[var] = num_powers.get(var, 0) + 1

    # Формируем строку "Получаем в числителе..."
    simplified_num_parts = []
    for var in sorted(num_powers.keys()):
        p = num_powers[var]
        simplified_num_parts.append(f"{var}{to_superscript(p)}")
    simplified_num_str = " · ".join(simplified_num_parts)

    # Добавляем промежуточный итог в описание шага
    if simplified_num_parts:
        num_actions.append("") # Пустая строка для отступа
        num_actions.append("Получаем в числителе")
        num_actions.append(f"➡️ <b>{simplified_num_str}</b>")

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_SIMPLIFY_NUMERATOR",
        "description_params": {"expr": render_node(numerator)},
        "formula_calculation": "\n".join(num_actions)
    })
    step_num += 1

    # --- ШАГ 3 (Опциональный). Знаменатель ---
    denominator = tree["denominator"]
    den_powers = {}
    den_str = render_node(denominator)

    # Проверяем, сложный ли знаменатель: (ab)^n
    is_complex_den = False
    if denominator.get("type") == "power" and denominator["base"].get("type") == "product":
        is_complex_den = True

    # Сбор степеней знаменателя
    if denominator.get("type") == "power":
        d_exp = denominator["exp"]["value"]
        if denominator["base"].get("type") == "variable":
            den_powers[denominator["base"]["name"]] = d_exp
        elif denominator["base"].get("type") == "product":
             for sub in denominator["base"]["factors"]:
                 if sub.get("type") == "variable":
                     den_powers[sub["name"]] = d_exp
    elif denominator.get("type") == "variable":
        den_powers[denominator["name"]] = 1

    simplified_den_parts = []
    for var in sorted(den_powers.keys()):
        p = den_powers[var]
        simplified_den_parts.append(f"{var}{to_superscript(p)}")
    simplified_den_str = " · ".join(simplified_den_parts)

    # Если знаменатель был сложный ((ab)^18), добавляем отдельный шаг
    if is_complex_den:
        den_action = f"<b>{den_str} = {simplified_den_str}</b>"

        # Итоговая дробь после упрощения верха и низа
        full_fraction_str = f"({simplified_num_str}) / ({simplified_den_str})"

        steps.append({
            "step_number": step_num,
            "description_key": "STEP_SIMPLIFY_DENOMINATOR",
            "description_params": {"expr": den_str},
            "formula_calculation": f"{den_action}\n\nПолучили выражение\n➡️ <b>{full_fraction_str}</b>"
        })
        step_num += 1

    # --- ШАГ 4. Деление ---
    div_actions = []
    final_powers = {}
    final_vars_str_parts = []

    for var in sorted(num_powers.keys()):
        n_p = num_powers[var]
        d_p = den_powers.get(var, 0)
        res = n_p - d_p
        final_powers[var] = res

        line = f"{var}{to_superscript(n_p)} : {var}{to_superscript(d_p)} = {var}{to_superscript(str(n_p)+'-'+str(d_p))} = {var}{to_superscript(res)}"
        div_actions.append(f"<b>{line}</b>")

        # Собираем a^2 для итога
        final_vars_str_parts.append(f"{var}{to_superscript(res)}")

    final_vars_str = " · ".join(final_vars_str_parts)

    # Добавляем "После сокращения..."
    div_actions.append("")
    div_actions.append("После сокращения получили выражение")
    div_actions.append(f"➡️ <b>{final_vars_str}</b>")

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_DIVIDE_POWERS",
        "formula_calculation": "\n".join(div_actions)
    })
    step_num += 1

    # --- ШАГ 5. Подстановка (Цепочка) ---
    # Формируем: a^2 · b^2 = 3^2 · 5^2 = 9 · 25 = 225

    chain_algebra = final_vars_str
    chain_subst_parts = []
    chain_calc_parts = []
    final_val = 1.0
    is_fraction_res = False

    for var in sorted(final_powers.keys()):
        p = final_powers[var]
        v_disp = vars_disp[var]
        v_val = variables[var]

        if p < 0:
            is_fraction_res = True

        # 3^2
        chain_subst_parts.append(f"{v_disp}{to_superscript(p)}")

        # 9 (Вычисление)
        val_pow = v_val ** p

        # --- ВСТАВЛЯЕМ ЛЕКАРСТВО ЗДЕСЬ ---
        val_pow = round(val_pow, 9)  # Округляем, чтобы убрать 0.4999999
        # ---------------------------------

        chain_calc_parts.append(fmt_number(int(val_pow) if val_pow.is_integer() else val_pow))
        final_val *= val_pow

    chain_subst = " · ".join(chain_subst_parts)
    chain_calc = " · ".join(chain_calc_parts)
    final_res_str = task_data["answer"]

    # Если цепочка имеет смысл (не просто одно число)
    if len(final_powers) > 0:
        full_chain = f"<b>{chain_algebra} = {chain_subst} = {chain_calc} = {final_res_str}</b>"

        steps.append({
            "step_number": step_num,
            "description_key": "STEP_SUBSTITUTE_AND_CALC",
            "description_params": {"vars": vars_str},
            "formula_calculation": full_chain
        })
    else:
        # Fallback, если переменные исчезли (хотя в этом типе такого не бывает)
        steps.append({
            "step_number": step_num,
            "description_key": "STEP_WRITE_ANSWER",
            "formula_calculation": f"<b>{final_res_str}</b>"
        })

    return steps


# ============================================================================
# 2. ALG_RADICAL_POWER
# ============================================================================
def _solve_radical_power(task_data: Dict[str, Any]) -> Dict[str, Any]:
    steps = _build_steps_for_radical_power(task_data)
    return {
        "question_id": "task8_alg_radical_power",
        "question_group": "task_8_integer_expressions",
        "explanation_idea_key": "IDEA_ALG_RADICAL_POWER",
        "knowledge_tips_key": "KNOWLEDGE_ALG_RADICAL_POWER",
        "calculation_steps": steps,
        "final_answer": {
            "value_display": task_data["answer"],
        },
    }

def _build_steps_for_radical_power(task_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    tree = task_data["expression_tree"]
    variables = task_data["variables"]
    vars_disp = task_data.get("variables_display") or {k: fmt_number(v) for k, v in variables.items()}

    steps = []
    step_num = 1

    # --- ШАГ 1. Рассмотрим исходное выражение ---
    expr_str = render_node(tree)
    # ИСПРАВЛЕНИЕ: Сначала создаем переменную, чтобы использовать её и тут, и в конце
    vars_str = ", ".join([f"<b>{k} = {v}</b>" for k, v in vars_disp.items()])

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_INITIAL",
        "description_params": {
            "expr": expr_str,
            "vars": vars_str
        }
    })
    step_num += 1

    radicand = tree["radicand"]
    simplify_actions = []
    final_powers = {}
    final_coeff = 1

    # 2. Simplify
    if radicand.get("type") == "fraction":
        desc_key = "STEP_SIMPLIFY_RADICAND_FRACTION"
        # Упрощенный сбор (копируем логику из прошлого кода, но сжато)
        # ... Логика сбора степеней и деления ...
        # Для экономии места я тут ставлю заглушку логики, т.к. мы фокусируемся на паттерне 3.
        # Но в реальном файле тут должен быть код из прошлого моего ответа про radical_power.
        # (Я его вернул ниже, чтобы файл был полным)
        num_c, num_p = _collect_powers_from_node(radicand["numerator"])
        den_c, den_p = _collect_powers_from_node(radicand["denominator"])
        final_coeff = int(num_c / den_c)
        for var, n_val in num_p.items():
            d_val = den_p.get(var, 0)
            res = n_val - d_val
            final_powers[var] = res
            line = f"{var}{to_superscript(n_val)} / {var}{to_superscript(d_val)} = {var}{to_superscript(res)}"
            simplify_actions.append(f"<b>{line}</b>")
    else:
        desc_key = "STEP_SIMPLIFY_RADICAND_PRODUCT"
        final_coeff, final_powers = _collect_powers_from_node(radicand)

    if simplify_actions:
        steps.append({
            "step_number": step_num,
            "description_key": desc_key,
            "formula_calculation": "\n".join(simplify_actions)
        })
    else:
        steps.append({
            "step_number": step_num,
            "description_key": "STEP_RADICAND_ALREADY_SIMPLE"
        })
    step_num += 1

    # 3. Substitute back
    radicand_parts = []
    if final_coeff != 1: radicand_parts.append(str(final_coeff))
    for var, p in final_powers.items(): radicand_parts.append(f"{var}{to_superscript(p)}")
    # Склеиваем без точек для компактности под корнем, как в эталоне: 100a²
    rad_str = "".join(radicand_parts)
    if len(radicand_parts) > 1 and radicand_parts[0].isdigit():
         rad_str = radicand_parts[0] + "·" + "".join(radicand_parts[1:])

    full_root = f"√({rad_str})"
    steps.append({
        "step_number": step_num,
        "description_key": "STEP_SUBSTITUTE_INTO_ROOT",
        "formula_calculation": f"<b>{full_root}</b>"
    })
    step_num += 1

    # 4. Extract
    split_parts = []
    res_parts = []
    calc_coeff = 1
    final_vars = {}

    if final_coeff != 1:
        split_parts.append(f"√{final_coeff}")
        root_v = int(final_coeff ** 0.5)
        res_parts.append(str(root_v))
        calc_coeff = root_v

    for var, p in final_powers.items():
        split_parts.append(f"√{var}{to_superscript(p)}")
        new_p = p // 2
        final_vars[var] = new_p
        if new_p == 1: res_parts.append(var)
        else: res_parts.append(f"{var}{to_superscript(new_p)}")

    split_str = " · ".join(split_parts)
    res_str = "".join(res_parts)

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_EXTRACT_ROOT",
        "formula_calculation": f"<b>{full_root} = {split_str} = {res_str}</b>"
    })
    step_num += 1

    # 5. Calc
    calc_expr = []
    final_val = calc_coeff
    if calc_coeff != 1: calc_expr.append(str(calc_coeff))

    for var, p in final_vars.items():
        v_val = variables[var]
        v_disp = vars_disp.get(var, str(v_val))
        if p == 1:
            calc_expr.append(v_disp)
            final_val *= v_val
        else:
            calc_expr.append(f"{v_disp}{to_superscript(p)}")
            final_val *= (v_val ** p)

    calc_s = " · ".join(calc_expr)
    res_final = fmt_number(int(final_val) if final_val.is_integer() else final_val)

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_SUBSTITUTE_FINAL",
        "description_params": {"vars": vars_str},
        "formula_calculation": f"<b>{calc_s} = {res_final}</b>"
    })

    return steps


# ============================================================================
# 3. ALG_RADICAL_FRACTION (НОВЫЙ ПАТТЕРН)
# ============================================================================
def _solve_radical_fraction(task_data: Dict[str, Any]) -> Dict[str, Any]:
    steps = _build_steps_for_radical_fraction(task_data)

    tree = task_data["expression_tree"]

    # Определяем, где сложность: в числителе или знаменателе?
    # Если числитель - это произведение (product), значит сложность там.
    if tree["numerator"].get("type") == "product":
        location_text = "числителе"
    else:
        # Иначе считаем, что в знаменателе (как в твоем примере с багами)
        location_text = "знаменателе"

    # Логика обнаружения "пропавшей" переменной для подсказки
    input_vars = set(task_data["variables"].keys())
    # Эвристика: берем последний шаг (подстановка), ищем скрытые параметры
    attention_key = steps[-1].get("__attention_key")
    attention_params = steps[-1].get("__attention_params")

    return {
        "question_id": "task8_alg_radical_fraction",
        "question_group": "task_8_integer_expressions",
        "explanation_idea_key": "IDEA_ALG_RADICAL_FRACTION",
        # ПЕРЕДАЕМ ПАРАМЕТР ДЛЯ ИДЕИ
        "explanation_idea_params": {"location": location_text},

        "knowledge_tips_key": "KNOWLEDGE_ALG_RADICAL_FRACTION",
        "calculation_steps": steps,
        "final_answer": {
            "value_display": task_data["answer"],
        },
        "attention_tips_key": attention_key,
        "attention_tips_params": attention_params
    }

def _build_steps_for_radical_fraction(task_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    tree = task_data["expression_tree"]
    variables = task_data["variables"]
    vars_disp = task_data.get("variables_display") or {k: fmt_number(v) for k, v in variables.items()}

    steps = []
    step_num = 1

    # 1. Initial
    steps.append({
        "step_number": step_num,
        "description_key": "STEP_INITIAL",
        "description_params": {
            "expr": render_node(tree),
            "vars": ", ".join([f"<b>{k} = {v}</b>" for k, v in vars_disp.items()])
        }
    })
    step_num += 1

    # --- ВНУТРЕННЯЯ ФУНКЦИЯ АНАЛИЗА ЧАСТИ ---
    def _analyze_part(node):
            factors = node.get("factors", [node]) if node.get("type") == "product" else [node]
            is_complex = (len(factors) > 1)

            formulas = []
            transformed_parts = []

            # Аккумуляторы для этой части
            p_out_c, p_out_v = 1, {}
            p_in_c, p_in_v = 1, {}

            for f in factors:
                if f.get("type") == "sqrt":
                    # 1. Детальное разложение (твоя логика)
                    raw_c, raw_p = _collect_powers_from_node(f["radicand"])
                    parts_split = []
                    parts_roots = []

                    if raw_c != 1:
                        parts_split.append(str(raw_c))
                        parts_roots.append(f"√{raw_c}")

                    for v, p in raw_p.items():
                        even_p = (p // 2) * 2
                        rem_p = p % 2
                        if even_p > 0:
                            parts_split.append(f"{v}{to_superscript(even_p)}")
                            parts_roots.append(f"√{v}{to_superscript(even_p)}")
                        if rem_p > 0:
                            parts_split.append(v)
                            parts_roots.append(f"√{v}")

                    str_split = " · ".join(parts_split)
                    str_roots = " · ".join(parts_roots)

                    # 2. Итог части
                    out_c, out_v, in_c, in_v = _decompose_sqrt_node(f)
                    res_str = _format_radical_component(out_c, out_v, in_c, in_v)
                    src_str = render_node(f)

                    # Строка шага
                    if str_split and str_split != src_str.replace("√", "").replace("(", "").replace(")", ""):
                        full_line = f"<b>{src_str} = √({str_split}) = {str_roots} = {res_str}</b>"
                        formulas.append(full_line)
                    elif is_complex:
                        formulas.append(f"<b>{src_str} = {res_str}</b>")

                    transformed_parts.append(res_str)

                    # Суммируем показатели
                    p_out_c *= out_c
                    p_in_c *= in_c
                    for v, p in out_v.items(): p_out_v[v] = p_out_v.get(v, 0) + p
                    for v, p in in_v.items(): p_in_v[v] = p_in_v.get(v, 0) + p

                else:
                    # Не корень (редкость)
                    transformed_parts.append(render_node(f))
                    f_c, f_p = _extract_linear_powers(f)
                    p_out_c *= f_c
                    for v, p in f_p.items(): p_out_v[v] = p_out_v.get(v, 0) + p

            final_str = _format_radical_component(p_out_c, p_out_v, p_in_c, p_in_v)

            if is_complex:
                join_trans = " · ".join(transformed_parts)
                formulas.append(f"<b>{join_trans} = {final_str}</b>")

            return final_str, formulas, p_out_c, p_out_v, p_in_c, p_in_v, is_complex

    # --- АНАЛИЗ ---
    # Получаем данные и по числителю, и по знаменателю
    num_res, num_forms, num_out_c, num_out_v, num_in_c, num_in_v, num_is_complex = _analyze_part(tree["numerator"])
    den_res, den_forms, den_out_c, den_out_v, den_in_c, den_in_v, den_is_complex = _analyze_part(tree["denominator"])

    # 2. Transform (Выбираем, что показать)
    # Если знаменатель сложный, а числитель простой -> показываем про знаменатель
    target_is_numerator = True
    if den_is_complex and not num_is_complex:
        target_is_numerator = False

    # Данные для шага 2
    formulas_to_show = num_forms if target_is_numerator else den_forms
    res_to_show = num_res if target_is_numerator else den_res

    # Текстовые параметры для шаблона
    part_genitive = "числителе" if target_is_numerator else "знаменателе" # (в)
    part_accusative = "числитель" if target_is_numerator else "знаменатель" # (подставим)

    decomp_str = "\n".join([f"➡️ {line}" for line in formulas_to_show])

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_TRANSFORM_PART",
        "description_params": {
            "part": part_genitive,
            "decomp_str": decomp_str
        },
        "formula_calculation": f"<b>{res_to_show}</b>"
    })
    step_num += 1

    # 3. Substitute (Подстановка в дробь)
    num_raw = render_node(tree["numerator"])
    den_raw = render_node(tree["denominator"])

    if target_is_numerator:
        # Упростили числитель: (New) / Old
        frac_show = f"<b>({num_res}) / {den_raw}</b>"
    else:
        # Упростили знаменатель: Old / (New)
        frac_show = f"<b>{num_raw} / ({den_res})</b>"

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_SUBSTITUTE_INTO_FRACTION",
        "description_params": {"part": part_accusative},
        "formula_calculation": frac_show
    })
    step_num += 1

    # 4. Reduce (Сокращение и формирование красивой дроби)
    # А. Математические значения (для вычислений в Шаге 5)
    res_out_c = num_out_c / den_out_c
    res_in_c = num_in_c / den_in_c # = 1

    res_out_v = {}
    all_vars = set(num_out_v) | set(den_out_v)
    for v in all_vars:
        p = num_out_v.get(v, 0) - den_out_v.get(v, 0)
        if p != 0: res_out_v[v] = p
    res_in_v = {}

    # Б. Визуальные значения (для красивого отображения 1 / 10ab)
    # Находим общий множитель коэффициентов
    common_gcd = math.gcd(int(num_out_c), int(den_out_c))
    vis_num_c = int(num_out_c) // common_gcd
    vis_den_c = int(den_out_c) // common_gcd

    # Распределяем переменные: у кого степень больше, тот и остается хозяином
    vis_num_v = {}
    vis_den_v = {}
    for v in all_vars:
        n = num_out_v.get(v, 0)
        d = den_out_v.get(v, 0)
        if n >= d:
            if n - d > 0: vis_num_v[v] = n - d
        else:
            if d - n > 0: vis_den_v[v] = d - n

    # Собираем части
    str_num = _format_radical_component(vis_num_c, vis_num_v, 1, {})
    str_den = _format_radical_component(vis_den_c, vis_den_v, 1, {})

    if str_den == "1":
        final_res_str = str_num
    else:
        final_res_str = f"{str_num} / {str_den}"

    # На что сокращали?
    term_reduce = den_raw if target_is_numerator else num_raw
    n_fin = f"({num_res})" if num_is_complex else num_raw
    d_fin = f"({den_res})" if den_is_complex else den_raw

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_REDUCE_ROOTS",
        "description_params": {"term": term_reduce},
        "formula_calculation": f"<b>{n_fin} / {d_fin} = {final_res_str}</b>"
    })
    step_num += 1

    # 5. Final Calc
    # 1. Преобразуем математический результат в числитель и знаменатель
    frac_c = Fraction(res_out_c).limit_denominator()
    fn_c = frac_c.numerator
    fd_c = frac_c.denominator

    fn_vars = {}
    fd_vars = {}
    for v, p in res_out_v.items():
        if p > 0: fn_vars[v] = p
        elif p < 0: fd_vars[v] = abs(p)

    # 2. Хелпер для сборки частей
    def _build_parts(coeff, var_map):
        alg_parts = []
        subst_parts = []
        val_parts = []
        current_val = coeff

        if coeff != 1 or not var_map:
            alg_parts.append(str(coeff))
            subst_parts.append(str(coeff))
            val_parts.append(str(coeff))

        for v, p in var_map.items():
            val = variables[v]
            disp = vars_disp[v]

            if p == 1: alg_parts.append(v)
            else: alg_parts.append(f"{v}{to_superscript(p)}")

            if p == 1: subst_parts.append(disp)
            else: subst_parts.append(f"{disp}{to_superscript(p)}")

            v_pow = val ** p
            v_pow = round(v_pow, 9)
            v_fmt = fmt_number(int(v_pow) if v_pow.is_integer() else v_pow)
            val_parts.append(v_fmt)

            current_val *= v_pow

        return " · ".join(alg_parts), " · ".join(subst_parts), " · ".join(val_parts), current_val

    alg_n, sub_n, val_n_str, val_n = _build_parts(fn_c, fn_vars)
    alg_d, sub_d, val_d_str, val_d = _build_parts(fd_c, fd_vars)

    # Хелпер: добавляет скобки, если в выражении есть умножение
    def _wrap(s):
        if "·" in s: return f"({s})"
        return s

    # 3. Собираем формулу
    final_ans_str = task_data["answer"]

    if val_d == 1:
        # Линейный случай: 10 · 3² = ...
        if sub_n == val_n_str:
             formula_str = f"<b>{alg_n} = {sub_n} = {final_ans_str}</b>"
        else:
             formula_str = f"<b>{alg_n} = {sub_n} = {val_n_str} = {final_ans_str}</b>"
    else:
        # Дробный случай: 1 / (10 · a²)
        # Оборачиваем знаменатель (и числитель, если сложный) в скобки
        frac_alg = f"{_wrap(alg_n)} / {_wrap(alg_d)}"
        frac_sub = f"{_wrap(sub_n)} / {_wrap(sub_d)}"
        frac_val = f"{_wrap(val_n_str)} / {_wrap(val_d_str)}"

        simple_n = fmt_number(int(val_n) if val_n.is_integer() else val_n)
        simple_d = fmt_number(int(val_d) if val_d.is_integer() else val_d)
        frac_simple = f"{simple_n} / {simple_d}"

        show_mid = (sub_n != val_n_str) or (sub_d != val_d_str)

        if show_mid:
            formula_str = f"<b>{frac_alg} = {frac_sub} = {frac_val} = {frac_simple} = {final_ans_str}</b>"
        else:
            formula_str = f"<b>{frac_alg} = {frac_sub} = {frac_simple} = {final_ans_str}</b>"

    # 4. Attention & Vars Formatting
    vars_in_result = set(fn_vars.keys()) | set(fd_vars.keys())
    vars_in_input = set(variables.keys())
    gone_vars = vars_in_input - vars_in_result

    attention_key = None
    attention_params = {}
    if gone_vars:
        attention_key = "ATTENTION_ALG_RADICAL_FRACTION_VAR_GONE"
        attention_params = {"var": list(gone_vars)[0]}

    vars_to_show = vars_in_result if vars_in_result else vars_in_input

    # ИСПРАВЛЕНО: Форматируем числа переменных (1.0 -> 1)
    vars_list = []
    for k in vars_to_show:
        v = variables[k]
        # Если число целое (например, 10.0), делаем int -> str (10)
        # Иначе оставляем как есть, fmt_number сделает запятую
        v_clean = int(v) if v.is_integer() else v
        vars_list.append(f"<b>{k}={fmt_number(v_clean)}</b>")

    vars_str = ", ".join(vars_list)

    steps.append({
        "step_number": step_num,
        "description_key": "STEP_SUBSTITUTE_FINAL",
        "description_params": {"vars": vars_str},
        "formula_calculation": formula_str,
        "__attention_key": attention_key,
        "__attention_params": attention_params
    })

    return steps


# ============================================================================
# HELPERS
# ============================================================================

def _collect_powers_from_node(node: Dict[str, Any]) -> Tuple[int, Dict[str, int]]:
    """Собирает коэффициент и степени переменных из узла."""
    p_map = {}
    c_val = 1
    factors = node.get("factors", [node]) if node.get("type") == "product" else [node]
    for f in factors:
        if f.get("type") == "power":
            if f["base"].get("type") == "variable":
                name = f["base"]["name"]
                p_map[name] = p_map.get(name, 0) + f["exp"]["value"]
            elif f["base"].get("type") == "product":
                 for sub in f["base"]["factors"]:
                     if sub.get("type") == "variable":
                         p_map[sub["name"]] = p_map.get(sub["name"], 0) + f["exp"]["value"]
        elif f.get("type") == "variable":
            p_map[f["name"]] = p_map.get(f["name"], 0) + 1
        elif f.get("type") == "integer":
            c_val *= f["value"]
    return c_val, p_map

def _decompose_sqrt_node(node: Dict[str, Any]) -> Tuple[int, Dict[str, int], int, Dict[str, int]]:
    """
    Разбивает sqrt(...) на внешнюю и внутреннюю часть.
    Returns: (out_c, out_v, in_c, in_v)
    """
    coeff, powers = _collect_powers_from_node(node["radicand"])

    out_c = 1
    in_c = coeff

    # Извлекаем корень из числа, если полный квадрат
    root_c = math.isqrt(coeff)
    if root_c * root_c == coeff:
        out_c = root_c
        in_c = 1
    # Если не полный, оставляем внутри (упрощенно)

    out_v = {}
    in_v = {}

    for v, p in powers.items():
        out_p = p // 2
        in_p = p % 2
        if out_p > 0: out_v[v] = out_p
        if in_p > 0: in_v[v] = in_p

    return out_c, out_v, in_c, in_v

def _format_radical_component(out_c, out_v, in_c, in_v) -> str:
    """Собирает строку вида 5a√b или 10ab²√(ab)."""
    parts = []
    # Outside (Множители перед корнем)
    if out_c != 1: parts.append(str(out_c))
    for v, p in out_v.items():
        if p == 1: parts.append(v)
        else: parts.append(f"{v}{to_superscript(p)}")

    outside = "".join(parts)

    # Inside (Множители под корнем)
    in_parts = []
    if in_c != 1: in_parts.append(str(in_c))
    for v, p in in_v.items():
        if p == 1: in_parts.append(v)
        else: in_parts.append(f"{v}{to_superscript(p)}")

    inside = "".join(in_parts) # например "a" или "ab"

    if not inside: return outside or "1"

    # ЛОГИКА СКОБОК:
    # Если под корнем один элемент (например "a" или "5") -> √a
    # Если под корнем несколько элементов ("ab" или "2a") -> √(ab)
    if len(in_parts) > 1:
        rad_str = f"√({inside})"
    else:
        rad_str = f"√{inside}"

    if not outside: return rad_str
    return f"{outside}{rad_str}"

def _extract_linear_powers(node: Dict[str, Any]) -> Tuple[Fraction, Dict[str, int]]:
    """
    Разворачивает выражение в коэффициент и показатели степеней по переменным.
    (Вспомогательная функция для анализа структуры).
    """
    node_type = node.get("type")

    if node_type == "integer":
        return Fraction(node["value"]), {}

    if node_type == "variable":
        return Fraction(1), {node["name"]: 1}

    if node_type == "power":
        base_coeff, base_powers = _extract_linear_powers(node["base"])
        exp_node = node["exp"]

        # Если степень - целое число
        if exp_node.get("type") == "integer":
            exp_value = exp_node["value"]
            coeff = base_coeff ** exp_value
            powers = {var: power * exp_value for var, power in base_powers.items()}
            return coeff, powers

        # Если степень сложная (например, произведение -1 * n)
        # Для упрощения считаем базу как есть (1), а степени не трогаем
        # (В рамках нашей задачи это редкий кейс для линейного разбора)
        return Fraction(1), {}

    if node_type == "product":
        coeff = Fraction(1)
        powers = {}
        factors = node.get("factors", [])
        for factor in factors:
            f_coeff, f_powers = _extract_linear_powers(factor)
            coeff *= f_coeff
            for var, power in f_powers.items():
                powers[var] = powers.get(var, 0) + power
        return coeff, powers

    if node_type == "fraction":
        num_coeff, num_powers = _extract_linear_powers(node["numerator"])
        den_coeff, den_powers = _extract_linear_powers(node["denominator"])
        coeff = num_coeff / den_coeff

        # Вычитаем степени знаменателя
        final_powers = num_powers.copy()
        for var, p in den_powers.items():
            final_powers[var] = final_powers.get(var, 0) - p

        return coeff, final_powers

    # Если тип не распознан или это sqrt (его обрабатываем отдельно)
    return Fraction(1), {}
