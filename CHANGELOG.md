# Changelog

All notable changes to Cerium are documented in this file.

## [0.5.0] - 2026-11-22

### Added

- bilingual documentation site under `website/`, built with MkDocs Material and deployed to
  GitHub Pages.

### Changed

- **BREAKING:** the project is renamed from Hydrogen to Cerium because the old name was
  already used by another language;
- source file extension changed from `.hy` to `.ce`;
- compiler command and Python package renamed from `hydrogenc` to `ceriumc`;
- C runtime prefix renamed from `hy_` to `ce_`, `HY_FILE` to `CE_FILE`;
- all user-facing documentation translated to English;
- GitHub repository moved from `rusward/hydrogen` to `rusward/cerium`.

## [0.4.0] - 2026-11-22

### Added

- explicit conversions: `toString(value)`, `toInt(text)`, `toDouble(text)`, `toBool(text)`;
- numeric-to-string formatting matching `log` (`%g` for doubles);
- runtime errors for invalid conversion input;
- `examples/conversions.hy` and tests for conversions.

## [0.3.0] - 2026-11-22

### Added

- console input builtins: `input()`, `inputInt()`, `inputDouble()`, `inputBool()`;
- optional string prompt argument that is printed and flushed before reading;
- typed parsing with runtime errors for invalid input and unexpected EOF;
- `examples/input.hy` and end-to-end tests that feed stdin to compiled programs.

## [0.2.0] - 2026-11-22

### Added

- user-defined functions: `func name(...) -> type`, `void` returns, recursion;
- forward calls and mutual recursion via signature pre-pass;
- `struct` declarations, struct literals without `new`, field access and field assignment;
- structs as parameters and return values, passed by value;
- C-style `for` loops with scoped init declarations;
- infinite `loop` with `break` and `continue`;
- missing-return analysis for non-void functions;
- tests for functions, structs, loops and new error cases;
- `docs/syntax.md`: syntax guide for v0.2;
- packaging metadata (`pyproject.toml`), CI workflow, MIT license;
- project logo reference in `logo/`.

### Changed

- assignment targets can now be fields: `p.x = value;`;
- calls may be used as statements even when they return a value;
- `SPEC.md` updated to the v0.2 grammar and semantics.

### Fixed

- division and modulo by zero now report the exact `.hy` line;
- integer overflow uses defined two's-complement wraparound helpers.

## [0.1.0] - 2026-11-22

### Added

- lexer, recursive-descent parser and AST for the initial language;
- static type checker with block scopes and multiple diagnostics;
- C99 backend, gcc driver, `#line` mapping and runtime helpers;
- scalar types `int`, `double`, `bool`, `string`;
- `if`/`else if`/`else`, `while`, `log(...)`;
- CLI: `build`, `check`, `emit-c`, `--version`;
- unit and end-to-end test suite;
- examples and initial documentation.
