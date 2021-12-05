from pathlib import Path
from typing import Any, Dict, List

from simple_env_setup.models.dict_objects import DictSingleton
from simple_env_setup.utils.io import read_local_tomls
from simple_env_setup.utils.logging import log_step


class Settings(DictSingleton):
    root: bool = True

    dict_keys = [("root", bool)]

    @classmethod
    def _init(cls, context: Dict[str, Any], full_context: Dict[str, Any], path: List[str] = []) -> None:
        cls.root = context["root"]


@log_step("Parsing settings files...", True)
def parse_settings(settings_path: Path) -> None:
    assert settings_path.exists() and settings_path.is_dir(
    ), f"path to settings directory is invalid ({settings_path})"
    settings = read_local_tomls(settings_path.glob("*.toml"))
    Settings.init(settings)
