# Cerium syntax

Documentation for Cerium version 0.6. The formal EBNF grammar is in [SPEC.md](../SPEC.md).

## 0. What makes Cerium different

The syntax will feel familiar if you have written C# or Java, but the language has its own
character:

```csharp
func add(int a, int b) -> int {   // func plus an arrow return type
    return a + b;
}

struct Point {
    int x;
    int y;
}

Point p = Point { x = 3, y = 4 }; // struct literal without new
for (int i = 0; i < 3; i = i + 1) { ... }
loop { ... break; }               // infinite loop
```

- braces are always required;
- semicolons terminate simple statements;
- indentation does not affect parsing;
- strings use double quotes only;
- `log(...)` is the primary built-in output function.

## 1. Program structure

A program is a `.ce` file. It may contain:

- struct declarations (`struct`);
- function declarations (`func`);
- top-level statements.

Top-level statements execute from top to bottom and form the body of an implicit `main`.
Struct and function declarations are visible throughout the program regardless of their order.

```csharp
func twice(int x) -> int {
    return x * 2;
}

log(twice(21)); // 42
```

An empty program is valid. A user-defined `func main()` is not the entry point: it is an
ordinary function, while the entry point is the top-level statement sequence.

Rules:

- names are case-sensitive;
- line breaks and indentation do not affect syntax;
- simple statements end with `;`; no semicolon is needed after a `{ }` block.

## 2. Comments

```csharp
// A comment until the end of the line.

/*
   A block comment.
   Nested block comments are not supported.
*/
```

## 3. Identifiers and keywords

An identifier is:

```
[A-Za-z_][A-Za-z0-9_]*
```

Only Latin letters, digits, and `_` are allowed; an identifier cannot start with a digit.

Reserved words:

```
int  double  bool  string  void
func  struct  return
if  else  while  for  loop  break  continue
true  false
```

`log` is not a keyword, but it is a built-in function, and declaring your own `func log` is not
allowed. The same applies to the other built-ins listed in [SPEC.md](../SPEC.md).

## 4. Types

| Type     | Stores                          | Size / format                  |
|----------|---------------------------------|--------------------------------|
| `int`    | signed integer                  | 64-bit, two's complement       |
| `double` | floating-point number           | IEEE-754 binary64              |
| `bool`   | `true` or `false`               | boolean                        |
| `string` | immutable UTF-8 string          | pointer to bytes               |

Struct names introduce additional value types. There are no implicit conversions: `int` and
`double` cannot be mixed, and a string cannot be assigned to an `int`. There are no type casts;
explicit conversion functions are covered in §8.2.

```csharp
int count = 10;
double ratio = 0.5;
bool ready = false;
string label = "cerium";
```

## 5. Literals

### Integers

Decimal digits only:

```csharp
int a = 0;
int b = 42;
int c = -7; // unary minus applied to the literal 7
```

There are no hexadecimal, binary, octal, or `_`-separated literals. A literal must be in the
range `0` through `9223372036854775807`.

### Floating-point numbers

Digits are required on both sides of the decimal point:

```csharp
double pi = 3.14;
double zero = 0.0;
```

There is no exponent notation in literals, and forms such as `.5` or `5.` are not allowed.

### Booleans

```csharp
bool yes = true;
bool no = false;
```

Only lowercase forms are valid.

### Strings

Double quotes only. Supported escape sequences:

| Escape | Meaning          |
|--------|------------------|
| `\n`   | line feed        |
| `\t`   | tab              |
| `\r`   | carriage return  |
| `\\`   | backslash        |
| `\"`   | double quote     |

```csharp
log("first line\nsecond line");
log("quote: \" and slash: \\");
```

Single quotes, character literals, and string interpolation are not supported. A real newline
cannot appear inside a string; use `\n`.

## 6. Variables

### Declaration

The form is `type name = expression;`. An initializer is required.

```csharp
int age = 25;
double temperature = 36.6;
bool enabled = true;
string name = "Alice";
```

