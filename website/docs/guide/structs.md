---
title: Structs
---

# Structs

## Structs

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
- nested struct fields are not supported in v0.5.

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
