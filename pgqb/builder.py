"""Query building functions for pgqb.

This module provides a set of classes and functions for building SQL queries
in a Pythonic way. It includes support for various SQL operations such as
SELECT, INSERT, UPDATE, DELETE, JOIN, WHERE, ORDER BY, LIMIT, and OFFSET.
"""

from __future__ import annotations

import abc
import enum
import sys
import typing
from abc import ABC
from typing import Any, Type

from pgqb._snake import to_snake as snake
from pgqb.types import PGEnum, SQLType

if sys.version_info > (3, 10):  # pragma: no cover
    from typing import Self  # pragma: no cover
else:
    from typing_extensions import Self  # pragma: no cover


class QueryBuilder(abc.ABC):
    """Base class for all query builders.

    This abstract class defines the interface for all query builders in the system.
    All specific query builder classes should inherit from this base class.
    """

    @abc.abstractmethod
    def prepare(self) -> tuple[str, list[Any]]:
        """Get all params and the SQL string.

        Returns:
            A tuple containing the SQL string and a list of parameters.
        """


class _OperatorMixin(QueryBuilder, abc.ABC):  # noqa: PLW1641
    """Mixin class providing common SQL comparison and arithmetic operators.

    This mixin adds methods for common SQL operators like >, <, =, !=, +, -, *, /, %.
    It also includes IS and IS NOT operators.
    """

    def __gt__(self, other: Any) -> Expression:
        """Greater than operator.

        Args:
            other: The value to compare against.

        Returns:
            An Expression representing the "greater than" comparison.
        """
        return Expression(self, ">", other)

    def __ge__(self, other: Any) -> Expression:
        """Greater than or equal to operator.

        Args:
            other: The value to compare against.

        Returns:
            An Expression representing the "greater than or equal to" comparison.
        """
        return Expression(self, ">=", other)

    def __lt__(self, other: Any) -> Expression:
        """Less than operator.

        Args:
            other: The value to compare against.

        Returns:
            An Expression representing the "less than" comparison.
        """
        return Expression(self, "<", other)

    def __le__(self, other: Any) -> Expression:
        """Less than or equal to operator.

        Args:
            other: The value to compare against.

        Returns:
            An Expression representing the "less than or equal to" comparison.
        """
        return Expression(self, "<=", other)

    def __eq__(self, other: object) -> Expression:  # type: ignore
        """Equality operator.

        For None, True, or False, uses IS operator instead of =.

        Args:
            other: The value to compare against.

        Returns:
            An Expression representing the equality comparison.
        """
        if other is None or other is True or other is False:
            return Expression(self, "IS", other)
        return Expression(self, "=", other)

    def __ne__(self, other: object) -> Expression:  # type: ignore
        """Inequality operator.

        For None, True, or False, uses IS NOT operator instead of !=.

        Args:
            other: The value to compare against.

        Returns:
            An Expression representing the inequality comparison.
        """
        if other is None or other is True or other is False:
            return Expression(self, "IS NOT", other)
        return Expression(self, "!=", other)

    def __add__(self, other: Any) -> Expression:
        """Addition operator.

        Args:
            other: The value to add.

        Returns:
            An Expression representing the addition operation.
        """
        return Expression(self, "+", other)

    def __sub__(self, other: Any) -> Expression:
        """Subtraction operator.

        Args:
            other: The value to subtract.

        Returns:
            An Expression representing the subtraction operation.
        """
        return Expression(self, "-", other)

    def __mul__(self, other: Any) -> Expression:
        """Multiplication operator.

        Args:
            other: The value to multiply by.

        Returns:
            An Expression representing the multiplication operation.
        """
        return Expression(self, "*", other)

    def __truediv__(self, other: Any) -> Expression:
        """Division operator.

        Args:
            other: The value to divide by.

        Returns:
            An Expression representing the division operation.
        """
        return Expression(self, "/", other)

    def __mod__(self, other: Any) -> Expression:
        """Modulo operator.

        Args:
            other: The value to mod by.

        Returns:
            An Expression representing the modulo operation.
        """
        return Expression(self, "%", other)

    def is_(self, other: Any) -> Expression:
        """Equality operator using IS.

        Args:
            other: The value to compare against.

        Returns:
            An Expression representing the IS comparison.
        """
        if other is None or other is True or other is False:
            return Expression(self, "IS", other)
        return Expression(self, "=", other)

    def is_not(self, other: Any) -> Expression:
        """Inequality operator using IS NOT.

        Args:
            other: The value to compare against.

        Returns:
            An Expression representing the IS NOT comparison.
        """
        if other is None or other is True or other is False:
            return Expression(self, "IS NOT", other)
        return Expression(self, "!=", other)


