---
title: Examples and cheat sheet
---

# Examples and cheat sheet

## Complete example

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

Build and run:

```sh
./ceriumc build bank.ce -o bank
./bank
```

## Cheat sheet

```csharp
// comment
/* block comment */

int x = 10;                  // declaration
x = x + 1;                   // assignment

double d = 2.5;
bool flag = true;
string s = "text";

log("x =", x);               // arguments separated by a space + \n

string name = input("Name: ");   // string
int age = inputInt("Age: ");     // int
double h = inputDouble();        // double
bool ok = inputBool();           // true/false

string label = "age: " + toString(age); // number to string
int parsed = toInt("42");               // string to int

if (x > 5) {                 // condition must be bool
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
bool ok2 = n > 5 && !flag;
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
