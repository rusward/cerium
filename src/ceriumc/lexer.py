"""Lexer for the Cerium language."""

from dataclasses import dataclass

from .errors import CeriumError

KEYWORDS = {
    "int",
    "double",
    "bool",
    "string",
    "void",
    "func",
    "struct",
    "return",
    "if",
    "else",
    "while",
    "for",
    "loop",
    "break",
    "continue",
    "true",
    "false",
}

# Two-character operators must be matched before their one-character prefixes.
OPERATORS = [
    "==",
    "!=",
    "<=",
    ">=",
    "&&",
    "||",
    "->",
    "+",
    "-",
    "*",
    "/",
    "%",
    "=",
    "<",
    ">",
    "!",
    ".",
    "(",
    ")",
    "{",
    "}",
    ";",
    ",",
]

ESCAPES = {
    "n": "\n",
    "t": "\t",
    "r": "\r",
    "\\": "\\",
    '"': '"',
}


@dataclass
class Token:
    kind: str  # "ident" | "kw" | "int" | "double" | "string" | "op" | "eof"
    value: object
    line: int
    col: int

    def describe(self) -> str:
        if self.kind == "eof":
            return "end of file"
        if self.kind == "string":
            return "string literal"
        return f"'{self.value}'"


class Lexer:
    def __init__(self, text: str, filename: str = "<input>"):
        self.text = text
        self.filename = filename
        self.i = 0
        self.line = 1
        self.col = 1

    def tokenize(self):
        tokens = []
        while True:
            self._skip_trivia()
            if self.i >= len(self.text):
                tokens.append(Token("eof", None, self.line, self.col))
                return tokens

            line, col = self.line, self.col
            ch = self.text[self.i]

            if _is_ident_start(ch):
                value = self._read_identifier()
                kind = "kw" if value in KEYWORDS else "ident"
                tokens.append(Token(kind, value, line, col))
            elif ch.isdigit() and ch.isascii():
                kind, value = self._read_number()
                tokens.append(Token(kind, value, line, col))
            elif ch == '"':
                tokens.append(Token("string", self._read_string(), line, col))
            else:
                tokens.append(Token("op", self._read_operator(), line, col))

    # -- character helpers -------------------------------------------------

    def _advance(self, count: int = 1) -> None:
        for _ in range(count):
            if self.i >= len(self.text):
                return
            if self.text[self.i] == "\n":
                self.line += 1
                self.col = 1
            else:
                self.col += 1
            self.i += 1

    def _error(self, message: str, line=None, col=None):
        raise CeriumError(
            message,
            self.line if line is None else line,
            self.col if col is None else col,
        )

    # -- trivia ------------------------------------------------------------

    def _skip_trivia(self) -> None:
        text = self.text
        while self.i < len(text):
            ch = text[self.i]
            if ch in " \t\r\n":
                self._advance()
            elif text.startswith("//", self.i):
                while self.i < len(text) and text[self.i] != "\n":
                    self._advance()
            elif text.startswith("/*", self.i):
                line, col = self.line, self.col
                self._advance(2)
                closed = False
                while self.i < len(text):
                    if text.startswith("*/", self.i):
                        self._advance(2)
                        closed = True
                        break
                    self._advance()
                if not closed:
                    self._error("unterminated block comment", line, col)
            else:
                return

    # -- tokens ------------------------------------------------------------

    def _read_identifier(self) -> str:
        start = self.i
        while self.i < len(self.text) and _is_ident_char(self.text[self.i]):
            self._advance()
        return self.text[start:self.i]

    def _read_number(self):
        line, col = self.line, self.col
        start = self.i
        while self.i < len(self.text) and self.text[self.i].isdigit():
            self._advance()

        is_float = False
        if self.i < len(self.text) and self.text[self.i] == ".":
            if self.i + 1 < len(self.text) and self.text[self.i + 1].isdigit():
                is_float = True
                self._advance()
                while self.i < len(self.text) and self.text[self.i].isdigit():
                    self._advance()
            else:
                self._error("malformed number literal", line, col)

        if self.i < len(self.text) and _is_ident_char(self.text[self.i]):
            self._error("malformed number literal", line, col)

        raw = self.text[start:self.i]
        if is_float:
            return "double", raw
        return "int", int(raw)

    def _read_string(self) -> str:
        line, col = self.line, self.col
        self._advance()  # opening quote
        chars = []
        while True:
            if self.i >= len(self.text):
                self._error("unterminated string literal", line, col)
            ch = self.text[self.i]
            if ch == '"':
                self._advance()
                return "".join(chars)
            if ch == "\n":
                self._error("unterminated string literal", line, col)
            if ch == "\\":
                self._advance()
                if self.i >= len(self.text):
                    self._error("unterminated string literal", line, col)
                escape = self.text[self.i]
                if escape not in ESCAPES:
                    self._error(f"unknown escape sequence '\\{escape}'")
                chars.append(ESCAPES[escape])
                self._advance()
            else:
                chars.append(ch)
                self._advance()

    def _read_operator(self) -> str:
        for operator in OPERATORS:
            if self.text.startswith(operator, self.i):
                self._advance(len(operator))
                return operator
        ch = self.text[self.i]
        self._error(f"unexpected character {ch!r}")


def _is_ident_start(ch: str) -> bool:
    return ch == "_" or "a" <= ch <= "z" or "A" <= ch <= "Z"


def _is_ident_char(ch: str) -> bool:
    return _is_ident_start(ch) or ("0" <= ch <= "9")
