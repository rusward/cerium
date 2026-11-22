// functions.hy - user functions, recursion and void returns.
func factorial(int n) -> int {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

func add(int a, int b) -> int {
    return a + b;
}

func greet(string name) -> void {
    log("hello,", name);
}

greet("hydrogen");
log("3 + 4 =", add(3, 4));
log("5! =", factorial(5));
