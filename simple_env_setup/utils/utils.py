import re
from os import environ
from pathlib import Path
from typing import Any, Dict, List

from flatdict import FlatDict

ENV = dict(environ)
assert "HOME" in ENV, "$HOME environment variable must be set."
config_path = Path(ENV["HOME"]) / ".local" / "env_setup" / "config.toml"


def should_exist(config_path: Path) -> None:
    parent_dir = config_path.parents[0]
    parent_dir.mkdir(exist_ok=True, parents=True)


def trim_empty(content: str, max_lines: int = 2) -> str:
    if max_lines >= 1:
        return re.sub(f"\n{max_lines,}", "\n" * max_lines, content).strip()
    else:
        return content


def merge_dicts(dicts: List[Dict[str, Any]]) -> Dict[str, Any]:
    empty_dict: Dict[str, Any] = {}
    merged = FlatDict(empty_dict)
    for item in dicts:
        merged.update(FlatDict(item))
    return merged.as_dict()


# ---------------------------------------------------------------------------- #
#                                    checks                                    #
# ---------------------------------------------------------------------------- #

# def is_installed(cmd: str):
#     return shutil.which(cmd) is not None

# def should_install(cmd: str, force: bool):
#     installed = is_installed(cmd)
#     if installed:
#         if force:
#             log_section(f"Reinstall {cmd}")
#             return True
#         else:
#             log_section(f"{cmd} already installed")
#             return False
#     else:
#         log_section(f"Install {cmd}")
#         return True

# # ---------------------------------------------------------------------------- #
# #                              Resource Management                             #
# # ---------------------------------------------------------------------------- #

# def read(filename: str) -> str:
#     return read_text(resources, filename)

# @run_python
# def overwrite(dir: Path, filename: str) -> None:
#     # Check existence
#     dir.mkdir(exist_ok=True, parents=True)
#     content = read(filename)
#     with(open(dir / filename, "w")) as f:
#         f.write(content)