`int x;` is not supported.

### Assignment

```csharp
int x = 1;
x = x + 10;
x = 42;
```

`x = 1;` does not declare a variable: the name must already exist. A variable's type is fixed
at declaration.

```csharp
int n = 1;
n = 2;         // ok
// n = 2.5;    // error
// n = "no";   // error
```

## 7. Expressions and operators

### Arithmetic

```csharp
int a = 17;
int b = 5;

log(a + b); // 22
log(a - b); // 12
log(a * b); // 85
log(a / b); // 3 (truncates toward zero)
log(a % b); // 2
```

- `+ - * / %` work with `int`;
- `+ - * /` work with `double`; `%` is not allowed for `double`;
- both operands must have the same type;
- `int` overflow wraps according to two's-complement rules;
- `INT64_MIN / -1` yields `INT64_MIN`, and `INT64_MIN % -1` yields `0`.

### Strings

`+` concatenates two strings:

```csharp
string greeting = "hello, " + "world";
log(greeting); // hello, world
```

A string and a number cannot be added directly:

```csharp
log("n =", 42); // correct
// log("n = " + 42); // type error
// log("n = " + toString(42)); // correct
```

### Comparisons

```csharp
log(1 < 2);       // true
log(2 <= 2);      // true
log(1 == 1);      // true
log("a" == "a");  // true, contents are compared
log("a" != "b");  // true
```

- `< <= > >=` work only with `int` and `double` of the same type;
- `== !=` work with `int`, `double`, `bool`, and `string` of the same type;
- structs cannot be compared.

### Logic

```csharp
bool a = true;
bool b = false;

log(a && b); // false
log(a || b); // true
log(!a);     // false
```

Operands must be `bool`; evaluation short-circuits.

### Parentheses and precedence

From highest to lowest:

| Precedence | Operators              |
|------------|------------------------|
| 1          | `!`, unary `-`         |
| 2          | `*`, `/`, `%`          |
| 3          | `+`, `-`               |
| 4          | `<`, `<=`, `>`, `>=`   |
| 5          | `==`, `!=`             |
| 6          | `&&`                   |
| 7          | `\|\|`                 |

```csharp
log(1 + 2 * 3);   // 7
log((1 + 2) * 3); // 9
```

### Expression statements

Only a function call may be used as a standalone statement:

```csharp
log("ok");       // ok
f();             // ok, the result may be discarded
// 1 + 2;        // error: an expression statement must be a function call
```

## 8. Output: `log`

```csharp
log("hello");
log("n =", 42);
log("pi =", 3.14, "ok =", true);
log(); // prints an empty line
```

- arguments are printed to stdout separated by one space;
- a newline is appended at the end;
- `int` prints as a decimal number;
- `double` uses `%g` (`3.14`, `10`, `0.5`);
- `bool` prints as `true` or `false`;
- `string` prints as-is.

`log` returns `void` and does not accept structs as a whole:

```csharp
// log(log("nested")); // error
// log(point);         // error, print its fields instead
```

Because `log` separates every argument with a space, use string concatenation when exact
formatting matters:

```csharp
log("AVATAR: (", value, ")");              // AVATAR: ( value )
log("AVATAR: (" + toString(value) + ")");  // AVATAR: (value)
```

## 8.1 Input: `input`

| Function          | Argument               | Result   |
|-------------------|------------------------|----------|
| `input()`         | optional prompt        | `string` |
| `inputInt()`      | optional prompt        | `int`    |
| `inputDouble()`   | optional prompt        | `double` |
| `inputBool()`     | optional prompt        | `bool`   |

The prompt is a string expression. It is printed to stdout without a newline and flushed
immediately so that it appears before the program waits for input:

```csharp
string name = input("Name: ");
int age = inputInt("Age: ");
double height = inputDouble();
bool ok = inputBool("Continue? (true/false): ");

log("hello,", name);
log(age, height, ok);
```

Rules:

