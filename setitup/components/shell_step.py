from os import popen
from typing import Any, Dict, List

from setitup.models.steps import Step
from setitup.utils.click import Context
from setitup.utils.logging import log_step


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
