---
title: Getting started
---

# Getting started

Cerium compiles `.ce` source files to C99 and builds a native executable with `gcc`.
This guide takes you from a clean checkout to a running binary.

## Requirements

- Python 3.10 or newer;
- a C99 compiler (`gcc` by default);
- Linux x86-64 is the tested platform.

## Install

=== "Run from the repository"

    ```sh
    git clone https://github.com/rusward/cerium.git
    cd cerium
    ./ceriumc --version
    ```

    The `ceriumc` launcher uses the sources in `src/` directly.

=== "Install as a Python package"

    ```sh
    git clone https://github.com/rusward/cerium.git
    cd cerium
    python3 -m pip install -e .
    ceriumc --version
    ```

    After installation the `ceriumc` command is available everywhere in the active
    environment.

## Your first program

Create `hello.ce`:

```csharp
log("hello, cerium");
```

Build and run it:

```sh
./ceriumc build hello.ce -o hello
./hello
```

```
hello, cerium
```

## Check and inspect

`ceriumc` has three commands:

```sh
./ceriumc check hello.ce     # parse and type-check only
./ceriumc emit-c hello.ce    # print the generated C
./ceriumc build hello.ce -o hello
```

`check` reports every type error it can find without invoking the C compiler. `emit-c`
is useful when you want to see exactly what ends up in the generated program.

## Next steps

- [Program basics](guide/basics.md) — structure, comments, identifiers.
- [Types and variables](guide/types.md) — the type system and literals.
- [Functions](guide/functions.md) — declarations, returns and recursion.
- [Structs](guide/structs.md) — value types with fields.
- [Specification](spec.md) — the complete formal description.
