from typing import Optional, List, Dict

from ..model import Model, Entity, Property
from ..block import Block
from ..extensible import Writer
from ..utils import decamelize, to_identifier

class InfoWriter(Writer, name="info"):
    """Writer that creates basic information about the model"""

    block_types = ["entity_list"]

    variables = [
        ("decamelize", "Decamelize entity names into valid lowercase identifier"),
    ]

    def __init__(self, model: Model,
                 variables: Optional[Dict[str,str]]=None) -> None:
        self.model = model

        if "decamelize" in variables:
            self.decamelize = True
        else:
            self.decamelize = False

    def write_entity_list(self, entities: List[Entity]) -> Block:
        """Write list of entity names, one per line."""

        b = Block()

        for entity in entities:
            if self.decamelize:
                name = to_identifier(decamelize(entity.name))
            else:
                name = entity.name

            b += name

        return b


    def create_block(self, block_type: str,
                     entities: Optional[List[str]]=None) -> Block:
        write_ents = [self.model.entity(name)
                      for name in entities or self.model.entity_names]

        if block_type == "entity_list":
            return self.write_entity_list(write_ents)
        else:
            raise Exception("Unknown Python block type '{}'".format(block_type))
