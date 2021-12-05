from typing import (Any, Callable, Dict, Iterable, List, Optional, Tuple, Type,
                    TypeVar)

from simple_env_setup.utils.logging import pf


def stringy_check(items: Any) -> bool:
    if not isinstance(items, list):
        return False

    _items: List[Any] = items
    return all([isinstance(item, str) for item in _items])


def listify(stuff: str | Iterable[str]) -> List[str]:
    return list(stuff) if not isinstance(stuff, str) else [stuff]


def splitfy(stuff: str | Iterable[str], delimiter: str) -> List[str]:
    return list(stuff) if not isinstance(stuff, str) else stuff.split(delimiter)


KeySpec = Tuple[str, type | Callable[..., bool] | None]


def check_dict(
    context: Dict[str, Any],
    path: List[str],
    key_specs: List[KeySpec],
) -> Dict[str, Any]:
    # Tidy up path
    full_path_str = " => ".join(path)

    # Check path to current context
    curr_context: Dict[str, Any] | List[Any] = context
    for i, key in enumerate(path):
        # Parse numeric key
        try:
            key_int = int(key)
        except Exception:
            key_int = -1

        # When current context is dict
        if isinstance(curr_context, dict) and key in curr_context:
            curr_context = curr_context[key]
        # When current context is list
        elif isinstance(curr_context, list) and key_int >= 0 and len(curr_context) > key_int:
            curr_context = curr_context[key_int]
        else:
            curr_path_str = " => ".join(path[: i + 1])
            raise KeyError(
                [
                    f"Error looking for value at path {full_path_str}...",
                    f"Stopped at {curr_path_str}...",
                    "Current Context:",
                    pf(curr_context),
                    "Context:",
                    pf(context),
                ]
            )

    # Cannot stop at list
    if isinstance(curr_context, list):
        raise ValueError(
            [
                f"List found at path {full_path_str}...",
                "Current Context:",
                pf(curr_context),
                "Context:",
                pf(context),
            ]
        )

    # Check keys at current context
    for key, key_type in key_specs:
        if key not in curr_context:
            raise KeyError(
                [
                    f"Error looking for key {key} at path {full_path_str}...",
                    "Current Context:",
                    pf(curr_context),
                    "Context:",
                    pf(context),
                ]
            )

        failed_type = key_type and isinstance(
            key_type, type) and not isinstance(curr_context[key], key_type)
        failed_validator = key_type and not isinstance(
            key_type, type) and not key_type(curr_context[key])
        if failed_type or failed_validator:
            raise ValueError(
                [
                    f"Invalid value {curr_context[key]} at path {full_path_str} => {key}...",
                    "Current Context:",
                    pf(curr_context),
                    "Context:",
                    pf(context),
                ]
            )

    return curr_context


S = TypeVar("S", bound="DictObject")


class DictObject:

    dict_keys: List[KeySpec] = []

    @classmethod
    def _from_dict(cls: Type[S], context: Dict[str, Any], full_context: Dict[str, Any], path: List[str] = []) -> S:
        raise NotImplementedError(f"{cls.__name__}.from_dict not implemented")

    @classmethod
    def from_dict(cls: Type[S], full_context: Dict[str, Any], path: List[str] = []) -> S:
        try:
            sub_context = check_dict(full_context, path, cls.dict_keys)
            instance: S = cls._from_dict(sub_context, full_context, path)
        except Exception as e:
            if isinstance(e.args[0], list):
                raise type(e)(
                    [f"Error constructing {cls.__name__} from dict"] + e.args[0])
            else:
                raise type(e)(
                    [f"Error constructing {cls.__name__} from dict"] + list(e.args))
        return instance

    def to_dict(self) -> Dict[str, Any] | str:
        raise NotImplementedError(f"{self.__class__}.to_dict not implemented")


T = TypeVar("T")


class DictSingleton:

    _initialized: bool = False
    dict_keys: List[KeySpec] = []

    @classmethod
    def _init(cls, context: Dict[str, Any], full_context: Dict[str, Any], path: List[str] = []) -> None:
        raise NotImplementedError(f"{cls.__name__}._init not implemented")

    @classmethod
    def init(cls, full_context: Dict[str, Any], path: List[str] = []) -> None:
        try:
            sub_context = check_dict(full_context, path, cls.dict_keys)
            cls._init(sub_context, full_context, path)
            cls._initialized = True
        except Exception as e:
            if isinstance(e.args[0], list):
                raise type(e)(
                    [f"Error updating {cls.__name__} from dict"] + e.args[0])
            else:
                raise type(e)(
                    [f"Error updating {cls.__name__} from dict"] + list(e.args))

    @classmethod
    def ok(cls, item: Optional[T]) -> T:
        if item is None or not cls._initialized:
            raise ValueError(f"Singleton {cls.__name__} not yet initialized.")
        return item

    @classmethod
    @property
    def ready(cls) -> bool:
        return cls._initialized

    @classmethod
    def to_dict(cls) -> Dict[str, Any] | str:
        raise NotImplementedError(f"{cls.__name__}.to_dict not implemented")
