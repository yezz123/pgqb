"""A simple SQL query builder for PostgreSQL."""

from __future__ import annotations

__version__ = "0.1.0"

__all__ = (
    "As",
    "BIGINT",
    "BIGSERIAL",
    "BIT",
    "BOOLEAN",
    "BOX",
    "BYTEA",
    "CHAR",
    "CIDR",
    "CIRCLE",
    "Column",
    "Column",
    "DATE",
    "DOUBLE",
    "Delete",
    "Expression",
    "From",
    "INET",
    "INTEGER",
    "INTERVAL",
    "InsertInto",
    "JSON",
    "JSONB",
    "Join",
    "LINE",
    "LSEG",
    "LeftJoin",
    "LogicGate",
    "MACADDR",
    "MACADDR8",
    "MONEY",
    "NUMERIC",
    "On",
    "OrderBy",
    "PATH",
    "PGEnum",
    "PG_LSN",
    "PG_SNAPSHOT",
    "POINT",
    "POLYGON",
    "QueryBuilder",
    "QueryBuilder",
    "REAL",
    "RightJoin",
    "SERIAL",
    "SMALLINT",
    "SMALLSERIAL",
    "SQLType",
    "Select",
    "Set",
    "TEXT",
    "TEXT",
    "TIME",
    "TIMESTAMP",
    "TSQUERY",
    "TSVECTOR",
    "Table",
    "Table",
    "UUID",
    "UUID",
    "Update",
    "VARBIT",
    "VARCHAR",
    "Values",
    "Where",
    "XML",
    "delete_from",
    "insert_into",
    "select",
    "update",
)

from typing import Type

from pgqb.builder import (
    As,
    BooleanOperator,
    Column,
    Delete,
    Expression,
    From,
    InsertInto,
    Join,
    LeftJoin,
    LogicGate,
    On,
    OrderBy,
    QueryBuilder,
    RightJoin,
    Select,
    Set,
    Table,
    Update,
    Values,
    Where,
)
from pgqb.types import (
    BIGINT,
    BIGSERIAL,
    BIT,
    BOOLEAN,
    BOX,
    BYTEA,
    CHAR,
    CIDR,
    CIRCLE,
    DATE,
    DOUBLE,
    INET,
    INTEGER,
    INTERVAL,
    JSON,
    JSONB,
    LINE,
    LSEG,
    MACADDR,
    MACADDR8,
    MONEY,
    NUMERIC,
    PATH,
    PG_LSN,
    PG_SNAPSHOT,
    POINT,
    POLYGON,
    REAL,
    SERIAL,
    SMALLINT,
    SMALLSERIAL,
    TEXT,
    TIME,
    TIMESTAMP,
    TSQUERY,
    TSVECTOR,
    UUID,
    VARBIT,
    VARCHAR,
    XML,
    PGEnum,
    SQLType,
)


def insert_into(table: Type[Table]) -> InsertInto:
    """Build an insert query."""
    return InsertInto(table)


def delete_from(table: Type[Table]) -> Delete:
    """Build a delete query."""
    return Delete(table)


def select(*args: Column | Type[Table] | As) -> Select:
    """Build a select query."""
    return Select(*args)


def update(table: Type[Table]) -> Update:
    """Build an update query."""
    return Update(table)


def join(table: Type[Table]) -> Join:
    """Build a join query."""
    return Join(table)


def left_join(table: Type[Table]) -> Join:
    """Build a left join query."""
    return LeftJoin(table)


def right_join(table: Type[Table]) -> Join:
    """Build a right join query."""
    return RightJoin(table)


def on(evaluation: Expression, *evaluations: Expression | LogicGate) -> On:
    """Build an "on" query for a join."""
    return On(evaluation, *evaluations)


def and_(evaluation: Expression, *evaluations: Expression | LogicGate) -> LogicGate:
    """Build an "and" expression for a part of a query."""
    return LogicGate(BooleanOperator.AND, evaluation, *evaluations)


def and_not(evaluation: Expression, *evaluations: Expression | LogicGate) -> LogicGate:
    """Build an "and not" expression for a part of a query."""
    return LogicGate(BooleanOperator.AND_NOT, evaluation, *evaluations)


def or_(evaluation: Expression, *evaluations: Expression | LogicGate) -> LogicGate:
    """Build an "or" expression for a part of a query."""
    return LogicGate(BooleanOperator.OR, evaluation, *evaluations)


def or_not(evaluation: Expression, *evaluations: Expression | LogicGate) -> LogicGate:
    """Build an "or not" expression for a part of a query."""
    return LogicGate(BooleanOperator.OR_NOT, evaluation, *evaluations)
