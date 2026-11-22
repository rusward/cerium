---
title: Getting started
---

# Getting started

Cerium compiles `.ce` source files to C99 and builds a native executable with `gcc`.
This guide takes you from a clean checkout to a running binary.

## Requirements

- Python 3.10 or newer;
- a supported C99 compiler in `PATH`;
- Linux x86-64 is tested on every change; macOS and Windows are tested in CI.

On macOS install Xcode Command Line Tools (`xcode-select --install`). On Windows install
MinGW-w64 (MSYS2 UCRT64) or LLVM clang and add it to `PATH`; MSVC `cl.exe` is not supported.
`ceriumc` detects the compiler automatically and prefers `clang` on macOS, `gcc` elsewhere.
Use `--cc PATH` to override.

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
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -e .
    ceriumc --version
    ```

    After installation the `ceriumc` command is available everywhere in the active
    environment. On Fedora/Debian, never use `--break-system-packages`; the venv is the
    supported path.

On Windows use `py -m venv .venv`, activate it with `.venv\Scripts\activate`, then run
`python -m pip install -e .`. The installed `ceriumc` command and `ceriumc.cmd` from a source
checkout both work. Build outputs get a `.exe` extension automatically.

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
