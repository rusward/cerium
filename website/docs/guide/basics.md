---
title: Program basics
---

# Program basics

## Program structure

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

## Comments

```csharp
// A comment until the end of the line.

/*
   A block comment.
   Nested block comments are not supported.
*/
```

## Identifiers and keywords

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
allowed. The same applies to the other built-ins listed in [SPEC.md](../spec.md).
