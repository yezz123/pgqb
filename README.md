# PostgreSQL Query Builder

<p align="center">
<a href="https://github.com/yezz123/pgqb" target="_blank">
    <img src="https://raw.githubusercontent.com/yezz123/pgqb/main/.github/logo.png" alt="pgqb">
</a>
<p align="center">
    <em>Typed Python PostgreSQL query builder ✨</em>
</p>
<p align="center">
<a href="https://github.com/yezz123/pgqb/actions/workflows/ci.yml" target="_blank">
    <img src="https://github.com/yezz123/pgqb/actions/workflows/ci.yml/badge.svg" alt="Continuous Integration">
</a>
<a href="https://pypi.org/project/pgqb" target="_blank">
    <img src="https://img.shields.io/pypi/v/pgqb?color=%2334D058&label=pypi%20package" alt="Package version">
</a>
<a href="https://codecov.io/gh/yezz123/pgqb">
    <img src="https://codecov.io/gh/yezz123/pgqb/branch/main/graph/badge.svg"/>
</a>
</p>
</p>

---

**Source Code**: <https://github.com/yezz123/pgqb>

**Documentation**: TBD

---

pgqb is a Python library for building SQL queries for PostgreSQL databases. It provides a simple and intuitive interface for constructing SQL statements using functions like `delete`, `insert_into`, `select`, and `update`. This README provides a brief overview of how to use pgqb to build queries and execute them safely with parameter binding.

## Installation

You can install pgqb via pip:

```bash
pip install pgqb
```

## Project using

```py
from pgqb import Column, Table, select


class User(Table):
    id = Column()
    first = Column()
    last = Column()


class Task(Table):
    id = Column()
    user_id = Column()
    value = Column()


sql, params = (
    select(User)
    .from_(User)
    .join(Task)
    .on(Task.user_id == User.id)
    .where(User.id == 1)
    .order_by(Task.value.desc())
).prepare()

expected = " ".join(
    [
        'SELECT "user".id, "user".first, "user".last',
        'FROM "user"',
        'JOIN "task" ON "task".user_id = "user".id',
        'WHERE "user".id = ?',
        'ORDER BY "task".value DESC',
    ]
)


print(sql==expected)
# > True
```

### Create Table

```py
from pgqb import Column, Table, TEXT, TIMESTAMP, UUID


class User(Table):
    id = Column(UUID(), primary=True)
    email = Column(TEXT(), unique=True, index=True)
    first = Column(TEXT())
    last = Column(TEXT())
    verified_at = Column(TIMESTAMP(with_time_zone=True))

print(User.create_table())

# > CREATE TABLE IF NOT EXISTS "user" (
#  "id" UUID,
#  "email" TEXT NOT NULL UNIQUE,
#  "first" TEXT NOT NULL,
#  "last" TEXT NOT NULL,
#  "verified_at" TIMESTAMP WITH TIME ZONE NOT NULL,
#  PRIMARY KEY (id)
#);
# CREATE INDEX ON "user" (email);
```

## Development

### Setup environment

You should create a virtual environment and activate it:

> **Notes:** You need to have `python3.9` or higher installed.

I Use `uv` to manage virtual environments, you can install it with:

```bash
# Install uv
pip install uv

# Create a virtual environment
uv venv

# Activate the virtual environment
source .venv/bin/activate
```

And then install the development dependencies:

```bash
# Install dependencies
uv pip install -e .[test,lint]
```

### Run tests 🌝

You can run all the tests with:

```bash
bash scripts/tests.sh
```

### Format the code 🍂

Execute the following command to apply `pre-commit` formatting:

```bash
bash scripts/format.sh
```

Execute the following command to apply `mypy` type checking:

```bash
bash scripts/lint.sh
```

## License 🍻

This project is licensed under the terms of the MIT license.
