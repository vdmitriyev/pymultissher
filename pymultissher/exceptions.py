"""Provides module specific exceptions."""


class MultiSSHerException(Exception):
    """Generic exception for MultiSSHer."""


class MultiSSHerNotSupported(Exception):
    """Exception for non supported features."""


class MultiSSHerCreateClient(Exception):
    """MultiSSHer was not able to create SSH client."""


class YAMLGenericException(Exception):
    """MultiSSHer YAML validation error."""


class YAMLValidationError(Exception):
    """MultiSSHer YAML validation error."""


class YAMLConfigExists(Exception):
    """MultiSSHer YAML already exists error."""
