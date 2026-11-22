---
title: Control flow and scope
---

# Control flow and scope

## Conditions

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

## Loops

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

## Blocks and scope

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
