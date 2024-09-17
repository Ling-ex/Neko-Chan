import difflib
from typing import Optional


def get_suggestions(
    name_input: str,
    args_list: list[str],
    num=3,
    cutoff=0.6,
) -> Optional[list]:
    """
    Returns feature suggestions based on the input name.

    name_input: Input from user (string)
    args_list: List of available features (list of strings)
    num: Maximum number of suggestions to return (default: 3)
    cutoff: Similarity threshold value (default: 0.6)

    Return:
        List of feature suggestions (list of strings)
    """
    suggest = difflib.get_close_matches(
        name_input,
        args_list,
        n=num,
        cutoff=cutoff,
    )

    return suggest
