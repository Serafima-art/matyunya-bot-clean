"""Формирование человеко-понятного объяснения для решения дробей (задание 6)."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional
import re

# ---------------------------------------------------------------------------
# Шаблоны для описаний шагов
# ---------------------------------------------------------------------------

STEP_TEMPLATES: Dict[str, str] = {
    "SEE_ORIGINAL_EXPRESSION": "{ctx}📘 Рассмотрим выражение: {expression}",
    "CONVERT_ALL_NUMBERS_TO_FRACTIONS": (
        "{ctx}🔄 Переведём числа в дроби:\n"
        "{conversion_list}"
    ),
    "CALCULATE_POWER": "{ctx}⚡ Возводим степень. {extra_explanation}",
    "MULTIPLY_COEFFICIENTS": "{ctx}✳️ Домножаем коэффициенты. {extra_explanation}",
    "APPLY_POWER_OF_TEN_RULE": "{ctx}🔢 Складываем показатели степеней. {extra_explanation}",
    "FINAL_OPERATION": "{ctx}➖ Выполним {operation_name}. {extra_explanation}",
    "DIVIDE_AS_MULTIPLY": "{ctx}➗ Деление заменяем умножением на обратную дробь. {extra_explanation}",
    "FIND_FINAL_ANSWER": "{ctx}🎯 Ответ: {value}",
    "PERFORM_MULTIPLICATION": "{ctx}✖️ Выполним {operation_name}. {extra_explanation}",
    "INITIAL_EXPRESSION": "{ctx}👁️ Рассмотрим выражение: <b>{expression}</b>",
    "FIND_LCM": "{ctx}Находим наименьший общий знаменатель {den1} и {den2}: {lcm}.",
    "SCALE_TO_COMMON_DENOM": (
        "{ctx}Приводим дроби к общему знаменателю {lcm}: "
        "левая дробь становится {left_scaled_num}/{lcm}, правая — {right_scaled_num}/{lcm}."
    ),
    "ADD_OR_SUB_NUMERATORS": (
    "{ctx}{operation_name_cap} числители: {left_num} {sign} {right_num} = {result_num}."
    ),
    "REDUCE_FRACTION": (
        "{ctx}Сокращаем дробь {num}/{den} на {gcd}: получаем {result_num}/{result_den}."
    ),
    "FRACTION_ALREADY_REDUCED": "{ctx}Дробь {num}/{den} уже несократима.",
    "CONVERT_MIXED_FIRST": (
        "{ctx}Преобразуем смешанное число {mixed_text} в неправильную дробь: "
        "({whole}·{den} + {num})/{den} = {result_num}/{result_den}."
    ),
    "CONVERT_MIXED_NEXT": (
        "{ctx}Аналогично преобразуем {mixed_text}: "
        "({whole}·{den} + {num})/{den} = {result_num}/{result_den}."
    ),
    "SHOW_CONVERTED_EXPRESSION": "{ctx}После преобразования работаем с выражением {expression}.",
    "MULTIPLY_FRACTIONS_SETUP": (
        "{ctx}Записываем произведение дробей и вспоминаем правило умножения: "
        "(a/b) · (c/d) = (a·c)/(b·d)."
    ),
    "CROSS_CANCEL": (
        "{ctx}Выполняем предварительное сокращение: {cancellations_text}."
    ),
    "NO_CROSS_CANCEL": (
        "{ctx}Сократить нечего, оставляем множители {num1}, {num2} в числителе и "
        "{den1}, {den2} в знаменателе."
    ),
    "FINAL_MULTIPLICATION": (
    "{ctx}Перемножаем числители и знаменатели: "
    "{num1}·{num2} = {result_num}, {den1}·{den2} = {result_den}. "
    "Получаем произведение дробей."
    ),
    "DIVIDE_SAME_VALUE": "{ctx}Делим число само на себя и сразу получаем 1.",
    "DIVISION_TO_MULTIPLICATION": (
        "{ctx}Заменяем деление на умножение обратной дробью: "
        "{right_num}/{right_den} превращается в {flipped_num}/{flipped_den}."
    ),
    "DIVISION_COMBINED_CANCEL": (
        "{ctx}После замены выполняем сокращение: {cancellations_text}."
    ),
    "DIVISION_COMBINED_NO_CANCEL": (
        "{ctx}После замены деления на умножение сокращать нечего."
    ),
    "DIVISION_FINAL_RESULT": (
        "{ctx}Итоговое значение деления записываем как {result}."
    ),
    "COMPLEX_NUMERATOR_RESULT": "{ctx}Значение числителя равно {value}.",
    "COMPLEX_NUMERATOR_FINAL": "{ctx}Дробь уже несократима, поэтому значение числителя равно {value}.",
    "COMPLEX_DIVISION_SETUP": (
        "{ctx}Теперь делим числитель {numerator} на знаменатель {denominator}."
    ),
    "CONVERT_TO_DECIMAL": (
        "{ctx}Переводим дробь {num}/{den} в десятичное число: {decimal}."
    ),
    "EXTRACT_NUMERATOR": (
        "{ctx}Берём числитель из дроби {num}/{den}: это {num}."
    ),
    "EXTRACT_DENOMINATOR": (
        "{ctx}Берём знаменатель из дроби {num}/{den}: это {den}."
    ),
    "INITIAL_EXPRESSION_DECIMAL": "{ctx}Рассмотрим исходное выражение.",
    "CALCULATE_ADDITION_SIMPLE": "{ctx}Сложим числа {left} и {right}.",
    "CALCULATE_SUBTRACTION_SIMPLE": "{ctx}Вычтем {right} из {left}.",
    "CALCULATE_SUBTRACTION_IN_DENOMINATOR": (
        "{ctx}Выполним вычитание в знаменателе: {left} - {right}. Результат будет отрицательным."
    ),
    "CALCULATE_MULTIPLICATION_NEG_NEG": (
        "{ctx}Умножим {left} на {right}. Произведение двух отрицательных чисел положительно."
    ),
    "CALCULATE_MULTIPLICATION_MIXED_SIGN": (
        "{ctx}Умножим {left} на {right}. Результат будет отрицательным."
    ),
    "CALCULATE_MULTIPLICATION_DEFAULT": "{ctx}Выполним умножение: {left} · {right}.",
    "CALCULATE_DIVISION_FINAL": (
        "{ctx}Теперь разделим числитель {left} на полученный знаменатель {right}."
    ),
    "CALCULATE_DIVISION_DEFAULT": "{ctx}Выполним деление: {left} : {right}.",

    # --- Decimal fractions (task 6) ---
    "DECIMAL_ADD_BOTH_POSITIVE": "{ctx}Складываем положительные десятичные дроби {left} и {right}. Результат: {result}.",
    "DECIMAL_ADD_BOTH_NEGATIVE": "{ctx}Складываем отрицательные десятичные дроби {left} и {right}. Результат: {result}.",
    "DECIMAL_ADD_MIXED_SIGNS": "{ctx}Складываем числа {left} и {right}, имеющие разные знаки. Результат: {result}.",

    "DECIMAL_SUBTRACT_POSITIVE": "{ctx}Вычитаем положительное число {right} из {left}. Результат: {result}.",
    "DECIMAL_SUBTRACT_NEGATIVE": "{ctx}Вычитаем отрицательное число {right}, то есть прибавляем {converted_addend}. Результат: {result}.",

    "DECIMAL_MULTIPLY_BOTH_POSITIVE": "{ctx}Умножаем положительные числа {left} и {right}. Результат: {result}.",
    "DECIMAL_MULTIPLY_BOTH_NEGATIVE": "{ctx}Умножаем два отрицательных числа {left} и {right}. Произведение положительное: {result}.",
    "DECIMAL_MULTIPLY_MIXED_SIGNS": "{ctx}Умножаем числа {left} и {right} с разными знаками. Результат отрицательный: {result}.",

    "DECIMAL_DIVIDE_BOTH_POSITIVE": "{ctx}Выполним деление десятичных дробей {left} и {right}. Так как оба числа положительные, результат положительный: {result}.",
    "DECIMAL_DIVIDE_BOTH_NEGATIVE": "{ctx}Делим два отрицательных числа {left} и {right}. Результат положительный: {result}.",
    "DECIMAL_DIVIDE_MIXED_SIGNS": "{ctx}Делим числа {left} и {right} с разными знаками. Результат отрицательный: {result}.",

    "DECIMAL_SHOW_CONVERTED_EXPRESSION": "{ctx}После вычисления знаменателя работаем с выражением {expression}.",

    # --- Mixed fractions (task 6) ---
    "MIXED_CONVERT_DECIMALS": (
        "{ctx}Переведём все десятичные и смешанные дроби в обыкновенные. "
        "Например, {decimal_examples}."
    ),
    "MIXED_ADDITION_SUBTRACTION": (
        "{ctx}Теперь выполним {operation_name} дробей, соблюдая порядок действий. "
        "Приводим к общему знаменателю и вычисляем результат: {expression_result}."
    ),
    "MIXED_MULTIPLICATION_DIVISION": (
        "{ctx}Выполним умножение и деление дробей: {expression_result}. "
        "Не забываем, что при делении первую дробь умножаем на перевёрнутую вторую."
    ),
    "MIXED_CONVERT_ALL": (
        "{ctx}Конвертируем все числа в обыкновенные дроби:\n"
        "{formulas}"
    ),
    "MIXED_MULTIPLY": (
        "{ctx}Умножаем дроби с предварительным сокращением. В результате получаем: {formula_result}"
    ),
    "MIXED_DIVIDE": (
        "{ctx}Выполняем деление. Деление заменяем умножением на обратную дробь. В результате получаем: {formula_result}"
    ),
    "MIXED_ADD": (
        "{ctx}Выполняем сложение дробей. Приводим к общему знаменателю: {formula_result}"
    ),
    "MIXED_SUBTRACT": (
        "{ctx}Выполняем вычитание дробей. Приводим к общему знаменателю: {formula_result}"
    ),

    # --- Powers (task 6) ---
    "POWERS_FRACTION_POWER": (
        "{ctx}Возводим дробь <b>{num}/{den}</b> в степень <b>{exponent}</b>. "
        "Для этого возводим в степень и числитель, и знаменатель <b>(a/b)ⁿ = aⁿ / bⁿ</b>"
    ),
    "POWERS_MULTIPLY_WITH_CANCEL": (
    "{ctx}Умножаем <b>{left_num}</b> на дробь <b>{right_num}/{right_den}</b> с предварительным сокращением чисел <b>{cancel_num}</b> и <b>{cancel_den}</b> на <b>{cancel_gcd}</b>"
    ),
    "POWERS_MULTIPLY": (
        "{ctx}Умножаем <b>{left_num}</b> на дробь <b>{right_num}/{right_den}</b>"
    ),
    "POWERS_ADD_SAME_DENOM": (
        "{ctx}Складываем дроби с одинаковым знаменателем"
    ),
    "POWERS_ADD_DIFFERENT_DENOM": (
        "{ctx}Приводим дроби к общему знаменателю <b>{lcm}</b> и складываем числители"
    ),
    "POWERS_SUBTRACT_SAME_DENOM": (
        "{ctx}Вычитаем <b>{right_num}</b> из числа <b>{left_num}</b>"
    ),
    "POWERS_SUBTRACT_DIFFERENT_DENOM": (
        "{ctx}Приводим дроби к общему знаменателю <b>{lcm}</b> и вычитаем числители"
    ),
    "POWERS_REPRESENT_AS_PRODUCT": (
        "{ctx}Представим степень <b>({num}/{den})^{exponent}</b> как произведение"
    ),
    "POWERS_FACTOR_OUT": (
        "{ctx}Вынесем общий множитель <b>{num}/{den}</b> за скобки"
    ),
    "POWERS_ADD_IN_BRACKETS": (
        "{ctx}Складываем выражения в скобках"
    ),
    "POWERS_SUBTRACT_IN_BRACKETS": (
        "{ctx}Вычитаем в скобках"
    ),
    "POWERS_MULTIPLY_IN_BRACKETS": (
        "{ctx}Выполняем умножение в скобках с предварительным сокращением"
    ),
    "POWERS_FINAL_MULTIPLY": (
        "{ctx}Умножаем вынесенный множитель <b>{num}/{den}</b> на результат в скобках <b>{value}</b>"
    ),
    "POWERS_TEN_EXPAND_POWER": (
        "{ctx}Раскроем первые скобки, используя свойство <b>(a · b)ⁿ = aⁿ · bⁿ</b>. "
        "Затем применим свойство <b>(aⁿ)ᵐ = aⁿ ⁽ᵐ⁾</b>"
    ),
    "POWERS_TEN_REWRITE": (
        "{ctx}Теперь подставим полученный результат в исходное выражение"
    ),
    "POWERS_TEN_GROUP": (
        "{ctx}Группируем множители. Сгруппируем отдельно числовые множители и степени с основанием <b>10</b>"
    ),
    "POWERS_TEN_CALCULATE": (
        "{ctx}Выполняем вычисления. Перемножим числа. При умножении степеней с одинаковым основанием их показатели складываются <b>(aⁿ · aᵐ = aⁿ ⁺ ᵐ)</b>"
    ),
    "POWERS_TEN_FINAL": (
        "{ctx}Записываем финальный ответ. Выполним последнее умножение"
    ),
    "POWERS_FINAL_ADD_INTEGERS": (
    "Выполним финальное сложение."
    ),
    "POWERS_FINAL_SUBTRACT_INTEGERS": (
        "Выполним финальное вычитание."
    ),
}


# ---------------------------------------------------------------------------
# Шаблоны для идеи и подсказок
# ---------------------------------------------------------------------------

IDEA_TEMPLATES: Dict[str, str] = {
    "ADD_SUB_FRACTIONS_IDEA": (
    "Приводим дроби к общему знаменателю, {operation_name} числители и приводим результат к несократимому виду."
    ),
    "MULTIPLY_DIVIDE_FRACTIONS_IDEA": (
        "Если встречаются смешанные числа, преобразуем их в неправильные дроби, после чего используем правила умножения и деления дробей."
    ),
    "PARENTHESES_OPERATIONS_IDEA": (
        "Сначала выполняем действия в скобках, затем последовательно обрабатываем внешнюю операцию, соблюдая порядок действий."
    ),
    "COMPLEX_FRACTION_IDEA": (
        "Отдельно вычисляем числитель сложной дроби, затем делим его на знаменатель по правилу деления дробей."
    ),
    "DF_ADD_SUB_IDEA": (
    "Это простое действие с десятичными дробями. "
    "Главное — записывать числа так, чтобы запятая стояла под запятой. "
    "Складываем или вычитаем аккуратно — и получаем ответ без ошибок."
    ),
    "DF_LINEAR_OP_IDEA": (
    "В этом выражении важно соблюдать порядок действий: "
    "сначала выполняем умножение или деление, а потом сложение или вычитание. "
    "Следим за знаками — от этого зависит, будет ли результат положительным или отрицательным."
    ),
    "DF_FRACTION_STRUCT_IDEA": (
    "Сначала находим значение в скобках — это знаменатель дроби. "
    "Затем делим числитель на полученный результат, аккуратно соблюдая порядок действий. "
    "Так шаг за шагом выражение становится простым и понятным."
    ),
    "GENERIC_IDEA": (
        "Разберём выражение по шагам, чтобы чётко проследить каждое преобразование."
    ),
    "MIXED_FRACTIONS_IDEA": (
        "Чтобы избежать ошибок, приведём все числа к одному виду — обыкновенным дробям. "
        "Порядок действий: сначала умножение и деление, затем сложение и вычитание."
    ),
    "MIXED_FRACTIONS_EXTENDED_IDEA": (
        "Чтобы не запутаться 😊, сначала приведём все числа к одному виду — обыкновенным дробям. "
        "Так и смешанные, и десятичные будут выглядеть одинаково, и вычислять станет проще. "
        "Сначала выполним деление (или умножение) — ведь это первый шаг по порядку действий, "
        "а потом аккуратно сложим или вычтем полученные дроби. "
        "Главное — следить за знаком и не торопиться: шаг за шагом всё получится!"
    ),
    "POWERS_FRACTIONS_STANDARD_IDEA": (
        "Соблюдаем порядок действий: сначала возводим дробь в степень, "
        "затем выполняем умножение, и в конце — {final_operation}."
    ),
    "POWERS_FRACTIONS_RATIONAL_IDEA": (
        "В этом выражении можно заметить общий множитель — дробь, которая встречается несколько раз. "
        "Если вынести её за скобки, вычисления станут гораздо проще и быстрее!"
    ),
    "POWERS_FRACTIONS_IDEA": (
        "Соблюдаем порядок действий: сначала возводим дробь в степень, "
        "затем выполняем умножение, и в конце — {final_operation}."
    ),
    "POWERS_FRACTIONS_TWO_WAYS_IDEA": (
        "Эту задачу можно решить двумя способами: стандартным (по порядку действий) "
        "и более рациональным (через вынесение общего множителя за скобки). "
        "Второй способ часто оказывается быстрее и удобнее!"
    ),
    "POWERS_OF_TEN_IDEA": (
        "Для решения этого выражения воспользуемся свойствами степеней: "
        "<b>(a · b)ⁿ = aⁿ · bⁿ и aⁿ · aᵐ = a⁽ⁿ ⁺ ᵐ⁾</b>. "
        "Сначала раскроем скобки, затем отдельно умножим числа и степени с основанием <b>10</b>."
    ),
}

HINT_TEMPLATES: Dict[str, str] = {
    "HINT_ORDER_OF_OPERATIONS": (
        "Соблюдай порядок действий: сначала вычисляй выражения в скобках, затем выполни умножение или деление."
    ),
    "HINT_FIND_LCM": (
        "Для сложения и вычитания дробей приведи их к общему знаменателю через наименьшее общее кратное."
    ),
    "HINT_CHECK_REDUCTION": (
        "После вычислений проверь, можно ли сократить полученную дробь на общий делитель числителя и знаменателя."
    ),
    "HINT_CONVERT_MIXED": (
        "Смешанные числа удобнее преобразовать в неправильные дроби: целую часть умножь на знаменатель и прибавь числитель."
    ),
    "HINT_DIVIDE_AS_MULTIPLY": (
        "Чтобы разделить дроби, умножь первую дробь на обратную ко второй."
    ),
    "HINT_CROSS_CANCEL": (
        "Перед перемножением числителей и знаменателей попробуй выполнить перекрёстное сокращение, чтобы упростить вычисления."
    ),
    "HINT_MULTIPLY_AFTER_PARENTHESES": (
        "После упрощения выражения в скобках аккуратно перенеси результат во внешнюю операцию."
    ),
    "HINT_PROCESS_NUMERATOR": (
        "В сложной дроби сначала упрости выражение в числителе, затем переходи к делению на знаменатель."
    ),
    "HINT_DECIMAL_ALIGNMENT": (
        "При сложении или вычитании десятичных дробей в столбик, записывай числа так, чтобы запятая находилась строго под запятой."
    ),
    "HINT_MIXED_ORDER_AND_CONVERSION": (
        "🔹 Сначала переведи все смешанные и десятичные числа в обыкновенные дроби. "
        "Так будет легче понять, какие действия нужно выполнить первыми. "
        "Помни: сначала делим или умножаем, а уже потом складываем и вычитаем."
    ),
    "HINT_POWER_OF_FRACTION": (
        "Чтобы возвести дробь в степень, возведи в эту степень и числитель, и знаменатель: (a/b)ⁿ = aⁿ / bⁿ."
    ),
    "HINT_COMMON_FACTOR": (
        "Если в выражении одна и та же дробь встречается несколько раз, попробуй вынести её за скобки — это упростит вычисления."
    ),
    "HINT_POWER_PROPERTIES": (
        "Используй свойства степеней: (a · b)ⁿ = aⁿ · bⁿ, (aⁿ)ᵐ = a⁽ⁿ ⋅ ᵐ⁾, aⁿ · aᵐ = a⁽ⁿ ⁺ ᵐ⁾."
    ),
    "HINT_GROUP_FACTORS": (
        "При работе со степенями десяти удобно отдельно группировать числовые коэффициенты и степени с основанием 10."
    ),
    "HINT_ADD_EXPONENTS": (
        "При умножении степеней с одинаковым основанием их показатели складываются: aⁿ · aᵐ = a⁽ⁿ ⁺ ᵐ⁾."
    ),
}


# ---------------------------------------------------------------------------
# Публичные функции
# ---------------------------------------------------------------------------

def humanize(solution_core: Dict[str, Any]) -> str:
    """Возвращает HTML-представление solution_core."""

    parts: List[str] = []

    idea_text = _resolve_idea(solution_core)
    parts.append(f"<b>Идея решения:</b> {idea_text}")

    parts.append("🪜 <b>Пошаговое решение</b>")

    # ⭐ НОВАЯ ЛОГИКА: проверяем наличие calculation_paths
    if "calculation_paths" in solution_core:
        paths_block = _render_paths(solution_core["calculation_paths"])
        parts.append(paths_block)
    elif "calculation_steps" in solution_core:
        steps = solution_core.get("calculation_steps") or []
        rendered_steps = [_render_step(step) for step in steps]
        if rendered_steps:
            steps_block = "\n\n".join(rendered_steps)
            parts.append(steps_block)

    # Добавляем финальный ответ только если нет шага FIND_FINAL_ANSWER
    step_keys = []
    if "calculation_steps" in solution_core:
        step_keys = [s.get("description_key") for s in solution_core.get("calculation_steps", [])]
    elif "calculation_paths" in solution_core:
        # Собираем ключи из всех путей
        for path in solution_core.get("calculation_paths", []):
            step_keys.extend([s.get("description_key") for s in path.get("steps", [])])

    if "FIND_FINAL_ANSWER" not in step_keys:
        final_answer_block = _render_final_answer(solution_core.get("final_answer") or {})
        parts.append(final_answer_block)

    hints_block = _render_hints(solution_core)
    if hints_block:
        parts.append(hints_block)

    return "\n\n".join(parts)


def validate_solution_core(solution_core: Dict[str, Any]) -> bool:
    """Быстрая проверка структуры solution_core."""

    required_fields = ["question_id", "question_group", "final_answer"]
    if not all(field in solution_core for field in required_fields):
        return False

    # Проверяем наличие либо calculation_steps, либо calculation_paths
    has_steps = "calculation_steps" in solution_core
    has_paths = "calculation_paths" in solution_core

    if not (has_steps or has_paths):
        return False

    if has_steps:
        steps = solution_core.get("calculation_steps")
        if not isinstance(steps, list):
            return False
        for step in steps:
            if not isinstance(step, dict):
                return False
            if "step_number" not in step or "description_key" not in step:
                return False

    if has_paths:
        paths = solution_core.get("calculation_paths")
        if not isinstance(paths, list):
            return False
        for path in paths:
            if not isinstance(path, dict):
                return False
            if "steps" not in path:
                return False
            for step in path["steps"]:
                if not isinstance(step, dict):
                    return False
                if "step_number" not in step or "description_key" not in step:
                    return False

    final_answer = solution_core.get("final_answer")
    if not isinstance(final_answer, dict):
        return False
    if "value_display" not in final_answer:
        return False

    return True


def get_available_templates() -> List[str]:
    """Возвращает список доступных шаблонов описаний шагов."""
    return sorted(STEP_TEMPLATES.keys())


# ---------------------------------------------------------------------------
# Внутренние помощники
# ---------------------------------------------------------------------------

def _resolve_idea(solution_core: Dict[str, Any]) -> str:
    key = solution_core.get("explanation_idea_key")
    params = solution_core.get("explanation_idea_params") or {}
    if key in IDEA_TEMPLATES:
        return IDEA_TEMPLATES[key].format(**params)

    fallback = solution_core.get("explanation_idea")
    if isinstance(fallback, str) and fallback.strip():
        return fallback.strip()

    return IDEA_TEMPLATES["GENERIC_IDEA"]


def _render_paths(paths: List[Dict[str, Any]]) -> str:
    """Отрисовывает несколько способов решения (calculation_paths).

    Args:
        paths: Список путей решения, каждый содержит path_title, steps и опционально is_recommended

    Returns:
        Отформатированный HTML-блок со всеми способами решения
    """
    rendered_paths: List[str] = []

    for path in paths:
        path_title = path.get("path_title", "Решение")
        is_recommended = path.get("is_recommended", False)
        steps = path.get("steps", [])

        # Формируем заголовок пути
        if is_recommended:
            header = f"<b>⭐️ {path_title}</b>"
        else:
            header = f"<b>{path_title}</b>"

        # Рендерим шаги этого пути
        rendered_steps = [_render_step(step) for step in steps]
        steps_block = "\n\n".join(rendered_steps)

        # Объединяем заголовок и шаги
        path_content = f"{header}\n\n{steps_block}"
        rendered_paths.append(path_content)

    # Разделяем способы горизонтальной линией
    separator = "\n\n" + "─" * 40 + "\n\n"
    return separator.join(rendered_paths)


def _render_step(step: Dict[str, Any]) -> str:
    """ФИНАЛЬНАЯ ВЕРСИЯ: Отрисовывает шаг без `<code>` и дублирования."""
    number = step.get("step_number")
    description = _format_step_description(step)

    formula = ""
    key = step.get("description_key")

    # --- БЛОК 1: Собираем формулу (если она нужна) ---
    # Проверяем, нужно ли вообще показывать отдельную формулу
    if key != "INITIAL_EXPRESSION":
        formula = step.get("formula_calculation") or step.get("formula_representation") or ""

    # --- БЛОК 2: Украшаем формулу (если она есть) ---
    if formula:
        # Улучшаем отображение целых чисел в дробях (например, "2/1" становится "2")
        if "= " in formula:
            formula = re.sub(r"(\d+)/1(?!\d)", r"\1", formula)

        # Превращаем ^2 в надстрочные символы
        if "^" in formula:
            sup_map = str.maketrans("0123456789-()", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁽⁾")
            def replace_power(match):
                base = match.group(1)
                exponent = match.group(2)
                return f"{base}{exponent.translate(sup_map)}"
            formula = re.sub(r"(\S+)\^([-]?\d+|\(-?\d+\))", replace_power, formula)

    # --- БЛОК 3: Собираем финальный HTML ---
    # Убрали `<code>`, вернули `➡️`
    formula_html = f"\n➡️ {formula}" if formula else ""

    return f"<b>Шаг {number}.</b> {description}{formula_html}"


def _format_superscripts(text: str) -> str:
    """Преобразует ^N в надстрочные символы."""
    import re

    # Маппинг цифр и знаков на надстрочные символы
    superscript_map = {
        '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
        '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
        '-': '⁻', '+': '⁺', '(': '⁽', ')': '⁾'
    }

    def replace_power(match):
        exponent = match.group(1)
        # Преобразуем каждый символ показателя
        superscript = ''.join(superscript_map.get(c, c) for c in exponent)
        return superscript

    # Заменяем ^(...) и ^N на надстрочные символы
    # Сначала обрабатываем скобки: ^(-3) -> ⁽⁻³⁾
    text = re.sub(r'\^(\([^)]+\))', replace_power, text)
    # Затем обрабатываем простые числа: ^2 -> ²
    text = re.sub(r'\^(-?\d+)', replace_power, text)

    return text


def _format_step_description(step: Dict[str, Any]) -> str:
    key = step.get("description_key", "")
    params = dict(step.get("description_params") or {})

    ctx = _prepare_context(params.pop("context", None), step)
    params["ctx"] = ctx

    # Специальная обработка для POWERS_MULTIPLY_WITH_CANCEL
    if key == "POWERS_MULTIPLY_WITH_CANCEL" and "cancellations" in params:
        cancellations = params.pop("cancellations")
        if cancellations:
            first_cancel = cancellations[0]
            params["cancel_num"] = first_cancel.get("num")
            params["cancel_den"] = first_cancel.get("den")
            params["cancel_gcd"] = first_cancel.get("gcd")

    if "cancellations" in params:
        params["cancellations_text"] = _format_cancellations(params.pop("cancellations"))

    if key == "DIVISION_FINAL_RESULT":
        params.setdefault("result", step.get("calculation_result", ""))

    if key == "CONVERT_TO_DECIMAL":
        params["decimal"] = _format_decimal(params.get("decimal"))

    # динамический эмодзи для шага окончательной операции
    if key == "FINAL_OPERATION":
        op = (params.get("operation_name") or "").strip().lower()
        if op == "сложение":
            params.setdefault("op_emoji", "➕")
        elif op == "вычитание":
            params.setdefault("op_emoji", "➖")
        else:
            params.setdefault("op_emoji", "")
        params.setdefault("extra_explanation", "")

    # если шаг "FINAL_OPERATION" и нет extra_explanation, подставляем фразу по умолчанию
    if key == "FINAL_OPERATION" and "extra_explanation" not in params:
        params["extra_explanation"] = "Дроби приводим к общему знаменателю."

    template = STEP_TEMPLATES.get(key)
    if not template:
        return f"{ctx}{key}"

    try:
        return template.format(**params)
    except KeyError as missing:
        missing_key = missing.args[0]
        params[missing_key] = f"{{{missing_key}}}"
        return template.format(**params)


def _render_final_answer(final_answer: Dict[str, Any]) -> str:
    """Формирует блок финального ответа с лаконичным оформлением."""
    value = str(final_answer.get("value_display", "")).strip()
    return f"<b>Ответ:</b> <b>{value}</b>"


def _render_hints(solution_core: Dict[str, Any]) -> Optional[str]:
    hint_keys: Iterable[str] = solution_core.get("hints_keys") or []
    hints: List[str] = []

    for key in hint_keys:
        text = HINT_TEMPLATES.get(key)
        if text:
            hints.append(text)

    if not hints:
        raw_hints = solution_core.get("hints") or []
        hints.extend(str(item) for item in raw_hints if str(item).strip())

    if not hints:
        return None

    items = "\n".join(f"• {text}" for text in hints)
    return f"<tg-spoiler><b>Полезно помнить:</b>\n{items}</tg-spoiler>"


def _prepare_context(raw: Optional[str], step: Optional[Dict[str, Any]] = None) -> str:
    """Готовит текст контекста (например, 'В числителе.') для шага."""
    if not raw:
        return ""
    text = raw.strip()

    # Если это контекст вида 'В числителе' — превращаем в осмысленную фразу
    if text.lower().startswith("в числителе") and step:
        expr = step.get("formula_representation") or ""
        expr_clean = expr.strip()
        if expr_clean:
            return f"Находим значение числителя {expr_clean}. "

    if text and text[-1] not in ".!?:":
        text += "."
    return f"{text} "


def _format_cancellations(items: Iterable[Dict[str, Any]]) -> str:
    formatted: List[str] = []
    for item in items:
        num = item.get("num")
        den = item.get("den")
        gcd = item.get("gcd")
        num_result = item.get("num_result")
        den_result = item.get("den_result")
        formatted.append(
            f"{num} и {den} ÷ {gcd} → {num_result}/{den_result}"
        )
    return "; ".join(formatted)


def _format_decimal(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    return f"{number:g}"


def _escape_newlines(text: str) -> str:
    return text
