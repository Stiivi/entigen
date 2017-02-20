from typing import List, Dict, Any, Type, cast, Optional

from .model import Model
from .block import Block

class Extensible:
    __extensions__ = "unknown"

    readers: Dict[str, Type["Reader"]] = {}
    writers: Dict[str, Type["Writer"]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__()

        name = kwargs.get("name")
        
        if not name:
            return

        if cls.__extensions__ == "readers":
            cls.readers[name] = cast(Type["Reader"], cls)
        elif cls.__extensions__ == "writers":
            cls.writers[name] = cast(Type["Writer"], cls)
        else:
            raise Exception("Unknown module superclass: {}".format(cls))


class Reader(Extensible):
    __extensions__ = "readers"

    model: Model

    def __init__(self, model: Model) -> None:
        pass

    def read_model(self, path: str) -> None:
        pass

class Writer(Extensible):
    __extensions__ = "writers"

    block_types: List[str] = []

    def __init__(self, model: Model) -> None:
        pass

    def create_block(self, block_type: str,
                     entities: Optional[List[str]]=None) -> Block:
        """Write a block of type `block_type`."""
        raise NotImplementedError
