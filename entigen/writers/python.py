from typing import List, Optional, Dict

import re

from ..model import Model, Entity, Property, Enumeration
from ..block import Block, BlockType

from ..types import Type
from ..extensible import Writer

from ..errors import DatatypeError, ConfigError
from ..utils import to_bool, to_identifier, decamelize

from collections import namedtuple

PYTHON_BASE_TYPES = {
    "identifier": "str",
    "string": "str",
    "int": "int",
    "datetime": "datetime",
    "date": "date",
    "objref": "Any",
}

TypeImport = namedtuple("TypeImport", ["module", "symbol"])

PYTHON_TYPE_IMPORTS = {
    "datetime": TypeImport("datetime", "datetime"),
    "date": TypeImport("datetime", "date"),
    "list": TypeImport("typing", "List"),
    "dict": TypeImport("typing", "Dict"),
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

    entities_module: Optional[str]
    entity_per_module: bool
    enums_module: Optional[str]

    def __init__(self, model: Model,
                 variables: Optional[Dict[str,str]]=None) -> None:
        self.model = model

        self.entities_module = variables.get("entities_module")
        self.entity_per_module = to_bool(variables.get("entity_per_module")
                                         or False)
        self.enums_module = variables.get("enums_module")

    def type_annotation(self, type: Type) -> str:
        """Convert `type` into python Python annotation"""
        # TODO: nothing for now
        if type.is_composite:
            if type.name == "list":
                return "List[{}]".format(self.type_annotation(type.first_child))
            if type.name == "dict":
                keytype = self.type_annotation(type.children[0])
                valuetype = self.type_annotation(type.children[1])
                return "Dict[{},{}]".format(keytype, valuetype)
            else:
                raise DatatypeError("Can't convert composite type '{}' into "
                                    "Python type".format(type))

        # TODO: Handle enums
        if type.name in PYTHON_BASE_TYPES:
            return PYTHON_BASE_TYPES[type.name]
        elif self.model.is_entity(type.name):
            return type.name
        elif self.model.is_enum(type.name):
            return type.name
        else:
            raise DatatypeError(type.name)

    def _entity_import(self, entity: Entity) -> Optional[TypeImport]:

        if not self.entities_module:
            return None

        module: str = self.entities_module

        # If there is one module per entity, then import that entity from a
        # sub-module
        if self.entity_per_module:
            submodule = to_identifier(decamelize(entity.name))
            # Handle `.`, `..`, ... modules:
            if module.endswith("."):
                module += submodule
            else:
                module += "." + submodule

        return TypeImport(module, entity.name)

    def _enum_import(self, enum: Enumeration) -> Optional[TypeImport]:

        if not self.enums_module:
            return None

        return TypeImport(self.enums_module, enum.name)

    def type_imports(self, type: Type) -> List[TypeImport]:
        """Return list of imports that provide the type `type`."""
        imports: List[TypeImport] = []

        try:
            imp = PYTHON_TYPE_IMPORTS[type.name]
        except KeyError:
            pass
        else:
            imports.append(imp)

        if self.model.is_entity(type.name):
            imp = self._entity_import(self.model.entity(type.name))
            if imp:
                imports.append(imp)
        elif self.model.is_enum(type.name):
            imp = self._enum_import(self.model.enum(type.name))
            if imp:
                imports.append(imp)
            pass

        for child in type.children or []:
            imports += self.type_imports(child)

        return imports

    def entity_type_imports(self, entity: Entity) -> List[TypeImport]:
        """Collect all imports required for entity `entity`."""
        imports: List[TypeImport] = []

        for prop in entity.properties:
            imports += self.type_imports(prop.type)

        return imports

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

    def default_value(self, prop: Property) -> str:
        """Return appropriated default value for property `prop`"""
        if prop.default != "[]":
            return prop.default

        if prop.type.name == "list":
            return "[]"
        elif prop.type.name == "dict":
            return "{}"
        else:
            return prop.default

    def init_assignment(self, prop: Property) -> Block:
        """Return a __init__ asignment for property `prop` with assigned
        default value."""

        b = Block()

        # Nothing to do if there is no default value
        if prop.type.is_composite and prop.default:
            b += "if {} is None:".format(prop.name)
            b += "    self.{} = {}".format(prop.name, self.default_value(prop))
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

        imports: List[TypeImport] = []
        for ent in entities:
            imports += self.entity_type_imports(ent)
        imports = list(set(imports))


        b = Block()

        b += "from typing import Any, List, cast, Optional"

        for imp in imports:
            b += "from {} import {}".format(imp.module, imp.symbol)

        b += ""
        b += self.write_classes(entities)

        return b

    def write_enum(self, enum: Enumeration) -> Block:
        """Write enum definition"""

        b = Block()

        b += "class {}(Enum):".format(enum.name)

        values = Block(indent=4)
        for value in enum.values:
            values += "{} = {}".format(value.key, value.value)

        b += values

        return b

    def write_enums_file(self) -> Block:
        """Generate a file with enums"""

        b = Block()

        b += "from enum import Enum"
        b += ""

        for i, enum in enumerate(self.model.enums):
            b += self.write_enum(enum)
            if i < len(self.model.enums) - 1:
                b += ""

        return b

    def create_block(self, block_type: str,
                     entities: Optional[List[str]]=None) -> Block:
        write_ents = [self.model.entity(name)
                      for name in entities or self.model.entity_names]

        if block_type == "class":
            return self.write_classes(write_ents)
        elif block_type == "class_file":
            return self.write_class_file(write_ents)
        elif block_type == "enums_file":
            return self.write_enums_file()
        else:
            raise Exception("Unknown Python block type '{}'".format(block_type))
