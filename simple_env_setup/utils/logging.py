import traceback
from functools import partial, wraps
from typing import Any, Callable, Iterable, List, Optional, ParamSpec, TypeVar, cast

import yaml
from simple_env_setup.utils.click import Context
from termcolor import colored

P = ParamSpec("P")
T = TypeVar("T")

dump = cast(Callable[..., str], yaml.dump)
pf = partial(dump, sort_keys=False, default_flow_style=False)


def log_section(name: str) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def _log_section(f: Callable[P, T]) -> Callable[P, T]:
        @wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            print(colored(f"{name.upper()}", color="magenta", attrs=["bold"]))
            try:
                output = f(*args, **kwargs)
            except Exception as e:
                print(
                    colored(f"{name.upper()}", color="magenta", attrs=["bold"]),
                    colored("  ERROR", color="red", attrs=["bold"]),
                )
                arg0 = e.args[0]
                if isinstance(arg0, list):
                    arg0_list: List[Any] = arg0
                    for arg in arg0_list:
                        print(arg)
                else:
                    print(e)
                print(traceback.format_exc())
                exit(1)
            return output

        return wrapper

    return _log_section


def log_step(name: str, run_step: bool) -> Callable[[Callable[P, T]], Callable[P, Optional[T]]]:
    def _log_step(f: Callable[P, T]) -> Callable[P, Optional[T]]:
        @wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Optional[T]:
            if not run_step:
                print(
                    colored(f"  {name}", color="white", attrs=["bold"]),
                    colored("  SKIPPED", color="cyan", attrs=["bold"]),
                )
                return None
            else:
                print(
                    colored(f"  {name}", color="white", attrs=["bold"]),
                    colored("  STARTED", color="cyan", attrs=["bold"]),
                )
            try:
                output = f(*args, **kwargs)
            except Exception as e:
                print(
                    colored(f"  {name}", color="white", attrs=["bold"]),
                    colored("  ERROR", color="red", attrs=["bold"]),
                )
                for arg in e.args[0]:
                    print(arg)
                exit(1)
            print(
                colored(f"  {name}", color="white", attrs=["bold"]),
                colored("  SUCCESS", color="green", attrs=["bold"]),
            )
            if Context.verbose and output is not None:
                print(colored("Outputs", color="gray", attrs=["bold"]))
                print(output)
            return output

        return wrapper

    return _log_step


def last_words(logs: str | Iterable[str]):
    print(colored("\nERROR:", color="red", attrs=["bold"]))
    if isinstance(logs, str):
        logs = [logs]
    for log in logs:
        print(log)
    exit(1)
