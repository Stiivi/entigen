from typing import List, Optional

import re

from ..model import Model, Entity, Property
from ..block import Block, BlockType

from ..types import Type
from ..extensible import Writer

from ..errors import DatatypeError


PYTHON_BASE_TYPES = {
    "identifier": "str",
    "string": "str",
    "int": "int",
}


def sort_by_default(props: List[Property]) -> List[Property]:
    """Sort properties `props` by whether they have default value or not. Put
    the ones with default value at the end."""
    first: List[Property] = []
    last: List[Property] = []

    for prop in props:
        if prop.default is not None:
            last.append(prop)
        else:
            first.append(prop)

    return first + last


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
                raise DatatypeError("Can't convert composite type '{}' into "
                                    "Python type".format(type))

        # TODO: Handle enums
        if type.name in PYTHON_BASE_TYPES:
            return PYTHON_BASE_TYPES[type.name]
        elif self.model.is_entity(type.name):
            return type.name
        else:
            raise DatatypeError(type.name)

    def typed_property(self, prop: Property, wrap: Optional[str]=None) -> str:
        """Create type-annotated variable. `wrap` is optional type that the
        property type will be wrapped in, for example `Optional`"""
        type_str = self.type_annotation(prop.type)

        # Wrapt the type
        if wrap:
            type_str = "{}[{}]".format(wrap, type_str)

        return "{name}: {type_str}".format(name=prop.name, type_str=type_str)

    def docstring(self, text: str) -> str:
        return '"""{}"""'.format(text)

    def comment(self, text: str) -> Block:
        # TODO: Block with prefix
        return Block("# {}".format(text))

    def literal(self, value: str, type: Type) -> str:
        """Format literal value `value`"""

        if type.is_composite:
            raise NotImplementedError("Literal values for composite types is"
                                      "not supported.")

        if type.name in ("string", "identifier"):
            quoted_string = re.sub('"', '\\"', value)
            quoted_string = re.sub('\\', '\\\\', value)
            return '"{}"'.format(quoted_string)

        else:
            return value

    def init_argument(self, prop: Property) -> str:
        """Return a __init__ function argument for property `prop` with
        assigned default value."""

        # Nothing to do if there is no default value
        if not prop.default:
            return self.typed_property(prop)

        if not prop.type.is_composite:
            # Base type
            value = self.literal(prop.default, prop.type)
            wrap = None
        else:
            # Wrap the type as 'optiona' so we can pass the `None` and
            # later test for it
            value = "None"
            wrap = "Optional"

        typed_arg = self.typed_property(prop, wrap=wrap)
        return "{}={}".format(typed_arg, value)

    def init_assignment(self, prop: Property) -> Block:
        """Return a __init__ asignment for property `prop` with assigned
        default value."""

        b = Block()

        # Nothing to do if there is no default value
        if prop.type.is_composite and prop.default:
            b += "if {} is None:".format(prop.name)
            b += "    self.{} = {}".format(prop.name, prop.default)
            b += "else:".format(prop.name)
            b += "    self.{} = {}".format(prop.name, prop.name)
        else:
            b += "self.{} = {}".format(prop.name, prop.name)

        return b

    def init_method(self, entity: Entity) -> Block:
        """Generate ``__init__` method for entity `Entity"""

        args = Block(indent=13, suffix=",", last_suffix="")
        for prop in sort_by_default(entity.properties):
            args += self.init_argument(prop)

        inits = Block(indent=4)
        for prop in entity.properties:
            inits += self.init_assignment(prop)

        b = Block()

        b += "def __init__(self,"
        b += args
        b += "            ) -> None:"
        b += '    """Create {}"""'.format(entity.name)
        b += inits

        return b

    def eq_method(self, entity: Entity) -> Block:
        """Generate the comparator ``__eq__`` method."""

        """
        if self.p1 == other.p1 \\
            and self.p2 == other.p2:
        
        """

        comps = Block(indent=4,
                      first_indent=0,
                      first_prefix="if ",
                      prefix="and ",
                      suffix=" \\",
                      last_suffix=":")

        for i, prop in enumerate(entity.properties):
            comps += "self.{} == tother.{}".format(prop.name, prop.name)


        b = Block()
        b += "def __eq__(self, other: object) -> bool:".format(entity.name)

        ifb = Block(indent=4)
        ifb += "if not isinstance(other, {}):".format(entity.name)
        ifb += "    return False"
        ifb += ""
        ifb += "# 'typed' other" 
        ifb += "tother = cast({}, other)".format(entity.name)
        ifb += ""
        ifb += comps
        
        ifb += "    return True"
        ifb += "else:"
        ifb += "    return False"

        b += ifb

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

        b += ""
        b += Block(self.eq_method(entity), indent=4)

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

        b += "from typing import Any, List, cast, Optional"
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
