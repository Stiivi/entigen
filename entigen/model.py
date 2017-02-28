"""
Metamodel Entities
"""

from typing import List, Optional
from .errors import MetadataError
from .types import Type


class Property:
    """Property of an entity"""

    name: str
    """Property identifier""" 

    tag: int
    """Tag – similar to the Protobuf or Thrift tag"""

    raw_type: str
    """Data type as provided in the model source"""

    type: Type
    """Parsed data type"""

    label: str
    """Human-readable property label"""

    desc: str
    """Human-readable description of the property"""

    default: Optional[str]
    """String representation of the default value"""

    is_optional: bool
    """Flag whether the property is optional"""

    def __init__(self, name: str, tag: int, raw_type: str, label: str,
            desc: str, default: Optional[str], is_optional: bool) -> None:
        self.name = name
        self.tag = tag
        self.raw_type = raw_type
        # TODO: convert raw_type into type
        self.type = Type.from_string(raw_type)
        self.label = label
        self.desc = desc
        self.default = default
        self.is_optional = is_optional


class Entity:
    name: str
    properties: List[Property]

    def __init__(self, name: str, properties: List[Property]) -> None:
        self.name = name
        self.properties = properties


class EnumValue:
    key: str
    value: int
    label: str
    desc: str

    def __init__(self, key: str, value: int, label: str, desc: str) -> None:
        self.key = key
        self.value = value
        self.label = label
        self.desc = desc


class Enumeration:
    name: str
    values: List[EnumValue]

    def __init__(self, name: str, values: List[EnumValue]) -> None:
        self.name = name
        self.values = values


class Model:
    """Metamodel container – contains entities and other model elements."""
    entities: List[Entity]
    enums: List[Enumeration]

    def __init__(self) -> None:
        """Create an empty metamodel"""
        self.entities = []
        self.enums = []

    def add_entity(self, entity: Entity) -> None:
        """Add entity `entity` to the model. If entity with given name already
        exists an exception is raised."""
        if entity.name in self.entity_names:
            raise MetadataError("Entity '{}' already exists."
                                .format(entity.name))
        self.entities.append(entity)

    def add_enum(self, enum: Enumeration) -> None:
        """Add enum to the model. If enum with given name already
        exists an exception is raised."""
        if enum.name in self.enum_names:
            raise MetadataError("Enum '{}' already exists."
                                .format(enum.name))
        self.enums.append(enum)

    def entity(self, name: str) -> Entity:
        return [ent for ent in self.entities if ent.name == name][0]

    def enum(self, name: str) -> Enumeration:
        return [enum for enum in self.enums if enum.name == name][0]

    @property
    def entity_names(self) -> List[str]:
        """Return list of names of all entities in the model"""
        return [ent.name for ent in self.entities]

    @property
    def enum_names(self) -> List[str]:
        """Return list of names of all enumerations in the model"""
        return [enum.name for enum in self.enums]

    def is_entity(self, symbol: str) -> bool:
        """Return `true` if the symbol is an entity"""
        return symbol in self.entity_names

    def is_enum(self, symbol: str) -> bool:
        """Return `true` if the symbol is an entity"""
        return symbol in self.enum_names
