// input.hy - reading typed values from the console.
string name = input("Name: ");
int age = inputInt("Age: ");
double height = inputDouble("Height (m): ");
bool developer = inputBool("Developer? (true/false): ");

log("hello,", name);
log("age =", age, "height =", height, "developer =", developer);
