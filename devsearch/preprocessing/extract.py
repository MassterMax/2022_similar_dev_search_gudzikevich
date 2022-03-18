from collections import defaultdict
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

logger = logging.getLogger(__name__)


def get_change_differences(repo: Repo, change: TreeChange) -> Dict[str, int]:
    """
    A method that gives differences in one change
    Args:
        repo: repo that we handle
        change: change of this repo
    Returns: {"added": rows_added, "deleted": rows_deleted}
    """
    counter = defaultdict(int)

    if change.old.sha is None:
        # file was created
        new_blob: ShaFile = repo.get_object(change.new.sha)
        counter["added"] = len(new_blob.data.decode().splitlines())
        counter["rows_deleted"] = 0
    elif change.new.sha is None:
        # file was deleted
        old_blob: ShaFile = repo.get_object(change.old.sha)
        counter["added"] = 0
        counter["rows_deleted"] = len(old_blob.data.decode().splitlines())
    if not (change.old.sha is None or change.new.sha is None):
        old_blob: ShaFile = repo.get_object(change.old.sha)
        new_blob: ShaFile = repo.get_object(change.new.sha)

        differences = difflib.unified_diff(old_blob.data.decode().splitlines(), new_blob.data.decode().splitlines())

        for el in differences:
            if el.startswith("+") and not el.startswith("++"):
                counter["added"] += 1
            elif el.startswith("-") and not el.startswith("--"):
                counter["deleted"] += 1

    return counter


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
            blob_id = blob_id.decode()

            new_entity = {"author": author,
                          "commit_sha": commit_sha,
                          "path": path,
                          "repo_url": repo_url,
                          "blob_id": blob_id}

            try:
                new_entity.update(get_change_differences(repo, change))
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

         Method returns [change_1, change_2, ..., change_n]
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
