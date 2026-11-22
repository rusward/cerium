---
title: Примеры и шпаргалка
---

# Примеры и шпаргалка

## Полный пример

```csharp
// bank.ce
struct Account {
    string owner;
    int balance;
}

func deposit(Account account, int amount) -> Account {
    return Account {
        owner = account.owner,
        balance = account.balance + amount
    };
}

Account account = Account { owner = "Ada", balance = 100 };

for (int month = 1; month <= 3; month = month + 1) {
    account = deposit(account, 50);
    log("month", month, "balance =", account.balance);
}

if (account.balance >= 250) {
    log(account.owner, "can buy the compiler");
}
```

Сборка и запуск:

```sh
./ceriumc build examples/structs.ce -o structs
./structs
```

## Шпаргалка

```csharp
// комментарий
/* блочный комментарий */

int x = 10;                  // объявление
x = x + 1;                   // присваивание

double d = 2.5;
bool flag = true;
string s = "text";

log("x =", x);               // аргументы через пробел + \n

string name = input("Name: ");   // строка
int age = inputInt("Age: ");     // int
double h = inputDouble();        // double
bool ok = inputBool();           // true/false

string label = "age: " + toString(age); // число в строку
int parsed = toInt("42");               // строка в int

if (x > 5) {                 // условие типа bool
    log("big");
} else if (x == 5) {
    log("five");
} else {
    log("small");
}

while (x > 0) {
    x = x - 1;
}

for (int i = 0; i < 3; i = i + 1) {
    log(i);
}

loop {
    break;
}

int n = (1 + 2) * 3;
bool ok = n > 5 && !flag;
string t = s + "!";

struct Point {
    int x;
    int y;
}

Point p = Point { x = 1, y = 2 };
p.x = p.y;
log(p.x);

func add(int a, int b) -> int {
    return a + b;
}

func ping() -> void {
    log("ping");
}
```
