import click


@click.group()
def cli():
    pass


@cli.command()
@click.argument("message")
def hello(message: str):
    print(f"you wrote: {message}")


if __name__ == '__main__':
    cli()
