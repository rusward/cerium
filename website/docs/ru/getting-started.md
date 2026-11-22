---
title: Начало работы
---

# Начало работы

Cerium компилирует исходники `.ce` в C99 и собирает нативный исполняемый файл через `gcc`.
Этот раздел проведёт от чистого репозитория до запущенного бинарника.

## Требования

- Python 3.10 или новее;
- поддерживаемый C99-компилятор в `PATH`;
- Linux x86-64 проверяется на каждом изменении; macOS и Windows проверяются в CI.

На macOS установи Xcode Command Line Tools (`xcode-select --install`). На Windows установи
MinGW-w64 (MSYS2 UCRT64) или LLVM clang и добавь его в `PATH`; MSVC `cl.exe` не
поддерживается. `ceriumc` определяет компилятор автоматически: `clang` на macOS, `gcc` на
остальных платформах. Переопределить можно через `--cc PATH`.

## Установка

=== "Запуск из репозитория"

    ```sh
    git clone https://github.com/rusward/cerium.git
    cd cerium
    ./ceriumc --version
    ```

    Лаунчер `ceriumc` использует исходники из `src/` напрямую.

=== "Установка как Python-пакета"

    ```sh
    git clone https://github.com/rusward/cerium.git
    cd cerium
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -e .
    ceriumc --version
    ```

    После установки команда `ceriumc` доступна в любом месте активного окружения.
    На Fedora/Debian не используй `--break-system-packages` — правильный путь через venv.

На Windows используй `py -m venv .venv`, активируй `.venv\Scripts\activate`, затем
`python -m pip install -e .`. Работают и установленная команда `ceriumc`, и `ceriumc.cmd`
из репозитория. Собранные файлы автоматически получают расширение `.exe`.

Если используешь `uv`, можно поставить `ceriumc` как изолированный PATH-инструмент без venv:

```sh
uv tool install --editable . --python 3.12
ceriumc --version
```

`uv tool update-shell` добавляет `~/.local/bin` в PATH, если его там нет. Аналогичный вариант —
`pipx install --editable .`.

## Первая программа

Создай `hello.ce`:

```csharp
log("hello, cerium");
```

Собери и запусти:

```sh
./ceriumc build hello.ce -o hello
./hello
```

```
hello, cerium
```

## Проверка и просмотр

У `ceriumc` есть три команды:

```sh
./ceriumc check hello.ce     # только разбор и проверка типов
./ceriumc emit-c hello.ce    # напечатать сгенерированный C
./ceriumc build hello.ce -o hello
```

`check` сообщает обо всех найденных ошибках типов, не вызывая C-компилятор. `emit-c`
показывает, что именно попадает в сгенерированную программу.

## Что дальше

- [Основы программы](guide/basics.md) — структура, комментарии, идентификаторы.
- [Типы и переменные](guide/types.md) — система типов и литералы.
- [Функции](guide/functions.md) — объявления, возврат и рекурсия.
- [Структуры](guide/structs.md) — значимые типы с полями.
- [Спецификация](spec.md) — полное формальное описание.
