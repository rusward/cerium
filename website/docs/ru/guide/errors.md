---
title: Ошибки
---

# Ошибки

## Ошибки

Ошибки компиляции и типов печатаются с файлом, строкой и колонкой:

```
examples/errors/missing_return.ce:2:1: error: function 'absolute' must return a value on all paths
    func absolute(int x) -> int {
    ^
```

Все ошибки типов собираются за один прогон; код возврата — `1`.

Деление на ноль для `int` обнаруживается во время выполнения:

```
runtime error: division by zero: program.ce:5
```

Код возврата — `1`. Деление `double` на ноль не проверяется и даёт `inf` или `nan`.
