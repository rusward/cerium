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

static void hy_parse_fail(
    const char *kind,
    const char *label,
    const char *text,
    int line
) {
    fprintf(
        stderr,
        "runtime error: invalid %s %s: '%s': %s:%d\n",
        kind, label, text, HY_FILE, line
    );
    exit(1);
}

static char *hy_copy_text(const char *text) {
    size_t length = strlen(text);
    char *copy = (char *)malloc(length + 1);
    if (copy == NULL) {
        fputs("runtime error: out of memory\n", stderr);
        exit(1);
    }
    memcpy(copy, text, length + 1);
    return copy;
}

static void hy_prompt(const char *prompt) {
    if (prompt != NULL) {
        fputs(prompt, stdout);
        fflush(stdout);
    }
}

static char *hy_trim(char *text) {
    while (*text == ' ' || *text == '\t') {
        text++;
    }
    size_t length = strlen(text);
    while (length > 0 && (text[length - 1] == ' ' || text[length - 1] == '\t')) {
        text[--length] = '\0';
    }
    return text;
}

static char *hy_read_line(int line) {
    size_t capacity = 128;
    size_t length = 0;
    char *buffer = (char *)malloc(capacity);
    if (buffer == NULL) {
        fprintf(stderr, "runtime error: out of memory: %s:%d\n", HY_FILE, line);
        exit(1);
    }

    fflush(stdout);
    int ch;
    while ((ch = fgetc(stdin)) != EOF && ch != '\n') {
        if (length + 1 >= capacity) {
            capacity *= 2;
            char *grown = (char *)realloc(buffer, capacity);
            if (grown == NULL) {
                free(buffer);
                fprintf(
                    stderr,
                    "runtime error: out of memory: %s:%d\n",
                    HY_FILE, line
                );
                exit(1);
            }
            buffer = grown;
        }
        buffer[length++] = (char)ch;
    }

    if (ch == EOF && length == 0) {
        free(buffer);
        fprintf(
            stderr,
            "runtime error: unexpected end of input: %s:%d\n",
            HY_FILE, line
        );
        exit(1);
    }

    if (length > 0 && buffer[length - 1] == '\r') {
        length--;
    }
    buffer[length] = '\0';
    return buffer;
}

static int64_t hy_parse_int(const char *source, const char *label, int line) {
    char *buffer = hy_copy_text(source);
    char *text = hy_trim(buffer);
    char *end = NULL;

    errno = 0;
    long long value = strtoll(text, &end, 10);
    if (end == text || *end != '\0' || errno == ERANGE) {
        hy_parse_fail("int", label, text, line);
    }

    free(buffer);
    return (int64_t)value;
}

static double hy_parse_double(const char *source, const char *label, int line) {
    char *buffer = hy_copy_text(source);
    char *text = hy_trim(buffer);
    char *end = NULL;

    errno = 0;
    double value = strtod(text, &end);
    if (end == text || *end != '\0' || errno == ERANGE) {
        hy_parse_fail("double", label, text, line);
    }

    free(buffer);
    return value;
}

static bool hy_parse_bool(const char *source, const char *label, int line) {
    char *buffer = hy_copy_text(source);
    char *text = hy_trim(buffer);

    bool result;
    if (strcmp(text, "true") == 0) {
        result = true;
    } else if (strcmp(text, "false") == 0) {
        result = false;
    } else {
        hy_parse_fail("bool", label, text, line);
        result = false;
    }

    free(buffer);
    return result;
}

static const char *hy_input_string(const char *prompt, int line) {
    hy_prompt(prompt);
    return hy_read_line(line);
}

static int64_t hy_input_int(const char *prompt, int line) {
    hy_prompt(prompt);
    char *buffer = hy_read_line(line);
    int64_t value = hy_parse_int(buffer, "input", line);
    free(buffer);
    return value;
}

static double hy_input_double(const char *prompt, int line) {
    hy_prompt(prompt);
    char *buffer = hy_read_line(line);
    double value = hy_parse_double(buffer, "input", line);
    free(buffer);
    return value;
}

static bool hy_input_bool(const char *prompt, int line) {
    hy_prompt(prompt);
    char *buffer = hy_read_line(line);
    bool value = hy_parse_bool(buffer, "input", line);
    free(buffer);
    return value;
}

static int64_t hy_string_to_int(const char *text, int line) {
    return hy_parse_int(text, "value", line);
}

static double hy_string_to_double(const char *text, int line) {
    return hy_parse_double(text, "value", line);
}

static bool hy_string_to_bool(const char *text, int line) {
    return hy_parse_bool(text, "value", line);
}

static const char *hy_int_to_string(int64_t value) {
    char buffer[32];
    snprintf(buffer, sizeof(buffer), "%" PRId64, value);
    return hy_str_concat(buffer, "");
}

static const char *hy_double_to_string(double value) {
    char buffer[64];
    snprintf(buffer, sizeof(buffer), "%g", value);
    return hy_str_concat(buffer, "");
}

static const char *hy_bool_to_string(bool value) {
    return value ? "true" : "false";
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
