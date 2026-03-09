def get_display_name_for_slug(slug: str):
    """
    For a given string slug this generates the display name for the given slug.
    This generated display name will be displayed on the front end.
    """

    try:
        return slug.replace("_", " ").title()
    except:  # noqa
        return slug
    
def unpack_dj_choices(choices):
    """Return value and corresponding label for that choice."""

    return [{"id": key, "identity": str(value)} for key, value in choices]