// control_flow.hy - if/else if/else, while and boolean logic.
int score = 75;

if (score >= 90) {
    log("A");
} else if (score >= 70) {
    log("B");
} else {
    log("C");
}

int total = 0;
int i = 1;
while (i <= 5) {
    total = total + i;
    i = i + 1;
}
log("total =", total);

bool flag = false;
if (!flag && true) {
    log("logic works");
}

int counter = 0;
while (counter < 2) {
    int inner = counter * 10;
    log("inner =", inner);
    counter = counter + 1;
}
