---
title: Cerium
hide:
  - navigation
  - toc
  - footer
---

<div class="cerium-hero">
  <div class="cerium-hero__glow" aria-hidden="true"></div>
  <div class="cerium-hero__inner">
    <div class="cerium-hero__copy">
      <p class="cerium-eyebrow">STATICALLY TYPED · C99 BACKEND</p>
      <h1>Cerium</h1>
      <p class="cerium-lead">
        A small language with C#-like syntax, strict types and native binaries.
      </p>
      <div class="cerium-actions">
        <a class="cerium-button cerium-button--primary" href="getting-started/">Get started</a>
        <a class="cerium-button" href="guide/">Language guide</a>
        <a class="cerium-text-link" href="https://github.com/rusward/cerium">GitHub →</a>
      </div>
    </div>
    <img class="cerium-mascot" src="assets/cerium-mascot.png" alt="Cerium mascot">
  </div>
</div>

## Why Cerium

<div class="cerium-grid">
  <div class="cerium-card">
    <h3>Strict by default</h3>
    <p>64-bit <code>int</code>, <code>double</code>, <code>bool</code> and <code>string</code>.
    No implicit conversions, no surprises.</p>
  </div>
  <div class="cerium-card">
    <h3>Functions that compose</h3>
    <p>Declare with <code>func name(...) -&gt; type</code>, call before the declaration, and
    recurse naturally.</p>
  </div>
  <div class="cerium-card">
    <h3>Structs without ceremony</h3>
    <p>Build values with <code>Point { x = 1, y = 2 }</code>. No <code>new</code>, no
    constructors, no hidden allocation.</p>
  </div>
  <div class="cerium-card">
    <h3>Three loop forms</h3>
    <p><code>while</code>, C-style <code>for</code>, and an infinite <code>loop</code> with
    <code>break</code> and <code>continue</code>.</p>
  </div>
  <div class="cerium-card">
    <h3>Real native binaries</h3>
    <p>The compiler emits C99 and uses <code>gcc</code>. No VM, no interpreter at runtime.</p>
  </div>
  <div class="cerium-card">
    <h3>Console I/O built in</h3>
    <p><code>log</code>, typed <code>input*</code> functions, and explicit conversions such as
    <code>toString</code> and <code>toInt</code>.</p>
  </div>
</div>

## A quick look

```csharp
struct Point {
    int x;
    int y;
}

func distanceSquared(Point a, Point b) -> int {
    int dx = a.x - b.x;
    int dy = a.y - b.y;
    return dx * dx + dy * dy;
}

Point a = Point { x = 1, y = 2 };
Point b = Point { x = 4, y = 6 };

log("distance^2 =", distanceSquared(a, b));

for (int i = 1; i <= 3; i = i + 1) {
    log("step", i);
}
```

## Start in seconds

```sh
git clone https://github.com/rusward/cerium.git
cd cerium
./ceriumc build examples/hello.ce -o hello
./hello
```

New to the language? Read [Getting started](getting-started.md), then explore the
[language guide](guide/index.md). For the formal rules, see the
[specification](spec.md).
