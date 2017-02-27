class EntgenError(Exception):
    """Base class for Entgen errors"""


class DatatypeError(Exception):
    """Exception related to data types"""


class ConfigError(Exception):
    """Error with malformed or missing configuration"""

class MetadataError(Exception):
    """Error with malformed metadata"""

class NoSuchObjectError(MetadataError):
    """Error when a model object is not found."""
