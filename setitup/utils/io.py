from pathlib import Path
from typing import Any, Dict, Iterable, List, Literal

import toml
from setitup.utils.utils import merge_dicts, trim_empty


def read_local(file_path: Path, strip: Literal["l", "r", "b", None] = "r", max_empty_lines: int = 2) -> List[str]:
    """
    Reads a file on host computer. Returns empty list if non-existent.

    Args:
        file_path (Path): path to file.
        strip (Literal["l", "r", "b", None], optional): whether to strip each line. Defaults to "r".
        max_empty_lines (int, optional): maximum number of empty lines. Defaults to 2.

    Returns:
        List[str]: lines of file content.
    """

    if file_path.exists():
        content = open(file_path, "r").read()
        content = trim_empty(content, max_empty_lines).splitlines()
        match strip:
            case "l":
                content = [line.lstrip() for line in content]
            case "r":
                content = [line.rstrip() for line in content]
            case "b":
                content = [line.strip() for line in content]
        return content

    return []


def read_local_tomls(file_paths: Path | Iterable[Path]) -> Dict[str, Any]:
    """
    Read one or more toml files on host computer as dictionaries.

    Args:
        file_paths (Path): paths to toml files.

    Returns:
        Dict[str, Any]: combined dictionary.
    """
    if isinstance(file_paths, Path):
        file_paths = [file_paths]
    return merge_dicts([dict(toml.load(file_path))
                        for file_path in file_paths if file_path.exists()])