- each call reads one line from stdin;
- trailing `\n` and `\r` are removed;
- `input()` preserves the rest of the line, including surrounding spaces;
- an empty line is a valid `input()` value (an empty string);
- end of input (EOF) before the first character is a runtime error, even for `input()`;
- `inputInt`, `inputDouble`, and `inputBool` trim spaces and tabs on both sides and parse the
  entire remaining text:
  - `inputInt` accepts an optional sign and decimal digits within the 64-bit `int` range;
  - `inputDouble` accepts the decimal forms understood by C `strtod`, including fractions and
    exponents (`1.5e2`);
  - `inputBool` accepts exactly `true` or `false`.

Invalid input terminates the program with an error and exit code 1:

```
runtime error: invalid int input: '12abc': program.ce:3
runtime error: unexpected end of input: program.ce:5
```

The input built-ins cannot be redefined with `func input(...)`.

```csharp
int n = inputInt();        // input: 41
log(n + 1);                // 42

string text = input();     // input: hello world
log("[" + text + "]");     // [hello world]
```

## 8.2 Type conversions

There are no implicit conversions, so types are changed explicitly:

| Function          | Argument                            | Result   |
|-------------------|-------------------------------------|----------|
| `toString(value)` | `int`, `double`, `bool`, or `string` | `string` |
| `toInt(text)`     | `string`                            | `int`    |
| `toDouble(text)`  | `string`                            | `double` |
| `toBool(text)`    | `string`                            | `bool`   |

```csharp
string label = "answer: " + toString(42);
int port = toInt(" 8080 ");
double ratio = toDouble("2.5e-1");
bool enabled = toBool("true");

log(label);   // answer: 42
log(port);    // 8080
log(ratio);   // 0.25
log(enabled); // true
```

Rules:

- `toString` accepts one scalar. Integers print as decimal numbers, doubles use the same `%g`
  format as `log`, booleans become `true`/`false`, and strings are returned unchanged;
- structs cannot be passed to `toString`; convert individual fields instead;
- `toInt`, `toDouble`, and `toBool` accept only `string`, trim spaces and tabs, and parse the
  entire remaining text;
- accepted formats match `inputInt`, `inputDouble`, and `inputBool`;
- invalid text raises a runtime error and exits with code 1:

```
runtime error: invalid int value: '12abc': program.ce:3
runtime error: invalid bool value: 'yes': program.ce:7
```

A typical use is concatenating a number or boolean with a string:

```csharp
struct User {
    string name;
    int avatar;
}

User user = User { name = "TeamLED", avatar = 87123712 };
log("USERNAME: (" + user.name + ")");
log("AVATAR: (" + toString(user.avatar) + ")");
```

```
USERNAME: (TeamLED)
AVATAR: (87123712)
```

## 9. Conditions

```csharp
int score = 75;

if (score >= 90) {
    log("A");
} else if (score >= 70) {
    log("B");
} else {
    log("C");
}
```

- the condition is written in parentheses and must have type `bool`;
- braces are required;
- `else` is optional, and an `else if` chain can be any length;
- an empty block `{ }` is allowed;
- there is no truthiness: `if (1)` is an error.

## 10. Loops

### `while`

```csharp
int i = 0;
while (i < 3) {
    log("i =", i);
    i = i + 1;
}
```

### `for`

```csharp
for (int i = 1; i <= 5; i = i + 1) {
    log(i);
}
```

All three parts are required:

1. initialization — a variable declaration with `=`, or an assignment to an existing variable;
2. condition — an expression of type `bool`;
3. update — an assignment to a variable or a field.

A variable declared in the initialization is visible only inside the loop:

```csharp
for (int i = 0; i < 3; i = i + 1) { ... }
// log(i); // error: i no longer exists
```

Fields may also be assigned inside the body:

```csharp
Point p = Point { x = 0, y = 0 };
for (int i = 0; i < 3; i = i + 1) {
    p.x = p.x + 1;
}
```

### `loop`

An infinite loop, normally exited with `break`:

