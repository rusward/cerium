"""AST node definitions for Cerium."""

from dataclasses import dataclass
from typing import Any, List, Optional, Tuple


@dataclass
class Program:
    statements: List[Any]


# -- expressions -----------------------------------------------------------


@dataclass
class IntLit:
    value: int
    line: int
    col: int


@dataclass
class FloatLit:
    value: float
    raw: str
    line: int
    col: int


@dataclass
class StringLit:
    value: str
    line: int
    col: int


@dataclass
class BoolLit:
    value: bool
    line: int
    col: int


@dataclass
class Var:
    name: str
    line: int
    col: int


@dataclass
class FieldAccess:
    base: Any
    field: str
    line: int
    col: int


@dataclass
class FieldInit:
    name: str
    expr: Any
    line: int
    col: int


@dataclass
class StructLit:
    type_name: str
    fields: List[FieldInit]
    line: int
    col: int


@dataclass
class Call:
    name: str
    args: List[Any]
    line: int
    col: int


@dataclass
class Unary:
    op: str
    operand: Any
    line: int
    col: int


@dataclass
class Binary:
    op: str
    left: Any
    right: Any
    line: int
    col: int


# -- declarations ----------------------------------------------------------


@dataclass
class Field:
    name: str
    type_name: str
    line: int
    col: int


@dataclass
class StructDecl:
    name: str
    fields: List[Field]
    line: int
    col: int


@dataclass
class Param:
    name: str
    type_name: str
    line: int
    col: int


@dataclass
class FuncDecl:
    name: str
    params: List[Param]
    return_type: str
    body: List[Any]
    line: int
    col: int


# -- statements ------------------------------------------------------------


@dataclass
class VarDecl:
    name: str
    type_name: str
    expr: Any
    line: int
    col: int


@dataclass
class Assign:
    target: Any  # Var or FieldAccess
    expr: Any
    line: int
    col: int


@dataclass
class ExprStmt:
    expr: Any
    line: int
    col: int


@dataclass
class If:
    branches: List[Tuple[Any, List[Any]]]
    else_body: Optional[List[Any]]
    line: int
    col: int


@dataclass
class While:
    cond: Any
    body: List[Any]
    line: int
    col: int


@dataclass
class For:
    init: Any  # VarDecl or Assign
    cond: Any
    update: Assign
    body: List[Any]
    line: int
    col: int


@dataclass
class Loop:
    body: List[Any]
    line: int
    col: int


@dataclass
class Break:
    line: int
    col: int


@dataclass
class Continue:
    line: int
    col: int


@dataclass
class Return:
    expr: Optional[Any]
    line: int
    col: int
