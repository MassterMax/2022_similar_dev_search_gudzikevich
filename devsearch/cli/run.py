import click

from devsearch.preprocessing.extract import extract_repo
from devsearch.preprocessing.utils import save_data_as_json


@click.group()
def cli():
    """
    A group of cli methods
    """
    pass


@cli.command()
@click.argument("git_path")
@click.argument("target_path", type=click.Path())
@click.argument("output_path", type=click.Path())
def extract(git_path: str, target_path: str, output_path: str):
    """
    A command to extract info about commits from one repository
    Args:
        git_path: Repository GitHub URL
        target_path: Where to store (if not stored yet) the repository on your device
        output_path: path to serialize output, C:/path/to/result.json like
    Returns:

    """
    data = extract_repo(git_path, target_path)
    save_data_as_json(data, output_path)


if __name__ == '__main__':
    cli()
