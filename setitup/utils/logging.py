import traceback
from functools import partial, wraps
from typing import Any, Callable, Iterable, List, Optional, ParamSpec, TypeVar

import termcolor
import yaml
from setitup.utils.click import Context

colored = partial(termcolor.colored)


def fmt_yaml(obj: Any) -> str:
    return yaml.dump(obj, sort_keys=False)


def print_yaml(obj: Any):
    print(fmt_yaml(obj))


def print_bold(msg: str, color: str = "white"):
    print(colored(msg, color))


P = ParamSpec("P")
T = TypeVar("T")


def log_section(name: str) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def _log_section(f: Callable[P, T]) -> Callable[P, T]:
        @wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            print(colored(f"{name.upper()}", color="magenta"))
            try:
                output = f(*args, **kwargs)
            except Exception as e:
                print(
                    colored(f"{name.upper()}",
                            color="magenta"),
                    colored("  ERROR", color="red"),
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
    """
    Prints log message on the start, end and failure of a processing step.

    Args:
        name (str): name of step.
        run_step (bool): whether to run or to skip the step.

    Returns:
        Callable[[Callable[P, T]], Callable[P, Optional[T]]]: decorator function.
    """
    def _log_step(f: Callable[P, T]) -> Callable[P, Optional[T]]:
        @wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Optional[T]:
            # Step skipped
            if not run_step:
                print(
                    colored(f"  {name}", color="white"),
                    colored("  SKIPPED", color="cyan"),
                )
                return None
            else:
                print(
                    colored(f"  {name}", color="white"),
                    colored("  STARTED", color="cyan"),
                )
            try:
                output = f(*args, **kwargs)
            except Exception as e:
                print(
                    colored(f"  {name}", color="white"),
                    colored("  ERROR", color="red"),
                )
                for arg in e.args[0]:
                    print(arg)
                exit(1)
            print(
                colored(f"  {name}", color="white"),
                colored("  SUCCESS", color="green"),
            )
            if Context.verbose and output is not None:
                print(colored("Outputs", color="gray"))
                print(output)
            return output

        return wrapper

    return _log_step


def last_words(logs: str | Iterable[str]):
    print(colored("\nERROR:", color="red"))
    if isinstance(logs, str):
        logs = [logs]
    for log in logs:
        print(log)
    exit(1)
