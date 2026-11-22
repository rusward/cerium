import unittest

import support  # noqa: F401

from hydrogenc.checker import TypeChecker
from hydrogenc.errors import HydrogenErrors
from hydrogenc.lexer import Lexer
from hydrogenc.parser import Parser


def parse(text):
    tokens = Lexer(text, "test.hy").tokenize()
    return Parser(tokens, "test.hy").parse()


def check(text):
    return TypeChecker("test.hy").check(parse(text))


def error_messages(text):
    try:
        check(text)
    except HydrogenErrors as errors:
        return [diagnostic.message for diagnostic in errors.errors]
    raise AssertionError("expected type checking to fail")


class CheckerTests(unittest.TestCase):
    def test_valid_program(self):
        check(
            """
            int x = 1;
            x = x + 2;
            log(x);
            """
        )

    def test_valid_string_program(self):
        check(
            """
            string a = "hello";
            string b = a + " world";
            log(b);
            """
        )

    def test_valid_control_flow(self):
        check(
            """
            int i = 0;
            while (i < 3) {
                int next = i + 1;
                i = next;
            }
            if (i == 3) { log("done"); } else { log("pending"); }
            """
        )

    def test_valid_boolean_logic(self):
        check("bool a = true; bool b = !a; log(a && !b || false);")

    def test_initializer_type_mismatch(self):
        messages = error_messages('int n = "text";')
        self.assertTrue(
            any(
                "cannot initialize variable 'n'" in message
                and "'int'" in message
                and "'string'" in message
                for message in messages
            ),
            messages,
        )

    def test_assignment_type_mismatch(self):
        messages = error_messages("int n = 1; n = 2.5;")
        self.assertTrue(
            any("cannot assign a value of type 'double'" in message for message in messages),
            messages,
        )

    def test_undefined_variable(self):
        messages = error_messages("log(missing);")
        self.assertEqual(messages, ["undefined variable 'missing'"])

    def test_shadowing_outer_scope(self):
        messages = error_messages("int x = 1; if (true) { int x = 2; log(x); }")
        self.assertTrue(any("outer scope" in message for message in messages), messages)

    def test_duplicate_in_same_scope(self):
        messages = error_messages("int x = 1; int x = 2;")
        self.assertTrue(any("already declared" in message for message in messages), messages)

    def test_block_variable_not_visible_outside(self):
        messages = error_messages("if (true) { int inner = 1; } log(inner);")
        self.assertEqual(messages, ["undefined variable 'inner'"])

    def test_condition_must_be_bool(self):
        messages = error_messages("if (1) { log(1); }")
        self.assertEqual(messages, ["condition must be of type 'bool', got 'int'"])

    def test_while_condition_must_be_bool(self):
        messages = error_messages('while ("yes") { log(1); }')
        self.assertTrue(any("condition must be of type 'bool'" in m for m in messages), messages)

    def test_unknown_function(self):
        messages = error_messages("print(1);")
        self.assertEqual(messages, ["unknown function 'print'"])

    def test_expression_statement_must_be_call(self):
        messages = error_messages("1 + 2;")
        self.assertEqual(messages, ["expression statements must be function calls"])

    def test_mixed_numeric_arithmetic(self):
        messages = error_messages("int n = 1; double d = 2.5; log(n + d);")
        self.assertTrue(any("operator '+' cannot be applied" in m for m in messages), messages)

    def test_modulo_requires_int(self):
        messages = error_messages("log(5.0 % 2.0);")
        self.assertTrue(any("operator '%' cannot be applied" in m for m in messages), messages)

    def test_ordering_strings_rejected(self):
        messages = error_messages('log("a" < "b");')
        self.assertTrue(any("operator '<' cannot be applied" in m for m in messages), messages)

    def test_string_equality_allowed(self):
        check('log("a" == "a"); log("a" != "b");')

    def test_log_result_cannot_be_used(self):
        messages = error_messages('log(log("nested"));')
        self.assertTrue(any("type 'void'" in message for message in messages), messages)

    def test_integer_literal_out_of_range(self):
        messages = error_messages("log(9223372036854775808);")
        self.assertTrue(any("out of range" in message for message in messages), messages)

    def test_multiple_errors_are_collected(self):
        messages = error_messages("int a = true; int b = false; log(a + b);")
        self.assertGreaterEqual(len(messages), 1)

    def test_valid_functions_and_recursion(self):
        check(
            """
            func factorial(int n) -> int {
                if (n <= 1) { return 1; }
                return n * factorial(n - 1);
            }
            log(factorial(5));
            """
        )

    def test_function_used_before_declaration(self):
        check(
            """
            log(twice(21));
            func twice(int x) -> int { return x * 2; }
            """
        )

    def test_void_function(self):
        check('func ping(string name) -> void { log(name); } ping("hy");')

    def test_discarding_non_void_result_is_allowed(self):
        check("func one() -> int { return 1; } one();")

    def test_missing_return_path(self):
        messages = error_messages(
            "func absolute(int x) -> int { if (x >= 0) { return x; } }"
        )
        self.assertTrue(
            any("must return a value on all paths" in m for m in messages),
            messages,
        )

    def test_if_else_that_returns_everywhere_is_valid(self):
        check(
            "func sign(int x) -> int {"
            "  if (x >= 0) { return 1; } else { return -1; }"
            "}"
        )

    def test_return_type_mismatch(self):
        messages = error_messages('func f() -> int { return "no"; }')
        self.assertTrue(
            any("cannot return a value of type 'string'" in m for m in messages),
            messages,
        )

    def test_bare_return_in_non_void_function(self):
        messages = error_messages("func f() -> int { return; }")
        self.assertTrue(
            any("must return a value" in m for m in messages), messages
        )

    def test_value_return_in_void_function(self):
        messages = error_messages("func f() -> void { return 1; }")
        self.assertTrue(
            any("cannot return a value" in m for m in messages), messages
        )

    def test_return_outside_function(self):
        messages = error_messages("return 1;")
        self.assertEqual(messages, ["'return' outside of a function"])

    def test_break_outside_loop(self):
        messages = error_messages("break;")
        self.assertEqual(messages, ["'break' outside of a loop"])

    def test_continue_outside_loop(self):
        messages = error_messages("continue;")
        self.assertEqual(messages, ["'continue' outside of a loop"])

    def test_break_and_continue_inside_for(self):
        check(
            "for (int i = 0; i < 3; i = i + 1) {"
            "  if (i == 1) { continue; }"
            "  if (i == 2) { break; }"
            "}"
        )

    def test_for_init_variable_is_scoped_to_loop(self):
        messages = error_messages(
            "for (int i = 0; i < 1; i = i + 1) { log(i); } log(i);"
        )
        self.assertEqual(messages, ["undefined variable 'i'"])

    def test_for_update_type_mismatch(self):
        messages = error_messages(
            "int i = 0; for (i = 0; i < 3; i = 1.5) { log(i); }"
        )
        self.assertTrue(
            any("cannot assign a value of type 'double'" in m for m in messages),
            messages,
        )

    def test_unknown_function_call(self):
        messages = error_messages("missing(1);")
        self.assertEqual(messages, ["unknown function 'missing'"])

    def test_function_arity(self):
        messages = error_messages(
            "func add(int a, int b) -> int { return a + b; } log(add(1));"
        )
        self.assertTrue(
            any("expects 2 arguments, got 1" in m for m in messages), messages
        )

    def test_function_argument_type(self):
        messages = error_messages(
            'func add(int a, int b) -> int { return a + b; } log(add(1, "x"));'
        )
        self.assertTrue(
            any(
                "argument 2 of function 'add' must have type 'int'" in m
                for m in messages
            ),
            messages,
        )

    def test_duplicate_function(self):
        messages = error_messages(
            "func f() -> int { return 1; } func f() -> int { return 2; }"
        )
        self.assertTrue(
            any("function 'f' is already declared" in m for m in messages),
            messages,
        )

    def test_duplicate_parameter(self):
        messages = error_messages(
            "func f(int a, int a) -> int { return a; }"
        )
        self.assertTrue(
            any("variable 'a' is already declared" in m for m in messages),
            messages,
        )

    def test_builtin_log_cannot_be_redefined(self):
        messages = error_messages('func log() -> void { }')
        self.assertTrue(
            any("cannot declare function 'log'" in m for m in messages),
            messages,
        )

    def test_function_cannot_see_top_level_variables(self):
        messages = error_messages(
            "int x = 1; func f() -> int { return x; }"
        )
        self.assertEqual(messages, ["undefined variable 'x'"])

    def test_valid_structs(self):
        check(
            """
            struct Point { int x; int y; }
            struct User { string name; bool active; }

            func make(int x, int y) -> Point {
                return Point { x = x, y = y };
            }

            Point p = make(1, 2);
            p.x = p.x + 10;
            User u = User { name = "Ada", active = true };
            log(p.x, p.y, u.name, u.active);
            """
        )

    def test_struct_declared_after_use(self):
        check(
            "Point p = Point { x = 1, y = 2 }; "
            "struct Point { int x; int y; } "
            "log(p.x);"
        )

    def test_unknown_struct_type(self):
        messages = error_messages("Point p = Point { x = 1 };")
        self.assertTrue(
            any("unknown type 'Point'" in m for m in messages), messages
        )
        self.assertTrue(
            any("unknown struct 'Point'" in m for m in messages), messages
        )

    def test_struct_field_must_be_scalar(self):
        messages = error_messages(
            "struct A { int x; } struct B { A a; }"
        )
        self.assertTrue(
            any("must have a scalar type" in m for m in messages), messages
        )

    def test_duplicate_struct_field(self):
        messages = error_messages("struct Point { int x; int x; }")
        self.assertTrue(
            any("field 'x' is already declared" in m for m in messages),
            messages,
        )

    def test_struct_field_type_mismatch(self):
        messages = error_messages(
            'struct Point { int x; } Point p = Point { x = "no" };'
        )
        self.assertTrue(
            any("must have type 'int', got 'string'" in m for m in messages),
            messages,
        )

    def test_unknown_struct_field_in_literal(self):
        messages = error_messages(
            "struct Point { int x; } Point p = Point { x = 1, z = 2 };"
        )
        self.assertTrue(
            any("has no field 'z'" in m for m in messages), messages
        )

    def test_missing_struct_field_in_literal(self):
        messages = error_messages(
            "struct Point { int x; int y; } Point p = Point { x = 1 };"
        )
        self.assertTrue(
            any("field 'y' of struct 'Point' is not initialized" in m for m in messages),
            messages,
        )

    def test_duplicate_struct_field_in_literal(self):
        messages = error_messages(
            "struct Point { int x; } Point p = Point { x = 1, x = 2 };"
        )
        self.assertTrue(
            any("initialized more than once" in m for m in messages), messages
        )

    def test_field_access_on_scalar(self):
        messages = error_messages("int x = 1; log(x.y);")
        self.assertTrue(
            any("type 'int' has no fields" in m for m in messages), messages
        )

    def test_field_assignment_type_mismatch(self):
        messages = error_messages(
            'struct Point { int x; } Point p = Point { x = 1 }; p.x = "no";'
        )
        self.assertTrue(
            any(
                "cannot assign a value of type 'string' to field 'p.x'" in m
                for m in messages
            ),
            messages,
        )

    def test_struct_cannot_be_logged(self):
        messages = error_messages(
            "struct Point { int x; } Point p = Point { x = 1 }; log(p);"
        )
        self.assertTrue(
            any("cannot pass struct 'Point' to function 'log'" in m for m in messages),
            messages,
        )


if __name__ == "__main__":
    unittest.main()
