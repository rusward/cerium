---
title: Командная строка
---

# Командная строка

## CLI кратко

```sh
./ceriumc build file.ce -o program   # собрать бинарник
./ceriumc check file.ce              # только проверить синтаксис и типы
./ceriumc emit-c file.ce             # показать сгенерированный C
./ceriumc --version
```

Дополнительные флаги `build`: `--emit-c PATH`, `--keep-c`, `--static`, `--cc NAME`.
