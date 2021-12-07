from typing import Any, Callable, List, ParamSpec

import click
from click.core import Command

P = ParamSpec("P")


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
                parent_name = names[0]
                alias_names = names[1:]
            parent_kwargs = kwargs
            if "help" in parent_kwargs:
                parent_kwargs["help"] += f" (Aliases: {' '.join(names[1:])})"
            alias_kwargs = {**kwargs, "hidden": True}

            parent_cmd = super(AliasGroup, self).command(
                parent_name, *args, **parent_kwargs)(f)

            for name in alias_names:
                super(AliasGroup, self).command(name, *args, **alias_kwargs)(f)

            return parent_cmd

        return decorator
