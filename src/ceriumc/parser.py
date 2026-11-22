"""Recursive-descent parser for Cerium."""

from . import nodes
from .errors import CeriumError

TYPE_KEYWORDS = ("int", "double", "bool", "string")


class Parser:
    def __init__(self, tokens, filename: str = "<input>"):
        self.tokens = tokens
        self.filename = filename
        self.i = 0

    # -- token helpers -----------------------------------------------------

    @property
    def current(self):
        return self.tokens[self.i]

    def peek(self, offset: int = 0):
        index = min(self.i + offset, len(self.tokens) - 1)
        return self.tokens[index]

    def advance(self):
        token = self.current
        if token.kind != "eof":
            self.i += 1
        return token

    def check(self, value: str) -> bool:
        token = self.current
        return token.kind in ("op", "kw") and token.value == value

    def match(self, *values: str):
        for value in values:
            if self.check(value):
                return self.advance()
        return None

    def expect(self, value: str):
        if self.check(value):
            return self.advance()
        raise self.error(f"expected '{value}', got {self.current.describe()}")

    def expect_identifier(self):
        token = self.current
        if token.kind == "ident":
            return self.advance()
        raise self.error(f"expected identifier, got {token.describe()}")

    def expect_type(self):
        token = self.current
        if token.kind == "kw" and token.value in TYPE_KEYWORDS:
            self.advance()
            return token.value, token
        if token.kind == "ident":
            self.advance()
            return token.value, token
        raise self.error(f"expected type, got {token.describe()}")

    def error(self, message: str, token=None) -> CeriumError:
        token = token or self.current
        return CeriumError(message, token.line, token.col)

    # -- program -----------------------------------------------------------

    def parse(self) -> nodes.Program:
        statements = []
        while self.current.kind != "eof":
            statements.append(self.parse_statement())
        return nodes.Program(statements)

    def parse_statement(self):
        token = self.current

        if token.kind == "kw":
            if token.value == "func":
                return self.parse_func_decl()
            if token.value == "struct":
                return self.parse_struct_decl()
            if token.value == "if":
                return self.parse_if()
            if token.value == "while":
                return self.parse_while()
            if token.value == "for":
                return self.parse_for()
            if token.value == "loop":
                return self.parse_loop()
            if token.value == "return":
                return self.parse_return()
            if token.value == "break":
                return self.parse_break()
            if token.value == "continue":
                return self.parse_continue()

        if self.starts_var_decl():
            return self.parse_var_decl()

        if self.looks_like_assignment():
            return self.parse_assignment()

        return self.parse_expr_statement()

    # -- declarations ------------------------------------------------------

    def parse_struct_decl(self) -> nodes.StructDecl:
        start = self.advance()  # 'struct'
        name_token = self.expect_identifier()
        self.expect("{")
        fields = []
        while not self.check("}"):
            if self.current.kind == "eof":
                raise self.error("expected '}', got end of file")
            type_name, type_token = self.expect_type()
            field_token = self.expect_identifier()
            self.expect(";")
            fields.append(
                nodes.Field(
                    field_token.value,
                    type_name,
                    field_token.line,
                    field_token.col,
                )
            )
        self.expect("}")
        if not fields:
            raise self.error(
                f"struct '{name_token.value}' must declare at least one field",
                name_token,
            )
        return nodes.StructDecl(
            name_token.value, fields, start.line, start.col
        )

    def parse_func_decl(self) -> nodes.FuncDecl:
        start = self.advance()  # 'func'
        name_token = self.expect_identifier()
        self.expect("(")
        params = []
        while not self.check(")"):
            type_name, _ = self.expect_type()
            param_token = self.expect_identifier()
            params.append(
                nodes.Param(
                    param_token.value,
                    type_name,
                    param_token.line,
                    param_token.col,
                )
            )
            if not self.check(","):
                break
            self.advance()
        self.expect(")")
        self.expect("->")

        if self.check("void"):
            return_type = "void"
            self.advance()
        else:
            return_type, _ = self.expect_type()

        body = self.parse_block()
        return nodes.FuncDecl(
            name_token.value,
            params,
            return_type,
            body,
            start.line,
            start.col,
        )

    # -- statements --------------------------------------------------------

    def parse_var_decl(self) -> nodes.VarDecl:
        type_name, _ = self.expect_type()
        name_token = self.expect_identifier()
        self.expect("=")
        value = self.parse_expression()
        self.expect(";")
        return nodes.VarDecl(
            name_token.value,
            type_name,
            value,
            name_token.line,
            name_token.col,
        )

    def parse_assignment(self, require_semicolon: bool = True) -> nodes.Assign:
        start = self.current
        target = self.parse_lvalue()
        self.expect("=")
        value = self.parse_expression()
        if require_semicolon:
            self.expect(";")
        return nodes.Assign(target, value, start.line, start.col)

    def parse_lvalue(self):
        token = self.expect_identifier()
        base = nodes.Var(token.value, token.line, token.col)
        while self.check("."):
            dot = self.advance()
            field_token = self.expect_identifier()
            base = nodes.FieldAccess(
                base, field_token.value, dot.line, dot.col
            )
        return base

    def parse_expr_statement(self) -> nodes.ExprStmt:
        token = self.current
        value = self.parse_expression()
        self.expect(";")
        return nodes.ExprStmt(value, token.line, token.col)

    def parse_if(self) -> nodes.If:
        start = self.advance()  # 'if'
        branches = []

        self.expect("(")
        condition = self.parse_expression()
        self.expect(")")
        branches.append((condition, self.parse_block()))

        else_body = None
        while self.check("else"):
            self.advance()
            if self.check("if"):
                self.advance()
                self.expect("(")
                condition = self.parse_expression()
                self.expect(")")
                branches.append((condition, self.parse_block()))
            else:
                else_body = self.parse_block()
                break

        return nodes.If(branches, else_body, start.line, start.col)

    def parse_while(self) -> nodes.While:
        start = self.advance()  # 'while'
        self.expect("(")
        condition = self.parse_expression()
        self.expect(")")
        body = self.parse_block()
        return nodes.While(condition, body, start.line, start.col)

    def parse_for(self) -> nodes.For:
        start = self.advance()  # 'for'
        self.expect("(")

        if self.starts_var_decl():
            init = self.parse_var_decl()
        else:
            init = self.parse_assignment()

        condition = self.parse_expression()
        self.expect(";")
        update = self.parse_assignment(require_semicolon=False)
        self.expect(")")
        body = self.parse_block()
        return nodes.For(init, condition, update, body, start.line, start.col)

    def parse_loop(self) -> nodes.Loop:
        start = self.advance()  # 'loop'
        body = self.parse_block()
        return nodes.Loop(body, start.line, start.col)

    def parse_return(self) -> nodes.Return:
        start = self.advance()  # 'return'
        value = None
        if not self.check(";"):
            value = self.parse_expression()
        self.expect(";")
        return nodes.Return(value, start.line, start.col)

    def parse_break(self) -> nodes.Break:
        start = self.advance()  # 'break'
        self.expect(";")
        return nodes.Break(start.line, start.col)

    def parse_continue(self) -> nodes.Continue:
        start = self.advance()  # 'continue'
        self.expect(";")
        return nodes.Continue(start.line, start.col)

    def parse_block(self):
        self.expect("{")
        statements = []
        while not self.check("}"):
            if self.current.kind == "eof":
                raise self.error("expected '}', got end of file")
            statements.append(self.parse_statement())
        self.expect("}")
        return statements

    # -- expression detection ---------------------------------------------

    def starts_var_decl(self) -> bool:
        token = self.current
        if token.kind == "kw" and token.value in TYPE_KEYWORDS:
            return True
        return token.kind == "ident" and self.peek(1).kind == "ident"

    def looks_like_assignment(self) -> bool:
        if self.current.kind != "ident":
            return False
        offset = 1
        while True:
            token = self.peek(offset)
            if token.kind == "op" and token.value == ".":
                if self.peek(offset + 1).kind != "ident":
                    return False
                offset += 2
                continue
            break
        token = self.peek(offset)
        return token.kind == "op" and token.value == "="

    # -- expressions -------------------------------------------------------

    def parse_expression(self):
        return self.parse_or()

    def parse_or(self):
        expr = self.parse_and()
        while self.check("||"):
            operator = self.advance()
            right = self.parse_and()
            expr = nodes.Binary("||", expr, right, operator.line, operator.col)
        return expr

    def parse_and(self):
        expr = self.parse_equality()
        while self.check("&&"):
            operator = self.advance()
            right = self.parse_equality()
            expr = nodes.Binary("&&", expr, right, operator.line, operator.col)
        return expr

    def parse_equality(self):
        expr = self.parse_comparison()
        while self.check("==") or self.check("!="):
            operator = self.advance()
            right = self.parse_comparison()
            expr = nodes.Binary(operator.value, expr, right, operator.line, operator.col)
        return expr

    def parse_comparison(self):
        expr = self.parse_term()
        while (
            self.check("<")
            or self.check("<=")
            or self.check(">")
            or self.check(">=")
        ):
            operator = self.advance()
            right = self.parse_term()
            expr = nodes.Binary(operator.value, expr, right, operator.line, operator.col)
        return expr

    def parse_term(self):
        expr = self.parse_factor()
        while self.check("+") or self.check("-"):
            operator = self.advance()
            right = self.parse_factor()
            expr = nodes.Binary(operator.value, expr, right, operator.line, operator.col)
        return expr

    def parse_factor(self):
        expr = self.parse_unary()
        while self.check("*") or self.check("/") or self.check("%"):
            operator = self.advance()
            right = self.parse_unary()
            expr = nodes.Binary(operator.value, expr, right, operator.line, operator.col)
        return expr

    def parse_unary(self):
        token = self.current
        if token.kind == "op" and token.value in ("-", "!"):
            self.advance()
            operand = self.parse_unary()
            return nodes.Unary(token.value, operand, token.line, token.col)
        return self.parse_primary()

    def parse_primary(self):
        expr = self.parse_primary_atom()
        while self.check("."):
            dot = self.advance()
            field_token = self.expect_identifier()
            expr = nodes.FieldAccess(
                expr, field_token.value, dot.line, dot.col
            )
        return expr

    def parse_primary_atom(self):
        token = self.current

        if token.kind == "int":
            self.advance()
            return nodes.IntLit(token.value, token.line, token.col)

        if token.kind == "double":
            self.advance()
            return nodes.FloatLit(
                float(token.value), token.value, token.line, token.col
            )

        if token.kind == "string":
            self.advance()
            return nodes.StringLit(token.value, token.line, token.col)

        if token.kind == "kw" and token.value in ("true", "false"):
            self.advance()
            return nodes.BoolLit(token.value == "true", token.line, token.col)

        if token.kind == "ident":
            self.advance()
            if self.check("("):
                args = self.parse_arguments()
                return nodes.Call(token.value, args, token.line, token.col)
            if self.check("{"):
                fields = self.parse_struct_fields()
                return nodes.StructLit(
                    token.value, fields, token.line, token.col
                )
            return nodes.Var(token.value, token.line, token.col)

        if self.check("("):
            self.advance()
            expr = self.parse_expression()
            self.expect(")")
            return expr

        raise self.error(f"expected expression, got {token.describe()}")

    def parse_struct_fields(self):
        self.expect("{")
        fields = []
        if not self.check("}"):
            while True:
                name_token = self.expect_identifier()
                self.expect("=")
                value = self.parse_expression()
                fields.append(
                    nodes.FieldInit(
                        name_token.value,
                        value,
                        name_token.line,
                        name_token.col,
                    )
                )
                if not self.check(","):
                    break
                self.advance()
        self.expect("}")
        return fields

    def parse_arguments(self):
        self.expect("(")
        args = []
        if not self.check(")"):
            args.append(self.parse_expression())
            while self.check(","):
                self.advance()
                args.append(self.parse_expression())
        self.expect(")")
        return args