```csharp
int n = 0;
loop {
    n = n + 1;
    if (n == 3) {
        break;
    }
}
log(n); // 3
```

### `break` and `continue`

```csharp
for (int i = 0; i < 10; i = i + 1) {
    if (i % 2 != 0) {
        continue; // jump to i = i + 1
    }
    if (i > 6) {
        break;
    }
    log(i); // 0 2 4 6
}
```

- `break` and `continue` are valid only inside `while`, `for`, or `loop`;
- `continue` in a `for` still executes the update clause;
- using either outside a loop is a compile-time error.

## 11. Blocks and scope

`if`, loops, and function bodies introduce scopes:

```csharp
int x = 1;

if (true) {
    int y = 2;
    log(x + y); // 3
}

// log(y); // error: y is not visible here
```

Rules:

- a variable is visible only in its block and nested blocks;
- shadowing an outer variable is not allowed;
- redeclaring a name in the same block is an error;
- using a variable before its declaration is an error.

## 12. Functions

### Declaration

```csharp
func add(int a, int b) -> int {
    return a + b;
}

func greet(string name) -> void {
    log("hello,", name);
}
```

- `func` is the keyword, followed by the name, parameters, `->`, and the return type;
- `void` means no result;
- parameters are written as `type name`, separated by commas;
- the body is a `{ }` block;
- functions may only be declared at the top level;
- there is no overloading: function names are unique.

### Calls

```csharp
log(add(2, 3)); // 5
greet("cerium");
```

Arguments are checked for count and type. A result may be discarded:

```csharp
add(2, 3); // allowed
```

Functions are visible throughout the program regardless of declaration order, so forward
calls and mutual recursion are supported:

```csharp
log(isEven(10)); // true

func isEven(int n) -> bool {
    if (n == 0) { return true; }
    return isOdd(n - 1);
}

func isOdd(int n) -> bool {
    if (n == 0) { return false; }
    return isEven(n - 1);
}
```

### `return`

```csharp
func sign(int x) -> int {
    if (x > 0) {
        return 1;
    } else if (x < 0) {
        return -1;
    } else {
        return 0;
    }
}

func logTwice(string text) -> void {
    log(text);
    log(text);
    return; // optional
}
```

- `return expression;` returns a value;
- `return;` is only valid in a `void` function;
- a function with a result must return a value on every path;
- the check is conservative: `if`/`else` chains are analyzed, but infinite loops are not
  treated as guaranteed returns. Ending a function with `return`, or with an `if`/`else` where
  every branch returns, satisfies the check;
- `return` outside a function is an error.

### Function scope

A function body has its own scope. Parameters are visible inside it, but top-level variables are
not:

```csharp
int global = 10;

func broken() -> int {
    // return global; // error: top-level variables are not visible
    return 0;
}
```

Parameters and local variables cannot shadow each other.

## 13. Structs

### Declaration

```csharp
struct Point {
    int x;
    int y;
}

struct User {
    string name;
    bool active;
}
```

- structs may only be declared at the top level;
- fields use `type name;`; a field type must be scalar (`int`, `double`, `bool`, or `string`);
- at least one field is required;
- field names are unique;
- nested struct fields are not supported in v0.6.

### Struct literals

```csharp
Point p = Point { x = 3, y = 4 };
User user = User { name = "Ada", active = true };
```

- `new` is not needed;
- every field must be initialized exactly once;
- field order is free;
- value types are checked.

```csharp
Point p = Point { x = 3, y = 4 };
log(p.x, p.y); // 3 4
```

### Fields

```csharp
Point p = Point { x = 1, y = 2 };

p.x = p.x + 10; // field assignment
log(p.x);       // 11

Point copy = p; // copied by value
copy.y = 0;
log(p.y, copy.y); // 2 0
```

- access uses `value.field`;
- fields can be assigned;
- structs are passed to functions and returned by value;
- structs cannot be compared with `==`/`!=`;
- structs cannot be printed with `log`; print fields instead.

### Structs in functions

