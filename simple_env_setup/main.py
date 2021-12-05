from pathlib import Path

import click

from simple_env_setup.models.recipes import Recipes, parse_recipes
from simple_env_setup.models.settings import parse_settings
from simple_env_setup.utils.click import AliasGroup
from simple_env_setup.utils.logging import log_section, pf


@log_section("Parsing input directory...")
def parse_directory(directory: str):
    dir_path = Path(directory)
    parse_settings(dir_path / "settings")
    parse_recipes(dir_path / "recipes")
    print(pf(Recipes.to_dict()))


@click.group(cls=AliasGroup, context_settings=dict(help_option_names=["-h", "--help"]))
@click.argument("directory")
def main(directory: str):
    parse_directory(directory)


@main.command(["install", "i"])
def i():
    pass
