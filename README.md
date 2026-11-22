<p align="center">
  <img src="logo/cerium-logo.png" alt="Cerium logo" width="420">
</p>

<h1 align="center">Cerium</h1>

<p align="center">
  A small statically typed language with C#-like syntax and a character of its own.
</p>

<p align="center">
  <sub>CI passing · MIT · Python 3.10+ · C99 + gcc</sub>
</p>

Cerium (`ceriumc`) compiles `.ce` to C99 and builds a native binary with `gcc`.
Functions are declared with `func ... -> type`, structs are built with literals and no `new`,
and there are three loop forms — `while`, `for`, and `loop`.

**Documentation:** <https://rusward.github.io/cerium/> — English and Russian, with search,
dark mode, and the complete language guide.


> **Status:** early version 0.5.0. The language and syntax may still change.

## Features

- strict types `int` (64-bit), `double`, `bool`, `string` with no implicit conversions;
- functions, parameters, return values, recursion, and forward calls;
- structs with fields, literals `Point { x = 1, y = 2 }`, field access and assignment;
- structs passed to and returned from functions by value;
- `if / else if / else`, `while`, `for`, `loop`, `break`, `continue`;
- output via `log(...)` and console input: `input()`, `inputInt()`, `inputDouble()`, `inputBool()`;
- explicit conversions: `toString`, `toInt`, `toDouble`, `toBool`;
- block scoping and detailed diagnostics with positions in `.ce` files;
- a compiler written in Python with no external dependencies.

## Example

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

## Console input

```csharp
string name = input("Name: ");
int age = inputInt("Age: ");
double height = inputDouble("Height: ");
bool ok = inputBool("Continue? (true/false): ");

log("hello,", name);
log(age, height, ok);
```

The prompt is optional. It is printed without a trailing newline and flushed immediately.
Each call reads one line. Typed functions parse the whole line and terminate the program with a
`runtime error` and exit code 1 on invalid input or EOF.

## Type conversions

There are no implicit conversions, so types change explicitly:

```csharp
log("answer: " + toString(42));
int port = toInt(" 8080 ");
double ratio = toDouble("2.5e-1");
bool enabled = toBool("true");

log(port, ratio, enabled); // 8080 0.25 true
```

`toString` accepts `int`, `double`, `bool`, or `string`. `toInt`, `toDouble`, and `toBool`
accept a string, trim surrounding whitespace, and terminate with a `runtime error` if the text
does not parse.

## Requirements

- Python 3.10+
- A C99 compiler (`gcc` by default)

Cerium is developed and tested on Linux x86-64.

## Installation

```sh
git clone https://github.com/rusward/cerium.git
cd cerium

python3 -m pip install -e .
ceriumc --version
```

You can also run the launcher from the repository root without installing:

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

- `build` compiles a native binary;
- `check` validates syntax and types without invoking the C compiler;
- `emit-c` prints the generated C;
- `--emit-c PATH` saves the C source during a build;
- `--keep-c` keeps the temporary C file;
- `--cc NAME` selects the C compiler.

Exit codes: `0` success, `1` compilation/type/runtime error, `2` CLI usage error, `3` C
backend failure.

## Tests

```sh
make test
```

End-to-end tests compile real binaries and are skipped automatically when `gcc` is not
available.

## Project structure

```
src/ceriumc/     compiler (lexer, parser, type checker, codegen)
examples/        sample programs and intentional error cases
tests/           unittest suite
docs/syntax.md   practical syntax guide
SPEC.md          formal grammar and semantics
logo/            logo assets
```

## Documentation

- [Online documentation](https://rusward.github.io/cerium/) — bilingual EN/RU site with search,
  dark mode, and the full guide.
- [docs/syntax.md](docs/syntax.md) — syntax guide and examples.
- [SPEC.md](SPEC.md) — EBNF grammar, types, semantics, and diagnostics.
- [CHANGELOG.md](CHANGELOG.md) — change history.
- [CONTRIBUTING.md](CONTRIBUTING.md) — how to build, test, and contribute.

The site lives in `website/` and is built with MkDocs Material. To preview it locally:

```sh
make docs-install
make docs-serve
```

## Roadmap

- arrays and `foreach`;
- `switch`;
- string and math functions in the standard library;
- modules/imports;
- package publication and release binaries.

## License

[MIT](LICENSE) © Cerium contributors.
