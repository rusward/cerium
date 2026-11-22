import unittest

import support  # noqa: F401  (adds src to sys.path)

from hydrogenc.errors import HydrogenError
from hydrogenc.lexer import Lexer


def lex(text):
    return Lexer(text, "test.hy").tokenize()


def without_eof(text):
    return lex(text)[:-1]


class LexerTests(unittest.TestCase):
    def test_keywords_and_identifiers(self):
        tokens = without_eof("int x = 1; log(x);")
        self.assertEqual(
            [(token.kind, token.value) for token in tokens],
            [
                ("kw", "int"),
                ("ident", "x"),
                ("op", "="),
                ("int", 1),
                ("op", ";"),
                ("ident", "log"),
                ("op", "("),
                ("ident", "x"),
                ("op", ")"),
                ("op", ";"),
            ],
        )

    def test_numbers(self):
        tokens = without_eof("42 3.14")
        self.assertEqual(
            [(token.kind, token.value) for token in tokens],
            [("int", 42), ("double", "3.14")],
        )

    def test_two_character_operators(self):
        tokens = without_eof("== != <= >= && ||")
        self.assertEqual(
            [token.value for token in tokens],
            ["==", "!=", "<=", ">=", "&&", "||"],
        )

    def test_positions(self):
        tokens = lex("int x = 1;\nbool y = true;")
        y_token = [token for token in tokens if token.value == "y"][0]
        self.assertEqual((y_token.line, y_token.col), (2, 6))
        eof = tokens[-1]
        self.assertEqual(eof.kind, "eof")

    def test_line_comments(self):
        tokens = without_eof("// a comment\n42 // trailing")
        self.assertEqual([token.value for token in tokens], [42])

    def test_block_comments(self):
        tokens = without_eof("1 /* one\ntwo */ 2")
        self.assertEqual([token.value for token in tokens], [1, 2])

    def test_string_escapes(self):
        token = lex(r'"a\nb\t\"c\\"')[0]
        self.assertEqual(token.value, 'a\nb\t"c\\')

    def test_unterminated_string(self):
        with self.assertRaises(HydrogenError) as caught:
            lex('"abc')
        self.assertIn("unterminated string", caught.exception.message)

    def test_newline_in_string(self):
        with self.assertRaises(HydrogenError):
            lex('"abc\ndef"')

    def test_unknown_escape(self):
        with self.assertRaises(HydrogenError) as caught:
            lex(r'"a\q"')
        self.assertIn("unknown escape", caught.exception.message)

    def test_unterminated_block_comment(self):
        with self.assertRaises(HydrogenError) as caught:
            lex("/* nope")
        self.assertIn("unterminated block comment", caught.exception.message)

    def test_malformed_number(self):
        with self.assertRaises(HydrogenError):
            lex("12abc")

    def test_malformed_float(self):
        with self.assertRaises(HydrogenError):
            lex("1.")

    def test_unexpected_character(self):
        with self.assertRaises(HydrogenError) as caught:
            lex("a @ b")
        self.assertIn("unexpected character", caught.exception.message)

    def test_new_keywords(self):
        tokens = without_eof("func struct void for loop break continue return")
        self.assertEqual([token.kind for token in tokens], ["kw"] * 8)

    def test_arrow_and_dot_operators(self):
        tokens = without_eof("-> .")
        self.assertEqual([token.value for token in tokens], ["->", "."])


if __name__ == "__main__":
    unittest.main()
