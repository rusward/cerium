// Unknown field.
struct Point {
    int x;
    int y;
}

Point p = Point { x = 1, y = 2 };
log(p.z);
