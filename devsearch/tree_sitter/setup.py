import json
from pathlib import Path

from git import Repo
from tqdm import tqdm
from tree_sitter import Language
from tree_sitter import Parser


class ParserLibrary:
    _PARSER_LIB_DIR_PATH = Path(__file__).resolve().parent / "lib"
    _PARSER_LIB_PATH = _PARSER_LIB_DIR_PATH / "my-languages.so"
    _PARSER_CONFIG_PATH = Path(__file__).resolve().parent / "parsers.json"

    def __init__(self):
        if not self._PARSER_LIB_DIR_PATH.exists():
            self._PARSER_LIB_DIR_PATH.mkdir()
        if not self._PARSER_LIB_PATH.exists():
            self.update_library()

    def update_library(self) -> None:
        with open(str(self._PARSER_CONFIG_PATH), "r") as fp:
            config = json.load(fp)

        languages_path = []

        for language in tqdm(config["parsers"]):
            url_parts = language["parser"].split("/")
            clone_path = Path(self._PARSER_LIB_DIR_PATH / url_parts[-2] / url_parts[-1]).resolve()

            if not clone_path.exists():
                Repo.clone_from(language["parser"], clone_path)

            if "grammars" in language:
                languages_path.extend(clone_path / grammar_dir for grammar_dir in language["grammars"])
            else:
                languages_path.append(clone_path)

        Language.build_library(str(self._PARSER_LIB_PATH), languages_path)

    def get_parser(self, language: str) -> Parser:
        parser = Parser()
        parser.set_language(self.get_language(language))
        return parser

    def get_language(self, language: str):
        return Language(self._PARSER_LIB_PATH, language)


parser_library = ParserLibrary()
