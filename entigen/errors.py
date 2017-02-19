class EntgenError(Exception):
    """Base class for Entgen errors"""


class TypeError(Exception):
    """Exception related to data types"""


class MetadataError(Exception):
    """Error with malformed metadata"""

class NoSuchObjectError(MetadataError):
    """Error when a model object is not found."""
