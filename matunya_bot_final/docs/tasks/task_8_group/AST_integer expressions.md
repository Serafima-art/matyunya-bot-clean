🧱 1. Общая идея AST для alg_power_fraction

Для темы integer_expressions (и особенно для 1.1) AST будет:

максимально похож на expression_tree,

но чуть проще:

степени храним как целые числа int, а не как отдельные узлы;

нет узла sqrt в паттерне 1.1.

🔹 Типы узлов AST

Каждый узел AST — dict с ключом "kind":

{"kind": "integer", "value": int}

{"kind": "variable", "name": "a" | "b"}

{"kind": "power", "base": <AST>, "exp": int}

{"kind": "product", "factors": [<AST>, ...]}

{"kind": "fraction", "numerator": <AST>, "denominator": <AST>}

⚠ Важно:
В AST нет sqrt, нет "type", только "kind".
sqrt нам понадобится в 1.2 и 1.3, не здесь.

🔹 Нормализация степеней

Токены POW + INT и SUP уже на этапе разбора собираем в одно целое число:

a^5 → {"kind": "power", "base": VAR(a), "exp": 5}

a³ → {"kind": "power", "base": VAR(a), "exp": 3}

a⁻² → {"kind": "power", "base": VAR(a), "exp": -2}

🎯 2. Эталонный AST для формы 1: ((aᵐ)ⁿ · aʳ) / aˢ

Пример (тот же, что и в доках):
((a³)⁵ · a³) / a²⁰

AST:

{
  "kind": "fraction",
  "numerator": {
    "kind": "product",
    "factors": [
      {
        "kind": "power",
        "base": {
          "kind": "power",
          "base": { "kind": "variable", "name": "a" },
          "exp": 3
        },
        "exp": 5
      },
      {
        "kind": "power",
        "base": { "kind": "variable", "name": "a" },
        "exp": 3
      }
    ]
  },
  "denominator": {
    "kind": "power",
    "base": { "kind": "variable", "name": "a" },
    "exp": 20
  }
}


📌 Особенности:

верхний уровень — fraction

в числителе — product из двух power

первая power — башня: base = power(a,3), exp = 5

все степени — целые числа в exp

🎯 3. Эталонный AST для формы 2: (aᵐ · (bⁿ)ʳ) / (a·b)ˢ

Пример:
(a⁶ · (b²)⁴) / (a·b)⁷

AST:

{
  "kind": "fraction",
  "numerator": {
    "kind": "product",
    "factors": [
      {
        "kind": "power",
        "base": { "kind": "variable", "name": "a" },
        "exp": 6
      },
      {
        "kind": "power",
        "base": {
          "kind": "power",
          "base": { "kind": "variable", "name": "b" },
          "exp": 2
        },
        "exp": 4
      }
    ]
  },
  "denominator": {
    "kind": "power",
    "base": {
      "kind": "product",
      "factors": [
        { "kind": "variable", "name": "a" },
        { "kind": "variable", "name": "b" }
      ]
    },
    "exp": 7
  }
}


📌 Особенности:

опять верхний уровень — fraction

числитель — product двух power

башня на b: (b²)⁴

знаменатель — power от product(a,b):

base = product(a,b)

exp = 7

🔁 Как это потом поедет в expression_tree

Переход AST → expression_tree:

"kind": "integer" → "type": "integer"

"kind": "variable" → "type": "variable"

"kind": "power" → "type": "power", а exp: int → {"type": "integer", "value": ...}

"kind": "product" → "type": "product"

"kind": "fraction" → "type": "fraction"

То есть структура сохраняется почти 1 в 1, просто:

kind → type

exp: int → оборачиваем в узел integer.





🧱 AST для Паттерна 1.2 — alg_radical_power
🔍 Что важно понять заранее

Паттерн 1.2 всегда имеет один главный корень сверху:

√(...)


То есть верхний узел AST всегда:

{ "kind": "sqrt", "radicand": <AST> }


⚠ В AST и финальном дереве мы НЕ используем value.
Всегда строго "radicand".

Подкоренное выражение (radicand) может быть:

fraction

product

power

product из power и integer

⚠ Но никогда не бывает суммы, разности и прочих конструкций — только чистая алгебра степеней.

Теперь давай эталоны.

✅ ЭТАЛОН AST — СЛУЧАЙ A
√(100 · a²¹ / a¹⁹)
🧱 Вход:
√(100 · a²¹ / a¹⁹)

🧱 AST:
{
  "kind": "sqrt",
  "radicand": {
    "kind": "fraction",
    "numerator": {
      "kind": "product",
      "factors": [
        { "kind": "integer", "value": 100 },
        {
          "kind": "power",
          "base": { "kind": "variable", "name": "a" },
          "exp": 21
        }
      ]
    },
    "denominator": {
      "kind": "power",
      "base": { "kind": "variable", "name": "a" },
      "exp": 19
    }
  }
}

✅ ЭТАЛОН AST — СЛУЧАЙ B
√(25 · a⁶)
🧱 Вход:
√(25 · a⁶)

