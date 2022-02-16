import difflib
import json
from typing import Dict

from dulwich import porcelain
from dulwich.objects import Commit, ShaFile
from dulwich.repo import Repo
from dulwich.walk import WalkEntry

SUPPORTED_EXTENSIONS = {".py"}


def handle_blob(old_blob, new_blob) -> Dict:
    differences = difflib.unified_diff(old_blob.data.decode().splitlines(), new_blob.data.decode().splitlines())

    rows_added = 0
    rows_deleted = 0
    for el in list(differences):
        if el.startswith("+") and not el.startswith("++"):
            rows_added += 1
        elif el.startswith("-") and not el.startswith("--"):
            rows_deleted += 1

    return {"added": rows_added, "deleted": rows_deleted}


def handle_entry(repo: Repo, entry: WalkEntry):
    """
    A method to handle one WalkEntry
    Args:
        repo: repo that we handle
        entry: entry to handle

    Returns: meta-information about entry

    """

    data = []
    commit: Commit = entry.commit

    repo_url = (repo.get_config().get((b'remote', b'origin'), b'url')).decode()

    author = commit.author.decode()
    commit_sha = commit.id.decode()

    for changes in entry.changes():
        # for some reason change could be a sequence of changes
        if not isinstance(changes, list):
            changes = [changes]

        for change in changes:
            # we ignore file deleting and creating
            if change.old.path is None or change.new.path is None:
                continue

            # we process only some extensions
            if not change.new.path.decode().endswith(tuple(SUPPORTED_EXTENSIONS)):
                continue

            path = f"{repo_url}/blob/{commit.id.decode()}/{change.new.path.decode()}"
            # print(path)

            old_blob: ShaFile = repo.get_object(change.old.sha)
            new_blob: ShaFile = repo.get_object(change.new.sha)

            new_entity = {"author": author,
                          "commit_sha": commit_sha,
                          "path": path,
                          "repo_url": repo_url,
                          "blob_id": change.new.sha.decode()}

            temp = {**new_entity, **handle_blob(old_blob, new_blob)}
            data.append(temp)

    return data


def extract_repo(git_path: str, target_path: str, should_clone=False, limit=100000):
    """
    A method to extract data from one repository
    Args:
        git_path: GitHub URL path
        target_path: A path where to store Git repo on disk
        should_clone: If should clone GitHub then clone else repo should be in target path
        limit: Limit of processed commits

    Returns:

    """
    if should_clone:
        porcelain.clone(git_path, target_path)

    repo = Repo(target_path)
    total_changes = 0
    total_size = 0

    for i, entry in enumerate(repo.get_walker()):
        if limit == i:
            break

        entry: WalkEntry
        data = handle_entry(repo, entry)
        total_changes += len(data)
        total_size += len(json.dumps(data))

    print(f"total changes: {total_changes}")
    print(f"total serialized size: {total_size}B, that is {total_size / 1024 / 1024}MB")
