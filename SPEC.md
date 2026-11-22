# Hydrogen language specification

Version 0.2 (MVP).

## 1. Overview

Hydrogen is a small statically typed language. Programs are stored in `.hy` files and compiled
by `hydrogenc` into native executables. The compiler parses the source, verifies types, emits
C99, and invokes a C compiler.

The syntax is C#-like but reduced, with a few of its own touches:

- functions are introduced by `func` and declare the return type with `->`;
- struct values are built with literals without `new`: `Point { x = 1, y = 2 }`;
- loops are `while`, C-style `for`, and infinite `loop`;
- braces are mandatory, semicolons terminate simple statements.

## 2. Lexical structure

- Source is UTF-8. Whitespace is insignificant; line breaks do not terminate statements.
- Identifiers: `[A-Za-z_][A-Za-z0-9_]*`. Keywords are reserved:
  `int`, `double`, `bool`, `string`, `void`, `func`, `struct`, `return`, `if`, `else`,
  `while`, `for`, `loop`, `break`, `continue`, `true`, `false`.
- Integer literals: decimal digits only, e.g. `0`, `42`.
- Floating literals: digits `.` digits, e.g. `3.14`, `0.5`. Exponent notation is not supported.
- String literals use double quotes. Supported escapes: `\n`, `\t`, `\r`, `\\`, `\"`.
  A literal newline inside a string is an error.
- Comments: `//` to end of line and `/* ... */`. Block comments do not nest.
- Punctuation and operators:
  `== != <= >= && || -> + - * / % = < > ! . ( ) { } ; ,`

## 3. Grammar

```
program     := top_level*
top_level   := struct_decl | func_decl | stmt

struct_decl := 'struct' IDENT '{' field_decl+ '}'
field_decl  := scalar_type IDENT ';'
scalar_type := 'int' | 'double' | 'bool' | 'string'

func_decl   := 'func' IDENT '(' param_list? ')' '->' return_type block
param_list  := param (',' param)*
param       := type IDENT
return_type := type | 'void'
type        := scalar_type | IDENT

stmt        := var_decl | assign_stmt | if_stmt | while_stmt | for_stmt
             | loop_stmt | break_stmt | continue_stmt | return_stmt
             | expr_stmt

var_decl    := type IDENT '=' expr ';'
assign_stmt := lvalue '=' expr ';'
lvalue      := IDENT ('.' IDENT)*

if_stmt     := 'if' '(' expr ')' block ('else' 'if' '(' expr ')' block)* ('else' block)?
while_stmt  := 'while' '(' expr ')' block
for_stmt    := 'for' '(' (var_decl | assign_stmt) expr ';' assign_expr ')' block
loop_stmt   := 'loop' block
break_stmt  := 'break' ';'
continue_stmt := 'continue' ';'
return_stmt := 'return' expr? ';'
block       := '{' stmt* '}'
expr_stmt   := expr ';'

assign_expr := lvalue '=' expr

expr        := logic_or
logic_or    := logic_and ('||' logic_and)*
logic_and   := equality ('&&' equality)*
equality    := comparison (('==' | '!=') comparison)*
comparison  := term (('<' | '<=' | '>' | '>=') term)*
term        := factor (('+' | '-') factor)*
factor      := unary (('*' | '/' | '%') unary)*
unary       := ('-' | '!') unary | postfix
postfix     := primary ('.' IDENT)*
primary     := INT | DOUBLE | STRING | 'true' | 'false'
             | IDENT | call | struct_lit | '(' expr ')'
call        := IDENT '(' (expr (',' expr)*)? ')'
struct_lit  := IDENT '{' (field_init (',' field_init)*)? '}'
field_init  := IDENT '=' expr
```

Operator precedence, low to high: `||`, `&&`, equality, comparison, `+ -`, `* / %`, unary,
postfix field access.

## 4. Types

