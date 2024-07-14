def handle_dict_keys(data: dict, key: str) -> None:
    """Check if key exists in dict and add it, if it doesn't exist.

    Args:
        data (dict): dictionary with data
        key (str): key of the dit to be checked
    """

    if key not in data:
        data[key] = {}
