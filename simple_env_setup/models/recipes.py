from os import popen
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from simple_env_setup.models.dict_objects import (DictObject, DictSingleton,
                                                  stringy_check)
from simple_env_setup.models.settings import Settings
from simple_env_setup.utils.click import Context
from simple_env_setup.utils.io import read_local_tomls
from simple_env_setup.utils.logging import log_step


def format(line: str):
    return line.format(settings=Settings, context=Context, env=Context.env)


class Step(DictObject):

    dict_keys = [
        ("kind", lambda x: x in ["shell", "guard", "overwrite", "update"])]

    @classmethod
    def _from_dict(cls, context: Dict[str, Any], full_context: Dict[str, Any], path: List[str]) -> "Step":
        kind: Literal["shell", "guard",
                      "overwrite", "update"] = context["kind"]
        match kind:
            case "shell":
                return ShellStep.from_dict(full_context, path)
            case "guard":
                return GuardStep.from_dict(full_context, path)
            case "overwrite":
                return OverwriteStep.from_dict(full_context, path)
            case "update":
                return UpdateStep.from_dict(full_context, path)

    def run(self) -> None:
        raise NotImplementedError(f"{self.__class__}.run not implemented")


class ShellStep(Step):

    dict_keys = [("command", str)]

    def __init__(self, command: str) -> None:
        self.command = command

    @classmethod
    def _from_dict(cls, context: Dict[str, Any], full_context: Dict[str, Any], path: List[str],) -> "ShellStep":

        return cls(context["command"])

    @staticmethod
    def _run(cmd: str) -> None:
        proc = popen(cmd)
        log = proc.read()
        status = proc.close()
        if status is not None:
            raise Exception(log, status)

    def to_dict(self) -> str:
        return f"CMD: {self.command}"

    def run(self) -> None:
        log_step(f"{self}", Context.run_step)(self._run)(self.command)


class GuardStep(Step):

    dict_keys = [("conditions", stringy_check)]

    def __init__(self, conditions: List[str]) -> None:
        self.conditions = conditions

    @classmethod
    def _from_dict(cls, context: Dict[str, Any], full_context: Dict[str, Any], path: List[str]) -> "GuardStep":
        return cls(context["conditions"])

    @staticmethod
    def _run(conditions: List[str]) -> None:
        Context.run_step = all([eval(item) for item in conditions])

    def to_dict(self) -> str:
        return f"Guards: {', '.join(self.conditions)}"

    def run(self) -> None:
        log_step(f"{self}", True)(self._run)(self.conditions)


class OverwriteStep(Step):

    dict_keys = [("source", str), ("target", str)]

    def __init__(self, source: str, target: str) -> None:
        self.source = source
        self.target = target

    @classmethod
    def _from_dict(cls, context: Dict[str, Any], full_context: Dict[str, Any], path: List[str]) -> "OverwriteStep":
        return cls(context["source"], context["target"])

    @staticmethod
    def _run(source: str, target: str) -> None:
        pass

    def to_dict(self) -> str:
        return f"Overwrite: {self.target} with {self.source}"

    def run(self) -> None:
        log_step(f"{self}", True)(self._run)(self.source, self.target)


class UpdateStep(Step):

    dict_keys = [("source", str), ("target", str)]

    def __init__(self, source: str, target: str) -> None:
        self.source = source
        self.target = target

    @classmethod
    def _from_dict(cls, context: Dict[str, Any], full_context: Dict[str, Any], path: List[str]) -> "UpdateStep":
        return cls(context["source"], context["target"])

    @staticmethod
    def _run(source: str, target: str) -> None:
        pass

    def to_dict(self) -> str:
        return f"Update: {self.target} with {self.source}"

    def run(self) -> None:
        log_step(f"{self}", True)(self._run)(self.source, self.target)


class InstallModel(DictObject):

    dict_keys = [("steps", list)]

    def __init__(self, steps: List[Step]) -> None:
        self.steps = steps

    @classmethod
    def _from_dict(cls, context: Dict[str, Any], full_context: Dict[str, Any], path: List[str]) -> "InstallModel":
        return cls([Step.from_dict(full_context, path + ["steps", str(i)]) for i, _ in enumerate(context["steps"])])

    def to_dict(self) -> Dict[str, Any]:
        return {"steps": [item.to_dict() for item in self.steps]}


class ConfigModel(DictObject):

    dict_keys = [("steps", list)]

    def __init__(self, steps: List[Step]) -> None:
        self.steps = steps

    @classmethod
    def _from_dict(cls, context: Dict[str, Any], full_context: Dict[str, Any], path: List[str]) -> "ConfigModel":
        return cls([Step.from_dict(full_context, path + ["steps", str(i)]) for i, _ in enumerate(context["steps"])])

    def to_dict(self) -> Dict[str, Any]:
        return {"steps": [item.to_dict() for item in self.steps]}


class Recipe(DictObject):
    install: Optional[InstallModel]
    config: Optional[ConfigModel]

    dict_keys = []

    def __init__(self, install: Optional[InstallModel], config: Optional[ConfigModel]) -> None:
        self.install = install
        self.config = config

    @classmethod
    def _from_dict(cls, context: Dict[str, Any], full_context: Dict[str, Any], path: List[str]) -> "Recipe":
        return cls(
            InstallModel.from_dict(
                full_context, path + ["install"]) if "install" in context else None,
            ConfigModel.from_dict(full_context, path +
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


def parse_recipes(recipes_path: Path) -> None:
    assert recipes_path.exists() and recipes_path.is_dir(
    ), f"path to recipes directory is invalid ({recipes_path})"
    recipe_files = recipes_path.glob("*.toml")
    Recipes.init(read_local_tomls(recipe_files))
