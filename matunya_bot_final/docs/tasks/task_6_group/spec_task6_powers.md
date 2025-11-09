# Спецификация вспомогательных функций для подтипа `powers`

Документ фиксирует общий контракт helper-функций, которые будут использоваться
и в `powers_validator.py`, и в `powers_solver.py`.

## 1. `is_ten_power_node(node) -> Tuple[bool, int]`
- **Назначение:** определить, представляет ли узел дерева выражений степень числа 10.
- **Допустимые формы узла:**
  - новый тип `{"type": "ten_power", "exp": n}`;
  - классический `{"operation": "power", "operands": [base, exponent]}`, где `base` — узел со значением 10, `exponent` — целое.
- **Возвращает:** кортеж `(True, n)` если узел подходит, иначе `(False, 0)`.
- **Использование:** валидатор проверяет паттерн `powers_of_ten`, solver — извлекает показатель при составлении формул.

## 2. Форматтеры

### `format_fraction(value) -> str`
- Принимает `Fraction | int | float`.
- Возвращает строку `num/den`, если знаменатель ≠ 1, иначе просто числитель.
- Применяется во всех шагах, где нужно показать промежуточную дробь.

### `format_power(base: str, exponent: int) -> str`
- Возвращает строку `"{base}^{exponent}"`.
- Используется в шагах `CALCULATE_POWER` для единообразного отображения возведения в степень.

### `format_power_of_ten(coefficient, exponent) -> str`
- Принимает коэффициент (любое число, приводимое к `Fraction`) и показатель степени.
- Возвращает `"{coef} · 10^{exp}"`.
- Нужен там, где solver сообщает промежуточный результат вида `a · 10^n`.

## 3. Расположение и импорт
- Модуль: `matunya_bot_final/utils/task6/powers_helpers.py`.
- Импортируется из `help_core/solvers/task_6/powers_solver.py` и `task_generators/task_6/validators/powers_validator.py`.
- Дополнительно может использоваться генераторами при построении `expression_tree`.

## 4. Следующие шаги
1. Подключить новые helper’ы в валидатор/solver.
2. Расширить expression_tree паттерна `powers_of_ten` (узел `ten_power`).
3. Настроить humanizer: добавить шаблоны для шагов `CALCULATE_POWER`, `APPLY_POWER_OF_TEN_RULE`.
