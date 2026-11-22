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
