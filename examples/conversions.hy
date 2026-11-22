// conversions.hy - explicit conversions between scalar types.
struct User {
    string name;
    int avatar;
}

User user = User { name = "TeamLED", avatar = 87123712 };

log("USERNAME: (" + user.name + ")");
log("AVATAR: (" + toString(user.avatar) + ")");

int port = toInt(" 8080 ");
double ratio = toDouble("2.5e-1");
bool enabled = toBool("true");

log("port =", toString(port));
log("ratio =", toString(ratio), "enabled =", toString(enabled));
