"""Query building functions for pgqb."""

from __future__ import annotations

import abc
import enum
import typing
from abc import ABC
from typing import Any, Type

from pgqb._snake import to_snake as snake
from pgqb.types import PGEnum, SQLType


class QueryBuilder(abc.ABC):
    """Base class for all query builders."""

    @abc.abstractmethod
    def prepare(self) -> tuple[str, list[Any]]:
        """Get all params and the SQL string."""

    def __str__(self) -> str:
        """Get the SQL string."""
        return self.prepare()[0]  # pragma: no cover

    def __repr__(self) -> str:
        """Get the SQL string."""
        return self.prepare()[0]  # pragma: no cover


class _LogicGateMixin(QueryBuilder, abc.ABC):
    """
    Logic gate mixin.

    This mixin is used to add logic gates to the query builder.

    Args:
        QueryBuilder: The query builder to add logic gates to.
        abc.ABC: The abstract base class.
    """

    def and_(self, evaluation: Expression | LogicGate) -> LogicGate:
        """
        And.

        Args:
            evaluation: The evaluation to add to the query.

        Returns:
            The query builder with the evaluation added.
        """
        return LogicGate(self, "AND", evaluation)

    def or_(self, evaluation: Expression | LogicGate) -> LogicGate:
        """Or.
        Args:
            evaluation: The evaluation to add to the query.

        Returns:
            The query builder with the evaluation added.
        """
        return LogicGate(self, "OR", evaluation)

    def and_not(self, evaluation: Expression | LogicGate) -> LogicGate:
        """And not.
        Args:
            evaluation: The evaluation to add to the query.

        Returns:
            The query builder with the evaluation added.
        """
        return LogicGate(self, "AND NOT", evaluation)

    def or_not(self, evaluation: Expression | LogicGate) -> LogicGate:
        """Or not.
        Args:
            evaluation: The evaluation to add to the query.

        Returns:
            The query builder with the evaluation added.
        """
        return LogicGate(self, "OR NOT", evaluation)


class _OperatorMixin(_LogicGateMixin, abc.ABC):
    """
    Operator mixin.

    Args:
        _LogicGateMixin: The logic gate mixin to add operators to.
        abc.ABC: The abstract base class.
    Returns:
        The query builder with the evaluation added.
    """

    def __gt__(self, other: Any) -> Expression:
        """Greater than operator."""
        return Expression(self, ">", other)

    def __ge__(self, other: Any) -> Expression:
        """Greater than or equal to operator."""
        return Expression(self, ">=", other)

    def __lt__(self, other: Any) -> Expression:
        """Less than operator."""
        return Expression(self, "<", other)

    def __le__(self, other: Any) -> Expression:
        """Less than or equal to operator."""
        return Expression(self, "<=", other)

    def __eq__(self, other: object) -> Expression:  # type: ignore
        """Equality operator."""
        if other is None or other is True or other is False:
            return Expression(self, "IS", other)
        return Expression(self, "=", other)

    def __ne__(self, other: object) -> Expression:  # type: ignore
        """Inequality operator."""
        if other is None or other is True or other is False:
            return Expression(self, "IS NOT", other)
        return Expression(self, "!=", other)

    def __add__(self, other: Any) -> Expression:
        """Addition operator."""
        return Expression(self, "+", other)

    def __sub__(self, other: Any) -> Expression:
        """Subtraction operator."""
        return Expression(self, "-", other)

    def __mul__(self, other: Any) -> Expression:
        """Multiplication operator."""
        return Expression(self, "*", other)

    def __truediv__(self, other: Any) -> Expression:
        """Division operator."""
        return Expression(self, "/", other)  # pragma: no cover

    def __mod__(self, other: Any) -> Expression:
        """Modulo operator."""
        return Expression(self, "%", other)

    def is_(self, other: Any) -> Expression:
        """Equality operator."""
        if other is None or other is True or other is False:
            return Expression(self, "IS", other)
        return Expression(self, "=", other)

    def is_not(self, other: Any) -> Expression:
        """Inequality operator."""
        if other is None or other is True or other is False:
            return Expression(self, "IS NOT", other)
        return Expression(self, "!=", other)


