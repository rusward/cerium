# Contributing to Cerium

Thanks for taking a look at Cerium. The project is an early MVP, so small focused changes are
the easiest to review.

## Requirements

- Python 3.10+
- A C99 compiler (`gcc` by default)
- GNU Make (optional, used by the convenience targets)

## Development setup

```sh
git clone https://github.com/rusward/cerium.git
cd cerium

python3 -m pip install -e .
# or run without installing:
./ceriumc --version

make test
```

`make test` runs the whole `unittest` suite. End-to-end tests compile real binaries and are
skipped automatically when `gcc` is not available.

Useful commands:

```sh
make check        # type-check examples/hello.ce
make examples     # build every example into build/
make clean
```

## Project layout

```
src/ceriumc/
  lexer.py        tokens, comments, literals
  parser.py       recursive descent, AST construction
  nodes.py        dataclass AST nodes
  checker.py      scopes, functions, structs, type rules
  codegen_c.py    C99 emission
  runtime.py      C runtime helpers embedded in generated programs
  cli.py          command-line interface and gcc driver
tests/            unit and end-to-end tests
examples/         sample programs and intentional error cases
docs/syntax.md    user-facing syntax guide (Russian)
SPEC.md           formal grammar and semantics
```

## Adding a language feature

1. Add tokens/keywords to `lexer.py` if needed.
2. Add AST nodes in `nodes.py`.
3. Extend the parser in `parser.py`.
4. Implement typing and diagnostics in `checker.py`.
5. Emit C in `codegen_c.py`; add runtime helpers in `runtime.py` if necessary.
6. Add positive and negative tests (`tests/test_*.py`).
7. Add or update an example, `SPEC.md`, and `docs/syntax.md` when the feature is user-facing.

## Style

- Python standard library only; avoid new dependencies unless discussed in an issue.
- Follow the existing formatting and naming style (PEP 8, 4 spaces, f-strings).
- Keep compiler diagnostics precise: report the file, line, and column, and prefer specific
  messages over generic ones.
- Do not commit compiled binaries, virtual environments, or editor files.

## Pull requests

- Keep one feature or fix per pull request.
- Make sure `make test` passes and the examples still build.
- Describe the change, the motivation, and any user-visible syntax changes.
- Update `CHANGELOG.md` for user-visible changes.

## Documentation site

The public documentation lives in `website/docs/` and is built with MkDocs Material. The English
pages are at the root of that directory, and Russian translations are under `website/docs/ru/`.
Root `SPEC.md` and `CHANGELOG.md` are copied into the site during `make docs-build` and in CI.

```sh
make docs-install   # install mkdocs-material and the i18n plugin
make docs-serve     # live preview on http://127.0.0.1:8000
make docs-build     # strict build, including both languages
```

When changing a page, update the corresponding page under `ru/` as well. Keep navigation labels
in `website/mkdocs.yml` and their `nav_translations` in sync.

By contributing you agree that your changes are licensed under the MIT License.