```csharp
struct Point {
    int x;
    int y;
}

func makePoint(int x, int y) -> Point {
    return Point { x = x, y = y };
}

func lengthSquared(Point p) -> int {
    return p.x * p.x + p.y * p.y;
}

Point p = makePoint(3, 4);
log(lengthSquared(p)); // 25
log(makePoint(1, 2).x); // 1
```

## 14. Errors

Compile-time and type errors include the file, line, and column:

```
examples/errors/missing_return.ce:2:1: error: function 'absolute' must return a value on all paths
    func absolute(int x) -> int {
    ^
```

All type errors are collected in one run; the exit code is `1`.

Integer division by zero is detected at run time:

```
runtime error: division by zero: program.ce:5
```

The exit code is `1`. Double division by zero is not checked and produces `inf` or `nan`.

Invalid input and invalid conversions are also runtime errors:

```
runtime error: invalid int input: '12abc': program.ce:3
runtime error: invalid int value: '12abc': program.ce:7
runtime error: unexpected end of input: program.ce:5
```

## 15. Complete example

```csharp
// bank.ce
struct Account {
    string owner;
    int balance;
}

func deposit(Account account, int amount) -> Account {
    return Account {
        owner = account.owner,
        balance = account.balance + amount
    };
}

Account account = Account { owner = "Ada", balance = 100 };

for (int month = 1; month <= 3; month = month + 1) {
    account = deposit(account, 50);
    log("month", month, "balance =", account.balance);
}

if (account.balance >= 250) {
    log(account.owner, "can buy the compiler");
}
```

Build and run:

```sh
./ceriumc build bank.ce -o bank
./bank
```

## 16. Cheat sheet

```csharp
// comment
/* block comment */

int x = 10;                  // declaration
x = x + 1;                   // assignment

double d = 2.5;
bool flag = true;
string s = "text";

log("x =", x);               // arguments separated by a space + \n

string name = input("Name: ");   // string
int age = inputInt("Age: ");     // int
double h = inputDouble();        // double
bool ok = inputBool();           // true/false

string label = "age: " + toString(age); // number to string
int parsed = toInt("42");               // string to int

if (x > 5) {                 // condition must be bool
    log("big");
} else if (x == 5) {
    log("five");
} else {
    log("small");
}

while (x > 0) {
    x = x - 1;
}

for (int i = 0; i < 3; i = i + 1) {
    log(i);
}

loop {
    break;
}

int n = (1 + 2) * 3;
bool ok2 = n > 5 && !flag;
string t = s + "!";

struct Point {
    int x;
    int y;
}

Point p = Point { x = 1, y = 2 };
p.x = p.y;
log(p.x);

func add(int a, int b) -> int {
    return a + b;
}

func ping() -> void {
    log("ping");
}
```

## 17. Limitations in v0.6

Not supported:

- arrays, lists, and string indexing;
- methods and constructors for structs;
- nested structs and struct-typed fields;
- comparing or printing whole structs;
- function overloading;
- `for` with omitted clauses, `do while`, and `switch`;
- type casts (`(int)`, `int(...)`); use explicit conversion functions;
- `++`, `--`, `+=`, `-=`, and other compound assignments;
- the ternary operator `? :`;
- string interpolation;
- modules, imports, and generics;
- garbage collection: concatenated strings, strings returned by `input()`, and `toString`
  results live until the process exits.

## 18. CLI at a glance

```sh
./ceriumc build file.ce -o program   # build a binary
./ceriumc check file.ce              # check syntax and types only
./ceriumc emit-c file.ce             # print the generated C
./ceriumc --version
```

Additional `build` flags: `--emit-c PATH`, `--keep-c`, `--static`, `--cc NAME`.

On Windows use the installed `ceriumc` command or `ceriumc.cmd` from the repository; binaries
get a `.exe` extension automatically. The C compiler is auto-detected (`clang` on macOS,
`gcc` elsewhere); MSVC `cl.exe` is not supported. `--static` is not available on macOS.
