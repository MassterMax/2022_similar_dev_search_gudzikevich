import click

from devsearch.preprocessing.extract import extract_repo


@click.group()
def cli():
    pass


@cli.command()
@click.argument("git_path")
@click.argument("target_path", type=click.Path())
def extract(git_path: str, target_path: str):
    """
    A command to extract info about commits from one repository
    Args:
        git_path: Repository GitHub URL
        target_path: Where to store (if not stored yet) the repository on your device

    Returns:

    """
    extract_repo(git_path, target_path)


if __name__ == '__main__':
    cli()
