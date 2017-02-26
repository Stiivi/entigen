import re

def decamelize(name: str) -> str:
    """Decamelize `name`. Convert `CamelCase` into `Camel Case`."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1)


def to_identifier(name: str) -> str:
    """Replace spaces with underscores ``_`` and make the string lower-case."""
    return re.sub(r' ', r'_', name).lower()

