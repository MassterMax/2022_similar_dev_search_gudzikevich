from dulwich import porcelain
from dulwich.repo import Repo


def handle_commit(commit):
    print(commit.id)
    print(commit.author)


def extract_repo(git_path: str, target_path: str, should_clone=False):
    try:
        if should_clone:
            porcelain.clone(git_path, target_path)
    except Exception as e:
        print(f"An exception occured: {e}")

    repo = Repo(target_path)
    for entry in repo.get_walker():
        handle_commit(entry.commit)
