import inspect

import pytest

from pgqb import (
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
    Column,
    PGEnum,
    Table,
)


class User(Table):
    id = Column(UUID(), primary=True)
    bigint = Column(BIGINT(), primary=True)
    bigserial = Column(BIGSERIAL())
    bit = Column(BIT())
    varbit = Column(VARBIT())
    boolean = Column(BOOLEAN())
    box = Column(BOX())
    bytea = Column(BYTEA())
    char = Column(CHAR())
    varchar = Column(VARCHAR())
    cidr = Column(CIDR())
    circle = Column(CIRCLE())
    date = Column(DATE())
    double = Column(DOUBLE())
    inet = Column(INET())
    integer = Column(INTEGER())
    interval = Column(INTERVAL())
    json = Column(JSON())
    jsonb = Column(JSONB())
    line = Column(LINE())
    lseg = Column(LSEG())
    macaddr = Column(MACADDR())
    macaddr8 = Column(MACADDR8())
    money = Column(MONEY())
    numeric = Column(NUMERIC())
    path = Column(PATH())
    pg_lsn = Column(PG_LSN())
    pg_snapshot = Column(PG_SNAPSHOT())
    point = Column(POINT())
    polygon = Column(POLYGON())
    real = Column(REAL())
    smallint = Column(SMALLINT())
    smallserial = Column(SMALLSERIAL())
    serial = Column(SERIAL())
    text = Column(TEXT())
    time = Column(TIME())
    timestamp = Column(TIMESTAMP())
    tsquery = Column(TSQUERY())
    tsvector = Column(TSVECTOR())
    uuid = Column(UUID())
    xml = Column(XML())


def test_create_table() -> None:
    sql = User.create_table()
    assert sql == inspect.cleandoc(
        """
        CREATE TABLE IF NOT EXISTS "user" (
          "id" UUID,
          "bigint" BIGINT,
          "bigserial" BIGSERIAL NOT NULL,
          "bit" BIT NOT NULL,
          "varbit" VARBIT NOT NULL,
          "boolean" BOOLEAN NOT NULL,
          "box" BOX NOT NULL,
          "bytea" BYTEA NOT NULL,
          "char" CHAR NOT NULL,
          "varchar" VARCHAR NOT NULL,
          "cidr" CIDR NOT NULL,
          "circle" CIRCLE NOT NULL,
          "date" DATE NOT NULL,
          "double" DOUBLE PRECISION NOT NULL,
          "inet" INET NOT NULL,
          "integer" INTEGER NOT NULL,
          "interval" INTERVAL NOT NULL,
          "json" JSON NOT NULL,
          "jsonb" JSONB NOT NULL,
          "line" LINE NOT NULL,
          "lseg" LSEG NOT NULL,
          "macaddr" MACADDR NOT NULL,
          "macaddr8" MACADDR8 NOT NULL,
          "money" MONEY NOT NULL,
          "numeric" NUMERIC NOT NULL,
          "path" PATH NOT NULL,
          "pg_lsn" PG_LSN NOT NULL,
          "pg_snapshot" PG_SNAPSHOT NOT NULL,
          "point" POINT NOT NULL,
          "polygon" POLYGON NOT NULL,
          "real" REAL NOT NULL,
          "smallint" SMALLINT NOT NULL,
          "smallserial" SMALLSERIAL NOT NULL,
          "serial" SERIAL NOT NULL,
          "text" TEXT NOT NULL,
          "time" TIME NOT NULL,
          "timestamp" TIMESTAMP NOT NULL,
          "tsquery" TSQUERY NOT NULL,
          "tsvector" TSVECTOR NOT NULL,
          "uuid" UUID NOT NULL,
          "xml" XML NOT NULL,
          PRIMARY KEY (id, bigint)
        );
        """
    )


class TypeOptionsTable(Table):
    char = Column(CHAR(1), null=True)
    varchar = Column(VARCHAR(1), default="", null=True)
    interval = Column(INTERVAL(fields="DAY TO SECOND", precision=1), null=True)
    numeric = Column(NUMERIC(10, 2), null=True)
    numeric_two = Column(NUMERIC(10), null=True)
    time = Column(TIME(1, with_time_zone=True), null=True)
    timestamp = Column(TIMESTAMP(1, with_time_zone=True), null=True)


def test_type_options() -> None:
    sql = TypeOptionsTable.create_table()
    assert sql == inspect.cleandoc(
        """
        CREATE TABLE IF NOT EXISTS "type_options_table" (
          "char" CHAR(1),
          "varchar" VARCHAR(1) DEFAULT '',
          "interval" INTERVAL DAY TO SECOND(1),
          "numeric" NUMERIC(10, 2),
          "numeric_two" NUMERIC(10),
          "time" TIME(1) WITH TIME ZONE,
          "timestamp" TIMESTAMP(1) WITH TIME ZONE
        );
        """
    )

    with pytest.raises(ValueError):
        Column(NUMERIC(scale=1))._create()


class ColumnOptionsTable(Table):
    integer = Column(
        INTEGER(),
        check="integer > 0",
        default=1,
        index=True,
        null=True,
        unique=True,
    )
    fk = Column(foreign_key=User.id)
    fk2 = Column(foreign_key=User.bigint)


def test_column_options() -> None:
    sql = ColumnOptionsTable.create_table()
    assert sql == inspect.cleandoc(
        """
        CREATE TABLE IF NOT EXISTS "column_options_table" (
          "integer" INTEGER DEFAULT 1 UNIQUE CHECK (integer > 0),
          "fk" UUID NOT NULL,
          "fk2" BIGINT NOT NULL,
          FOREIGN KEY (fk, fk2) REFERENCES "user" (id, bigint)
        );
        CREATE INDEX ON "column_options_table" (integer);
        """
    )


def test_enum() -> None:
    class MyE(PGEnum):
        A = "apple"
        B = "bee"

    assert MyE.pg_enum_get_create() == "CREATE TYPE MY_E AS ENUM ('apple', 'bee');"

    class UsesEnum(Table):
        col = Column(MyE, null=True)

    assert UsesEnum.create_table() == inspect.cleandoc(
        """
        CREATE TABLE IF NOT EXISTS "uses_enum" (
          "col" MY_E
        );
        """
    )
