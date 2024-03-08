import re
from typing import Union


def to_snake(string: str) -> str:
    """
    Return a version of the string in `snake_case` format.

    Args:
        string: The string to convert to snake_case.

    Returns:
        The string in snake_case format.
    """
    return "_".join(w.lower() for w in get_words(string))


def get_words(string: str) -> list[str]:
    """
    Get a list of the words in a string in the order they appear.

    Args:
        string: The string to get the words from.

    Returns:
        A list of the words in the string.
    """
    words = [it for it in re.split(r"\b|_", string) if re.match(r"\w", it)]
    words = _split_words_on_regex(words, re.compile(r"(?<=[a-z])(?=[A-Z])"))
    words = _split_words_on_regex(words, re.compile(r"(?<=[A-Z])(?=[A-Z][a-z])"))
    words = _split_words_on_regex(words, re.compile(r"(?<=\d)(?=[A-Za-z])"))
    return words


def _split_words_on_regex(words: list[str], regex: Union[re.Pattern, str]) -> list[str]:  # type: ignore
    """
    Split words on a regex.

    Args:
        words (list[str]): The list of words to split.
        regex (Union[Pattern, str]): The regex to split on.

    Returns:
        list[str]: The list of words with the split words inserted.
    """
    words = words.copy()
    for i, word in enumerate(words):
        split_words = re.split(regex, word)
        if len(split_words) > 1:
            words.pop(i)
            for j, sw in enumerate(split_words):
                words.insert(i + j, sw)
    return words
