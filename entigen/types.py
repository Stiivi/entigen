"""
Data types used in the metamodel.
"""

import re

from typing import Optional, List

from .errors import DatatypeError


BASE_TYPES = [
    "string",
    "int",
    # Special case of a string data type for which certain validation rules
    # might apply
    "identifier",
]

COMPOSITE_TYPES = [
    "list"        
]

COMPOSITE_PATTERN = r"^(\w+)<(\w+)>$"

"""Pattern for composite data type. Note that we accept only composite of a
base type, no recursion is allowed."""

class Type:
    """Simple data type representation."""

    name: str
    """Top-level type name"""
    children: Optional[List["Type"]]
    """Children types of the data type. For example, if the type is a list,
    then there is one child describing which type the list is composed of."""

    @classmethod
    def from_string(cls, string: str) -> "Type":
        """Create a data type from a string. The string can be:
            
        * One of the base types: ``string``, ``int``, ``identifier``
        * List type: ``list<BASETYPE>``"""

        match = re.match(COMPOSITE_PATTERN, string)

        if match:
            typename = match.groups()[0]

            if typename in BASE_TYPES:
                raise Exception("Can't use base type '{}' as a composite type"
                                .format(typename))

            child = Type(match.groups()[1])

            return Type(typename, children=[child])
        else:
            return Type(string)

    def __init__(self, name: str, children: Optional[List["Type"]]=None) -> None:
        """Create a data type `name`. If no `children` are provided, then the
        type is basic type, otherwise it is a complex type composed of
        `children`"""
        self.name = name
        self.children = children

    @property
    def is_composite(self) -> bool:
        return self.name in COMPOSITE_TYPES

    @property
    def first_child(self) -> "Type":
        """Returns typename of the first child if the type is composite type or
        raise an exception if the type is not composite."""

        if not self.is_composite:
            raise DatatypeError("Type '{}' is not a composite type"
                            .format(str(self)))

        return self.children[0]

    def __str__(self) -> str:
        if self.children:
            children_str = ",".join(str(child) for child in self.children)
            return "{}<children_str>".format(self.name)
        else:
            return self.name


