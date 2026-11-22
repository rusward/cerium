// structs.hy - struct declarations, literals, fields and field assignment.
struct Point {
    int x;
    int y;
}

struct User {
    string name;
    bool active;
}

func makePoint(int x, int y) -> Point {
    return Point { x = x, y = y };
}

func lengthSquared(Point p) -> int {
    return p.x * p.x + p.y * p.y;
}

Point origin = Point { x = 0, y = 0 };
Point p = makePoint(3, 4);

log("origin =", origin.x, origin.y);
log("p =", p.x, p.y);
log("length^2 =", lengthSquared(p));

p.x = 6;
log("p.x =", p.x);

User user = User { name = "Ada", active = true };
if (user.active) {
    log(user.name, "is active");
}

Point copy = p;
log("copy.x =", copy.x);
log("direct =", makePoint(1, 2).y);
