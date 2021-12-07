from pathlib import Path

import click

from setitup.models.recipes import Recipes, parse_recipes
from setitup.models.settings import Settings, parse_settings
from setitup.utils.click import AliasGroup, Context
from setitup.utils.logging import (log_section, log_step, print_bold,
                                   print_yaml)
from setitup.utils.parsing import parse_package


@log_section("Parsing input directory...")
def parse_directory(directory: str):
    dir_path = Path(directory)
    parse_settings(dir_path / "settings")
    parse_recipes(dir_path / "recipes")


@click.group(cls=AliasGroup, context_settings=dict(help_option_names=["-h", "--help"]))
@click.argument("directory")
def main(directory: str):
    Context.base_directory = directory


@main.command(["i", "install"])
def install():
    pass


@main.command(["c", "config"])
def config():
    pass


@main.command(["l", "ls", "list"])
def ls():
    parse_directory(Context.base_directory)
    installable = []
    configurable = []

    for item, recipe in Recipes.recipes.items():
        if recipe.install:
            installable.append(item)
        if recipe.config:
            configurable.append(item)
    print("")
    print_bold("Installable:", color="yellow")
    print_yaml(installable)
    print_bold("Configurable:", color="yellow")
    print_yaml(configurable)
    print_bold("Bundles:", color="yellow")
    for k, v in Settings.bundles.items():
        print(f"{k}: {', '.join(v)}")


@log_section("Dry run")
def dry_run_packages():
    for package in Context.packages:
        log_step(f"Dry run for {package}", True)(
            print_yaml)(Recipes.recipes[package].to_dict())


@main.command(["dry", "drydry"], help="wee")
@click.argument("package")
def dry(package: str):
    parse_directory(Context.base_directory)
    parse_package(package)
    dry_run_packages()
