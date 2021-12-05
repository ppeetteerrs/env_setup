import atexit
from functools import partial
from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp
from typing import Any, Callable, Dict, List, ParamSpec

from simple_env_setup.utils.utils import ENV

import click
from click.core import Command

P = ParamSpec("P")

# A convenient wrapper around click.option
force = partial(click.option, "--force", "-f", "force", is_flag=True, help="Force resinstallation.")


class Context:
    force: bool = False
    verbose: bool = False
    run_step: bool = True
    env: Dict[str, str] = ENV
    homr_dir: Path = Path(ENV["HOME"])
    tmp_dir: Path = Path(mkdtemp())

    @staticmethod
    @atexit.register
    def rm_temp_dir() -> None:
        if Context.tmp_dir is not None and Context.tmp_dir.is_dir():
            rmtree(Context.tmp_dir)


class AliasGroup(click.Group):
    """
    A custom click command group with support for command aliases.
    A command with name as the list of aliases will be shown. Alias commands will be hidden but available.
    """

    def command(self, names: str | List[str], *args: Any, **kwargs: Any) -> Callable[[Callable[P, Any]], Command]:
        def decorator(f: Callable[P, Any]):
            # Add parent command
            if isinstance(names, str):
                parent_name = names
                alias_names = []
            else:
                parent_name = ",".join(names)
                alias_names = names
            parent_kwargs = kwargs
            alias_kwargs = {**kwargs, "hidden": True}

            parent_cmd = super(AliasGroup, self).command(parent_name, *args, **parent_kwargs)(f)

            for name in alias_names:
                super(AliasGroup, self).command(name, *args, **alias_kwargs)(f)

            return parent_cmd

        return decorator
