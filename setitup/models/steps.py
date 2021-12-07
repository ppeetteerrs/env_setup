from os import popen
from shutil import Error
from typing import Any, Callable, Dict, List, Literal

from setitup.models.dict_objects import DictObject
from setitup.models.settings import Settings
from setitup.utils.click import Context
from setitup.utils.logging import log_step
from setitup.utils.utils import is_string_list

StringDict = dict[str, str]


class DotDict(StringDict):
    __getattr__: Callable[..., str | None] = StringDict.get
    __setattr__: Callable[..., None] = StringDict.__setitem__
    __delattr__: Callable[..., None] = StringDict.__delitem__


def sub(line: str) -> str:
    return line.format(settings=Settings, context=Context, env=DotDict(Context.env))


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
            case _:
                raise Error("Something is very wrong")

    def run(self) -> Any:
        raise NotImplementedError(f"{self.__class__}.run not implemented")


class ShellStep(Step):

    dict_keys = [("command", str)]

    def __init__(self, command: str) -> None:
        self.command = sub(command)

    @classmethod
    def _from_dict(cls, context: Dict[str, Any], full_context: Dict[str, Any], path: List[str],) -> "ShellStep":

        return cls(context["command"])

    @staticmethod
    def _run(cmd: str) -> str:
        proc = popen(cmd)
        log = proc.read()
        status = proc.close()
        if status is not None:
            raise Exception(log, status)
        return log

    def to_dict(self) -> str:
        return f"CMD: {self.command}"

    def run(self) -> str | None:
        return log_step(f"{self}", Context.run_step)(self._run)(self.command)


class GuardStep(Step):

    dict_keys = [("conditions", is_string_list)]

    def __init__(self, conditions: List[str]) -> None:
        self.conditions = conditions
        if len(self.conditions) == 0:
            self.run_step = True
        else:
            self.run_step = all([eval(sub(item)) for item in conditions])

    @classmethod
    def _from_dict(cls, context: Dict[str, Any], full_context: Dict[str, Any], path: List[str]) -> "GuardStep":
        return cls(context["conditions"])

    @staticmethod
    def _run(run_step: bool) -> None:
        Context.run_step = run_step

    def to_dict(self) -> str:
        return f"Guards: [{', '.join(self.conditions)}] => {'RUN' if self.run_step else 'SKIP'}"

    def run(self) -> None:
        log_step(f"{self}", True)(self._run)(self.run_step)


class OverwriteStep(Step):

    dict_keys = [("source", str), ("target", str)]

    def __init__(self, source: str, target: str) -> None:
        self.source = sub(source)
        self.target = sub(target)

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

    dict_keys = [("source", str), ("target", str),
                 ("sections", is_string_list), ("markers", is_string_list)]

    def __init__(self, source: str, target: str, sections: List[str], markers: List[str]) -> None:
        self.source = sub(source)
        self.target = sub(target)
        self.sections = sections
        self.markers = markers

    @classmethod
    def _from_dict(cls, context: Dict[str, Any], full_context: Dict[str, Any], path: List[str]) -> "UpdateStep":
        return cls(context["source"], context["target"], context["sections"], context["markers"])

    @staticmethod
    def _run(source: str, target: str) -> None:
        pass

    def to_dict(self) -> str:
        return f"Update: {self.target} with {self.source}"

    def run(self) -> None:
        log_step(f"{self}", True)(self._run)(self.source, self.target)
