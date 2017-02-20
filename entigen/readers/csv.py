"""
CSV File Reader
"""

import csv
import os.path

from collections import defaultdict
from typing import Optional, Iterable, Dict, List

from ..errors import MetadataError
from ..model import Model, Entity, Property
from ..extensible import Reader


PROPERTIES_FILE = "properties.csv"
ENTITIES_FILE = "entities.csv"


class CSVReader(Reader, name="csv"):

    model: Model

    def __init__(self, model: Optional[Model]=None) -> None:
        self.model = model or Model()

    def read_model(self, path: str) -> None:
        self.read_entities_file(os.path.join(path, ENTITIES_FILE))
        self.read_properties_file(os.path.join(path, PROPERTIES_FILE))

    def read_entities_file(self, filename: str) -> None:
        pass

    def read_properties_file(self, filename: str) -> None:
        with open(filename) as f:
            reader = csv.DictReader(f)
            self._read_property_rows(reader)

    def _property_from_row(self, row: Dict[str, str]) -> Property:
        name = row.get("name")
        if not name:
            raise MetadataError("Property in entity '{}' has no name"
                                .format(row.get("entity")))

        entity_name = row.get("entity")
        if not entity_name:
            raise MetadataError("Property '{}' has no entity."
                               .format(row.get("name")))

        try:
            tag = int(row["tag"])
        except TypeError:
            raise MetadataError("Invalid tag for property '{}.{}'"
                                .format(entity_name, name))

        # Empty string in CSV is interpreted None
        default: Optional[str] = row["default"] or None

        prop = Property(
            name=row["name"],
            tag=int(row["tag"]),
            raw_type=row["type"],
            label=row["label"],
            desc=row["description"],
            default=default,
        )

        return prop

    def _read_property_rows(self, rows: Iterable[Dict[str,str]]) -> None:
        """Read properties from list of dictionaries where keys are
        meta-property names and values are meta-property values."""

        props: Dict[str,List[Property]]
        props = defaultdict(list)

        for row in rows:
            prop = self._property_from_row(row)
            entname = row["entity"]

            props[entname].append(prop)

        for entname, entprops in props.items():
            entity = Entity(name=entname, properties=entprops)
            self.model.add_entity(entity)

