from pathlib import Path
from typing import Any, Dict, List

from setitup.models.dict_objects import DictSingleton
from setitup.utils.io import read_local_tomls
from setitup.utils.logging import log_step
from setitup.utils.utils import is_string_list


class Settings(DictSingleton):
    root: bool = True
    bundles: Dict[str, List[str]]

    dict_keys = [("root", bool), ("bundles", lambda x: all(
        is_string_list(v) for v in x.values()))]

    @classmethod
    def _init(cls, context: Dict[str, Any], full_context: Dict[str, Any], path: List[str] = []) -> None:
        cls.root = context["root"]
        cls.bundles = context["bundles"]


@log_step("Parsing settings files...", True)
def parse_settings(settings_path: Path) -> None:
    assert settings_path.exists() and settings_path.is_dir(
    ), f"path to settings directory is invalid ({settings_path})"
    settings = read_local_tomls(settings_path.glob("*.toml"))
    Settings.init(settings)
