import click


@click.command()
@click.argument("reference")
@click.argument("clean")
def run():
    print("huh")
