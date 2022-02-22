from collections import defaultdict
import difflib
import json
from typing import Any, Dict, Iterator, List, Union

from dulwich import porcelain
from dulwich.diff_tree import TreeChange
from dulwich.objects import Commit, ShaFile
from dulwich.repo import Repo
from dulwich.walk import WalkEntry
from tqdm import tqdm

SUPPORTED_EXTENSIONS = {".py"}


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


def extract_repo(git_path: str, target_path: str, should_clone=False) -> Iterator[Dict[str, Any]]:
    """
    A method to extract following data from one repository and return it iteratively:

    {"author": author of commit,
     "commit_sha": commit sha,
     "path": path to changed file,
     "repo_url": url of repository,
     "blob_id": blob id,
     "added": rows that were added,
     "deleted": rows that were deleted}

    Args:
        git_path: GitHub URL path
        target_path: A path where to store Git repo on disk
        should_clone: If should clone GitHub then clone else repo should be in target path

    Returns:

    """
    if should_clone:
        porcelain.clone(git_path, target_path)

    repo = Repo(target_path)
    repo_url = (repo.get_config().get((b"remote", b"origin"), b"url")).decode()

    for entry in tqdm(repo.get_walker()):
        entry: WalkEntry
        commit: Commit = entry.commit

        author = commit.author.decode()
        commit_sha = commit.id.decode()

        for change_sequence in entry.changes():
            # for some reason change could be a sequence of changes - despite it is a single commit
            if not isinstance(change_sequence, list):
                change_sequence = [change_sequence]

            for change in change_sequence:
                file_name = change.new.path or change.old.path
                file_name = file_name.decode()

                # print(file_name)
                # we process only some extensions todo
                if not file_name.endswith(tuple(SUPPORTED_EXTENSIONS)):
                    continue

                path = f"{repo_url}/blob/{commit_sha}/{file_name}"
                blob_id = change.new.sha or change.old.sha
                blob_id = blob_id.decode()

                new_entity = {"author": author,
                              "commit_sha": commit_sha,
                              "path": path,
                              "repo_url": repo_url,
                              "blob_id": blob_id}
                new_entity.update(get_change_differences(repo, change))

                yield new_entity


def save_data_as_json(data: Union[List, Dict], path: str) -> None:
    """
    A method to serialize json-like object
    Args:
        data: data to save
        path: path to save like C:/path/to/file.jsonl

    """
    assert path.endswith("jsonl")

    with open(path, "a") as fp:
        fp.write(json.dumps(data))
        fp.write("\n")
