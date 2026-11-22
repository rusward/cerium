---
title: Главная
hide:
  - navigation
  - toc
  - footer
---

<div class="cerium-hero">
  <div class="cerium-hero__glow" aria-hidden="true"></div>
  <div class="cerium-hero__inner">
    <div class="cerium-hero__copy">
      <p class="cerium-eyebrow">СТРОГАЯ ТИПИЗАЦИЯ · БЭКЕНД C99</p>
      <h1>Cerium</h1>
      <p class="cerium-lead">
        Небольшой язык с C#-подобным синтаксисом, строгими типами и нативными бинарниками.
      </p>
      <div class="cerium-actions">
        <a class="cerium-button cerium-button--primary" href="getting-started/">Начать</a>
        <a class="cerium-button" href="guide/">Руководство</a>
        <a class="cerium-text-link" href="https://github.com/rusward/cerium">GitHub →</a>
      </div>
    </div>
    <img class="cerium-mascot" src="../assets/cerium-mascot.png" alt="Маскот Cerium">
  </div>
</div>

## Почему Cerium

<div class="cerium-grid">
  <div class="cerium-card">
    <h3>Строгость по умолчанию</h3>
    <p>64-битный <code>int</code>, <code>double</code>, <code>bool</code> и <code>string</code>.
    Никаких неявных преобразований и сюрпризов.</p>
  </div>
  <div class="cerium-card">
    <h3>Функции, которые собираются</h3>
    <p>Объявление <code>func name(...) -&gt; type</code>, вызов до объявления и естественная
    рекурсия.</p>
  </div>
  <div class="cerium-card">
    <h3>Структуры без церемоний</h3>
    <p>Значения собираются через <code>Point { x = 1, y = 2 }</code>. Без <code>new</code>,
    конструкторов и скрытых аллокаций.</p>
  </div>
  <div class="cerium-card">
    <h3>Три вида циклов</h3>
    <p><code>while</code>, C-подобный <code>for</code> и бесконечный <code>loop</code> с
    <code>break</code> и <code>continue</code>.</p>
  </div>
  <div class="cerium-card">
    <h3>Настоящие нативные бинарники</h3>
    <p>Компилятор генерирует C99 и использует <code>gcc</code>. Без VM и интерпретатора во
    время выполнения.</p>
  </div>
  <div class="cerium-card">
    <h3>Ввод и вывод в комплекте</h3>
    <p><code>log</code>, типизированные <code>input*</code> и явные преобразования вроде
    <code>toString</code> и <code>toInt</code>.</p>
  </div>
</div>

## Быстрый взгляд

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

## Начать за секунды

```sh
git clone https://github.com/rusward/cerium.git
cd cerium
./ceriumc build examples/hello.ce -o hello
./hello
```

Впервые видишь язык? Начни с раздела [Начало работы](getting-started.md), затем открой
[руководство](guide/index.md). Формальные правила — в [спецификации](spec.md).
