import unittest

import support  # noqa: F401

from ceriumc import nodes
from ceriumc.errors import CeriumError
from ceriumc.lexer import Lexer
from ceriumc.parser import Parser


def parse(text):
    tokens = Lexer(text, "test.ce").tokenize()
    return Parser(tokens, "test.ce").parse()


class ParserTests(unittest.TestCase):
    def test_empty_program(self):
        self.assertEqual(parse("").statements, [])

    def test_variable_declaration(self):
        program = parse("int answer = 42;")
        statement = program.statements[0]
        self.assertIsInstance(statement, nodes.VarDecl)
        self.assertEqual(statement.name, "answer")
        self.assertEqual(statement.type_name, "int")
        self.assertIsInstance(statement.expr, nodes.IntLit)
        self.assertEqual(statement.expr.value, 42)

    def test_assignment_is_not_expression_statement(self):
        program = parse("x = 1;")
        self.assertIsInstance(program.statements[0], nodes.Assign)

    def test_operator_precedence(self):
        program = parse("log(1 + 2 * 3);")
        argument = program.statements[0].expr.args[0]
        self.assertIsInstance(argument, nodes.Binary)
        self.assertEqual(argument.op, "+")
        self.assertIsInstance(argument.right, nodes.Binary)
        self.assertEqual(argument.right.op, "*")

    def test_logical_precedence(self):
        program = parse("log(!true || false && true);")
        argument = program.statements[0].expr.args[0]
        self.assertEqual(argument.op, "||")
        self.assertIsInstance(argument.right, nodes.Binary)
        self.assertEqual(argument.right.op, "&&")

    def test_call_with_arguments(self):
        program = parse('log("a", 1, 2.5, true);')
        call = program.statements[0].expr
        self.assertIsInstance(call, nodes.Call)
        self.assertEqual(call.name, "log")
        self.assertEqual(len(call.args), 4)

    def test_call_without_arguments(self):
        call = parse("log();").statements[0].expr
        self.assertEqual(call.args, [])

    def test_if_else_if_else(self):
        program = parse(
            "if (1 > 2) { log(1); } else if (2 > 3) { log(2); } else { log(3); }"
        )
        statement = program.statements[0]
        self.assertIsInstance(statement, nodes.If)
        self.assertEqual(len(statement.branches), 2)
        self.assertIsNotNone(statement.else_body)

    def test_if_without_else(self):
        statement = parse("if (true) { }").statements[0]
        self.assertIsNone(statement.else_body)

    def test_while(self):
        statement = parse("while (true) { log(1); }").statements[0]
        self.assertIsInstance(statement, nodes.While)
        self.assertEqual(len(statement.body), 1)

    def test_missing_semicolon(self):
        with self.assertRaises(CeriumError) as caught:
            parse("int x = 1\nlog(x);")
        self.assertIn("expected ';'", caught.exception.message)
        self.assertEqual(caught.exception.line, 2)

    def test_missing_closing_brace(self):
        with self.assertRaises(CeriumError) as caught:
            parse("while (true) { log(1);")
        self.assertIn("expected '}'", caught.exception.message)

    def test_missing_condition_parentheses(self):
        with self.assertRaises(CeriumError):
            parse("if true { log(1); }")

    def test_expected_expression(self):
        with self.assertRaises(CeriumError) as caught:
            parse("int x = ;")
        self.assertIn("expected expression", caught.exception.message)

    def test_function_declaration(self):
        program = parse(
            "func add(int a, int b) -> int { return a + b; }"
        )
        function = program.statements[0]
        self.assertIsInstance(function, nodes.FuncDecl)
        self.assertEqual(function.name, "add")
        self.assertEqual(function.return_type, "int")
        self.assertEqual(
            [(param.type_name, param.name) for param in function.params],
            [("int", "a"), ("int", "b")],
        )
        self.assertIsInstance(function.body[0], nodes.Return)
        self.assertIsInstance(function.body[0].expr, nodes.Binary)

    def test_void_function(self):
        function = parse("func ping() -> void { return; }").statements[0]
        self.assertEqual(function.return_type, "void")
        self.assertIsNone(function.body[0].expr)

    def test_struct_declaration(self):
        program = parse("struct Point { int x; double y; }")
        struct = program.statements[0]
        self.assertIsInstance(struct, nodes.StructDecl)
        self.assertEqual(struct.name, "Point")
        self.assertEqual(
            [(field.type_name, field.name) for field in struct.fields],
            [("int", "x"), ("double", "y")],
        )

    def test_struct_literal_and_field_access(self):
        program = parse("Point p = Point { x = 1, y = 2 };")
        declaration = program.statements[0]
        self.assertIsInstance(declaration.expr, nodes.StructLit)
        self.assertEqual(declaration.expr.type_name, "Point")
        self.assertEqual(
            [field.name for field in declaration.expr.fields], ["x", "y"]
        )

        call = parse("log(p.x);").statements[0].expr
        self.assertIsInstance(call.args[0], nodes.FieldAccess)
        self.assertEqual(call.args[0].field, "x")

    def test_field_assignment(self):
        statement = parse("p.x = 5;").statements[0]
        self.assertIsInstance(statement, nodes.Assign)
        self.assertIsInstance(statement.target, nodes.FieldAccess)

    def test_for_loop(self):
        statement = parse(
            "for (int i = 0; i < 3; i = i + 1) { log(i); }"
        ).statements[0]
        self.assertIsInstance(statement, nodes.For)
        self.assertIsInstance(statement.init, nodes.VarDecl)
        self.assertEqual(statement.cond.op, "<")
        self.assertIsInstance(statement.update, nodes.Assign)
        self.assertEqual(len(statement.body), 1)

    def test_for_update_must_be_assignment(self):
        with self.assertRaises(CeriumError) as caught:
            parse("for (int i = 0; i < 3; i + 1) { log(i); }")
        self.assertIn("expected '='", caught.exception.message)

    def test_loop_break_continue(self):
        statement = parse("loop { break; continue; }").statements[0]
        self.assertIsInstance(statement, nodes.Loop)
        self.assertIsInstance(statement.body[0], nodes.Break)
        self.assertIsInstance(statement.body[1], nodes.Continue)

    def test_return_without_value(self):
        statement = parse("return;").statements[0]
        self.assertIsInstance(statement, nodes.Return)
        self.assertIsNone(statement.expr)

    def test_function_requires_arrow(self):
        with self.assertRaises(CeriumError) as caught:
            parse("func f() int { return 1; }")
        self.assertIn("expected '->'", caught.exception.message)

    def test_empty_struct_is_rejected(self):
        with self.assertRaises(CeriumError) as caught:
            parse("struct Empty { }")
        self.assertIn("at least one field", caught.exception.message)


if __name__ == "__main__":
    unittest.main()
