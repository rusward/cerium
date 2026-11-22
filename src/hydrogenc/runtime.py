"""C runtime helpers embedded into every generated program."""

RUNTIME_SOURCE = r"""
static void hy_print_int(int64_t value) {
    printf("%" PRId64, value);
}

static void hy_print_double(double value) {
    printf("%g", value);
}

static void hy_print_bool(bool value) {
    fputs(value ? "true" : "false", stdout);
}

static void hy_print_string(const char *value) {
    fputs(value, stdout);
}

static const char *hy_str_concat(const char *a, const char *b) {
    size_t a_len = strlen(a);
    size_t b_len = strlen(b);
    char *result = (char *)malloc(a_len + b_len + 1);
    if (result == NULL) {
        fputs("runtime error: out of memory\n", stderr);
        exit(1);
    }
    memcpy(result, a, a_len);
    memcpy(result + a_len, b, b_len + 1);
    return result;
}

static bool hy_str_eq(const char *a, const char *b) {
    return strcmp(a, b) == 0;
}

/* Two's-complement wraparound, matching C# unchecked arithmetic. */
static int64_t hy_add_int(int64_t a, int64_t b) {
    return (int64_t)((uint64_t)a + (uint64_t)b);
}

static int64_t hy_sub_int(int64_t a, int64_t b) {
    return (int64_t)((uint64_t)a - (uint64_t)b);
}

static int64_t hy_mul_int(int64_t a, int64_t b) {
    return (int64_t)((uint64_t)a * (uint64_t)b);
}

static int64_t hy_neg_int(int64_t a) {
    return (int64_t)(0u - (uint64_t)a);
}

static void hy_fatal_div(int line) {
    fprintf(stderr, "runtime error: division by zero: %s:%d\n", HY_FILE, line);
    exit(1);
}

static int64_t hy_div_int(int64_t a, int64_t b, int line) {
    if (b == 0) {
        hy_fatal_div(line);
    }
    if (a == INT64_MIN && b == -1) {
        return INT64_MIN;
    }
    return a / b;
}

static int64_t hy_mod_int(int64_t a, int64_t b, int line) {
    if (b == 0) {
        hy_fatal_div(line);
    }
    if (a == INT64_MIN && b == -1) {
        return 0;
    }
    return a % b;
}
"""
