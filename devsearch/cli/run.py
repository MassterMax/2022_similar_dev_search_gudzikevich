import click

from devsearch.github_api.extract import process_stargazers
from devsearch.preprocessing.extract import extract_repo, save_data_as_json


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
@click.argument("output_path", type=click.Path())
@click.option('--access_token', '-tkn', default=None)
@click.option('--token_env_key', '-env', default=None)
def extract_stargazers(repo_name: str, output_path: str, access_token: str, token_env_key: str) -> None:
    """
    A method that calls process_stargazers
    Args:
        repo_name: name of the repo to handle
        output_path: a path where to store result, C:/path/to/result.json like
        access_token: github api token, something like: 198hfh7sm2ap9198hfh7sg4ap9198hfh7sg_ap9a
        token_env_key: env key where github api token stored, for example: access_token
    """
    data = process_stargazers(repo_name, access_token=access_token, token_env_key=token_env_key)
    save_data_as_json(data, output_path)


if __name__ == "__main__":
    cli()