| Type     | Representation            | Notes                                  |
|----------|---------------------------|----------------------------------------|
| `int`    | signed 64-bit             | wraps on overflow (two's complement)   |
| `double` | IEEE-754 binary64         | inf/NaN allowed, division not checked  |
| `bool`   | `true` / `false`          | no truthiness conversions              |
| `string` | immutable UTF-8 bytes     | concatenation allocates, freed at exit |

Struct names introduce additional value types. There are no implicit conversions. `int + double`
is a type error; there is no cast syntax in the MVP.

Every variable declaration and assignment must preserve its declared type. Variables are
mutable, but their type is fixed at declaration.

### Structs

```
struct Point {
    int x;
    int y;
}
```

- Struct declarations are only allowed at top level.
- Fields must have scalar types (`int`, `double`, `bool`, `string`); nested struct fields are
  not supported in v0.2.
- Field names must be unique within a struct; at least one field is required.
- Struct types can be used for variables, parameters, and return types.
- Struct values are passed to functions and returned from them by value.
- Struct literals must initialize every field exactly once; field order is free.
- Field access: `p.x`; field assignment: `p.x = 5;`.
- Structs cannot be compared with `==`/`!=` and cannot be passed to `log`; access fields instead.
- `Point copy = p;` copies the struct by value.

## 5. Functions

```
func add(int a, int b) -> int {
    return a + b;
}

func greet(string name) -> void {
    log("hello,", name);
}
```

- Functions are declared only at top level. No nested functions, no overloading.
- The return type follows `->`; use `void` when there is no result.
- All function signatures are collected before bodies are checked, so functions can be called
  before their declaration, including mutual recursion.
- Function bodies have their own scope. Parameters share it with the outermost function block.
  Top-level variables are not visible inside functions.
- `log` is built in and cannot be redefined as a function.
- A call whose result is not needed may be used as a statement, even for non-void functions.

### Return

- `return expr;` returns a value; `return;` is only valid in a `void` function.
- A non-void function must return a value on every path. The check is conservative:
  `if`/`else` chains are analysed, loops are not treated as guaranteed returns. A trailing
  `return` (or an `if`/`else` where all branches return) satisfies the check.
- `return` outside a function is an error.

### Recursion

Supported naturally:

```
func factorial(int n) -> int {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}
```

## 6. Statements

### Variable declarations and assignment

```
int x = 1;
x = x + 1;
```

Initialization is mandatory. `x = 1;` never declares a variable: the name must already exist.
The type of the variable is fixed.

### Blocks and scopes

- Blocks introduce scopes; a variable declared in a block is not visible outside it.
- Declaring a name that already exists in the current or an outer scope is an error.
- Reading a variable before its declaration is an error.
- Struct and function declarations are top-level only; nesting them is an error.

### `if` / `else if` / `else`

```
if (score >= 90) {
    log("A");
} else if (score >= 70) {
    log("B");
} else {
    log("C");
}
```

Conditions must be `bool`; braces are mandatory even for a single statement.

### `while`

```
while (i < 3) {
    i = i + 1;
}
```

### `for`

```
for (int i = 1; i <= 5; i = i + 1) {
    log(i);
}
```

- The init clause is either a variable declaration with initializer or an assignment.
- The condition is required and must be `bool`.
- The update clause must be an assignment to a variable or a field, e.g. `i = i + 1` or
  `p.x = p.x + 1`.
- A variable declared in the init clause is scoped to the loop.
- `break` and `continue` are supported; `continue` still runs the update clause.

### `loop`

```
int n = 0;
loop {
    n = n + 1;
    if (n == 3) {
        break;
    }
}
```

`loop` is an infinite loop; it is normally exited with `break`.

### `break` / `continue`

Only valid inside `while`, `for`, or `loop`. `break` outside a loop is an error, as is
`continue` outside a loop.

### Expression statements

Only function calls may be used as standalone statements; `1 + 2;` is an error.

## 7. Built-in `log`

```
log(expr, ...);
```

- Variadic; accepts any number of arguments of scalar types.
- Arguments are printed to stdout separated by a single space, followed by `\n`.
- `int` prints as a decimal number, `double` with `%g`, `bool` as `true`/`false`,
  `string` as-is.
- `log()` prints an empty line.
- `log` returns `void`; its result cannot be used in an expression.
- Struct values cannot be passed directly to `log`.

## 8. Operators

| Operator        | Operand types            | Result  |
|-----------------|--------------------------|---------|
| `+`             | `int`, `double`, `string`| same    |
| `- * /`         | `int`, `double`          | same    |
| `%`             | `int`                    | `int`   |
| `< <= > >=`     | `int`, `double`          | `bool`  |
| `== !=`         | any single scalar type   | `bool`  |
| `&& \|\|`       | `bool`                   | `bool`  |
| unary `-`       | `int`, `double`          | same    |
| unary `!`       | `bool`                   | `bool`  |
| `.`             | struct value             | field   |

- `int` division and `%` truncate toward zero.
- Integer division/modulo by zero raises a runtime error and exits with code 1:
  `runtime error: division by zero: file.hy:LINE`.
- Double division by zero follows IEEE-754 (`inf` / `nan`, printed by `%g`).
- `int` arithmetic wraps on overflow; `INT64_MIN / -1` yields `INT64_MIN` and
  `INT64_MIN % -1` yields `0`.
- String comparison `==`/`!=` compares contents, not pointers.
- `&&` and `||` short-circuit.

## 9. Diagnostics

Compile errors use the form:

```
file.hy:3:5: error: cannot assign a value of type 'string' to variable 'n' of type 'int'
    n = "text";
        ^
```

All type errors in a program are reported before exiting. Exit code is `1`.

Generated C contains `#line` directives, so C compiler diagnostics also refer to the
original `.hy` file.

## 10. Compiler CLI

```
hydrogenc build <file.hy> [-o out] [--emit-c PATH] [--keep-c] [--static] [--cc NAME]
hydrogenc check <file.hy>
hydrogenc emit-c <file.hy> [-o out.c]
hydrogenc --version
```

- `build` writes an executable named after the source file by default.
- `--emit-c PATH` also writes the generated C source.
- `--keep-c` keeps the temporary C file and prints its path to stderr.
- `--static` passes `-static` to the C compiler.
- `--cc` selects the C compiler (default `gcc`).

Exit codes: `0` success, `1` compilation/type/runtime error, `2` CLI usage error,
`3` C backend failure.

## 11. Complete example

```csharp
struct Point {
    int x;
    int y;
}

func distanceSquared(Point a, Point b) -> int {
    int dx = a.x - b.x;
    int dy = a.y - b.y;
    return dx * dx + dy * dy;
}

Point a = Point { x = 1, y = 2 };
Point b = Point { x = 4, y = 6 };

log("distance^2 =", distanceSquared(a, b));

for (int i = 1; i <= 3; i = i + 1) {
    log("step", i);
}
```

## 12. Out of scope for v0.2

Arrays, methods and constructors, nested structs, struct equality, `for` without clauses,
`do while`, `switch`, casts, `++`/`+=`, ternary operator, string interpolation, generics,
modules/imports, garbage collection. Concatenated strings are allocated for the lifetime of
the process.
