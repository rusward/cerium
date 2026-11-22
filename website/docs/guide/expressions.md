---
title: Expressions and operators
---

# Expressions and operators

## Expressions and operators

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
