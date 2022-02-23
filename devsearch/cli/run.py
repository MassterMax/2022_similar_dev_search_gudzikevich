import click

from devsearch.preprocessing.extract import extract_repo, process_stargazers, save_data_as_json


@click.group()
def cli():
    """
    A group of cli methods
    """
    pass


@cli.command()
@click.argument("local_path", type=click.Path(exists=True))
@click.argument("output_path", type=click.Path())
def extract(local_path: str, output_path: str) -> None:
    """
    A command to extract info about commits from one repository
    Args:
        local_path: Where the git repository stored on your device
        output_path: path to serialize output, C:/path/to/result.jsonl like
    """
    for list_entity in extract_repo(local_path):
        for dict_entity in list_entity:
            save_data_as_json(dict_entity, output_path)


@cli.command()
@click.argument("repo_name")
def extract_stargazers(repo_name: str) -> None:
    """
    A method that calls process_stargazers
    Args:
        repo_name: name of the repo to handle
    """
    process_stargazers(repo_name)


if __name__ == "__main__":
    cli()
