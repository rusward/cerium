---
title: Types and variables
---

# Types and variables

## Types

| Type     | Stores                          | Size / format                  |
|----------|---------------------------------|--------------------------------|
| `int`    | signed integer                  | 64-bit, two's complement       |
| `double` | floating-point number           | IEEE-754 binary64              |
| `bool`   | `true` or `false`               | boolean                        |
| `string` | immutable UTF-8 string          | pointer to bytes               |

Struct names introduce additional value types. There are no implicit conversions: `int` and
`double` cannot be mixed, and a string cannot be assigned to an `int`. There are no type casts;
explicit conversion functions are covered in [Input, output and conversions](io.md).

```csharp
int count = 10;
double ratio = 0.5;
bool ready = false;
string label = "cerium";
```

## Literals

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

## Variables

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
