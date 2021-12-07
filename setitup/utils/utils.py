import re
from typing import Any, Callable, Dict, List

from flatdict import FlatDict
from setitup.models.context import Context
from setitup.models.settings import Settings

# ---------------------------------------------------------------------------- #
#                              String Manipulation                             #
# ---------------------------------------------------------------------------- #


def sub(line: str) -> str:
    """
    Formats a string using settings, context and environment.

    Args:
        line (str): string to be formatted.

    Returns:
        str: formatted string.
    """
    return line.format(settings=Settings, context=Context, env=Context.env)


def trim_empty(content: str, max_lines: int = 2) -> str:
    """
    Trims consecutive newlines.

    Args:
        content (str): line content.
        max_lines (int, optional): max number of consecutive newlines. Defaults to 2.

    Returns:
        str: trimmed line content.
    """
    if max_lines >= 1:
        return re.sub(f"\n{max_lines,}", "\n" * max_lines, content).strip()
    else:
        return content

# ---------------------------------------------------------------------------- #
#                                  Validators                                  #
# ---------------------------------------------------------------------------- #


def is_string_list(items: Any) -> bool:
    """
    Check for a list of strings. Can be empty.
    """
    if not isinstance(items, list):
        return False

    _items: List[Any] = items
    return all([isinstance(item, str) for item in _items])


# def should_exist(config_path: Path) -> None:
#     parent_dir = config_path.parents[0]
#     parent_dir.mkdir(exist_ok=True, parents=True)


# ---------------------------------------------------------------------------- #
#                                Data Structure                                #
# ---------------------------------------------------------------------------- #

def merge_dicts(dicts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Deep merge dictionaries by flattening.

    Args:
        dicts (List[Dict[str, Any]]): dictionaries to be merged.

    Returns:
        Dict[str, Any]: merged dictionary.
    """
    empty_dict: Dict[str, Any] = {}
    merged = FlatDict(empty_dict)
    for item in dicts:
        merged.update(FlatDict(item))
    return merged.as_dict()

# @run_python
# def overwrite(dir: Path, filename: str) -> None:
#     # Check existence
#     dir.mkdir(exist_ok=True, parents=True)
#     content = read(filename)
#     with(open(dir / filename, "w")) as f:
#         f.write(content)
