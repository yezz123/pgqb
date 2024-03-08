import enum
import uuid
from typing import Any

from pgqb import Column, Table, delete_from, insert_into, select, update


class MyEnum(enum.Enum):
    """Test enum."""

    OPTION = "option"


class User(Table):
    id = Column()
    first = Column()
    last = Column()


class Task(Table):
    id = Column()
    user_id = Column()
    value = Column()


def test_select() -> None:
    query, params = (
        select(User)
        .from_(User)
        .join(Task)
        .on(Task.user_id == User.id)
        .left_join(Task)
        .on(Task.value == 1)
        .right_join(Task)
        .on(Task.value >= 2)
        .join(Task)
        .on(Task.value <= MyEnum.OPTION)
        .where(Task.value > "a string")
        .order_by(Task.value.asc(), Task.value.desc())
    ).prepare()
    assert params == [1, 2, "option", "a string"]
    expected = " ".join(
        [
            'SELECT "user".id, "user".first, "user".last',
            'FROM "user" JOIN "task" ON "task".user_id = "user".id',
            'LEFT JOIN "task" ON "task".value = ?',
            'RIGHT JOIN "task" ON "task".value >= ?',
            'JOIN "task" ON "task".value <= ?',
            'WHERE "task".value > ?',
            'ORDER BY "task".value ASC,',
            '"task".value DESC',
        ]
    )
    assert query == expected


def test_select_columns() -> None:
    sql, params = (
        select(User.id, User.first.as_("name"), Task.id)
        .from_(User)
        .left_join(Task)
        .on(Task.user_id == User.id)
        .limit(20)
        .offset(20)
        .prepare()
    )
    assert params == []
    assert sql == " ".join(
        [
            'SELECT "user".id, "user".first AS name, "task".id',
            'FROM "user" LEFT JOIN "task" ON "task".user_id = "user".id',
            "LIMIT 20 OFFSET 20",
        ]
    )


def test_insert() -> None:
    id = uuid.uuid4()
    query, params = (insert_into(User).values({User.id: id})).prepare()
    assert params == [id]
    assert query == 'INSERT INTO "user" ("id") VALUES (?)'


def test_insert_str_columns() -> None:
    id = uuid.uuid4()
    query, params = (insert_into(User).values({"id": id})).prepare()
    assert params == [id]
    assert query == 'INSERT INTO "user" ("id") VALUES (?)'


def test_expressions() -> None:
    query = (
        select(User)
        .from_(User)
        .and_(User.id > 1)
        .and_(User.id < User.id)
        .and_not(User.id >= User.id)
        .or_(User.id <= User.id)
        .or_not(User.id != User.id)
    )
    sql, params = query.prepare()
    assert params == [1]
    assert sql == " ".join(
        [
            'SELECT "user".id, "user".first, "user".last',
            'FROM "user" WHERE "user".id > ?',
            'AND "user".id < "user".id',
            'AND NOT "user".id >= "user".id',
            'OR "user".id <= "user".id',
            'OR NOT "user".id != "user".id',
        ]
    )


# noinspection PyComparisonWithNone
def test_operators() -> None:
    false: Any = False
    # noinspection PyUnresolvedReferences
    query = (
        select(User, (User.id == 3).as_("mocha"))
        .from_(User)
        .where(User.id > 1)
        .and_(User.last.is_(None).or_(User.first.is_not(True)))
        .and_(User.last.is_(1).or_(User.first.is_not(1)))
        .and_((User.last == false).or_(User.first != false))
    )
    sql, params = query.prepare()
    assert params == [3, 1, 1, 1]
    assert sql == " ".join(
        [
            'SELECT "user".id, "user".first, "user".last, "user".id = ? AS mocha',
            'FROM "user"',
            'WHERE "user".id > ?',
            'AND ("user".last IS NULL OR "user".first IS NOT TRUE)',
            'AND ("user".last = ? OR "user".first != ?)',
            'AND ("user".last IS FALSE OR "user".first IS NOT FALSE)',
        ]
    )


def test_operators_chained() -> None:
    query = (
        select(User)
        .from_(User)
        .where((User.id + 1 > Task.id - 2).and_(User.id > 12))
        .or_(User.id * 5 % 6 > 7)
    )
    sql, params = query.prepare()
    assert params == [1, 2, 12, 5, 6, 7]
    assert sql == " ".join(
        [
            'SELECT "user".id, "user".first, "user".last',
            'FROM "user"',
            'WHERE ("user".id + ? > "task".id - ? AND "user".id > ?)',
            'OR "user".id * ? % ? > ?',
        ]
    )


def test_update() -> None:
    sql, params = (
        update(User)
        .set(
            {
                User.first: "Potato",
                User.last: "Wedge",
                User.id: select(Task.id).from_(Task).where(Task.id == 1),
            }
        )
        .where(User.id == 2)
    ).prepare()
    assert params == ["Potato", "Wedge", 1, 2]
    assert sql == " ".join(
        [
            'UPDATE "user"',
            'SET "first" = ?, "last" = ?,',
            '"id" = (SELECT "task".id FROM "task" WHERE "task".id = ?)',
            'WHERE "user".id = ?',
        ]
    )


def test_update_str_columns() -> None:
    sql, params = (
        update(User)
        .set(
            {
                "first": "Potato",
                "last": "Wedge",
                "id": select(Task.id).from_(Task).where(Task.id == 1),
            }
        )
        .where(User.id == 2)
    ).prepare()
    assert params == ["Potato", "Wedge", 1, 2]
    assert sql == " ".join(
        [
            'UPDATE "user"',
            'SET "first" = ?, "last" = ?,',
            '"id" = (SELECT "task".id FROM "task" WHERE "task".id = ?)',
            'WHERE "user".id = ?',
        ]
    )


def test_delete() -> None:
    sql, params = delete_from(User).where(User.first == "Potato").prepare()
    assert params == ["Potato"]
    assert sql == 'DELETE FROM "user" WHERE "user".first = ?'
