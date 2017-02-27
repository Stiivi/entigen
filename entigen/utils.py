from typing import Optional, Union
import re

def decamelize(name: str) -> str:
    """Decamelize `name`. Convert `CamelCase` into `Camel Case`."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1)


def to_identifier(name: str) -> str:
    """Replace spaces with underscores ``_`` and make the string lower-case."""
    return re.sub(r' ', r'_', name).lower()


def to_bool(value: Union[str,bool,int]) -> Optional[bool]:
    """Convert a string to boolean. True values: 1, yes, true, false values:
    0, no, false, otherwise returns `None`."""

    if isinstance(value, bool):
        return value
    elif isinstance(value, int):
        return bool(value)
    elif isinstance(value, str):

        lower: str = value.lower()

        if lower in ("1", "true", "yes"):
            return True
        elif lower in ("0", "false", "no"):
            return False
        else:
            return None
    else:
        raise TypeError("Can't convert value of type '{}"
                        "to bool".format(type(value)))
