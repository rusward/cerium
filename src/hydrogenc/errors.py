"""Error types and diagnostic rendering."""

from dataclasses import dataclass


@dataclass
class Diagnostic:
    message: str
    line: int
    col: int


class HydrogenError(Exception):
    """A single fatal error raised by the lexer or the parser."""

    def __init__(self, message: str, line: int = 1, col: int = 1):
        super().__init__(message)
        self.message = message
        self.line = line
        self.col = col


class HydrogenErrors(Exception):
    """A batch of errors collected by the type checker."""

    def __init__(self, errors):
        super().__init__("type checking failed")
        self.errors = list(errors)


def render(filename: str, source: str, diagnostic: Diagnostic) -> str:
    """Render an error with a source excerpt and a caret."""
    lines = source.splitlines()
    if 0 < diagnostic.line <= len(lines):
        raw = lines[diagnostic.line - 1]
    else:
        raw = ""

    # Expand tabs consistently so the caret lines up with the excerpt.
    prefix = raw[: max(diagnostic.col - 1, 0)].expandtabs(4)
    shown = raw.expandtabs(4)
    caret = " " * len(prefix) + "^"

    header = f"{filename}:{diagnostic.line}:{diagnostic.col}: error: {diagnostic.message}"
    return f"{header}\n    {shown}\n    {caret}"
