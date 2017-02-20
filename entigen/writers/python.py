from typing import List, Optional
from ..model import Model, Entity, Property
from ..block import Block, BlockType

from ..types import Type
from ..extensible import Writer

class TextResult:
    lines: List[str]
    indent: int


PYTHON_BASE_TYPES = {
    "identifier": "str",
    "string": "str",
    "int": "int",
}

class PythonWriter(Writer, name="python"):

    block_types = ["class_file", "class"]

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

    def write_classes(self, entities: List[Entity]) -> Block:
        """Generate class definition file for `entity`"""

        b = Block()

        for ent in entities:
            b += self.write_class(ent)
            b += ""

        return b

    def write_class_file(self, entities: List[Entity]) -> Block:
        """Generate class definition file for `entity`"""

        b = Block()

        b += "from typing import Any, List"
        b += ""

        b += self.write_classes(entities)

        return b

    def create_block(self, block_type: str,
                     entities: Optional[List[str]]=None) -> Block:
        write_ents = [self.model.entity(name)
                      for name in entities or self.model.entity_names]

        if block_type == "class":
            return self.write_classes(write_ents)
        elif block_type == "class_file":
            return self.write_class_file(write_ents)
        else:
            raise Exception("Unknown Python block type '{}'".format(block_type))