🧱 AST:
{
  "kind": "sqrt",
  "radicand": {
    "kind": "product",
    "factors": [
      { "kind": "integer", "value": 25 },
      {
        "kind": "power",
        "base": { "kind": "variable", "name": "a" },
        "exp": 6
      }
    ]
  }
}

✅ ЭТАЛОН AST — СЛУЧАЙ C
√((-a)⁶ · a⁴)

⚠ Сложный случай, потому что здесь присутствует минус внутри степени.

Мы решили:

НЕ вводить отдельный узел unary_minus

вместо него представлять (-a) как:

product(integer(-1), variable(a))

🧱 Вход:
√((-a)⁶ · a⁴)

🧱 AST:
{
  "kind": "sqrt",
  "radicand": {
    "kind": "product",
    "factors": [
      {
        "kind": "power",
        "base": {
          "kind": "product",
          "factors": [
            { "kind": "integer", "value": -1 },
            { "kind": "variable", "name": "a" }
          ]
        },
        "exp": 6
      },
      {
        "kind": "power",
        "base": { "kind": "variable", "name": "a" },
        "exp": 4
      }
    ]
  }
}

📌 Замечания по стандарту AST для alg_radical_power
1. Верхний уровень всегда:
kind: "sqrt"

2. radicand может быть:

fraction

product

power

product из power

3. Внутри нет сокращений:

a²¹ / a¹⁹ не упрощаем в AST

это делает уже решатель после построения дерева

4. Exp всегда — целое число:
exp: 6

5. Unary minus → product(-1, variable)
6. Все узлы всегда содержат:

"kind"

только валидные ключи из стандарта



🟦 ПАТТЕРН 1.3 — alg_radical_fraction
AST (официальный эталон)

Паттерн имеет две формы:
🟡 √(K₁·aᵐ) · √(K₂·bⁿ) / √(ab)
🟡 √(ab) / (√(K₁ · aᵐ) · √(K₂ · bⁿ))


Во всех случаях:

✔ верхний AST-узел — всегда div (fraction)
✔ каждый корень — sqrt(radicand=...)
✔ radicand — только mul, pow, int, var
✔ никаких сокращений внутри AST (всё сокращает решатель!)
⭐ ЕДИНЫЙ НАБОР УЗЛОВ (AST)

Ты уже знаешь, но фиксируем, чтобы документ был самодостаточным:

integer:
{ "node": "int", "value": 25 }

variable:
{ "node": "var", "name": "a" }

power:
{ "node": "pow", "base": {...}, "exp": {...} }

product:
{ "node": "mul", "factors": [ ... ] }

fraction:
{ "node": "div", "num": {...}, "den": {...} }

sqrt:
{ "node": "sqrt", "radicand": {...} }

🎯 AST ЭТАЛОН 1 — Форма A
(√(25·a) · √(4·b³)) / √(ab)

Исходное выражение:

(√(25a) · √(4b^3)) / √(ab)


AST:

{
  "node": "div",
  "num": {
    "node": "mul",
    "factors": [
      {
        "node": "sqrt",
        "radicand": {
          "node": "mul",
          "factors": [
            { "node": "int", "value": 25 },
            { "node": "var", "name": "a" }
          ]
        }
      },
      {
        "node": "sqrt",
        "radicand": {
          "node": "mul",
          "factors": [
            { "node": "int", "value": 4 },
            {
              "node": "pow",
              "base": { "node": "var", "name": "b" },
              "exp": { "node": "int", "value": 3 }
            }
          ]
        }
      }
    ]
  },
  "den": {
    "node": "sqrt",
    "radicand": {
      "node": "mul",
      "factors": [
        { "node": "var", "name": "a" },
        { "node": "var", "name": "b" }
      ]
    }
  }
}

🎯 AST ЭТАЛОН 2 — Форма B
√(ab) / (√(9·a²) · √(16·b))

Исходное выражение:

√(ab) / (√(9a^2) · √(16b))


AST:

{
  "node": "div",
  "num": {
    "node": "sqrt",
    "radicand": {
      "node": "mul",
      "factors": [
        { "node": "var", "name": "a" },
        { "node": "var", "name": "b" }
      ]
    }
  },
  "den": {
    "node": "mul",
    "factors": [
      {
        "node": "sqrt",
        "radicand": {
          "node": "mul",
          "factors": [
            { "node": "int", "value": 9 },
            {
              "node": "pow",
              "base": { "node": "var", "name": "a" },
              "exp": { "node": "int", "value": 2 }
            }
          ]
        }
      },
      {
        "node": "sqrt",
        "radicand": {
          "node": "mul",
          "factors": [
            { "node": "int", "value": 16 },
            { "node": "var", "name": "b" }
          ]
        }
      }
    ]
  }
}

🧩 Итоги — структура 1.3 полностью определена
✔ Верхний уровень — div
✔ Корни — sqrt(radicand=...)
✔ В radicand только mul, pow, int, var
✔ AST не сокращает выражение
✔ Идеально подходит для expression_tree
✔ Идеально подходит для валидатора и решателя
