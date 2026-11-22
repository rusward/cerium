// hello.hy - variables, typed values and log().
string name = "world";
int n = 42;
double pi = 3.14;
bool ok = true;

log("hello, " + name);
log("n =", n, "pi =", pi, "ok =", ok);

if (n > 40) {
    log("big");
} else {
    log("small");
}

int i = 0;
while (i < 3) {
    log("i =", i);
    i = i + 1;
}
