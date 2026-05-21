DATE_POSTED_OPTIONS = ["Any time", "Past month", "Past week", "Past 24 hours"]


def next_date_posted_filter(
    current_filter: str,
    stop_at_24hr: bool,
    date_options: list[str] | None = None,
) -> str:
    """
    Return the next LinkedIn date-posted filter for non-stop search cycling.
    """
    options = date_options or DATE_POSTED_OPTIONS
    if current_filter not in options:
        return options[0]

    next_index = options.index(current_filter) + 1
    if stop_at_24hr:
        return options[min(next_index, len(options) - 1)]

    return options[0 if next_index >= len(options) else next_index]
