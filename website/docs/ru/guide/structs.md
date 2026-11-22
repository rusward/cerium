---
title: Структуры
---

# Структуры

## Структуры

### Объявление

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

- объявляются только на верхнем уровне;
- поля — `тип имя;`; тип поля обязан быть скалярным
  (`int`, `double`, `bool`, `string`);
- хотя бы одно поле;
- имена полей уникальны;
- вложенные структуры в v0.6 не поддерживаются.

### Литерал структуры

```csharp
Point p = Point { x = 3, y = 4 };
User user = User { name = "Ada", active = true };
```

- `new` не нужен;
- нужно инициализировать все поля ровно один раз;
- порядок полей произвольный;
- типы значений проверяются.

```csharp
Point p = Point { x = 3, y = 4 };
log(p.x, p.y); // 3 4
```

### Поля

```csharp
Point p = Point { x = 1, y = 2 };

p.x = p.x + 10; // присваивание полю
log(p.x);       // 11

Point copy = p; // копирование по значению
copy.y = 0;
log(p.y, copy.y); // 2 0
```

- доступ — `точка.поле`;
- полям можно присваивать;
- структуры передаются в функции и возвращаются по значению;
- сравнивать структуры через `==`/`!=` нельзя;
- печатать структуру в `log` нельзя — печатайте поля.

### Структуры в функциях

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
