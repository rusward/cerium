---
title: Errors
---

# Errors

## Errors

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
