from typing import List

from setitup.models.recipes import Recipes
from setitup.models.settings import Settings
from setitup.utils.click import Context
from setitup.utils.logging import log_section


@log_section("Parsing packages")
def parse_package(package: str):
    packages: List[str] = []

    # Check if package is bundle
    if package in Settings.bundles:
        packages = Settings.bundles[package]
    else:
        packages = [package]

    # Check for missing recipes
    for pk in packages:
        if pk not in Recipes.recipes:
            raise KeyError("Missing recipe for package {pk}")

    Context.packages = packages
