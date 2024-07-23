import importlib.metadata as importlib_metadata


def package_summary(package_name: str = "pymultissher"):
    """Prints information about a Python package based on its metadata.

    Args:
        package_name (str): The name of the package. Defaults to "pymultissher".
    """
    info = []
    try:
        metadata = importlib_metadata.distribution(package_name)
        info.append({"field": "Version", "value": metadata.version})
        info.append({"field": "Package name", "value": metadata.metadata["Name"]})
        info.append({"field": "Summary", "value": metadata.metadata.get("Summary")})
    except importlib_metadata.PackageNotFoundError:
        print(f"Package '{package_name}' not found.")

    return info


def package_version(package_name: str = "pymultissher") -> str:
    """Returns version information about a Python package based on its metadata.

    Args:
        package_name (str): The name of the package. Defaults to "pymultissher".

    Returns:
        str: version. Defaults to "0.0.0"
    """

    version = "0.0.0"
    try:
        metadata = importlib_metadata.distribution(package_name)
        version = metadata.version
    except importlib_metadata.PackageNotFoundError:
        print(f"Package '{package_name}' not found.")

    return version
