"""System prompts for Task 8 (Algebraic Expressions) GPT dialog."""

from __future__ import annotations

from textwrap import dedent
from typing import Any, Dict, List, Optional, Union, Sequence

# --- ИМПОРТЫ ОБЩИХ СТАНДАРТОВ ---
from matunya_bot_final.gpt.prompts.rules_format import RULES_FORMAT
from matunya_bot_final.gpt.prompts.prompt_utils import gender_words, safe_text

from matunya_bot_final.gpt.prompts.behavior_protocols import (
    BASE_CHATTER_PERSONA,
    TASK_FOCUS_PROTOCOL,
    DIALOG_HISTORY_PROTOCOL,
)

# --- ИМПОРТЫ СПЕЦИФИКИ ЗАДАНИЯ 8 ---
# Форматтер формул (чтобы GPT видела условие так же, как ученик)
from matunya_bot_final.help_core.solvers.task_8.task_8_text_formatter import render_node, fmt_number
# Шаблоны текстов (чтобы восстановить текст шагов из ключей)
from matunya_bot_final.help_core.humanizers.template_humanizers.task_8_humanizer import (
    IDEA_TEMPLATES,
    STEP_TEMPLATES,
    KNOWLEDGE_TEMPLATES
)


def get_task_8_dialog_prompt(
    task_data: Dict[str, Any],
    solution_core: Dict[str, Any],
    dialog_history: List[Dict[str, Any]],  # Используется в общем контексте, здесь может быть не нужен, но сохраняем сигнатуру
    student_name: Optional[str] = None,
    gender: Optional[str] = None,
    golden_set: Union[Dict[str, str], Sequence[str], None] = None,
) -> str:
    """
    Генерирует системный промпт для диалога по Заданию 8.
    """
    name = student_name or "друг"

    # Определяем формы слов для обращения
    gw = gender_words(gender) # returns {'ready': 'готова', ...}

    # Формируем обращение к ученику (для инструкции)
    if gender in ['female', 'жен', 'ж']:
        pronoun = "ученице"
        suffix_l = ""     # поняла
    else:
        pronoun = "ученику"
        suffix_l = "а"    # понял

    # 1. ФОРМИРУЕМ УСЛОВИЕ ЗАДАЧИ
    try:
        tree = task_data.get("expression_tree")
        source_expression = render_node(tree)

        # Если есть переменные, добавляем их значения
        vars_dict = task_data.get("variables", {})
        if vars_dict:
            v_list = [f"{k}={fmt_number(v)}" for k, v in vars_dict.items()]
            source_expression += f" при {', '.join(v_list)}"
    except Exception:
        source_expression = "выражение из задания"

    # 2. ВОССТАНАВЛИВАЕМ ЭТАЛОННОЕ РЕШЕНИЕ (из ключей solution_core)

    # Идея
    idea_key = solution_core.get("explanation_idea_key", "")
    idea_params = solution_core.get("explanation_idea_params") or {}
    idea_text = _resolve_template(idea_key, IDEA_TEMPLATES, idea_params)

    # Шаги
    steps_text = _format_steps_for_ai(solution_core.get("calculation_steps", []))

    # Ответ
    final_answer = solution_core.get("final_answer", {}).get("value_display", "N/A")

    # Подсказки (Theory)
    know_key = solution_core.get("knowledge_tips_key", "")
    knowledge_list = KNOWLEDGE_TEMPLATES.get(know_key, [])
    # Если нужно подставить параметры в подсказки (как мы делали для radical_product)
    # используем те же параметры, что и для идеи
    hints_formatted = []
    for item in knowledge_list:
        try:
            hints_formatted.append(item.format(**idea_params))
        except Exception:
            hints_formatted.append(item)

    hints_text = "\n".join([f"• {h}" for h in hints_formatted])


    # 3. СБОРКА БАЗЫ ЗНАНИЙ (Golden Set)
    golden_block = ""
    if golden_set:
        entries: list[str] = []
        if isinstance(golden_set, (list, tuple)):
            for phrase in golden_set:
                entries.append(f'- {phrase}')
        if entries:
            golden_block = "\n### БАЗА ЗНАНИЙ (GOLDEN SET)\n" + "\n".join(entries)


    # 4. ФИНАЛЬНЫЙ ПРОМПТ
    return dedent(f"""
    Ты — Матюня, тёплый, внимательный и заботливый репетитор по математике для 9-классников.
    Ты помогаешь {pronoun} {name} разобраться с **Заданием 8** ОГЭ (Алгебраические выражения: степени и корни).

    # КОНТЕКСТ ЗАДАЧИ
    Ученик решает задание: <code>{source_expression}</code>

    # ЭТАЛОННОЕ РЕШЕНИЕ (ТВОЯ ШПАРГАЛКА)
    В диалоге опирайся на этот алгоритм. Не придумывай другие способы, если ученик не просит.

    **Основная идея:** {idea_text}

    {steps_text}

    **Итоговый ответ:** {final_answer}

    # ПОЛЕЗНЫЕ СВОЙСТВА (ТЕОРИЯ)
    {hints_text}
    {golden_block}

    # ТВОЯ РОЛЬ И ПРАВИЛА

    1. **Главная цель:** Не решить за ученика, а привести его к пониманию. Если ученик просит ответ, скажи: "Давай лучше разберемся, как его получить, чтобы на экзамене ты справился сам!".

    2. **Верификация (КРИТИЧЕСКИ ВАЖНО):**
       Когда ученик пишет формулу или ответ, **СНАЧАЛА** переспроси, правильно ли ты понял{suffix_l}.
       Пример: "Проверю, правильно ли я тебя понял{suffix_l}. Ты имеешь в виду, что $2^3 * 2^2 = 2^6$? Всё верно?"
       Только после подтверждения объясняй ошибку (правильно будет $2^5$).

    3. **Специфика Задания 8 (Алгебра):**
       - **Терминология:** ИСПОЛЬЗУЙ слово **«раскладываем»** (на множители). НИКОГДА не пиши «разлагаем» (это звучит плохо).
       - **Свойства степеней:** Следи, чтобы ученик не путал сложение показателей (при умножении) и умножение показателей (при возведении степени в степень).
       - **Корни:** Напоминай, что большие числа под корнем лучше **раскладывать** на множители, а не перемножать в столбик. Используй метафоры из решения ("сундуки", "шпионы"), если они там есть.
       - **Порядок:** Напоминай: сначала упрощаем буквенное выражение, и только в самом конце подставляем числа.

    4. **Социальный протокол:**
       - Если ученик спрашивает «Как тебя зовут?», «Ты робот?»: отвечай коротко и дружелюбно ("Я Матюня, твой цифровой помощник!"), и сразу возвращай фокус к задаче.
       - Не начинай сообщение с "Привет", вы уже в диалоге.
       - Обращайся по имени: <b>{name}</b>.

    5. **Форматирование:**
       - Используй HTML теги: <code>...</code> для формул и чисел, <b>...</b> для акцентов.
       - Не используй LaTeX ($...$).

    {RULES_FORMAT}
    """).strip()


# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def _resolve_template(key: str, templates: Dict[str, str], params: Dict[str, Any]) -> str:
    """Восстанавливает текст из ключа шаблона и параметров."""
    template = templates.get(key, "")
    if not template: return ""
    try:
        # Убираем HTML теги для промпта (чтобы GPT было легче читать структуру),
        # или оставляем как есть. GPT хорошо понимает HTML. Оставим, но заменим <br> на \n
        text = template.format(**params)
        return text.replace("<br>", "\n")
    except Exception:
        return template

def _format_steps_for_ai(steps: list) -> str:
    """Превращает список шагов из solution_core в понятный текст для GPT."""
    if not steps:
        return "Шаги решения отсутствуют."

    lines = ["**Пошаговое решение:**"]
    for step in steps:
        # 1. Номер шага
        num = step.get("step_number", "?")

        # 2. Описание (восстанавливаем из ключа или берем сырое)
        desc_key = step.get("description_key")
        params = step.get("description_params") or {}
        desc_text = _resolve_template(desc_key, STEP_TEMPLATES, params)

        if not desc_text:
             desc_text = str(step.get("description", "")) # Fallback на случай отсутствия шаблона

        # Чистим описание от HTML для промпта
        clean_desc = desc_text.replace("<b>", "").replace("</b>", "")

        # 3. Формула
        formula = str(step.get("formula_calculation") or "")

        # ЧИСТКА ФОРМУЛЫ: Убираем HTML и наш служебный маркер text:
        # Заменяем <b> на ` (markdown код) для GPT
        clean_formula = formula.replace("<b>", "`").replace("</b>", "`").replace("\n", " ")
        clean_formula = clean_formula.replace("text:", "")

        # Сборка блока
        step_block = f"Шаг {num}. {clean_desc}"
        if clean_formula.strip(): # Проверяем, что осталось что-то кроме пробелов
            step_block += f"\n   Формула: {clean_formula.strip()}"

        lines.append(step_block)

    return "\n\n".join(lines)
