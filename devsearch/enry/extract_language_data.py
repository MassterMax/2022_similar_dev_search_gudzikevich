from functools import lru_cache

from enry import get_language


@lru_cache(maxsize=None)
def get_code_language(filename: str, source_code: bytes) -> str:
    """
    This method allows to get normalized source code language
    Args:
        filename: name of file with code
        source_code: source code
    Returns: language of source code
    """

    language = get_language(filename, source_code)

    # normalizing
    language = language.lower()

    return language