class As(QueryBuilder):
    """As alias.

    Args:
        sub_query: The sub query to alias.
        alias: The alias to use.

    Returns:
        The query builder with the evaluation added.
    """

    def __init__(self, sub_query: Column | Expression, alias: str) -> None:
        """As alias."""
        self._sub_query = sub_query
        self._alias = alias

    def prepare(self) -> tuple[str, list[Any]]:
        """Get column as SQL."""
        if isinstance(self._sub_query, Column):
            return f"{self._sub_query} AS {self._alias}", []
        sql, params = self._sub_query.prepare()
        return f"{sql} AS {self._alias}", params


class Column(_OperatorMixin):
    """Query building class for SQL."""

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
        """Query building class for SQL.

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
        """Get the string representation of this column."""
        return f"{self.table}.{self.name}"

    def __hash__(self) -> int:
        """Get the hash of this column."""
        return hash(str(self))

    def _create(self) -> str:
        """Get column create SQL."""
        null = " NOT NULL" if not self._null and not self._primary else ""
        unique = " UNIQUE" if self._unique else ""
        check = f" CHECK ({self._check})" if self._check else ""
        if self._default is not None:
            default = (
                " DEFAULT ''" if self._default == "" else f" DEFAULT {self._default}"
            )
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
        """Get column as SQL."""
        return str(self), []

    def as_(self, alias: str) -> As:
        """Alias for column."""
        return As(self, alias)

    def asc(self) -> Column:
        """Get this column ASC."""
        return self.column(True)

    def desc(self) -> Column:
        """Get this column ASC."""
        return self.column(False)

    def column(self, argument: bool) -> Column:
        """Get this column with argument."""
        col = Column()
        col.name = self.name
        col.table = self.table
        col._asc = argument
        return col


class Table(type):
    """Represents a SQL table."""

    __table_name__ = ""
    __table_columns__: dict[str, Column] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Initialize the table."""
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
        """Get create table SQL script."""
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
        if col_str:  # pragma: no cover
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


class _JoinMixin(QueryBuilder, abc.ABC):
    """Mixin for join expressions."""

    def join(self, table: Type[Table]) -> Join:
        """Join expression."""
        return Join(self, table)

    def left_join(self, table: Type[Table]) -> LeftJoin:
        """Left join expression."""
        return LeftJoin(self, table)

    def right_join(self, table: Type[Table]) -> RightJoin:
        """Right join expression."""
        return RightJoin(self, table)


class _LimitMixin(QueryBuilder, abc.ABC):
    def limit(self, limit: int) -> Limit:
        """Limit expression."""
        return Limit(self, limit)


class _OffsetMixin(QueryBuilder, abc.ABC):
    def offset(self, offset: int) -> Offset:
        """Offset expression."""
        return Offset(self, offset)


class _PaginateMixin(_OffsetMixin, _LimitMixin, ABC):
    """Paginate expression."""

    pass


class _OrderByMixin(QueryBuilder, abc.ABC):
    def order_by(self, *columns: Column) -> OrderBy:
        """Order by columns."""
        return OrderBy(self, *columns)


class _WhereMixin(QueryBuilder, abc.ABC):
    def where(self, evaluation: Expression | LogicGate) -> Where:
        """Where expression."""
        return Where(self, evaluation)

    def and_(self, evaluation: Expression | LogicGate) -> Where:
        """Where expression."""
        return Where(self, evaluation)


class LogicGate(_LogicGateMixin, _OrderByMixin, _PaginateMixin):
    """Represents a SQL `AND` expression."""

    def __init__(
        self, subquery: _LogicGateMixin, gate: str, left_operand: Expression | LogicGate
    ) -> None:
        """Represents a SQL `AND` expression.

        Args:
            subquery: The query to where.
            gate: The gate to where.
            left_operand: The left operand to where.
        """
        self._subquery = subquery
        self._gate = gate
        self._left_operand = left_operand

    def prepare(self) -> tuple[str, list[Any]]:
        """Get all params and the SQL string."""
        sql, params = self._subquery.prepare()
        eval_sql, eval_params = self._left_operand.prepare()
        if isinstance(self._left_operand, LogicGate):
            eval_sql = f"({eval_sql})"
        return f"{sql} {self._gate} {eval_sql}", params + eval_params


