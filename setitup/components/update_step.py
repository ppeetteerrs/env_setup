from typing import Any, Dict, List

from setitup.utils.logging import log_step
from setitup.utils.utils import is_string_list


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
