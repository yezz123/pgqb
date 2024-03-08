""" "Typed Python PostgreSQL query builder using Pydantic"""

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
