from functools import cache
from typing import Iterator, Tuple

from tree_sitter import Node, Tree

from devsearch.tree_sitter.setup import parser_library


def traverse_tree(node: Node, _level: int = 0) -> Iterator[Tuple[int, Node]]:
    """
    This method traverses AST tree of code from start node and yields each node with its level
    Args:
        node: start node
        _level: level of the node
    Returns: tuple of node level and node itself
    """
    yield _level, node
    for child in node.children:
        yield from traverse_tree(child, _level + 1)


@cache
def get_identifiers_with_traverse(language: str, source_code: bytes) -> Iterator[str]:
    """
    This method returns all identifiers in given source_code via traversing
    Args:
        language: code language
        source_code: source code
    Returns: iterator of identifiers
    """
    parser = parser_library.get_parser(language)
    tree: Tree = parser.parse(source_code)
    for el in traverse_tree(tree.root_node, 0):
        level, node = el
        if node.type == "identifier":
            ident = source_code[node.start_byte: node.end_byte].decode()
            yield ident


@cache
def get_identifiers_with_query(language: str, source_code: bytes) -> Iterator[str]:
    """
    This method returns all identifiers in given source_code via pattern matching
    Args:
        language: code language
        source_code: source code
    Returns: iterator of identifiers
    """
    parser = parser_library.get_parser(language)
    query = parser_library.get_language(language).query(
        """(
          (identifier) @constant
        )""")  # todo maybe specify identifier to any language

    captures = query.captures(parser.parse(source_code).root_node)
    for capture in captures:
        node = capture[0]
        ident = source_code[node.start_byte: node.end_byte].decode()
        yield ident
