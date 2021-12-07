from pathlib import Path
from typing import Any, Dict, List, Optional

from setitup.models.dict_objects import DictObject, DictSingleton
from setitup.models.steps import Step
from setitup.utils.io import read_local_tomls
from setitup.utils.logging import log_step


class InstallSpec(DictObject):

    dict_keys = [("steps", list)]

    def __init__(self, steps: List[Step]) -> None:
        self.steps = steps

    @classmethod
    def _from_dict(cls, context: Dict[str, Any], full_context: Dict[str, Any], path: List[str]) -> "InstallModel":
        return cls([Step.from_dict(full_context, path + ["steps", str(i)]) for i, _ in enumerate(context["steps"])])

    def to_dict(self) -> Dict[str, Any]:
        return {"steps": [item.to_dict() for item in self.steps]}


class ConfigSpec(DictObject):

    dict_keys = [("steps", list)]

    def __init__(self, steps: List[Step]) -> None:
        self.steps = steps

    @classmethod
    def _from_dict(cls, context: Dict[str, Any], full_context: Dict[str, Any], path: List[str]) -> "ConfigSpec":
        return cls([Step.from_dict(full_context, path + ["steps", str(i)]) for i, _ in enumerate(context["steps"])])

    def to_dict(self) -> Dict[str, Any]:
        return {"steps": [item.to_dict() for item in self.steps]}


class Recipe(DictObject):
    install: Optional[InstallSpec]
    config: Optional[ConfigSpec]

    dict_keys = []

    def __init__(self, install: Optional[InstallSpec], config: Optional[ConfigSpec]) -> None:
        self.install = install
        self.config = config

    @classmethod
    def _from_dict(cls, context: Dict[str, Any], full_context: Dict[str, Any], path: List[str]) -> "Recipe":
        return cls(
            InstallSpec.from_dict(
                full_context, path + ["install"]) if "install" in context else None,
            ConfigSpec.from_dict(full_context, path +
                                 ["config"]) if "config" in context else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        res: Dict[str, Any] = {}

        if self.install:
            res["install"] = self.install.to_dict()

        if self.config:
            res["config"] = self.config.to_dict()

        return res


class Recipes(DictSingleton):
    recipes: Dict[str, Recipe] = {}

    @classmethod
    def _init(cls, context: Dict[str, Any], full_context: Dict[str, Any], path: List[str] = []) -> None:
        cls.recipes = {k: Recipe.from_dict(
            context, [k]) for k in context.keys()}

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        return {k: v.to_dict() for k, v in cls.recipes.items()}


@log_step("Parsing recipes files", True)
def parse_recipes(recipes_path: Path) -> None:
    assert recipes_path.exists() and recipes_path.is_dir(
    ), f"path to recipes directory is invalid ({recipes_path})"
    recipe_files = recipes_path.glob("*.toml")
    Recipes.init(read_local_tomls(recipe_files))
