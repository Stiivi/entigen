from typing import List
from ..model import Model, Entity, Property
from ..block import Block, BlockType

from ..types import Type

class TextResult:
    lines: List[str]
    indent: int


PYTHON_BASE_TYPES = {
    "identifier": "str",
    "string": "str",
    "int": "int",
}

class PythonWriter:
    def __init__(self, model: Model) -> None:
        self.model = model

    def type_annotation(self, type: Type) -> str:
        """Convert `type` into python Python annotation"""
        # TODO: nothing for now
        if type.is_composite:
            if type.name == "list":
                return "List[{}]".format(self.type_annotation(type.first_child))
            else:
                raise TypeError("Can't convert composite type '{}' into Python type"
                                .format(type))

        # TODO: Handle enums
        return PYTHON_BASE_TYPES.get(type.name, "Any")

    def typed_property(self, prop: Property) -> str:
        """Create type-annotated variable."""
        type_str = self.type_annotation(prop.type)
        return "{name}:{type_str}".format(name=prop.name, type_str=type_str)

    def docstring(self, text: str) -> str:
        return '"""{}"""'.format(text)

    def comment(self, text: str) -> Block:
        # TODO: Block with prefix
        return Block("# {}".format(text))

    def init_method(self, entity: Entity) -> Block:
        """Generate ``__init__` method for entity `Entity"""

        args = Block(indent=13, suffix=",")
        for prop in entity.properties:
            arg = "{}".format(self.typed_property(prop))
            args += arg

        inits = Block(indent=4)
        for prop in entity.properties:
            var = "self.{} = {}".format(prop.name, prop.name)
            inits += var

        b = Block()

        b += "def __init__(self,"
        b += args
        b += "            ) -> None:"
        b += '    """Create {}"""'.format(entity.name)
        b += inits

        return b

    def write_class(self, entity: Entity) -> Block:
        """Generate class for `entity`"""

        b = Block()

        b += "class {}:".format(entity.name)

        instance_vars: List[BlockType] = []
        
        for prop in entity.properties:
            instance_vars.append(self.comment(prop.label))
            instance_vars.append(self.typed_property(prop))
            if prop.desc:
                instance_vars.append(self.docstring(prop.desc))
        
        [self.typed_property(prop) for prop in entity.properties]

        b += ""
        b += Block(instance_vars, indent=4)

        b += ""
        b += Block(self.init_method(entity), indent=4)

        return b

    def write_class_file(self, entity: Entity) -> Block:
        """Generate class definition file for `entity`"""

        b = Block()

        b += "from typing import Any, List"
        b += ""

        b += self.write_class(entity)

        return b
