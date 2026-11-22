---
title: Functions
---

# Functions

## Functions

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
