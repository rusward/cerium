"""Command-line interface for the Cerium compiler."""

import os
import shutil
import subprocess
import sys
import tempfile

from . import __version__
from .checker import TypeChecker
from .codegen_c import CCodegen
from .errors import Diagnostic, CeriumError, CeriumErrors, render
from .lexer import Lexer
from .parser import Parser

USAGE = """usage: ceriumc <command> [options] <file.ce>

commands:
  build     compile a .ce program into a native executable
  check     parse and type-check without producing a binary
  emit-c    print the generated C source

options:
  -o, --output PATH   output path (binary for build, C file for emit-c)
  --emit-c PATH       also write the generated C source (build)
  --keep-c            keep the temporary C file and print its path
  --static            link the executable statically
  --cc NAME           C compiler to use (default: auto-detect)
  -h, --help          show this help
  --version           show version
"""


def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    try:
        return run(list(argv))
    except KeyboardInterrupt:
        return 130
    except BrokenPipeError:
        return 0


def run(argv) -> int:
    if not argv:
        print(USAGE, file=sys.stderr)
        return 2

    command = argv[0]

    if command in ("-h", "--help", "help"):
        print(USAGE)
        return 0

    if command == "--version":
        print(f"ceriumc {__version__}")
        return 0

    if command not in ("build", "check", "emit-c"):
        return usage_error(f"unknown command '{command}'")

    if "-h" in argv[1:] or "--help" in argv[1:]:
        print(USAGE)
        return 0

    options, message = parse_options(argv[1:], command)
    if message is not None:
        return usage_error(message)

    source_path = options["source"]
    source = read_source(source_path)
    if source is None:
        return 1

    try:
        c_source = compile_to_c(source, source_path)
    except CeriumError as error:
        diagnostic = Diagnostic(error.message, error.line, error.col)
        sys.stderr.write(render(source_path, source, diagnostic) + "\n")
        return 1
    except CeriumErrors as errors:
        for diagnostic in sorted(errors.errors, key=lambda d: (d.line, d.col)):
            sys.stderr.write(render(source_path, source, diagnostic) + "\n")
        return 1

    if command == "check":
        return 0

    if command == "emit-c":
        output = options["output"]
        if output is None:
            sys.stdout.write(c_source)
            return 0
        return write_text(output, c_source)

    return build_binary(c_source, source_path, options)


# -- compilation ---------------------------------------------------------


def compile_to_c(source: str, source_path: str) -> str:
    tokens = Lexer(source, source_path).tokenize()
    program = Parser(tokens, source_path).parse()
    checker = TypeChecker(source_path)
    types = checker.check(program)
    return CCodegen(program, types, source_path).generate()


def read_source(path: str):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError as error:
        reason = error.strerror or str(error)
        print(f"ceriumc: error: cannot read '{path}': {reason}", file=sys.stderr)
        return None


def write_text(path: str, text: str) -> int:
    try:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
    except OSError as error:
        reason = error.strerror or str(error)
        print(f"ceriumc: error: cannot write '{path}': {reason}", file=sys.stderr)
        return 1
    return 0


