

def enum(**enums):
    """
    return an enum type with given values
    """
    return type('Enum', (), enums)