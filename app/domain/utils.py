def camelize_snakecase(string: str) -> str:
    parts = string.split("_")

    return parts[0].lower() + "".join(part.title() for part in parts[1:]) if len(parts) > 1 else string