def build_binary(c_source: str, source_path: str, options) -> int:
    output = options["output"] or default_output(source_path)
    if os.name == "nt" and options["output"] and not os.path.splitext(output)[1]:
        output += ".exe"

    compiler = options["cc"] or find_c_compiler()
    if compiler is None:
        print(
            "ceriumc: error: no supported C compiler found; "
            "install MinGW-w64 or LLVM clang and add it to PATH, "
            "or pass --cc PATH",
            file=sys.stderr,
        )
        return 3

    if os.name == "nt" and os.path.basename(compiler).lower() in ("cl", "cl.exe"):
        print(
            "ceriumc: error: MSVC cl is not supported; "
            "use MinGW-w64 gcc or LLVM clang",
            file=sys.stderr,
        )
        return 3

    if options["static"] and sys.platform == "darwin":
        print(
            "ceriumc: error: static linking is not supported on macOS",
            file=sys.stderr,
        )
        return 3

    if options["emit_c"] is not None:
        status = write_text(options["emit_c"], c_source)
        if status != 0:
            return status

    temporary = tempfile.TemporaryDirectory(prefix="ceriumc-")
    if options["keep_c"]:
        directory = tempfile.mkdtemp(prefix="ceriumc-")
        temporary.cleanup()
        cleanup = None
    else:
        directory = temporary.name
        cleanup = temporary

    try:
        c_path = os.path.join(directory, "program.c")
        with open(c_path, "w", encoding="utf-8") as handle:
            handle.write(c_source)

        command = [compiler, "-std=c99", "-O2"]
        if options["static"]:
            command.append("-static")
        command.extend([c_path, "-o", output])

        try:
            result = subprocess.run(
                command, capture_output=True, text=True, errors="replace"
            )
        except FileNotFoundError:
            print(
                f"ceriumc: error: C compiler '{compiler}' not found",
                file=sys.stderr,
            )
            return 3
        except OSError as error:
            print(
                f"ceriumc: error: cannot run C compiler: {error}",
                file=sys.stderr,
            )
            return 3

        if result.returncode != 0:
            if result.stderr:
                sys.stderr.write(result.stderr)
                if not result.stderr.endswith("\n"):
                    sys.stderr.write("\n")
            print("ceriumc: error: C compilation failed", file=sys.stderr)
            if options["keep_c"]:
                print(f"ceriumc: kept C source at {c_path}", file=sys.stderr)
            return 3

        if options["keep_c"]:
            print(f"ceriumc: kept C source at {c_path}", file=sys.stderr)
        return 0
    finally:
        if cleanup is not None:
            cleanup.cleanup()


def find_c_compiler():
    configured = os.environ.get("CC")
    if configured:
        return configured

    if sys.platform == "darwin":
        candidates = ("clang", "gcc", "cc")
    else:
        candidates = ("gcc", "clang", "cc")

    for candidate in candidates:
        if shutil.which(candidate):
            return candidate
    return None


def default_output(source_path: str) -> str:
    stem = os.path.splitext(os.path.basename(source_path))[0]
    if os.name == "nt":
        return (stem or "a") + ".exe"
    return stem or "a.out"


# -- option parsing ------------------------------------------------------


def parse_options(args, command: str):
    options = {
        "source": None,
        "output": None,
        "emit_c": None,
        "keep_c": False,
        "static": False,
        "cc": None,
    }

    allowed = {
        "build": {"output", "emit_c", "keep_c", "static", "cc"},
        "check": set(),
        "emit-c": {"output"},
    }[command]

    index = 0
    while index < len(args):
        argument = args[index]

        if argument in ("-o", "--output"):
            if "output" not in allowed:
                return options, f"option '{argument}' is not valid for '{command}'"
            if index + 1 >= len(args):
                return options, f"option '{argument}' requires a value"
            options["output"] = args[index + 1]
            index += 2
            continue

        if argument == "--emit-c":
            if "emit_c" not in allowed:
                return options, f"option '{argument}' is not valid for '{command}'"
            if index + 1 >= len(args):
                return options, "option '--emit-c' requires a value"
            options["emit_c"] = args[index + 1]
            index += 2
            continue

        if argument == "--cc":
            if "cc" not in allowed:
                return options, f"option '{argument}' is not valid for '{command}'"
            if index + 1 >= len(args):
                return options, "option '--cc' requires a value"
            options["cc"] = args[index + 1]
            index += 2
            continue

        if argument == "--keep-c":
            if "keep_c" not in allowed:
                return options, f"option '{argument}' is not valid for '{command}'"
            options["keep_c"] = True
            index += 1
            continue

        if argument == "--static":
            if "static" not in allowed:
                return options, f"option '{argument}' is not valid for '{command}'"
            options["static"] = True
            index += 1
            continue

        if argument.startswith("-"):
            return options, f"unknown option '{argument}'"

        if options["source"] is not None:
            return options, "only one input file may be specified"
        options["source"] = argument
        index += 1

    if options["source"] is None:
        return options, "missing input file"

    return options, None


def usage_error(message: str) -> int:
    print(f"ceriumc: error: {message}", file=sys.stderr)
    print(USAGE, file=sys.stderr)
    return 2
