from functools import cache

from enry import get_language


# todo maybe remove this method
@cache
def get_code_language(filename: str, source_code: bytes) -> str:
    """
    This method allows to get source code language
    Args:
        filename: name of file with code
        source_code: source code
    Returns: language of source code
    """
    language = get_language(filename, source_code)
    return language
