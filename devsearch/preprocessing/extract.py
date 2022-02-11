from dulwich import porcelain
from dulwich.repo import Repo


def handle_commit(commit):
    print(f'author: {commit.author.decode()}, sha: {commit.id.decode()}')


def extract_repo(git_path: str, target_path: str, should_clone=False, limit=10):
    try:
        if should_clone:
            porcelain.clone(git_path, target_path)
    except Exception as e:
        print(f"An exception occured: {e}")

    repo = Repo(target_path)
    for entry in repo.get_walker():
        limit -= 1
        handle_commit(entry.commit)
        if limit == 0:
            break
