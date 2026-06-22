def split_location(raw_location):

    if not raw_location:
        return None, None

    parts = [part.strip() for part in raw_location.split(",") if part.strip()]

    if not parts:
        return None, None

    if len(parts) == 1:
        return parts[0], None

    country = parts[-1]
    city = ", ".join(parts[:-1])

    return country, city
