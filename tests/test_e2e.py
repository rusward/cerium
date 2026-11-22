import os
import shutil
import subprocess
import tempfile
import unittest

import support

GCC = shutil.which("gcc")


@unittest.skipUnless(GCC, "gcc is required for end-to-end tests")
class EndToEndTests(unittest.TestCase):
    def make_project(self):
        directory = tempfile.mkdtemp(prefix="hydrogenc-test-")
        self.addCleanup(shutil.rmtree, directory, True)
        return directory

    def build(self, source, name="prog.hy"):
        directory = self.make_project()
        source_path = os.path.join(directory, name)
        support.write(source_path, source)
        binary = os.path.join(directory, "prog")
        result = support.cli("build", source_path, "-o", binary)
        self.assertEqual(result.returncode, 0, result.stderr)
        return binary, directory, source_path

    def run_binary(self, binary, stdin=""):
        return subprocess.run(
            [binary], input=stdin, capture_output=True, text=True
        )

    def test_hello_example(self):
        binary, _, _ = self.build(support.read(os.path.join(support.EXAMPLES, "hello.hy")))
        result = self.run_binary(binary)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            result.stdout,
            "hello, world\n"
            "n = 42 pi = 3.14 ok = true\n"
            "big\n"
            "i = 0\n"
            "i = 1\n"
            "i = 2\n",
        )

    def test_types_example(self):
        binary, _, _ = self.build(support.read(os.path.join(support.EXAMPLES, "types.hy")))
        result = self.run_binary(binary)
        self.assertEqual(
            result.stdout,
            "count = 7\n"
            "ratio = 0.5\n"
            "ready = false\n"
            "label = types\n"
            "types: done\n",
        )

    def test_arithmetic_example(self):
        binary, _, _ = self.build(
            support.read(os.path.join(support.EXAMPLES, "arithmetic.hy"))
        )
        result = self.run_binary(binary)
        self.assertEqual(
            result.stdout,
            "a + b = 22\n"
            "a - b = 12\n"
            "a * b = 85\n"
            "a / b = 3\n"
            "a % b = 2\n"
            "x + y = 10\n"
            "x / y = 3\n"
            "x > y = true\n"
            "x == 7.5 = true\n",
        )

    def test_control_flow_example(self):
        binary, _, _ = self.build(
            support.read(os.path.join(support.EXAMPLES, "control_flow.hy"))
        )
        result = self.run_binary(binary)
        self.assertEqual(
            result.stdout,
            "B\n"
            "total = 15\n"
            "logic works\n"
            "inner = 0\n"
            "inner = 10\n",
        )

    def test_string_equality_uses_value_semantics(self):
        binary, _, _ = self.build(
            'string a = "hy"; string b = "d" + "rogen"; log(a + b == "hydrogen");\n'
        )
        result = self.run_binary(binary)
        self.assertEqual(result.stdout, "true\n")

    def test_integer_wraparound(self):
        binary, _, _ = self.build(
            "int big = 9223372036854775807; log(big + 1);\n"
        )
        result = self.run_binary(binary)
        self.assertEqual(result.stdout, "-9223372036854775808\n")

    def test_division_by_zero_is_a_runtime_error(self):
        directory = self.make_project()
        source_path = os.path.join(directory, "div_by_zero.hy")
        support.write(source_path, "int zero = 0;\nlog(10 / zero);\n")
        binary = os.path.join(directory, "prog")
        result = support.cli("build", source_path, "-o", binary)
        self.assertEqual(result.returncode, 0, result.stderr)

        run = self.run_binary(binary)
        self.assertEqual(run.returncode, 1)
        self.assertIn("runtime error: division by zero", run.stderr)
        self.assertIn("div_by_zero.hy:2", run.stderr)

    def test_modulo_by_zero_is_a_runtime_error(self):
        binary, _, _ = self.build("int zero = 0;\nlog(10 % zero);\n")
        run = self.run_binary(binary)
        self.assertEqual(run.returncode, 1)
        self.assertIn("runtime error: division by zero", run.stderr)

    def test_default_output_name(self):
        directory = self.make_project()
        source_path = os.path.join(directory, "hello.hy")
        support.write(source_path, 'log("ok");\n')
        result = support.cli("build", source_path, cwd=directory)
        self.assertEqual(result.returncode, 0, result.stderr)
        binary = os.path.join(directory, "hello")
        self.assertTrue(os.path.exists(binary))
        self.assertEqual(self.run_binary(binary).stdout, "ok\n")

    def test_check_accepts_valid_program(self):
        directory = self.make_project()
        source_path = os.path.join(directory, "valid.hy")
        support.write(source_path, "int x = 1; log(x);\n")
        result = support.cli("check", source_path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_check_reports_type_error_location(self):
        directory = self.make_project()
        source_path = os.path.join(directory, "bad.hy")
        support.write(source_path, 'int x = "no";\n')
        result = support.cli("check", source_path)
        self.assertEqual(result.returncode, 1)
        self.assertIn(f"{source_path}:1:5: error:", result.stderr)
        self.assertIn("cannot initialize variable 'x'", result.stderr)
        self.assertIn("^", result.stderr)

    def test_syntax_error_location(self):
        directory = self.make_project()
        source_path = os.path.join(directory, "bad.hy")
        support.write(source_path, "int x = 1\nlog(x);\n")
        result = support.cli("check", source_path)
        self.assertEqual(result.returncode, 1)
        self.assertIn(f"{source_path}:2:1: error:", result.stderr)
        self.assertIn("expected ';'", result.stderr)

    def test_emit_c_to_stdout(self):
        directory = self.make_project()
        source_path = os.path.join(directory, "prog.hy")
        support.write(source_path, "int x = 1; log(x);\n")
        result = support.cli("emit-c", source_path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("#include <stdint.h>", result.stdout)
        self.assertIn("int main(void)", result.stdout)
        self.assertIn('#line 1 "', result.stdout)

    def test_build_with_emit_c(self):
        directory = self.make_project()
        source_path = os.path.join(directory, "prog.hy")
        support.write(source_path, 'log("ok");\n')
        binary = os.path.join(directory, "prog")
        c_path = os.path.join(directory, "prog.c")
        result = support.cli(
            "build", source_path, "-o", binary, "--emit-c", c_path
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(os.path.exists(c_path))
        self.assertIn("hy_print_string", support.read(c_path))

    def test_missing_c_compiler(self):
        directory = self.make_project()
        source_path = os.path.join(directory, "prog.hy")
        support.write(source_path, 'log("ok");\n')
        result = support.cli(
            "build",
            source_path,
            "-o",
            os.path.join(directory, "prog"),
            "--cc",
            "definitely-not-a-compiler",
        )
        self.assertEqual(result.returncode, 3)
        self.assertIn("not found", result.stderr)

    def test_unknown_function_is_rejected_before_gcc(self):
        directory = self.make_project()
        source_path = os.path.join(directory, "prog.hy")
        support.write(source_path, "println(1);\n")
        result = support.cli("build", source_path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("unknown function 'println'", result.stderr)

    def test_functions_example(self):
        binary, _, _ = self.build(
            support.read(os.path.join(support.EXAMPLES, "functions.hy"))
        )
        result = self.run_binary(binary)
        self.assertEqual(
            result.stdout,
            "hello, hydrogen\n"
            "3 + 4 = 7\n"
            "5! = 120\n",
        )

    def test_structs_example(self):
        binary, _, _ = self.build(
            support.read(os.path.join(support.EXAMPLES, "structs.hy"))
        )
        result = self.run_binary(binary)
        self.assertEqual(
            result.stdout,
            "origin = 0 0\n"
            "p = 3 4\n"
            "length^2 = 25\n"
            "p.x = 6\n"
            "Ada is active\n"
            "copy.x = 6\n"
            "direct = 2\n",
        )

    def test_loops_example(self):
        binary, _, _ = self.build(
            support.read(os.path.join(support.EXAMPLES, "loops.hy"))
        )
        result = self.run_binary(binary)
        self.assertEqual(
            result.stdout,
            "sum = 15\n"
            "evens = 12\n"
            "n = 3\n",
        )

    def test_structs_passed_and_returned_by_value(self):
        binary, _, _ = self.build(
            """
            struct Pair {
                int a;
                int b;
            }

            func swap(Pair p) -> Pair {
                return Pair { a = p.b, b = p.a };
            }

            Pair p = swap(Pair { a = 1, b = 2 });
            log(p.a, p.b);
            log(swap(p).a);
            """
        )
        result = self.run_binary(binary)
        self.assertEqual(result.stdout, "2 1\n1\n")

    def test_for_continue_runs_update(self):
        binary, _, _ = self.build(
            """
            int total = 0;
            for (int i = 0; i < 5; i = i + 1) {
                if (i % 2 == 0) {
                    continue;
                }
                total = total + i;
            }
            log(total);
            """
        )
        result = self.run_binary(binary)
        self.assertEqual(result.stdout, "4\n")

    def test_function_returns_struct_field(self):
        binary, _, _ = self.build(
            """
            struct Point { int x; int y; }
            func make(int x, int y) -> Point {
                return Point { x = x, y = y };
            }
            log(make(7, 9).x, make(7, 9).y);
            """
        )
        result = self.run_binary(binary)
        self.assertEqual(result.stdout, "7 9\n")

    def test_forward_declarations_of_functions_and_structs(self):
        binary, _, _ = self.build(
            """
            Point p = make(2, 3);
            struct Point { int x; int y; }
            func make(int x, int y) -> Point {
                return Point { x = x, y = y };
            }
            log(p.x, p.y);
            """
        )
        result = self.run_binary(binary)
        self.assertEqual(result.stdout, "2 3\n")

    def test_struct_parameters_are_passed_by_value(self):
        binary, _, _ = self.build(
            """
            struct Point { int x; int y; }
            func bump(Point p) -> Point {
                p.x = p.x + 1;
                return p;
            }
            Point p = Point { x = 1, y = 2 };
            Point q = bump(p);
            log(p.x, q.x);
            """
        )
        result = self.run_binary(binary)
        self.assertEqual(result.stdout, "1 2\n")

    def test_input_builtins(self):
        binary, _, _ = self.build(
            'string name = input("name? ");'
            'int age = inputInt("age? ");'
            'double height = inputDouble("height? ");'
            'bool ok = inputBool("ok? ");'
            'log("hello,", name);'
            "log(age, height, ok);"
        )
        result = self.run_binary(
            binary, stdin="Ada\n42\n1.75\ntrue\n"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout,
            "name? age? height? ok? hello, Ada\n"
            "42 1.75 true\n",
        )

    def test_input_example(self):
        binary, _, _ = self.build(
            support.read(os.path.join(support.EXAMPLES, "input.hy"))
        )
        result = self.run_binary(
            binary, stdin="Ada\n36\n1.8\ntrue\n"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout,
            "Name: Age: Height (m): Developer? (true/false): "
            "hello, Ada\n"
            "age = 36 height = 1.8 developer = true\n",
        )

    def test_input_preserves_spaces_and_strips_crlf(self):
        binary, _, _ = self.build(
            'string text = input(); log("[" + text + "]");'
        )
        result = self.run_binary(binary, stdin="  hello world  \r\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "[  hello world  ]\n")

    def test_input_empty_line_is_a_valid_string(self):
        binary, _, _ = self.build(
            'string text = input(); log("empty:", text == "");'
        )
        result = self.run_binary(binary, stdin="\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "empty: true\n")

    def test_input_int_accepts_surrounding_whitespace(self):
        binary, _, _ = self.build("int n = inputInt(); log(n + 1);")
        result = self.run_binary(binary, stdin=" 41 \n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "42\n")

    def test_input_double_accepts_exponent(self):
        binary, _, _ = self.build("double d = inputDouble(); log(d);")
        result = self.run_binary(binary, stdin="1.5e2\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "150\n")

    def test_input_invalid_int_is_a_runtime_error(self):
        directory = self.make_project()
        source_path = os.path.join(directory, "input_bad.hy")
        support.write(source_path, "int n = inputInt();\nlog(n);\n")
        binary = os.path.join(directory, "prog")
        result = support.cli("build", source_path, "-o", binary)
        self.assertEqual(result.returncode, 0, result.stderr)

        run = self.run_binary(binary, stdin="12abc\n")
        self.assertEqual(run.returncode, 1)
        self.assertIn("runtime error: invalid int input: '12abc'", run.stderr)
        self.assertIn("input_bad.hy:1", run.stderr)

    def test_input_invalid_bool_is_a_runtime_error(self):
        binary, _, _ = self.build("bool b = inputBool(); log(b);")
        run = self.run_binary(binary, stdin="yes\n")
        self.assertEqual(run.returncode, 1)
        self.assertIn("runtime error: invalid bool input: 'yes'", run.stderr)

    def test_input_unexpected_eof_is_a_runtime_error(self):
        binary, _, _ = self.build("string s = input(); log(s);")
        run = self.run_binary(binary, stdin="")
        self.assertEqual(run.returncode, 1)
        self.assertIn("runtime error: unexpected end of input", run.stderr)


class CliTests(unittest.TestCase):
    def test_version(self):
        result = support.run_cli("--version")
        self.assertEqual(result.returncode, 0)
        self.assertTrue(result.stdout.startswith("hydrogenc "))

    def test_no_arguments(self):
        result = support.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertIn("usage: hydrogenc", result.stderr)

    def test_unknown_command(self):
        result = support.run_cli("frobnicate")
        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown command", result.stderr)

    def test_missing_source_argument(self):
        result = support.run_cli("build")
        self.assertEqual(result.returncode, 2)
        self.assertIn("missing input file", result.stderr)

    def test_invalid_option_for_check(self):
        result = support.run_cli("check", "--static", "x.hy")
        self.assertEqual(result.returncode, 2)
        self.assertIn("not valid for 'check'", result.stderr)

    def test_help(self):
        result = support.run_cli("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage: hydrogenc", result.stdout)


if __name__ == "__main__":
    unittest.main()
