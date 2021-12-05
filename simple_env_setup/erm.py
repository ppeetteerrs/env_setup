from pathlib import Path
from pprint import PrettyPrinter

import click
import toml

from simple_env_setup.utils.click import AliasGroup, merge_dicts, parse_dict

pp = PrettyPrinter(compact=False).pprint


@click.group(cls=AliasGroup, context_settings=dict(help_option_names=["-h", "--help"]))
@click.argument("directory")
def main(directory: str):
    parse_stuff(Path(directory))


@main.command(["install", "i"])
def i():
    pass


def parse_stuff(path: Path):
    files_str = merge_dicts([dict(toml.load(item))
                             for item in (path / "recipes").glob("*.toml")])
    parse_dict(files_str)
