<p align="center">
  <img src="logo/cerium-logo-ref.png" alt="Cerium mascot" width="420">
</p>

<h1 align="center">Cerium</h1>

<p align="center">
  Небольшой статически типизированный язык с C#-подобным синтаксисом и собственным характером.
</p>

<p align="center">
  <a href="https://github.com/rusward/cerium/actions/workflows/ci.yml">
    <img src="https://github.com/rusward/cerium/actions/workflows/ci.yml/badge.svg" alt="CI">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="License: MIT">
  </a>
  <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/backend-C99%20%2B%20gcc-lightgrey.svg" alt="C99 backend">
</p>

Cerium (`ceriumc`) компилирует `.ce` в C99 и собирает нативный бинарник через `gcc`.
Функции объявляются через `func ... -> тип`, структуры собираются литералами без `new`,
а циклы бывают трёх видов — `while`, `for` и `loop`.

> **Статус:** ранняя версия 0.5.0. Язык и синтаксис ещё могут меняться.

## Возможности

- строгие типы `int` (64 бита), `double`, `bool`, `string` без неявных преобразований;
- функции, параметры, возвращаемые значения, рекурсия и вызовы вперёд;
- структуры с полями, литералы `Point { x = 1, y = 2 }`, доступ и присваивание полей;
- передача и возврат структур по значению;
- `if / else if / else`, `while`, `for`, `loop`, `break`, `continue`;
- вывод через `log(...)` и ввод с консоли: `input()`, `inputInt()`, `inputDouble()`, `inputBool()`;
- явные преобразования: `toString`, `toInt`, `toDouble`, `toBool`;
- блочные области видимости и подробная диагностика с позицией в `.ce`;
- компилятор на Python без внешних зависимостей.

## Пример

```csharp
struct Point {
    int x;
    int y;
}

func distanceSquared(Point a, Point b) -> int {
    int dx = a.x - b.x;
    int dy = a.y - b.y;
    return dx * dx + dy * dy;
}

Point a = Point { x = 1, y = 2 };
Point b = Point { x = 4, y = 6 };

log("distance^2 =", distanceSquared(a, b));

for (int i = 1; i <= 3; i = i + 1) {
    log("step", i);
}
```

```
$ ceriumc build example.ce -o example
$ ./example
distance^2 = 25
step 1
step 2
step 3
```

## Ввод с консоли

```csharp
string name = input("Name: ");
int age = inputInt("Age: ");
double height = inputDouble("Height: ");
bool ok = inputBool("Continue? (true/false): ");

log("hello,", name);
log(age, height, ok);
```

Промпт необязателен, печатается без перевода строки и сразу сбрасывается. Ввод читается
по одной строке. Типизированные функции разбирают строку целиком, а при неверном формате
или EOF завершают программу с `runtime error` и кодом 1.

## Преобразования типов

Неявных преобразований нет, поэтому тип меняется явно:

```csharp
log("answer: " + toString(42));
int port = toInt(" 8080 ");
double ratio = toDouble("2.5e-1");
bool enabled = toBool("true");

log(port, ratio, enabled); // 8080 0.25 true
```

`toString` принимает `int`, `double`, `bool` или `string`. `toInt`, `toDouble`,
`toBool` принимают строку, обрезают пробелы по краям и при неверном формате завершают
программу с `runtime error`.

## Требования

- Python 3.10+
- C99-компилятор (`gcc` по умолчанию)

Проект разрабатывается и тестируется на Linux x86-64.

## Установка

```sh
git clone https://github.com/rusward/cerium.git
cd cerium

python3 -m pip install -e .
ceriumc --version
```

Можно обойтись без установки — в корне лежит launcher:

```sh
./ceriumc --version
./ceriumc build examples/hello.ce -o hello
./hello
```

## CLI

```
ceriumc build <file.ce> [-o out] [--emit-c PATH] [--keep-c] [--static] [--cc gcc]
ceriumc check <file.ce>
ceriumc emit-c <file.ce> [-o out.c]
ceriumc --version
```

- `build` собирает нативный бинарник;
- `check` проверяет синтаксис и типы без вызова C-компилятора;
- `emit-c` печатает сгенерированный C;
- `--emit-c PATH` сохраняет C-код при сборке;
- `--keep-c` оставляет временный C-файл;
- `--cc NAME` выбирает C-компилятор.

Коды возврата: `0` — успех, `1` — ошибка компиляции/типов/рантайма, `2` — ошибка
использования CLI, `3` — сбой C-компилятора.

## Тесты

```sh
make test
```

End-to-end тесты собирают настоящие бинарники и пропускаются, если `gcc` не найден.

## Структура проекта

```
src/ceriumc/    компилятор (лексер, парсер, проверка типов, кодоген)
examples/         примеры программ и примеры ошибок
tests/            unittest-набор
docs/syntax.md    практическое руководство по синтаксису (на русском)
SPEC.md           формальная грамматика и семантика
logo/             ассеты логотипа
```

## Документация

- [docs/syntax.md](docs/syntax.md) — синтаксис и примеры на русском.
- [SPEC.md](SPEC.md) — грамматика EBNF, типы, семантика и диагностика.
- [CHANGELOG.md](CHANGELOG.md) — история изменений.
- [CONTRIBUTING.md](CONTRIBUTING.md) — как собрать, тестировать и присылать изменения.

## Планы

- массивы и `foreach`;
- `switch`;
- строковые и математические функции в стандартной библиотеке;
- модули/импорты;
- публикация пакета и релизные бинарники.

## Лицензия

[MIT](LICENSE) © Cerium contributors.
