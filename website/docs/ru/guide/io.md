---
title: Ввод, вывод и преобразования
---

# Ввод, вывод и преобразования

## Вывод: `log`

```csharp
log("hello");
log("n =", 42);
log("pi =", 3.14, "ok =", true);
log(); // пустая строка
```

- аргументы печатаются в stdout через пробел;
- в конце добавляется `\n`;
- `int` — десятичное число;
- `double` — `%g` (`3.14`, `10`, `0.5`);
- `bool` — `true`/`false`;
- `string` — как есть.

`log` возвращает `void` и не принимает структуры целиком:

```csharp
// log(log("nested")); // ошибка
// log(point);         // ошибка, печатайте поля
```

## Ввод: `input`

| Функция             | Аргумент          | Результат |
|---------------------|-------------------|-----------|
| `input()`           | необязательный промпт | `string` |
| `inputInt()`        | необязательный промпт | `int`    |
| `inputDouble()`     | необязательный промпт | `double` |
| `inputBool()`       | необязательный промпт | `bool`   |

Промпт — строковое выражение. Он печатается в stdout без перевода строки и сразу
сбрасывается, чтобы приглашение появилось до чтения:

```csharp
string name = input("Name: ");
int age = inputInt("Age: ");
double height = inputDouble();
bool ok = inputBool("Continue? (true/false): ");

log("hello,", name);
log(age, height, ok);
```

Правила:

- каждый вызов читает одну строку из stdin;
- завершающие `\n` и `\r` отрезаются;
- `input()` сохраняет остальные символы, включая пробелы по краям;
- пустая строка — нормальное значение `input()` (пустая строка);
- конец ввода (EOF) до первого символа — ошибка рантайма, даже для `input()`;
- `inputInt`, `inputDouble`, `inputBool` обрезают пробелы и табуляцию по краям и
  разбирают строку целиком:
  - `inputInt` — знак и десятичные цифры, диапазон 64-битного `int`;
  - `inputDouble` — десятичная запись, которую понимает C `strtod`, включая дробную
    часть и экспоненту (`1.5e2`);
  - `inputBool` — строго `true` или `false`.

При неверном вводе программа печатает ошибку и завершается с кодом 1:

```
runtime error: invalid int input: '12abc': program.ce:3
runtime error: unexpected end of input: program.ce:5
```

Встроенные функции ввода нельзя переопределить через `func input(...)`.

```csharp
int n = inputInt();        // ввод: 41
log(n + 1);                // 42

string text = input();     // ввод: hello world
log("[" + text + "]");     // [hello world]
```

## Преобразования типов

Неявных преобразований нет, поэтому для смены типа используются явные функции:

| Функция             | Аргумент       | Результат |
|---------------------|----------------|-----------|
| `toString(value)`   | `int`, `double`, `bool` или `string` | `string` |
| `toInt(text)`       | `string`       | `int`     |
| `toDouble(text)`    | `string`       | `double`  |
| `toBool(text)`      | `string`       | `bool`    |

```csharp
string label = "answer: " + toString(42);
int port = toInt(" 8080 ");
double ratio = toDouble("2.5e-1");
bool enabled = toBool("true");

log(label);   // answer: 42
log(port);    // 8080
log(ratio);   // 0.25
log(enabled); // true
```

Правила:

- `toString` принимает один скаляр. `int` печатается десятичным числом, `double` — в
  формате `%g` (как в `log`), `bool` — как `true`/`false`, строка возвращается как есть;
- структуру в `toString` передать нельзя — конвертируйте отдельные поля;
- `toInt`, `toDouble`, `toBool` принимают только `string`, обрезают пробелы и табуляцию
  по краям и разбирают оставшийся текст целиком;
- форматы те же, что у `inputInt`, `inputDouble`, `inputBool`;
- при неверном тексте — ошибка рантайма и код 1:

```
runtime error: invalid int value: '12abc': program.ce:3
runtime error: invalid bool value: 'yes': program.ce:7
```

Типичное применение — склеить число или `bool` со строкой:

```csharp
struct User {
    string name;
    int avatar;
}

User user = User { name = "TeamLED", avatar = 87123712 };
log("USERNAME: (" + user.name + ")");
log("AVATAR: (" + toString(user.avatar) + ")");
```

```
USERNAME: (TeamLED)
AVATAR: (87123712)
```