class As(QueryBuilder):
    """Represents an SQL AS clause for aliasing.

    This class is used to create aliases for columns or expressions in SQL queries.
    """

    def __init__(self, sub_query: Column | Expression, alias: str) -> None:
        """Initialize an As instance.

        Args:
            sub_query: The Column or Expression to be aliased.
            alias: The alias name.
        """
        self._sub_query = sub_query
        self._alias = alias

    def prepare(self) -> tuple[str, list[Any]]:
        """Prepare the AS clause.

        Returns:
            A tuple containing the SQL string for the AS clause and any parameters.
        """
        if isinstance(self._sub_query, Column):
            return f"{self._sub_query} AS {self._alias}", []
        sql, params = self._sub_query.prepare()
        return f"{sql} AS {self._alias}", params


class Column(_OperatorMixin):
    """Represents a column in a SQL table.

    This class encapsulates the properties and behaviors of a database column,
    including its data type, constraints, and other attributes.
    """

    def __init__(  # noqa: PLR0913
        self,
        sql_type: SQLType | Type[PGEnum] | None = None,
        *,
        check: str | None = None,
        default: Any | None = None,
        foreign_key: Column | None = None,
        index: bool = False,
        null: bool = False,
        primary: bool = False,
        unique: bool = False,
    ) -> None:
        """Initialize a Column instance.

        Args:
            sql_type: The SQL type for this column.
            check: The check constraint for this column.
            default: The default value for this column.
            foreign_key: The foreign key for this column.
            index: Whether to create an index for this column.
            null: Whether this column is nullable.
            primary: Whether this column is a primary key.
            unique: Whether this column is unique.
        """
        self.name = ""
        self.table = ""
        self._asc = True
        self._check = check
        self._default = default
        self._foreign_key = foreign_key
        self._index = index
        self._null = null
        self._primary = primary
        self._unique = unique
        self._sql_type = sql_type

    def __str__(self) -> str:
        """Get the string representation of this column.

        Returns:
            A string in the format "table.column".
        """
        return f"{self.table}.{self.name}"

    def __hash__(self) -> int:
        """Get the hash of this column.

        Returns:
            An integer hash value based on the string representation of the column.
        """
        return hash(str(self))

    def _create(self) -> str:
        """Get column create SQL.

        Returns:
            A string containing the SQL definition for creating this column.
        """
        null = " NOT NULL" if not self._null and not self._primary else ""
        unique = " UNIQUE" if self._unique else ""
        check = f" CHECK ({self._check})" if self._check else ""
        if self._default is not None:
            default = f" DEFAULT {self._default}" if self._default else " DEFAULT ''"
        else:
            default = ""
        if self._foreign_key is not None:
            sql_type = self._foreign_key._sql_type
        elif hasattr(self._sql_type, "pg_enum_name"):
            sql_type = self._sql_type.pg_enum_name()  # type: ignore
        else:
            sql_type = self._sql_type
        return f'"{self.name}" {sql_type}{default}{null}{unique}{check}'

    def prepare(self) -> tuple[str, list[Any]]:
        """Get column as SQL.

        Returns:
            A tuple containing the SQL string for this column and an empty list of parameters.
        """
        return str(self), []

    def as_(self, alias: str) -> As:
        """Create an alias for this column.

        Args:
            alias: The alias name for the column.

        Returns:
            An As instance representing the aliased column.
        """
        return As(self, alias)

    def asc(self) -> Column:
        """Set this column to be sorted in ascending order.

        Returns:
            A new Column instance with ascending sort order.
        """
        return self.asc_or_desc(True)

    def desc(self) -> Column:
        """Set this column to be sorted in descending order.

        Returns:
            A new Column instance with descending sort order.
        """
        return self.asc_or_desc(False)

    def asc_or_desc(self, asc: bool) -> Column:
        """Set this column to be sorted in ascending or descending order.

        Args:
            asc: True for ascending order, False for descending order.

        Returns:
            A new Column instance with the specified sort order.
        """
        col = Column()
        col.name = self.name
        col.table = self.table
        col._asc = asc
        return col


