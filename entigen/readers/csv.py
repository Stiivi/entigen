"""
CSV File Reader
"""

import csv
import os.path

from collections import defaultdict
from typing import Optional, Iterable, Dict, List

from ..errors import MetadataError
from ..model import Model, Entity, Property, Enumeration, EnumValue
from ..extensible import Reader


PROPERTIES_FILE = "properties.csv"
ENTITIES_FILE = "entities.csv"
ENUMS_FILE = "enums.csv"
ENUM_VALUES_FILE = "enum_values.csv"


class CSVReader(Reader, name="csv"):

    model: Model

    def __init__(self, model: Optional[Model]=None) -> None:
        self.model = model or Model()

    def read_model(self, path: str) -> None:
        self.read_entities_file(os.path.join(path, ENTITIES_FILE))
        self.read_properties_file(os.path.join(path, PROPERTIES_FILE))
        self.read_enumerations_file(os.path.join(path, ENUMS_FILE))
        self.read_enum_values_file(os.path.join(path, ENUM_VALUES_FILE))

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

    def read_enumerations_file(self, filename: str) -> None:
        pass

    def read_enum_values_file(self, filename: str) -> None:
        # Enum file is optional
        if not os.path.isfile(filename):
            return

        with open(filename) as f:
            reader = csv.DictReader(f)
            self._read_enum_rows(reader)

    def _enum_value_from_row(self, row: Dict[str, str]) -> EnumValue:
        name = row.get("key")
        if not name:
            raise MetadataError("Enum value in enum '{}' has no key"
                                .format(row.get("enum")))

        enum_name = row.get("enum")
        if not enum_name:
            raise MetadataError("Key '{}' has no enum name."
                               .format(row.get("key")))

        try:
            value = int(row["value"])
        except TypeError:
            raise MetadataError("Invalid enum value '{}.{}'"
                                .format(enum_name, name))

        prop = EnumValue(
            key=row["key"],
            value=value,
            label=row["label"],
            desc=row["description"],
        )

        return prop

    def _read_enum_rows(self, rows: Iterable[Dict[str,str]]) -> None:
        """Read values of enums. Keys are: enum, key, value, label, desc."""

        values: Dict[str,List[EnumValue]]
        values = defaultdict(list)

        for row in rows:
            value = self._enum_value_from_row(row)
            enumname = row["enum"]

            values[enumname].append(value)

        for enumname, enumvalues in values.items():
            enum = Enumeration(name=enumname, values=enumvalues)
            self.model.add_enum(enum)


