import difflib
import json
import logging
from typing import Any, Dict, Iterator, List, Union

from binaryornot.check import is_binary
from dulwich.diff_tree import TreeChange
from dulwich.objects import Commit, ShaFile
from dulwich.repo import Repo
from dulwich.walk import WalkEntry
from tqdm import tqdm

from devsearch.enry.extract_language_data import get_code_language
from devsearch.tree_sitter.parsing import get_identifiers_with_query

logger = logging.getLogger(__name__)


def get_change_differences(repo: Repo, language: str, change: TreeChange) -> Dict[str, Union[int, List[str]]]:
    """
    A method that gives differences in one change
    Args:
        repo: repo that we handle
        language: language of change code
        change: change of this repo
    Returns: {"rows_added": rows_added, "rows_deleted": rows_deleted, "identifiers": list_of_added_identifiers}
    """
    change_data = {"rows_added": 0, "rows_deleted": 0, "identifiers": []}

    if change.old.sha is None:
        # file was created
        new_blob: ShaFile = repo.get_object(change.new.sha)
        change_data["rows_added"] = len(new_blob.data.decode().splitlines())
        change_data["identifiers"] = list(get_identifiers_with_query(language, new_blob.data))
    elif change.new.sha is None:
        # file was deleted
        old_blob: ShaFile = repo.get_object(change.old.sha)
        change_data["rows_deleted"] = len(old_blob.data.decode().splitlines())
    if not (change.old.sha is None or change.new.sha is None):
        old_blob: ShaFile = repo.get_object(change.old.sha)
        new_blob: ShaFile = repo.get_object(change.new.sha)

        differences = difflib.unified_diff(old_blob.data.decode().splitlines(), new_blob.data.decode().splitlines())

        added_code = ""
        for el in differences:
            if el.startswith("+") and not el.startswith("++"):
                change_data["rows_added"] += 1
                added_code += el[1:] + "\n"
            elif el.startswith("-") and not el.startswith("--"):
                change_data["rows_deleted"] += 1

        change_data["identifiers"] = list(get_identifiers_with_query(language, str.encode(added_code)))

    return change_data


def handle_entry(entry: WalkEntry, repo: Repo) -> List[Dict[str, Any]]:
    """
    A method that returns all changes from one entry (=all changes in one commit)
    Args:
        entry: Entry to handle
        repo: Repo that contains handled entry

    Returns: A list of changes each has a structure: {"author": author of commit,
                                                     "commit_sha": commit sha,
                                                     "path": path to changed file,
                                                     "repo_url": url of repository,
                                                     "blob_id": blob id,
                                                     "added": rows that were added,
                                                     "deleted": rows that were deleted}
    """
    repo_url = (repo.get_config().get((b"remote", b"origin"), b"url")).decode()
    commit: Commit = entry.commit

    author = commit.author.decode()
    commit_sha = commit.id.decode()

    for change_sequence in entry.changes():
        # now we handle one file
        if not isinstance(change_sequence, list):
            change_sequence = [change_sequence]

        # now we handle each change of one file
        for change in change_sequence:
            file_name = change.new.path or change.old.path
            file_name = file_name.decode()

            # we skip binary files
            if is_binary(f"{repo.path}/{file_name}"):
                continue

            path = f"{repo_url}/blob/{commit_sha}/{file_name}"
            blob_id = change.new.sha or change.old.sha
            blob = repo.get_object(blob_id)
            blob_id = blob_id.decode()

            language = get_code_language(file_name, blob.data)
            new_entity = {"author": author,
                          "commit_sha": commit_sha,
                          "path": path,
                          "repo_url": repo_url,
                          "blob_id": blob_id,
                          "language": language}

            try:
                new_entity.update(get_change_differences(repo, language, change))
            except UnicodeDecodeError as e:
                logger.error(f"Exception in repository - {repo_url}, file - {path}, cause: {e}")
                continue

            yield new_entity


def extract_repo(local_path: str) -> Iterator[List[Dict[str, Any]]]:
    """
    A method to extract metadata from one repository and return it iteratively.

    Args:
        local_path: A path where Git repo stored on disk
    Returns:
        Iterator of List - each object is a list of changes

        One change has the following format:
        change_1 =  {"author": author of commit,
                     "commit_sha": commit sha,
                     "path": path to changed file,
                     "repo_url": url of repository,
                     "blob_id": blob id,
                     "added": rows that were added,
                     "deleted": rows that were deleted}

         Method yields [change_1, change_2, ..., change_n]
    """
    repo = Repo(local_path)

    for entry in tqdm(repo.get_walker()):
        yield handle_entry(entry, repo)


def save_data_as_json(data: Union[List, Dict], path: str) -> None:
    """
    A method to serialize json-like objects
    Args:
        data: data to save
        path: path to save like C:/path/to/file.jsonl
    """
    with open(path, "a") as fp:
        fp.write(json.dumps(data))
        fp.write("\n")
