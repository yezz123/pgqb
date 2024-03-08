import pytest

from pgqb import _snake as snake


@pytest.mark.parametrize(
    "input_str, expected_output",
    [
        ("PotatoHumanAlien", ["Potato", "Human", "Alien"]),
        ("Potato.Human.Alien", ["Potato", "Human", "Alien"]),
        ("Potato-Human-Alien", ["Potato", "Human", "Alien"]),
        ("Potato/Human/Alien", ["Potato", "Human", "Alien"]),
        ("Potato_Human_Alien", ["Potato", "Human", "Alien"]),
        ("Potato Human Alien", ["Potato", "Human", "Alien"]),
        ("Honey", ["Honey"]),
        ("DING", ["DING"]),
        ("", []),
        (
            "orange beer-PotatoAlien_food.yummy/honey",
            ["orange", "beer", "Potato", "Alien", "food", "yummy", "honey"],
        ),
        ("HumanNAMEDJason", ["Human", "NAMED", "Jason"]),
    ],
)
def test_get_words(input_str, expected_output):
    assert snake.get_words(input_str) == expected_output


@pytest.mark.parametrize(
    "input_str, expected_output",
    [
        ("PotatoHumanAlien", "potato_human_alien"),
        ("Potato.Human.Alien", "potato_human_alien"),
        ("Potato-Human-Alien", "potato_human_alien"),
        ("Potato/Human/Alien", "potato_human_alien"),
        ("Potato_Human_Alien", "potato_human_alien"),
        ("Potato Human Alien", "potato_human_alien"),
        ("Honey", "honey"),
        ("DING", "ding"),
        ("", ""),
        (
            "orange beer-PotatoAlien_food.yummy/honey",
            "orange_beer_potato_alien_food_yummy_honey",
        ),
        ("HumanNAMEDJason", "human_named_jason"),
    ],
)
def test_to_snake(input_str, expected_output):
    assert snake.to_snake(input_str) == expected_output


# Parametrized tests for happy path scenarios
@pytest.mark.parametrize(
    "words, regex, expected",
    [
        (["hello", "world"], r"\s", ["hello", "world"]),
        (["hello-world", "python"], r"-", ["hello", "world", "python"]),
        (["hello,world", "python,3.8"], r",", ["hello", "world", "python", "3.8"]),
        (["hello|world|again"], r"\|", ["hello", "world", "again"]),
    ],
    ids=lambda id: id,
)
def test_split_words_on_regex_happy_path(words, regex, expected):
    result = snake._split_words_on_regex(words, regex)
    assert result == expected, f"Expected {expected} but got {result}"


# Parametrized tests for edge cases
@pytest.mark.parametrize(
    "words, regex, expected",
    [
        ([], r"\s", []),
        ([""], r"\s", [""]),
    ],
    ids=lambda id: id,
)
def test_split_words_on_regex_edge_cases(words, regex, expected):
    result = snake._split_words_on_regex(words, regex)
    assert result == expected, f"Expected {expected} but got {result}"


# Parametrized tests for error cases
@pytest.mark.parametrize(
    "words, regex, expected_exception",
    [
        (["hello", "world"], None, TypeError),
        (["hello", "world"], 123, TypeError),
    ],
    ids=lambda id: id,
)
def test_split_words_on_regex_error_cases(words, regex, expected_exception):
    with pytest.raises(expected_exception):
        snake._split_words_on_regex(words, regex)
