---
title: Command line
---

# Command line

## CLI at a glance

```sh
./ceriumc build file.ce -o program   # build a binary
./ceriumc check file.ce              # check syntax and types only
./ceriumc emit-c file.ce             # print the generated C
./ceriumc --version
```

Additional `build` flags: `--emit-c PATH`, `--keep-c`, `--static`, `--cc NAME`.

On Windows use the installed `ceriumc` command or `ceriumc.cmd` from the repository; binaries
get a `.exe` extension automatically. The C compiler is auto-detected (`clang` on macOS,
`gcc` elsewhere); MSVC `cl.exe` is not supported. `--static` is not available on macOS.
