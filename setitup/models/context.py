import atexit
from os import environ
from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp
from typing import Callable, Dict, List

# ---------------------------------------------------------------------------- #
#                                Data Structures                               #
# ---------------------------------------------------------------------------- #

StringDict = dict[str, str]


class DotDict(StringDict):
    """
    Allows dot accessing of dictionary. Used for string substitution.
    """
    __getattr__: Callable[..., str | None] = StringDict.get
    __setattr__: Callable[..., None] = StringDict.__setitem__
    __delattr__: Callable[..., None] = StringDict.__delitem__


ENV = dict(environ)


class Context:
    base_directory: str = ""
    packages: List[str] = []
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
