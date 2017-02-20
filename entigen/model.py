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

    def __init__(self, name: str, tag: int, raw_type: str, label: str,
            desc: str, default: Optional[str]) -> None:
        self.name = name
        self.tag = tag
        self.raw_type = raw_type
        # TODO: convert raw_type into type
        self.type = Type.from_string(raw_type)
        self.label = label
        self.desc = desc
        self.default = default


class Entity:
    name: str
    properties: List[Property]

    def __init__(self, name: str, properties: List[Property]) -> None:
        self.name = name
        self.properties = properties


class Model:
    """Metamodel container – contains entities and other model elements."""
    entities: List[Entity]

    def __init__(self) -> None:
        """Create an empty metamodel"""
        self.entities = []

    def add_entity(self, entity: Entity) -> None:
        """Add entity `entity` to the model. If entity with given name already
        exists an exception is raised."""
        if entity.name in self.entity_names:
            raise MetadataError("Entity '{}' already exists."
                                .format(entity.name))
        self.entities.append(entity)

    def entity(self, name: str) -> Entity:
        return [ent for ent in self.entities if ent.name == name][0]

    @property
    def entity_names(self) -> List[str]:
        """Return list of names of all entities in the model"""
        return [ent.name for ent in self.entities]

    def is_entity(self, symbol: str) -> bool:
        """Return `true` if the symbol is an entity"""
        return symbol in self.entity_names