class Table(type):
    """Metaclass for representing SQL tables.

    This metaclass automatically processes class attributes to set up
    table names and columns based on the class definition.
    """

    __table_name__ = ""
    __table_columns__: dict[str, Column] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Initialize a subclass of Table.

        This method is called when a new subclass of Table is created. It sets up
        the table name and processes the class attributes to identify columns.

        Args:
            **kwargs: Additional keyword arguments.
        """
        super().__init_subclass__(**kwargs)
        table_name = f'"{snake(cls.__name__)}"'
        table_columns = {}
        for attr_name, attr_value in cls.__dict__.items():  # type: ignore
            if isinstance(attr_value, Column):
                column = getattr(cls, attr_name)
                column.name = attr_name
                column.table = table_name
                table_columns[attr_name] = column

        cls.__table_columns__ = table_columns
        cls.__table_name__ = table_name

    @classmethod
    def create_table(cls) -> str:
        """Generate SQL to create the table.

        Returns:
            A string containing the SQL CREATE TABLE statement for this table.
        """
        columns: list[str] = []
        foreign_keys: dict[str, list[tuple[str, str]]] = {}
        indexes: list[str] = []
        primaries: list[str] = []
        for col in cls.__table_columns__.values():
            columns.append(col._create())
            if fk := col._foreign_key:
                foreign_keys[fk.table] = foreign_keys.get(fk.table) or []
                foreign_keys[fk.table].append((col.name, fk.name))
            if col._index:
                indexes.append(f"CREATE INDEX ON {cls.__table_name__} ({col.name});")
            if col._primary:
                primaries.append(col.name)
        col_str = ",\n  ".join(columns)
        if col_str:
            col_str = f"  {col_str}"
        fks = []
        for table, column_pairs in foreign_keys.items():
            table_cols: list[str] = []
            other_table_cols: list[str] = []
            for pair in column_pairs:
                table_cols.append(pair[0])
                other_table_cols.append(pair[1])
            tc = ", ".join(table_cols)
            otc = ", ".join(other_table_cols)
            fks.append(f",\n  FOREIGN KEY ({tc}) REFERENCES {table} ({otc})")
        fk_str = "".join(fks)
        idx_str = "\n".join(indexes)
        if idx_str:
            idx_str = "\n" + idx_str
        pk_str = ", ".join(primaries)
        if pk_str:
            pk_str = f",\n  PRIMARY KEY ({pk_str})"
        table = (
            f"CREATE TABLE IF NOT EXISTS {cls.__table_name__}"
            f" (\n{col_str}{pk_str}{fk_str}\n)"
        )
        return f"{table};{idx_str}"


class _LimitMixin(QueryBuilder, abc.ABC):
    """Mixin class for adding LIMIT clause functionality."""

    def limit(self, limit: int) -> Limit:
        """Add a LIMIT clause to the query.

        Args:
            limit: The maximum number of rows to return.

        Returns:
            A Limit instance representing the LIMIT clause.
        """
        return Limit(self, limit)


class _OffsetMixin(QueryBuilder, abc.ABC):
    """Mixin class for adding OFFSET clause functionality."""

    def offset(self, offset: int) -> Offset:
        """Add an OFFSET clause to the query.

        Args:
            offset: The number of rows to skip.

        Returns:
            An Offset instance representing the OFFSET clause.
        """
        return Offset(self, offset)


class _PaginateMixin(_OffsetMixin, _LimitMixin, ABC):
    """Mixin class combining LIMIT and OFFSET functionality for pagination."""

    pass


class _OrderByMixin(QueryBuilder, abc.ABC):
    """Mixin class for adding ORDER BY clause functionality."""

    def order_by(self, *columns: Column) -> OrderBy:
        """Add an ORDER BY clause to the query.

        Args:
            *columns: The columns to order by.

        Returns:
            An OrderBy instance representing the ORDER BY clause.
        """
        return OrderBy(self, *columns)


class _WhereMixin(QueryBuilder, abc.ABC):
    """Mixin class for adding WHERE clause functionality."""

    def where(
        self, evaluation: Expression, *evaluations: Expression | LogicGate
    ) -> Where:
        """Add a WHERE clause to the query.

        Args:
            evaluation: The primary condition for the WHERE clause.
            *evaluations: Additional conditions to be combined with AND.

        Returns:
            A Where instance representing the WHERE clause.
        """
        return Where(self, evaluation, *evaluations)


class BooleanOperator(enum.Enum):
    """Enumeration of boolean operators used in SQL queries.

    This enum defines the various boolean operators that can be used
    in constructing complex SQL conditions.
    """

    AND = "AND"
    AND_NOT = "AND NOT"
    OR = "OR"
    OR_NOT = "OR NOT"
    IS = "IS"
    IS_NOT = "IS NOT"
    IN = "IN"
    NOT_IN = "NOT IN"


class LogicGate(QueryBuilder):
    """Represents a logical operation in SQL queries.

    This class is used to construct complex logical conditions by combining
    multiple expressions with boolean operators.
    """

    def __init__(
        self,
        boolean_operator: BooleanOperator,
        evaluation: Expression,
        *evaluations: Expression | LogicGate,
    ) -> None:
        """Initialize a LogicGate instance.

        Args:
            boolean_operator: The boolean operator to use.
            evaluation: The primary expression to evaluate.
            *evaluations: Additional expressions to combine with the primary expression.
        """
        self._evaluations = [evaluation] + list(evaluations)
        self._boolean_operator = boolean_operator

    def prepare(self) -> tuple[str, list[Any]]:
        """Prepare the logical operation for use in a SQL query.

        Returns:
            A tuple containing the SQL string for this logical operation and a list of parameters.
        """
        sql, params = _prepare_expressions(*self._evaluations)
        if len(self._evaluations) == 1:
            return f" {self._boolean_operator.value} {sql}", params
        return f" {self._boolean_operator.value} ({sql})", params


class Expression(_OperatorMixin):
    """Represents a SQL expression or condition.

    This class is used to construct SQL expressions involving comparisons,
    arithmetic operations, or function calls.
    """

    def __init__(
        self,
        left_operand: Column | Expression | _OperatorMixin,
        operator: str,
        right_operand: Any,
    ) -> None:
        """Initialize an Expression instance.

        Args:
            left_operand: The left side of the expression.
            operator: The operator to use in the expression.
            right_operand: The right side of the expression.
        """
        self._params: list[Any] = []
        self._left_operand = left_operand
        other_str = "?"
        if isinstance(right_operand, Column):
            other_str = str(right_operand)
        elif isinstance(right_operand, Expression):
            other_str, other_params = right_operand.prepare()
            self._params.extend(other_params)
        elif right_operand is None:
            other_str = "NULL"
        elif right_operand is True:
            other_str = "TRUE"
        elif right_operand is False:
            other_str = "FALSE"
        elif isinstance(right_operand, enum.Enum):
            self._params.append(right_operand.value)
        else:
            self._params.append(right_operand)
        self._operator = operator
        self._other_str = other_str

    def as_(self, alias: str) -> As:
        """Create an alias for this expression.

        Args:
            alias: The alias name for the expression.

        Returns:
            An As instance representing the aliased expression.
        """
        return As(self, alias)

    def prepare(self) -> tuple[str, list[Any]]:
        """Prepare the expression for use in a SQL query.

        Returns:
            A tuple containing the SQL string for this expression and a list of parameters.
        """
        sql, params = self._left_operand.prepare()
        return f"{sql} {self._operator} {self._other_str}", params + self._params


class Join(QueryBuilder):
    """Represents a JOIN operation in a SQL query.

    This class is used to construct various types of JOIN clauses.
    """

    def __init__(self, table: Type[Table]) -> None:
        """Initialize a Join instance.

        Args:
            table: The table to join with.
        """
        self._table = table
        self._on: On | None = None
        self._keyword: str = "JOIN"

    def prepare(self) -> tuple[str, list[Any]]:
        """Prepare the JOIN clause for use in a SQL query.

        Returns:
            A tuple containing the SQL string for this JOIN clause and a list of parameters.

        Raises:
            ValueError: If no ON condition has been set for the join.
        """
        if self._on is None:
            msg = "No condition set for join, need to call `join.on(...`"
            raise ValueError(msg)
        sql, params = self._on.prepare()
        return f"{self._keyword} {self._table.__table_name__} {sql}", params

    def on(self, *expressions: Expression | LogicGate) -> Self:
        """Set the ON condition for the JOIN.

        Args:
            *expressions: The conditions to use in the ON clause.

        Returns:
            The Join instance itself, allowing for method chaining.
        """
        self._on = On(*expressions)
        return self


class LeftJoin(Join):
    """Represents a LEFT JOIN operation in a SQL query."""

    def __init__(self, table: Type[Table]) -> None:
        """Initialize a LeftJoin instance.

        Args:
            table: The table to left join with.
        """
        super().__init__(table)
        self._keyword = "LEFT JOIN"


class RightJoin(Join):
    """Represents a RIGHT JOIN operation in a SQL query."""

    def __init__(self, table: Type[Table]) -> None:
        """Initialize a RightJoin instance.

        Args:
            table: The table to right join with.
        """
        super().__init__(table)
        self._keyword = "RIGHT JOIN"


class Limit(_OffsetMixin):
    """Represents a LIMIT clause in a SQL query."""

    def __init__(self, subquery: QueryBuilder, limit: int) -> None:
        """Initialize a Limit instance.

        Args:
            subquery: The query to apply the LIMIT to.
            limit: The maximum number of rows to return.
        """
        self.subquery = subquery
        self.limit = limit

    def prepare(self) -> tuple[str, list[Any]]:
        """Prepare the LIMIT clause for use in a SQL query.

        Returns:
            A tuple containing the SQL string with the LIMIT clause and a list of parameters.
        """
        sql, params = self.subquery.prepare()
        return f"{sql} LIMIT {self.limit}", params


class Offset(QueryBuilder):
    """Represents an OFFSET clause in a SQL query."""

    def __init__(self, subquery: QueryBuilder, offset: int) -> None:
        """Initialize an Offset instance.

        Args:
            subquery: The query to apply the OFFSET to.
            offset: The number of rows to skip.
        """
        self.subquery = subquery
        self.offset = offset

    def prepare(self) -> tuple[str, list[Any]]:
        """Prepare the OFFSET clause for use in a SQL query.

        Returns:
            A tuple containing the SQL string with the OFFSET clause and a list of parameters.
        """
        sql, params = self.subquery.prepare()
        return f"{sql} OFFSET {self.offset}", params


class On(_PaginateMixin):
    """Represents an ON clause in a JOIN operation."""

    def __init__(self, *expressions: Expression | LogicGate) -> None:
        """Initialize an On instance.

        Args:
            *expressions: The conditions to use in the ON clause.
        """
        self._expressions = expressions

    def prepare(self) -> tuple[str, list[Any]]:
        """Prepare the ON clause for use in a SQL query.

        Returns:
            A tuple containing the SQL string for the ON clause and a list of parameters.
        """
        sql, params = _prepare_expressions(*self._expressions)
        return f"ON {sql}", params


class From(_WhereMixin, _PaginateMixin):
    """Represents a FROM clause in a SQL query."""

    def __init__(self, select: Select, table: Type[Table], *joins: Join) -> None:
        """Initialize a From instance.

        Args:
            select: The SELECT clause of the query.
            table: The main table to select from.
            *joins: Any JOIN clauses to include.
        """
        self._select = select
        self._table = table
        self._joins = joins

    def prepare(self) -> tuple[str, list[Any]]:
        """Prepare the FROM clause for use in a SQL query.

        Returns:
            A tuple containing the SQL string for the FROM clause (including any JOINs) and a list of parameters.
        """
        sql, params = self._select.prepare()
        join_sql, joins_params = "", []
        for join in self._joins:
            s, p = join.prepare()
            join_sql += f" {s}"
            joins_params += p
        return (
            f"{sql} FROM {self._table.__table_name__}{join_sql}",
            params + joins_params,
        )


class OrderBy(_PaginateMixin):
    """Represents an ORDER BY clause in a SQL query."""

    def __init__(
        self, subquery: Select | From | On | _OrderByMixin, *columns: Column
    ) -> None:
        """Initialize an OrderBy instance.

        Args:
            subquery: The query to apply the ORDER BY to.
            *columns: The columns to order by.
        """
        self._subquery = subquery
        self.columns = list(columns)

    def prepare(self) -> tuple[str, list[Any]]:
        """Prepare the ORDER BY clause for use in a SQL query.

        Returns:
            A tuple containing the SQL string with the ORDER BY clause and a list of parameters.
        """
        sql, params = self._subquery.prepare()
        order_by = ", ".join(
            [f"{c} ASC" if c._asc else f"{c} DESC" for c in self.columns]
        )
        return f"{sql} ORDER BY {order_by}", params


class Values(QueryBuilder):
    """Represents a VALUES clause in an INSERT statement."""

    def __init__(self, subquery: InsertInto, values: dict[Column | str, Any]) -> None:
        """Initialize a Values instance.

        Args:
            subquery: The INSERT INTO clause.
            values: A dictionary mapping columns to their values.
        """
        self._subquery = subquery
        self.values = values

    def prepare(self) -> tuple[str, list[Any]]:
        """Prepare the VALUES clause for use in a SQL query.

        Returns:
            A tuple containing the SQL string with the VALUES clause and a list of parameter values.
        """
        sql, _ = self._subquery.prepare()
        values = ", ".join("?" for _ in range(len(self.values)))
        column_strs = []
        for column in self.values:
            if isinstance(column, Column):
                column_strs.append(f'"{column.name}"')
            else:
                column_name = self._subquery._table.__table_columns__[column].name
                column_strs.append(f'"{column_name}"')
        columns = ", ".join(column_strs)
        return f"{sql} ({columns}) VALUES ({values})", list(self.values.values())


class Where(_OrderByMixin, _PaginateMixin):
    """Represents a WHERE clause in a SQL query."""

    def __init__(
        self,
        subquery: Select | From | _WhereMixin,
        *expressions: Expression | LogicGate,
    ) -> None:
        """Initialize a Where instance.

        Args:
            subquery: The query to apply the WHERE clause to.
            *expressions: The conditions to use in the WHERE clause.
        """
        self._subquery = subquery
        sql, params = _prepare_expressions(*expressions)
        self._eval_params = params
        self._sql = sql

    def prepare(self) -> tuple[str, list[Any]]:
        """Prepare the WHERE clause for use in a SQL query.

        Returns:
            A tuple containing the SQL string with the WHERE clause and a list of parameters.
        """
        sql, params = self._subquery.prepare()
        return f"{sql} WHERE {self._sql}", params + self._eval_params


class Set(_WhereMixin):
    """Represents a SET clause in an UPDATE statement."""

    def __init__(self, subquery: Update, values: dict[Column | str, Any]) -> None:
        """Initialize a Set instance.

        Args:
            subquery: The UPDATE clause.
            values: A dictionary mapping columns to their new values.
        """
        self._subquery = subquery
        self.values = values

    def prepare(self) -> tuple[str, list[Any]]:
        """Prepare the SET clause for use in a SQL query.

        Returns:
            A tuple containing the SQL string with the SET clause and a list of parameter values.
        """
        sql, params = self._subquery.prepare()
        sql += " SET "
        sets = []
        for column, param in self.values.items():
            if isinstance(param, QueryBuilder):
                sub_q, sub_q_params = param.prepare()
                params.extend(sub_q_params)
                value = f"({sub_q})"
            else:
                params.append(param)
                value = "?"
            if isinstance(column, Column):
                sets.append(f'"{column.name}" = {value}')
            else:
                column_name = self._subquery._table.__table_columns__[column].name
                sets.append(f'"{column_name}" = {value}')
        return sql + ", ".join(sets), params


class InsertInto(QueryBuilder):
    """Represents an INSERT INTO statement in SQL."""

    def __init__(self, table: Type[Table]) -> None:
        """Initialize an InsertInto instance.

        Args:
            table: The table to insert into.
        """
        self._table = table

    def prepare(self) -> tuple[str, list[Any]]:
        """Prepare the INSERT INTO clause for use in a SQL query.

        Returns:
            A tuple containing the SQL string for the INSERT INTO clause and an empty list of parameters.
        """
        return f"INSERT INTO {self._table.__table_name__}", []

    def values(self, values: dict[Column | str, Any] | None = None) -> Values:
        """Add a VALUES clause to the INSERT statement.

        Args:
            values: A dictionary mapping columns to their values. If None, an empty dict is used.

        Returns:
            A Values instance representing the VALUES clause.
        """
        return Values(self, values or {})


class Delete(_WhereMixin):
    """Represents a DELETE statement in SQL."""

    def __init__(self, table: Type[Table]) -> None:
        """Initialize a Delete instance.

        Args:
            table: The table to delete from.
        """
        self._table = table

    def prepare(self) -> tuple[str, list[Any]]:
        """Prepare the DELETE statement for use in a SQL query.

        Returns:
            A tuple containing the SQL string for the DELETE statement and an empty list of parameters.
        """
        return f"DELETE FROM {self._table.__table_name__}", []  # noqa: S608


class Select(QueryBuilder):
    """Represents a SELECT statement in SQL."""

    def __init__(self, *args: Column | Type[Table] | As) -> None:
        """Initialize a Select instance.

        Args:
            *args: The columns, tables, or aliases to select from.

        Raises:
            ValueError: If an argument is not a Column, Table, or As instance.
        """
        self._columns: list[str] = []
        self._params: list[Any] = []
        for arg in args:
            if isinstance(arg, Column):
                self._columns.append(str(arg))
            elif isinstance(arg, As):
                sql, params = arg.prepare()
                self._params.extend(params)
                self._columns.append(sql)
            elif issubclass(arg, Table):
                self._columns.extend(map(str, arg.__table_columns__.values()))
            else:
                raise ValueError(f"Unsupported argument type: {type(arg)}")

    def prepare(self) -> tuple[str, list[Any]]:
        """Prepare the SELECT statement for use in a SQL query.

        Returns:
            A tuple containing the SQL string for the SELECT statement and a list of parameters.
        """
        select = f"SELECT {', '.join(self._columns)}"
        return select, self._params

    def from_(self, table: Type[Table], *args: Join) -> From:
        """Add a FROM clause to the SELECT statement.

        Args:
            table: The main table to select from.
            *args: Any JOIN clauses to include.

        Returns:
            A From instance representing the FROM clause.
        """
        return From(self, table, *args)


class Update(QueryBuilder):
    """Represents an UPDATE statement in SQL."""

    def __init__(self, table: Type[Table]) -> None:
        """Initialize an Update instance.

        Args:
            table: The table to update.
        """
        self._table = table

    def set(self, values: dict[Column | str, Any]) -> Set:
        """Add a SET clause to the UPDATE statement.

        Args:
            values: A dictionary mapping columns to their new values.

        Returns:
            A Set instance representing the SET clause.
        """
        return Set(self, values)

    def prepare(self) -> tuple[str, list[Any]]:
        """Prepare the UPDATE statement for use in a SQL query.

        Returns:
            A tuple containing the SQL string for the UPDATE statement and an empty list of parameters.
        """
        return f"UPDATE {self._table.__table_name__}", []


def _prepare_expressions(*expressions: Expression | LogicGate) -> tuple[str, list[Any]]:
    """Prepare multiple expressions for use in a SQL query.

    This function is used internally to combine multiple expressions or logic gates
    into a single SQL string with associated parameters.

    Args:
        *expressions: The expressions or logic gates to prepare.

    Returns:
        A tuple containing the combined SQL string and a list of all parameters.
    """
    sql, params = "", []
    for evaluation in expressions:
        s, p = evaluation.prepare()
        sql += s
        params += p
    return sql, params


if typing.TYPE_CHECKING:
    """Type hint for expressions."""
    Expression = bool  # type: ignore # pragma: no cover
