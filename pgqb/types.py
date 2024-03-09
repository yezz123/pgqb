"""PostgreSQL types for pgqb query builder library.

This module contains classes for PostgreSQL data types. The classes are
used to specify the type of a column in a table. The classes are used to
generate the SQL for creating a table.

From the docs: https://www.postgresql.org/docs/current/datatype.html
"""

from __future__ import annotations

import enum

from pgqb import _snake as snake


class PGEnum(enum.Enum):
    """Enum type class."""

    @classmethod
    def pg_enum_name(cls) -> str:
        """Get the SQL name for this custom enum.

        Args:
            cls: The class to get the SQL name for.

        Returns:
            str: The SQL name for this custom enum.
        """
        return snake.to_snake(cls.__name__).upper()

    @classmethod
    def pg_enum_get_create(cls) -> str:
        """Get create enum SQL.

        Args:
            cls: The class to get the create enum SQL for.

        Returns:
            str: The create enum SQL.
        """
        options = ", ".join(f"'{it.value}'" for it in cls)
        return f"CREATE TYPE {cls.pg_enum_name()} AS ENUM ({options});"


class SQLType:
    """Base SQL type class."""

    def __str__(self) -> str:
        """Get the string representation of this column."""
        return self.__class__.__name__


class BIGINT(SQLType):
    """Signed eight-byte integer."""


class BIGSERIAL(SQLType):
    """Auto-incrementing eight-byte integer."""


class BIT(SQLType):
    """Fixed-length bit string."""


class VARBIT(SQLType):
    """Variable-length bit string."""


class BOOLEAN(SQLType):
    """Logical Boolean (true/false)."""


class BOX(SQLType):
    """Rectangular box on a plane."""


class BYTEA(SQLType):
    """Binary data (“byte array”)."""


class CHAR(SQLType):
    """Fixed-length character string."""

    def __init__(self, fixed_length: int | None = None) -> None:
        """Fixed-length character string.

        Args:
            fixed_length: The fixed length of the string.
        """
        self._fixed_length = fixed_length

    def __str__(self) -> str:
        """Get the string representation of this column."""
        return f"CHAR({self._fixed_length})" if self._fixed_length else "CHAR"


class VARCHAR(SQLType):
    """Variable-length character string."""

    def __init__(self, variable_length: int | None = None) -> None:
        """Variable-length character string.

        Args:
            variable_length: The variable length of the string.
        """
        self._variable_length = variable_length

    def __str__(self) -> str:
        """Get the string representation of this column."""
        if self._variable_length:
            return f"VARCHAR({self._variable_length})"
        return "VARCHAR"


class CIDR(SQLType):
    """IPv4 or IPv6 network address."""


class CIRCLE(SQLType):
    """Circle on a plane."""


class DATE(SQLType):
    """Calendar date (year, month, day)."""


class DOUBLE(SQLType):
    """Double precision floating-point number (8 bytes)."""

    def __str__(self) -> str:
        """Get the string representation of this column."""
        return "DOUBLE PRECISION"


class INET(SQLType):
    """IPv4 or IPv6 host address."""


class INTEGER(SQLType):
    """Signed four-byte integer."""


class INTERVAL(SQLType):
    """Time span."""

    def __init__(self, fields: str | None = None, precision: int | None = None) -> None:
        """Time span.

        Args:
            fields: The fields of the interval.
            precision: The precision of the interval.
        """
        self._fields = fields
        self._precision = precision

    def __str__(self) -> str:
        """Get the string representation of this column."""
        fields = f" {self._fields}" if self._fields else ""
        precision = f"({self._precision})" if self._precision else ""
        return f"INTERVAL{fields}{precision}"


class JSON(SQLType):
    """Textual JSON data."""


class JSONB(SQLType):
    """Binary JSON data, decomposed."""


class LINE(SQLType):
    """Infinite line on a plane."""


class LSEG(SQLType):
    """Line segment on a plane."""


class MACADDR(SQLType):
    """MAC (Media Access Control) address."""


class MACADDR8(SQLType):
    """MAC (Media Access Control) address (EUI-64 format)."""


class MONEY(SQLType):
    """Currency amount."""


class NUMERIC(SQLType):
    """Exact numeric of selectable precision."""

    def __init__(self, precision: int | None = None, scale: int | None = None) -> None:
        """Exact numeric of selectable precision.

        Args:
            precision: The precision of the numeric.
            scale: The scale of the numeric.
        """
        self._precision = precision
        self._scale = scale

    def __str__(self) -> str:
        """Get the string representation of this column."""
        if self._precision and self._scale:
            args = f"({self._precision}, {self._scale})"
        elif self._precision:
            args = f"({self._precision})"
        elif self._scale:
            msg = "Precision must be set if scale is"
            raise ValueError(msg)
        else:
            args = ""
        return f"NUMERIC{args}"


class PATH(SQLType):
    """Geometric path on a plane."""


# noinspection PyPep8Naming
class PG_LSN(SQLType):  # noqa: N801
    """PostgreSQL Log Sequence Number."""


# noinspection PyPep8Naming
class PG_SNAPSHOT(SQLType):  # noqa: N801
    """User-level transaction ID snapshot."""


class POINT(SQLType):
    """Geometric point on a plane."""


class POLYGON(SQLType):
    """Closed geometric path on a plane."""


class REAL(SQLType):
    """Single precision floating-point number (4 bytes)."""


class SMALLINT(SQLType):
    """Signed two-byte integer."""


class SMALLSERIAL(SQLType):
    """Auto-incrementing two-byte integer."""


class SERIAL(SQLType):
    """Auto-incrementing four-byte integer."""


class TEXT(SQLType):
    """Variable-length character string."""


class TIME(SQLType):
    """Time of day."""

    def __init__(
        self, precision: int | None = None, *, with_time_zone: bool = False
    ) -> None:
        """Time of day.

        Args:
            precision: The precision of the time.
            with_time_zone: Whether to include the time zone.
        """
        self._precision = precision
        self._with_time_zone = with_time_zone

    def __str__(self) -> str:
        """Get the string representation of this column."""
        precision = f"({self._precision})" if self._precision else ""
        tz = " WITH TIME ZONE" if self._with_time_zone else ""
        return f"TIME{precision}{tz}"


class TIMESTAMP(SQLType):
    """Date and time."""

    def __init__(
        self, precision: int | None = None, *, with_time_zone: bool = False
    ) -> None:
        """Date and time.

        Args:
            precision: The precision of the timestamp.
            with_time_zone: Whether to include the time zone.
        """
        self._precision = precision
        self._with_time_zone = with_time_zone

    def __str__(self) -> str:
        """Get the string representation of this column."""
        precision = f"({self._precision})" if self._precision else ""
        tz = " WITH TIME ZONE" if self._with_time_zone else ""
        return f"TIMESTAMP{precision}{tz}"


class TSQUERY(SQLType):
    """Text search query."""


class TSVECTOR(SQLType):
    """Text search document."""


class UUID(SQLType):
    """Universally unique identifier."""


class XML(SQLType):
    """XML data."""
