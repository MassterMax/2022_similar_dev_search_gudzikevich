import difflib

from dulwich import porcelain
from dulwich.objects import Commit, ShaFile
from dulwich.repo import Repo
from dulwich.walk import WalkEntry


def handle_entry(repo: Repo, entry: WalkEntry):
    """
    A method to handle one WalkEntry
    Args:
        repo: repo that we handle
        entry: entry to handle

    Returns: meta-information about entry

    """

    commit: Commit = entry.commit
    print(f"total files changed in this commit: {len(entry.changes())}")
    print(f"author: {commit.author.decode()}, sha: {commit.id.decode()}")
    print(f"first change: {entry.changes()[0]}")
    print((entry.changes()[0]).new.sha)

    # get first blobs
    old_blob: ShaFile = repo.get_object((entry.changes()[0]).old.sha)
    new_blob: ShaFile = repo.get_object((entry.changes()[0]).new.sha)

    differences = difflib.unified_diff(old_blob.data.decode().splitlines(), new_blob.data.decode().splitlines())
    print(*list(differences), sep="\n")
    print("\n"*3)


def extract_repo(git_path: str, target_path: str, should_clone=False, limit=10):
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
    for i, entry in enumerate(repo.get_walker()):
        if limit == i:
            break

        entry: WalkEntry
        handle_entry(repo, entry)

        # print(entry.changes()[0])

        # print(repo.get_object(b"6307262210f041886275b3199abf440b5c4006b1").data.decode())
        # dulwich.patch.unified_diff(blob1, blob2)
