class MultiSSHerException(Exception):
    """Generic exception for MultiSSHer"""

    pass


class MultiSSHerCreateClient(Exception):
    """MultiSSHer was not able to create SSH client"""

    pass


class YAMLGenericException(Exception):
    """MultiSSHer YAML validation error"""

    pass


class YAMLValidationError(Exception):
    """MultiSSHer YAML validation error"""

    pass


class YAMLConfigExists(Exception):
    """MultiSSHer YAML already exists error"""

    pass
