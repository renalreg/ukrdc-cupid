class SchemaInvalidError(Exception):
    """Error caused by xml which which does not match the schema. Data cannot
    be loaded into the xsdata model when invalid.

    Args:
        Exception (_type_): _description_
    """