class Expression(_OperatorMixin, _PaginateMixin):
    """Represent a SQL evaluation."""

    def __init__(
        self,
        left_operand: Column | Expression | _OperatorMixin,
        operator: str,
        right_operand: Any,
    ) -> None:
        """Represent a SQL evaluation.

        Args:
            left_operand: The left operand.
            operator: The operator.
            right_operand: The right operand.
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
        """Alias for column."""
        return As(self, alias)

    def prepare(self) -> tuple[str, list[Any]]:
        """Evaluate an operation."""
        sql, params = self._left_operand.prepare()
        return f"{sql} {self._operator} {self._other_str}", params + self._params


class Join(QueryBuilder):
    """Join operator."""

    def __init__(
        self, from_: From | Join | On | _JoinMixin, table: Type[Table]
    ) -> None:
        """Join operator.

        Args:
            from_: The query to join.
            table: The table to join.
        """
        self._from = from_
        self._table = table

    def prepare(self) -> tuple[str, list[Any]]:
        """Get all params and the SQL string."""
        sql, params = self._from.prepare()
        return f"{sql} JOIN {self._table.__table_name__}", params

    def on(self, other: Expression) -> On:
        """Join on."""
        return On(self, other)


class LeftJoin(Join):
    """Left join operator."""

    def prepare(self) -> tuple[str, list[Any]]:
        """Get all params and the SQL string."""
        sql, params = self._from.prepare()
        return f"{sql} LEFT JOIN {self._table.__table_name__}", params


class RightJoin(Join):
    """Left join operator."""

    def prepare(self) -> tuple[str, list[Any]]:
        """Get all params and the SQL string."""
        sql, params = self._from.prepare()
        return f"{sql} RIGHT JOIN {self._table.__table_name__}", params


class Limit(_OffsetMixin):
    """Limit operator."""

    def __init__(self, subquery: QueryBuilder, limit: int) -> None:
        """Limit operator.

        Args:
            subquery: The query to limit.
            limit: The limit to limit.
        """
        self.subquery = subquery
        self.limit = limit

    def prepare(self) -> tuple[str, list[Any]]:
        """Get all params and the SQL string."""
        sql, params = self.subquery.prepare()
        return f"{sql} LIMIT {self.limit}", params


class Offset(QueryBuilder):
    """Offset operator."""

    def __init__(self, subquery: QueryBuilder, offset: int) -> None:
        """Offset operator.

        Args:
            subquery: The query to offset.
            offset: The offset to offset.
        """
        self.subquery = subquery
        self.offset = offset

    def prepare(self) -> tuple[str, list[Any]]:
        """Get all params and the SQL string."""
        sql, params = self.subquery.prepare()
        return f"{sql} OFFSET {self.offset}", params


class On(_JoinMixin, _WhereMixin, _PaginateMixin):
    """On operator."""

    def __init__(self, join: Join, other: Expression) -> None:
        """On operator.

        Args:
            join: The join to on.
            other: The other expression to on.
        """
        self._join = join
        self._other = other

    def prepare(self) -> tuple[str, list[Any]]:
        """Get all params and the SQL string."""
        sql, params = self._join.prepare()
        eval_sql, eval_params = self._other.prepare()
        return f"{sql} ON {eval_sql}", params + eval_params


class From(_JoinMixin, _WhereMixin, _PaginateMixin):
    """From expression."""

    def __init__(self, select: Select, table: Type[Table]) -> None:
        """From expression.

        Args:
            select: The query to from.
            table: The table to from.
        """
        self._select = select
        self._table = table

    def prepare(self) -> tuple[str, list[Any]]:
        """Get all params and the SQL string."""
        sql, params = self._select.prepare()
        return f"{sql} FROM {self._table.__table_name__}", params


class OrderBy(_PaginateMixin):
    """Order by expression."""

    def __init__(
        self, subquery: Select | From | On | _OrderByMixin, *columns: Column
    ) -> None:
        """Order by expression.

        Args:
            subquery: The query to order by.
            columns: The columns to order by.
        """
        self._subquery = subquery
        self._columns = columns

    def prepare(self) -> tuple[str, list[Any]]:
        """Get all params and the SQL string."""
        sql, params = self._subquery.prepare()

        order_by = ", ".join(
            [f"{c} ASC" if c._asc else f"{c} DESC" for c in self._columns]
        )
        return f"{sql} ORDER BY {order_by}", params


class Values(QueryBuilder):
    """SQL `VALUES` expression."""

    def __init__(self, subquery: InsertInto, values: dict[Column | str, Any]) -> None:
        """Values expression.

        Args:
            subquery: The query to values.
            values: The values to values.
        """
        self._subquery = subquery
        self._values = values

    def prepare(self) -> tuple[str, list[Any]]:
        """Get all params and the SQL string."""
        sql, _ = self._subquery.prepare()
        values = ", ".join("?" for _ in range(len(self._values)))
        column_strs = []
        for column in self._values:
            if isinstance(column, Column):
                column_strs.append(f'"{column.name}"')
            else:
                column_name = self._subquery._table.__table_columns__[column].name
                column_strs.append(f'"{column_name}"')
        columns = ", ".join(column_strs)
        return f"{sql} ({columns}) VALUES ({values})", list(self._values.values())


class Where(_LogicGateMixin, _OrderByMixin, _PaginateMixin):
    """Where expression."""

    def __init__(
        self,
        subquery: Select | From | On | _WhereMixin,
        evaluation: Expression | LogicGate,
    ) -> None:
        """Where expression.

        Args:
            subquery: The query to where.
            evaluation: The evaluation to where.
        """
        self._subquery = subquery
        sql, params = evaluation.prepare()
        self._eval_params = params
        if isinstance(evaluation, LogicGate):
            sql = f"({sql})"
        self._sql = sql

    def prepare(self) -> tuple[str, list[Any]]:
        """Get all params and the SQL string."""
        sql, params = self._subquery.prepare()
        return f"{sql} WHERE {self._sql}", params + self._eval_params


class Set(_WhereMixin):
    """Set expression."""

    def __init__(self, subquery: Update, values: dict[Column | str, Any]) -> None:
        """Set expression.

        Args:
            subquery: The query to set.
            values: The values to set.
        """
        self._subquery = subquery
        self._values = values

    def prepare(self) -> tuple[str, list[Any]]:
        """Get all params and the SQL string."""
        sql, params = self._subquery.prepare()
        sql += " SET "
        sets = []
        for column, param in self._values.items():
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
    """SQL `INSERT` query builder."""

    def __init__(self, table: Type[Table]) -> None:
        """Insert query builder.

        Args:
            table: The table to insert into.
        """
        self._table = table

    def prepare(self) -> tuple[str, list[Any]]:
        """Get all params and the SQL string."""
        return f"INSERT INTO {self._table.__table_name__}", []

    def values(self, values: dict[Column | str, Any] | None = None) -> Values:
        """Build SQL insert `VALUES` query."""
        return Values(self, values or {})


class Delete(_WhereMixin):
    """SQL `DELETE` query builder."""

    def __init__(self, table: Type[Table]) -> None:
        """Delete query builder.

        Args:
            table: The table to delete from.
        """
        self._table = table

    def prepare(self) -> tuple[str, list[Any]]:
        """Get all params and the SQL string."""
        return f"DELETE FROM {self._table.__table_name__}", []  # noqa: S608


class Select(QueryBuilder):
    """SQL `SELECT` query builder."""

    def __init__(self, *args: Column | Type[Table] | As) -> None:
        """Select query builder.

        Args:
            *args: The columns to select from the table.

        Raises:
            ValueError: If the argument is not a column or a table.
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
            elif issubclass(arg, Table):  # pragma: no cover
                self._columns.extend(map(str, arg.__table_columns__.values()))

    def prepare(self) -> tuple[str, list[Any]]:
        """Get all params and the SQL string."""
        select = f"SELECT {', '.join(self._columns)}"
        return select, self._params

    def from_(self, table: Type[Table]) -> From:
        """Build SQL FROM expression."""
        return From(self, table)


class Update(QueryBuilder):
    """SQL `UPDATE` query builder."""

    def __init__(self, table: Type[Table]) -> None:
        """Update query builder.

        Args:
            table: The table to update.
        """
        self._table = table

    def set(self, values: dict[Column | str, Any]) -> Set:
        """Build SQL `SET` expression."""
        return Set(self, values)

    def prepare(self) -> tuple[str, list[Any]]:
        """Get all params and the SQL string."""
        return f"UPDATE {self._table.__table_name__}", []


if typing.TYPE_CHECKING:
    """Type hint for expressions."""
    Expression = bool  # type: ignore # pragma: no cover
