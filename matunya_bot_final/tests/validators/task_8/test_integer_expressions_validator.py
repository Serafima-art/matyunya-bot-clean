import pytest

from matunya_bot_final.non_generators.task_8.validators.integer_expressions_validator import (
    normalize_superscripts,
    validate,
)


def _call_validator(raw: str):
    """
    Нормализует вход, приводит блок переменных к словарю и вызывает validate().
    Возвращает (result, variables_dict), где result — ответ валидатора или None.
    """
    normalized = normalize_superscripts(raw)
    parts = [p.strip() for p in normalized.split("|")]
    if len(parts) != 3:
        raise ValueError(f"Некорректный формат входа: {raw!r}")

    variables_block = parts[2]
    variables = {}
    if variables_block:
        for item in variables_block.split(","):
            name, value = item.split("=")
            variables[name.strip()] = float(value.strip())

    return validate(normalized), variables


# ------------------------- alg_power_fraction -------------------------

@pytest.mark.parametrize(
    "raw, expected",
    [
        # ((a³)⁵ · a³) / a²⁰ = a¹⁸ / a²⁰ = a⁻² = 1/25 = 0,04 при a=5
        ("alg_power_fraction | ((a³)⁵ · a³) / a²⁰ | a=5", "0,04"),
        # (a² · b³) / (a · b)² = b при a=10, b=2
        ("alg_power_fraction | (a² · b³) / (a · b)² | a=10, b=2", "2"),
        # (a⁵ · a²) / a⁷ = 1 при a=3
        ("alg_power_fraction | (a⁵ · a²) / a⁷ | a=3", "1"),
    ],
)
def test_alg_power_fraction_success(raw, expected):
    result, _ = _call_validator(raw)
    assert result is not None
    assert result["answer"] == expected


@pytest.mark.parametrize(
    "raw",
    [
        # Содержит корень в знаменателе — нарушает правила паттерна
        "alg_power_fraction | a² / √(a²) | a=4",
        # Степень превышает лимит 30
        "alg_power_fraction | a³¹ / a | a=2",
    ],
)
def test_alg_power_fraction_fail(raw):
    result, _ = _call_validator(raw)
    assert result is None


# ------------------------- alg_radical_power -------------------------

@pytest.mark.parametrize(
    "raw, expected",
    [
        ("alg_radical_power | √(100 · a²¹ / a¹⁹) | a=3", "30"),
        ("alg_radical_power | √(25 · a²) | a=7", "35"),
        ("alg_radical_power | √(4 · a⁶) | a=2", "16"),
    ],
)
def test_alg_radical_power_success(raw, expected):
    result, _ = _call_validator(raw)
    assert result is not None
    assert result["answer"] == expected


@pytest.mark.parametrize(
    "raw",
    [
        # Нет внешнего корня
        "alg_radical_power | (a³) | a=5",
        # Коэффициент под корнем не является полным квадратом
        "alg_radical_power | √(18 · a²) | a=3",
        # Разность степеней (m - n) нечётная
        "alg_radical_power | √(a² / a) | a=2",
    ],
)
def test_alg_radical_power_fail(raw):
    result, _ = _call_validator(raw)
    assert result is None


# ------------------------- alg_radical_fraction -------------------------

@pytest.mark.parametrize(
    "raw, expected",
    [
        # ( √(25a²) · √(4b²) ) / √(a²b²) = 10 при a=4, b=2
        ("alg_radical_fraction | ( √(25a²) · √(4b²) ) / √(a²b²) | a=4, b=2", "10"),
        # √(4a²b²) / √(a²) = 4 при a=5, b=2
        ("alg_radical_fraction | √(4a²b²) / √(a²) | a=5, b=2", "4"),
        # (√(49a⁴)) / (√(a²)) = 21 при a=3
        ("alg_radical_fraction | (√(49a⁴)) / (√(a²)) | a=3", "21"),
    ],
)
def test_alg_radical_fraction_success(raw, expected):
    result, _ = _call_validator(raw)
    assert result is not None
    assert result["answer"] == expected


@pytest.mark.parametrize(
    "raw",
    [
        # Неполный квадрат под корнем
        "alg_radical_fraction | √(18a²) / √(a²) | a=3",
        # Нечётные степени после объединения радикандов
        "alg_radical_fraction | ( √(25a²) · √(4b²) ) / √(ab) | a=4, b=2",
        # Знаменатель — целое число вместо корня
        "alg_radical_fraction | √(4a²) / 2 | a=5",
    ],
)
def test_alg_radical_fraction_fail(raw):
    result, _ = _call_validator(raw)
    assert result is None
