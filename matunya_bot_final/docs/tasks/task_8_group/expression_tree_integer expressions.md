🟦 Expression Tree — integer_expressions

Задание 8. Тема 1 — INTEGER EXPRESSIONS
Алгебраические выражения со степенями и корнями при подстановке.

📘 Общий стандарт узлов expression_tree

Каждый узел обязан быть одним из следующих типов:

1. integer
{ "type": "integer", "value": 25 }

2. variable
{ "type": "variable", "name": "a" }

3. power
{
  "type": "power",
  "base": { ... },
  "exp": { "type": "integer", "value": 6 }
}

4. product
{
  "type": "product",
  "factors": [ { ... }, { ... } ]
}

5. fraction
{
  "type": "fraction",
  "numerator": { ... },
  "denominator": { ... }
}

6. sqrt
{
  "type": "sqrt",
  "radicand": { ... }
}

❗ Унификация обязательна:
✔ exp всегда объект:

❌ exp": 6
✔ exp": { "type": "integer", "value": 6 }

✔ sqrt всегда содержит ключ radicand, не value:

❌ "value": { ... }
✔ "radicand": { ... }

✔ тип числа integer, не number:

❌ { "type": "number" … }
✔ { "type": "integer" … }

🎯 ПАТТЕРН 1.1 — alg_power_fraction

Алгебраическая дробь. Верхний элемент — ВСЕГДА "type": "fraction".

Поддерживает две формы:

1️⃣ ((aᵐ)ⁿ · aʳ) / aˢ
2️⃣ (aᵐ · (bⁿ)ʳ) / (a·b)ˢ

✅ ЭТАЛОН 1 — ((aᵐ)ⁿ · aʳ) / aˢ

Пример:

((a³)⁵ · a³) / a²⁰

{
  "type": "fraction",
  "numerator": {
    "type": "product",
    "factors": [
      {
        "type": "power",
        "base": {
          "type": "power",
          "base": { "type": "variable", "name": "a" },
          "exp": { "type": "integer", "value": 3 }
        },
        "exp": { "type": "integer", "value": 5 }
      },
      {
        "type": "power",
        "base": { "type": "variable", "name": "a" },
        "exp": { "type": "integer", "value": 3 }
      }
    ]
  },
  "denominator": {
    "type": "power",
    "base": { "type": "variable", "name": "a" },
    "exp": { "type": "integer", "value": 20 }
  }
}

✅ ЭТАЛОН 2 — (aᵐ · (bⁿ)ʳ) / (a·b)ˢ

Пример:

(a⁶ · (b²)⁴) / (a·b)⁷

{
  "type": "fraction",
  "numerator": {
    "type": "product",
    "factors": [
      {
        "type": "power",
        "base": { "type": "variable", "name": "a" },
        "exp": { "type": "integer", "value": 6 }
      },
      {
        "type": "power",
        "base": {
          "type": "power",
          "base": { "type": "variable", "name": "b" },
          "exp": { "type": "integer", "value": 2 }
        },
        "exp": { "type": "integer", "value": 4 }
      }
    ]
  },
  "denominator": {
    "type": "power",
    "base": {
      "type": "product",
      "factors": [
        { "type": "variable", "name": "a" },
        { "type": "variable", "name": "b" }
      ]
    },
    "exp": { "type": "integer", "value": 7 }
  }
}

🎯 ПАТТЕРН 1.2 — alg_radical_power

Корень ОДИН, накрывает всё выражение.

Поддерживает четыре формы:

√((K·aᵐ)/aⁿ)

√(K·aᵐ)

√((-a)ᵐ · aⁿ)

√((-a)ᵐ · (a⁻ⁿ)ᵖ)

✅ ЭТАЛОН A — Корень от дроби
√(100 · a²¹ / a¹⁹)

{
  "type": "sqrt",
  "radicand": {
    "type": "fraction",
    "numerator": {
      "type": "product",
      "factors": [
        { "type": "integer", "value": 100 },
        {
          "type": "power",
          "base": { "type": "variable", "name": "a" },
          "exp": { "type": "integer", "value": 21 }
        }
      ]
    },
    "denominator": {
      "type": "power",
      "base": { "type": "variable", "name": "a" },
      "exp": { "type": "integer", "value": 19 }
    }
  }
}

✅ ЭТАЛОН B — Корень от произведения
√(25 · a⁶)

{
  "type": "sqrt",
  "radicand": {
    "type": "product",
    "factors": [
      { "type": "integer", "value": 25 },
      {
        "type": "power",
        "base": { "type": "variable", "name": "a" },
        "exp": { "type": "integer", "value": 6 }
      }
    ]
  }
}

✅ ЭТАЛОН C — Корень от произведения с (-a)
√((-a)⁶ · a⁴)

{
  "type": "sqrt",
  "radicand": {
    "type": "product",
    "factors": [
      {
        "type": "power",
        "base": {
          "type": "product",
          "factors": [
            { "type": "integer", "value": -1 },
            { "type": "variable", "name": "a" }
          ]
        },
        "exp": { "type": "integer", "value": 6 }
      },
      {
        "type": "power",
        "base": { "type": "variable", "name": "a" },
        "exp": { "type": "integer", "value": 4 }
      }
    ]
  }
}

🎯 ПАТТЕРН 1.3 — alg_radical_fraction

(корни в числителе и/или знаменателе)
Два эталона — обе формы из Ященко.

✅ ЭТАЛОН 1 — Форма A
( √(25·a) · √(4·b³) ) / √(ab)

{
  "type": "fraction",
  "numerator": {
    "type": "product",
    "factors": [
      {
        "type": "sqrt",
        "radicand": {
          "type": "product",
          "factors": [
            { "type": "integer", "value": 25 },
            { "type": "variable", "name": "a" }
          ]
        }
      },
      {
        "type": "sqrt",
        "radicand": {
          "type": "product",
          "factors": [
            { "type": "integer", "value": 4 },
            {
              "type": "power",
              "base": { "type": "variable", "name": "b" },
              "exp": { "type": "integer", "value": 3 }
            }
          ]
        }
      }
    ]
  },
  "denominator": {
    "type": "sqrt",
    "radicand": {
      "type": "product",
      "factors": [
        { "type": "variable", "name": "a" },
        { "type": "variable", "name": "b" }
      ]
    }
  }
}

✅ ЭТАЛОН 2 — Форма B
√(ab) / ( √(9·a²) · √(16·b) )

{
  "type": "fraction",
  "numerator": {
    "type": "sqrt",
    "radicand": {
      "type": "product",
      "factors": [
        { "type": "variable", "name": "a" },
        { "type": "variable", "name": "b" }
      ]
    }
  },
  "denominator": {
    "type": "product",
    "factors": [
      {
        "type": "sqrt",
        "radicand": {
          "type": "product",
          "factors": [
            { "type": "integer", "value": 9 },
            {
              "type": "power",
              "base": { "type": "variable", "name": "a" },
              "exp": { "type": "integer", "value": 2 }
            }
          ]
        }
      },
      {
        "type": "sqrt",
        "radicand": {
          "type": "product",
          "factors": [
            { "type": "integer", "value": 16 },
            { "type": "variable", "name": "b" }
          ]
        }
      }
    ]
  }
}

🌟 ВСЁ ГОТОВО

✔ exp — объект
✔ sqrt — radicand
✔ integer вместо number
✔ исправлен заголовок 1.3
✔ все эталоны теперь 100% строгие
