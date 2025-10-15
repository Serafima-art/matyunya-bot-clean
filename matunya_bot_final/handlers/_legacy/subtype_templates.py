from fractions import Fraction
from decimal import Decimal

TEMPLATES = {
    # 1. Обычные дроби с преобразованием и скобками
    "обычные_дроби_скобки": {
        "steps": [
            "Шаг 1: Приведите дроби в скобках к общему знаменателю ({common_denom}).",
            "Шаг 2: Выполните действие в скобках: {step1_expr} = {step1_res}.",
            "Шаг 3: Умножьте на оставшийся множитель: {step1_res} · {multiplier} = {final_answer}."
        ],
        "logic": lambda t: {
            "common_denom": "12",  # Замените на расчётный
            "step1_expr": t["text"].split("·")[0].strip(),
            "step1_res": "7/12",   # Пример для (5/6 − 1/4)
            "multiplier": t["text"].split("·")[1].strip(),
            "final_answer": t["answer"]
        }
    },

    # 2. Десятичные дроби в дроби
    "десятичные_в_дроби": {
        "steps": [
            "Шаг 1: Преобразуйте десятичные дроби: {step1_convert}.",
            "Шаг 2: Выполните деление: {step2_expr} = {step2_res}.",
            "Шаг 3: Упростите: {step2_res} = {final_answer}."
        ],
        "logic": lambda t: {
            "step1_convert": "0.6 → 3/5, 1.5 → 3/2",
            "step2_expr": t["text"].split(":")[1].strip(),
            "step2_res": "2/5",
            "final_answer": t["answer"]
        }
    },

    # 3. Числитель несократимой дроби
    "числитель_несократимой": {
        "steps": [
            "Шаг 1: Вычислите выражение: {step1_expr} = {step1_res}.",
            "Шаг 2: Сократите дробь (если возможно).",
            "Шаг 3: Числитель итоговой дроби: {final_answer}."
        ],
        "logic": lambda t: {
            "step1_expr": t["text"].split(":")[1].strip(),
            "step1_res": "3/8",
            "final_answer": t["answer"]
        }
    },

    # 4. Степени с отрицательными основаниями
    "степени_отрицательные": {
        "steps": [
            "Шаг 1: Возведите в степень: {step1_expr} = {step1_res}.",
            "Шаг 2: Вычислите: {step1_res} − {step2_expr} = {final_answer}."
        ],
        "logic": lambda t: {
            "step1_expr": t["text"].split("−")[0].strip(),
            "step1_res": "9",
            "step2_expr": t["text"].split("−")[1].strip(),
            "final_answer": t["answer"]
        }
    },

    # 5. Три обычные дроби без скобок
    "три_дроби": {
        "steps": [
            "Шаг 1: Приведите дроби к общему знаменателю ({common_denom}).",
            "Шаг 2: Выполните сложение/вычитание: {step1_expr} = {final_answer}."
        ],
        "logic": lambda t: {
            "common_denom": "20",
            "step1_expr": t["text"].split(":")[1].strip(),
            "final_answer": t["answer"]
        }
    },

    # 6. Десятичные с отрицательными в скобках
    "десятичные_отрицательные_скобки": {
        "steps": [
            "Шаг 1: Умножьте числа в скобках: {step1_expr} = {step1_res}.",
            "Шаг 2: Прибавьте оставшеее число: {step1_res} + {add} = {final_answer}."
        ],
        "logic": lambda t: {
            "step1_expr": t["text"].split("+")[0].strip(),
            "step1_res": "0.6",
            "add": t["text"].split("+")[1].strip(),
            "final_answer": t["answer"]
        }
    },

    # 7. Дробь в дроби (A/(B±C))
    "дробь_в_дроби": {
        "steps": [
            "Шаг 1: Вычислите знаменатель: {denom_expr} = {denom_res}.",
            "Шаг 2: Разделите числитель на знаменатель: {num} ÷ {denom_res} = {final_answer}."
        ],
        "logic": lambda t: {
            "denom_expr": t["text"].split("/")[1].split(")")[0].strip(),
            "denom_res": "17/12",
            "num": t["text"].split("/")[0].strip(),
            "final_answer": t["answer"]
        }
    },

    # 8. Дробь с заданным знаменателем
    "дробь_с_знаменателем": {
        "steps": [
            "Шаг 1: Приведите выражение к виду X/{given_denom}.",
            "Шаг 2: Числитель X = {final_answer}."
        ],
        "logic": lambda t: {
            "given_denom": "8",  # Из условия
            "final_answer": t["answer"]
        }
    },

    # 9. Смешанные числа
    "смешанные_числа": {
        "steps": [
            "Шаг 1: Переведите смешанные числа в дроби: {step1_convert}.",
            "Шаг 2: Вычислите: {step1_res} = {final_answer}."
        ],
        "logic": lambda t: {
            "step1_convert": "1 1/2 → 3/2",
            "step1_res": "3/2 − 1/4 = 5/4",
            "final_answer": t["answer"]
        }
    },

    # 10. Дробь в степени
    "дробь_в_степени": {
        "steps": [
            "Шаг 1: Возведите дробь в степень: {step1_expr} = {step1_res}.",
            "Шаг 2: Вычислите итог: {step1_res} ± ... = {final_answer}."
        ],
        "logic": lambda t: {
            "step1_expr": t["text"].split("±")[0].strip(),
            "step1_res": "1/4",
            "final_answer": t["answer"]
        }
    },

    # 11. Степени с десятичными множителями
    "степени_десятичные": {
        "steps": [
            "Шаг 1: Вычислите степень: {step1_expr} = {step1_res}.",
            "Шаг 2: Умножьте на коэффициент: {step1_res} × {coeff} = {final_answer}."
        ],
        "logic": lambda t: {
            "step1_expr": "10^3",
            "step1_res": "1000",
            "coeff": "0.5",
            "final_answer": t["answer"]
        }
    }
}

def generate_help_steps(task: dict) -> list[str]:
    """Генерирует help_steps для задания."""
    if task["subtype"] not in TEMPLATES:
        return []
    
    data = TEMPLATES[task["subtype"]]["logic"](task)
    steps = [s.format(**data) for s in TEMPLATES[task["subtype"]]["steps"]]
    steps.append("Понятно, как мы это сделали?")
    return steps