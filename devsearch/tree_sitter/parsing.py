from typing import Iterator, Tuple

from enry import get_language
from tree_sitter import Node, Tree

from devsearch.tree_sitter.setup import parser_library


def traverse_tree(node: Node, _level: int = 0) -> Iterator[Tuple[int, Node]]:
    yield _level, node
    for child in node.children:
        yield from traverse_tree(child, _level + 1)


def get_identifiers_with_traverse(language: str, source_code: bytes) -> Iterator[str]:
    parser = parser_library.get_parser(language)
    tree: Tree = parser.parse(source_code)
    for el in traverse_tree(tree.root_node, 0):
        level, node = el
        if node.type == "identifier":
            ident = source_code[node.start_byte: node.end_byte].decode()
            yield ident


def get_identifiers_with_query(language: str, source_code: bytes) -> Iterator[str]:
    parser = parser_library.get_parser(language)
    query = parser_library.get_language(language).query(
        """(
          (identifier) @constant
        )""")  # todo change from identifier to each language

    captures = query.captures(parser.parse(source_code).root_node)
    for capture in captures:
        node = capture[0]
        ident = source_code[node.start_byte: node.end_byte].decode()
        yield ident


def get_identifiers_with_enry(filename: str, source_code: bytes) -> Iterator[str]:
    language = get_language(filename, source_code)
    yield from get_identifiers_with_query(language, source_code)
