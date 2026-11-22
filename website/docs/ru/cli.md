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

На Windows используй установленную команду `ceriumc` или `ceriumc.cmd` из репозитория;
бинарники автоматически получают расширение `.exe`. C-компилятор определяется
автоматически (`clang` на macOS, `gcc` на остальных платформах); MSVC `cl.exe` не
поддерживается. `--static` недоступен на macOS.
