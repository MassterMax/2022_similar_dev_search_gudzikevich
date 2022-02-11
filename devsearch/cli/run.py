import click

from devsearch.preprocessing.extract import extract_repo


@click.group()
def cli():
    pass


@cli.command()
@click.argument("message")
def hello(message: str):
    print(f"you wrote: {message}")


@cli.command()
@click.argument("git_path")
@click.argument("target_path", type=click.Path())
def extract(git_path: str, target_path: str):
    extract_repo(git_path, target_path)


if __name__ == '__main__':
    cli()
