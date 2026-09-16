def as_human_readable_size(bytes: int) -> str:
    """Transform a number of bytes into a human-readable format.

    Args:
        bytes (int): number of bytes

    Returns:
        str: human-readable size
    """
    assert bytes >= 0, "Expecting a positive number of bytes!"
    factored = float(bytes)
    for prefix in ("", "k", "M", "G", "T", "P", "E", "Z"):
        if factored < 1000:
            return f"{factored:.2f} {prefix}B" if prefix else f"{bytes:d} Bytes"
        factored /= 1000
    return f"{factored:.2f} YB"
