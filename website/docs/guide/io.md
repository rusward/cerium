---
title: Input, output and conversions
---

# Input, output and conversions

## Output: `log`

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

## Input: `input`

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

## Type conversions

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
