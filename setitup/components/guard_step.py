from typing import Any, Dict, List

from setitup.utils.click import Context
from setitup.utils.logging import log_step
from setitup.utils.utils import is_string_list


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
