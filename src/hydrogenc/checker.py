"""Static type checking for Hydrogen."""

from dataclasses import dataclass

from . import nodes
from .errors import Diagnostic, HydrogenErrors

INT = "int"
DOUBLE = "double"
BOOL = "bool"
STRING = "string"
VOID = "void"
ERROR = "<error>"

SCALARS = {INT, DOUBLE, BOOL, STRING}
NUMERIC = {INT, DOUBLE}

BUILTIN_NAMES = {
    "log",
    "input",
    "inputInt",
    "inputDouble",
    "inputBool",
    "toString",
    "toInt",
    "toDouble",
    "toBool",
}
INPUT_RETURN_TYPES = {
    "input": STRING,
    "inputInt": INT,
    "inputDouble": DOUBLE,
    "inputBool": BOOL,
}
CONVERSION_RETURN_TYPES = {
    "toString": STRING,
    "toInt": INT,
    "toDouble": DOUBLE,
    "toBool": BOOL,
}

INT64_MAX = 2**63 - 1


@dataclass
class FunctionSig:
    name: str
    param_types: list
    return_type: str


class TypeChecker:
    def __init__(self, filename: str = "<input>"):
        self.filename = filename
        self.scopes = [{}]
        self.errors = []
        self.types = {}
        self.structs = {}
        self.functions = {}
        self.current_return = None
        self.current_function = None
        self.loop_depth = 0

    def check(self, program: nodes.Program):
        self.collect_structs(program)
        self.collect_functions(program)

        for statement in program.statements:
            if isinstance(statement, (nodes.StructDecl, nodes.FuncDecl)):
                continue
            self.check_statement(statement)

        for statement in program.statements:
            if isinstance(statement, nodes.FuncDecl):
                self.check_function(statement)

        if self.errors:
            raise HydrogenErrors(self.errors)
        return self.types

    # -- declarations ------------------------------------------------------

    def collect_structs(self, program: nodes.Program) -> None:
        for statement in program.statements:
            if not isinstance(statement, nodes.StructDecl):
                continue
            if statement.name in self.structs:
                self.add_error(
                    statement, f"struct '{statement.name}' is already declared"
                )
                continue

            fields = {}
            for field in statement.fields:
                if field.type_name not in SCALARS:
                    self.add_error(
                        field,
                        f"field '{field.name}' must have a scalar type "
                        f"(int, double, bool or string)",
                    )
                if field.name in fields:
                    self.add_error(
                        field,
                        f"field '{field.name}' is already declared "
                        f"in struct '{statement.name}'",
                    )
                else:
                    fields[field.name] = (
                        field.type_name
                        if field.type_name in SCALARS
                        else ERROR
                    )
            self.structs[statement.name] = fields

    def collect_functions(self, program: nodes.Program) -> None:
        for statement in program.statements:
            if not isinstance(statement, nodes.FuncDecl):
                continue

            if statement.name in BUILTIN_NAMES:
                self.add_error(
                    statement,
                    f"cannot declare function '{statement.name}': it is built in",
                )
                continue

            param_types = []
            for param in statement.params:
                if param.type_name not in SCALARS and param.type_name not in self.structs:
                    self.add_error(
                        param, f"unknown type '{param.type_name}'"
                    )
                    param_types.append(ERROR)
                else:
                    param_types.append(param.type_name)

            if (
                statement.return_type != VOID
                and statement.return_type not in SCALARS
                and statement.return_type not in self.structs
            ):
                self.add_error(
                    statement, f"unknown return type '{statement.return_type}'"
                )
                return_type = ERROR
            else:
                return_type = statement.return_type

            if statement.name in self.functions:
                self.add_error(
                    statement,
                    f"function '{statement.name}' is already declared",
                )
                continue

            self.functions[statement.name] = FunctionSig(
                statement.name, param_types, return_type
            )

    def check_function(self, function: nodes.FuncDecl) -> None:
        saved_scopes = self.scopes
        saved_return = self.current_return
        saved_function = self.current_function
        saved_loop = self.loop_depth

        self.scopes = [{}]
        self.loop_depth = 0
        self.current_function = function.name

        if function.return_type == VOID:
            self.current_return = VOID
        elif function.return_type in SCALARS or function.return_type in self.structs:
            self.current_return = function.return_type
        else:
            self.current_return = ERROR

        for param in function.params:
            if param.type_name in SCALARS or param.type_name in self.structs:
                param_type = param.type_name
            else:
                param_type = ERROR
            self.declare(param.name, param_type, param)

        errors_before = len(self.errors)
        for statement in function.body:
            self.check_statement(statement)

        if (
            self.current_return not in (VOID, ERROR)
            and len(self.errors) == errors_before
            and not self.block_always_returns(function.body)
        ):
            self.add_error(
                function,
                f"function '{function.name}' must return a value on all paths",
            )

        self.scopes = saved_scopes
        self.current_return = saved_return
        self.current_function = saved_function
        self.loop_depth = saved_loop

    # -- helpers -----------------------------------------------------------

    def add_error(self, node, message: str) -> None:
        self.errors.append(Diagnostic(message, node.line, node.col))

    def set_type(self, node, type_name: str) -> str:
        self.types[id(node)] = type_name
        return type_name

    def declare(self, name: str, type_name: str, node) -> None:
        for index, scope in enumerate(self.scopes):
            if name in scope:
                if index == len(self.scopes) - 1:
                    self.add_error(
                        node, f"variable '{name}' is already declared in this scope"
                    )
                else:
                    self.add_error(
                        node, f"variable '{name}' is already declared in an outer scope"
                    )
                return
        self.scopes[-1][name] = type_name

    def lookup(self, name: str, node) -> str:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        self.add_error(node, f"undefined variable '{name}'")
        return ERROR

    def block_always_returns(self, statements) -> bool:
        for statement in statements:
            if self.statement_always_returns(statement):
                return True
        return False

    def statement_always_returns(self, statement) -> bool:
        if isinstance(statement, nodes.Return):
            return True
        if isinstance(statement, nodes.If):
            if statement.else_body is None:
                return False
            if not all(
                self.block_always_returns(body)
                for _, body in statement.branches
            ):
                return False
            return self.block_always_returns(statement.else_body)
        return False

    # -- statements --------------------------------------------------------

    def check_statement(self, statement) -> None:
        if isinstance(statement, nodes.VarDecl):
            value_type = self.check_expression(statement.expr)
            if statement.type_name not in SCALARS and statement.type_name not in self.structs:
                self.add_error(
                    statement, f"unknown type '{statement.type_name}'"
                )
                declared_type = ERROR
            else:
                declared_type = statement.type_name
                if value_type != ERROR and value_type != declared_type:
                    self.add_error(
                        statement,
                        f"cannot initialize variable '{statement.name}' "
                        f"of type '{declared_type}' "
                        f"with a value of type '{value_type}'",
                    )
            self.declare(statement.name, declared_type, statement)

        elif isinstance(statement, nodes.Assign):
            self.check_assignment(statement)

        elif isinstance(statement, nodes.ExprStmt):
            if not isinstance(statement.expr, nodes.Call):
                self.check_expression(statement.expr)
                self.add_error(
                    statement, "expression statements must be function calls"
                )
            else:
                self.check_expression(statement.expr)

        elif isinstance(statement, nodes.If):
            for condition, body in statement.branches:
                self.check_condition(condition)
                self.check_block(body)
            if statement.else_body is not None:
                self.check_block(statement.else_body)

        elif isinstance(statement, nodes.While):
            self.check_condition(statement.cond)
            self.loop_depth += 1
            self.check_block(statement.body)
            self.loop_depth -= 1

        elif isinstance(statement, nodes.For):
            self.scopes.append({})
            self.check_statement(statement.init)
            self.check_condition(statement.cond)
            self.check_assignment(statement.update)
            self.loop_depth += 1
            self.check_block(statement.body)
            self.loop_depth -= 1
            self.scopes.pop()

        elif isinstance(statement, nodes.Loop):
            self.loop_depth += 1
            self.check_block(statement.body)
            self.loop_depth -= 1

        elif isinstance(statement, nodes.Break):
            if self.loop_depth == 0:
                self.add_error(statement, "'break' outside of a loop")

        elif isinstance(statement, nodes.Continue):
            if self.loop_depth == 0:
                self.add_error(statement, "'continue' outside of a loop")

        elif isinstance(statement, nodes.Return):
            self.check_return(statement)

        elif isinstance(statement, (nodes.StructDecl, nodes.FuncDecl)):
            self.add_error(
                statement,
                "struct and function declarations are only allowed at top level",
            )

    def check_assignment(self, assignment: nodes.Assign) -> None:
        target_type = self.check_expression(assignment.target)
        value_type = self.check_expression(assignment.expr)
        if (
            target_type != ERROR
            and value_type != ERROR
            and target_type != value_type
        ):
            self.add_error(
                assignment,
                f"cannot assign a value of type '{value_type}' "
                f"to {self.describe_target(assignment.target)} "
                f"of type '{target_type}'",
            )

    def describe_target(self, target) -> str:
        if isinstance(target, nodes.Var):
            return f"variable '{target.name}'"
        if isinstance(target, nodes.FieldAccess):
            return f"field '{self.target_text(target)}'"
        return "target"

    def target_text(self, target) -> str:
        if isinstance(target, nodes.Var):
            return target.name
        if isinstance(target, nodes.FieldAccess):
            return f"{self.target_text(target.base)}.{target.field}"
        return "?"

    def check_return(self, statement: nodes.Return) -> None:
        if self.current_return is None:
            if statement.expr is not None:
                self.check_expression(statement.expr)
            self.add_error(statement, "'return' outside of a function")
            return

        if self.current_return == VOID:
            if statement.expr is not None:
                self.check_expression(statement.expr)
                self.add_error(
                    statement,
                    f"void function '{self.current_function}' cannot return a value",
                )
            return

        if statement.expr is None:
            self.add_error(
                statement,
                f"function '{self.current_function}' must return a value",
            )
            return

        value_type = self.check_expression(statement.expr)
        if (
            self.current_return != ERROR
            and value_type != ERROR
            and value_type != self.current_return
        ):
            self.add_error(
                statement,
                f"cannot return a value of type '{value_type}' "
                f"from function '{self.current_function}' "
                f"returning '{self.current_return}'",
            )

    def check_condition(self, condition) -> None:
        type_name = self.check_expression(condition)
        if type_name not in (BOOL, ERROR):
            self.add_error(
                condition,
                f"condition must be of type 'bool', got '{type_name}'",
            )

    def check_block(self, statements) -> None:
        self.scopes.append({})
        for statement in statements:
            self.check_statement(statement)
        self.scopes.pop()

    # -- expressions -------------------------------------------------------

    def check_expression(self, expression) -> str:
        if isinstance(expression, nodes.IntLit):
            if expression.value > INT64_MAX:
                self.add_error(
                    expression, "integer literal is out of range for type 'int'"
                )
                return self.set_type(expression, ERROR)
            return self.set_type(expression, INT)

        if isinstance(expression, nodes.FloatLit):
            return self.set_type(expression, DOUBLE)

        if isinstance(expression, nodes.StringLit):
            return self.set_type(expression, STRING)

        if isinstance(expression, nodes.BoolLit):
            return self.set_type(expression, BOOL)

        if isinstance(expression, nodes.Var):
            return self.set_type(expression, self.lookup(expression.name, expression))

        if isinstance(expression, nodes.FieldAccess):
            return self.check_field_access(expression)

        if isinstance(expression, nodes.StructLit):
            return self.check_struct_literal(expression)

        if isinstance(expression, nodes.Call):
            return self.check_call(expression)

        if isinstance(expression, nodes.Unary):
            return self.check_unary(expression)

        if isinstance(expression, nodes.Binary):
            left_type = self.check_expression(expression.left)
            right_type = self.check_expression(expression.right)
            result_type = self.binary_type(expression, left_type, right_type)
            return self.set_type(expression, result_type)

        raise AssertionError(f"unexpected expression node: {expression!r}")

    def check_field_access(self, access: nodes.FieldAccess) -> str:
        base_type = self.check_expression(access.base)
        if base_type == ERROR:
            return self.set_type(access, ERROR)

        if base_type not in self.structs:
            self.add_error(
                access, f"type '{base_type}' has no fields"
            )
            return self.set_type(access, ERROR)

        fields = self.structs[base_type]
        if access.field not in fields:
            self.add_error(
                access,
                f"struct '{base_type}' has no field '{access.field}'",
            )
            return self.set_type(access, ERROR)

        return self.set_type(access, fields[access.field])

    def check_struct_literal(self, literal: nodes.StructLit) -> str:
        field_types = {}
        for init in literal.fields:
            field_type = self.check_expression(init.expr)
            field_types[id(init)] = field_type

        if literal.type_name not in self.structs:
            self.add_error(
                literal, f"unknown struct '{literal.type_name}'"
            )
            return self.set_type(literal, ERROR)

        struct_fields = self.structs[literal.type_name]
        seen = set()

        for init in literal.fields:
            if init.name in seen:
                self.add_error(
                    init,
                    f"field '{init.name}' is initialized more than once",
                )
                continue
            seen.add(init.name)

            if init.name not in struct_fields:
                self.add_error(
                    init,
                    f"struct '{literal.type_name}' has no field '{init.name}'",
                )
                continue

            expected = struct_fields[init.name]
            actual = field_types[id(init)]
            if (
                expected != ERROR
                and actual != ERROR
                and expected != actual
            ):
                self.add_error(
                    init,
                    f"field '{init.name}' of struct '{literal.type_name}' "
                    f"must have type '{expected}', got '{actual}'",
                )

        for name in struct_fields:
            if name not in seen:
                self.add_error(
                    literal,
                    f"field '{name}' of struct "
                    f"'{literal.type_name}' is not initialized",
                )

        return self.set_type(literal, literal.type_name)

    def check_call(self, call: nodes.Call) -> str:
        if call.name == "log":
            for argument in call.args:
                argument_type = self.check_expression(argument)
                if argument_type == VOID:
                    self.add_error(
                        argument,
                        "cannot pass a value of type 'void' to function 'log'",
                    )
                elif argument_type in self.structs:
                    self.add_error(
                        argument,
                        f"cannot pass struct '{argument_type}' to function 'log'; "
                        f"pass its fields instead",
                    )
            return self.set_type(call, VOID)

        if call.name in INPUT_RETURN_TYPES:
            return self.check_input_call(call)

        if call.name in CONVERSION_RETURN_TYPES:
            return self.check_conversion_call(call)

        signature = self.functions.get(call.name)
        if signature is None:
            for argument in call.args:
                self.check_expression(argument)
            self.add_error(call, f"unknown function '{call.name}'")
            return self.set_type(call, ERROR)

        if len(call.args) != len(signature.param_types):
            self.add_error(
                call,
                f"function '{call.name}' expects "
                f"{len(signature.param_types)} arguments, "
                f"got {len(call.args)}",
            )

        for index, argument in enumerate(call.args):
            argument_type = self.check_expression(argument)
            if argument_type == VOID:
                self.add_error(
                    argument,
                    f"cannot pass a value of type 'void' "
                    f"to function '{call.name}'",
                )
                continue
            if index >= len(signature.param_types):
                continue
            expected = signature.param_types[index]
            if (
                expected != ERROR
                and argument_type != ERROR
                and expected != argument_type
            ):
                self.add_error(
                    argument,
                    f"argument {index + 1} of function '{call.name}' "
                    f"must have type '{expected}', got '{argument_type}'",
                )

        return self.set_type(call, signature.return_type)

    def check_input_call(self, call: nodes.Call) -> str:
        for argument in call.args:
            self.check_expression(argument)

        if len(call.args) > 1:
            self.add_error(
                call,
                f"function '{call.name}' takes at most 1 argument, "
                f"got {len(call.args)}",
            )

        if call.args:
            prompt_type = self.types[id(call.args[0])]
            if prompt_type not in (ERROR, STRING):
                self.add_error(
                    call.args[0],
                    f"argument 1 of function '{call.name}' "
                    f"must have type 'string', got '{prompt_type}'",
                )

        return self.set_type(call, INPUT_RETURN_TYPES[call.name])

    def check_conversion_call(self, call: nodes.Call) -> str:
        for argument in call.args:
            self.check_expression(argument)

        if len(call.args) != 1:
            self.add_error(
                call,
                f"function '{call.name}' expects 1 argument, "
                f"got {len(call.args)}",
            )
            return self.set_type(call, CONVERSION_RETURN_TYPES[call.name])

        argument_type = self.types[id(call.args[0])]
        if argument_type == ERROR:
            return self.set_type(call, CONVERSION_RETURN_TYPES[call.name])

        if call.name == "toString":
            if argument_type not in SCALARS:
                self.add_error(
                    call.args[0],
                    f"cannot convert a value of type '{argument_type}' to string",
                )
        elif argument_type != STRING:
            self.add_error(
                call.args[0],
                f"argument 1 of function '{call.name}' "
                f"must have type 'string', got '{argument_type}'",
            )

        return self.set_type(call, CONVERSION_RETURN_TYPES[call.name])

    def check_unary(self, expression: nodes.Unary) -> str:
        operand_type = self.check_expression(expression.operand)

        if expression.op == "-":
            if operand_type in NUMERIC:
                return self.set_type(expression, operand_type)
            if operand_type != ERROR:
                self.add_error(
                    expression,
                    f"unary '-' cannot be applied to type '{operand_type}'",
                )
            return self.set_type(expression, ERROR)

        if expression.op == "!":
            if operand_type == BOOL:
                return self.set_type(expression, BOOL)
            if operand_type != ERROR:
                self.add_error(
                    expression, f"unary '!' cannot be applied to type '{operand_type}'"
                )
            return self.set_type(expression, ERROR)

        raise AssertionError(f"unexpected unary operator: {expression.op}")

    def binary_type(self, expression: nodes.Binary, left: str, right: str) -> str:
        if left == ERROR or right == ERROR:
            return ERROR

        op = expression.op

        if op == "+":
            if left == right and left in (INT, DOUBLE, STRING):
                return left
        elif op in ("-", "*", "/"):
            if left == right and left in NUMERIC:
                return left
        elif op == "%":
            if left == INT and right == INT:
                return INT
        elif op in ("<", "<=", ">", ">="):
            if left == right and left in NUMERIC:
                return BOOL
        elif op in ("==", "!="):
            if left == right and left in SCALARS:
                return BOOL
        elif op in ("&&", "||"):
            if left == BOOL and right == BOOL:
                return BOOL

        self.add_error(
            expression,
            f"operator '{op}' cannot be applied to types '{left}' and '{right}'",
        )
        return ERROR
