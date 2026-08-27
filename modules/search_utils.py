DATE_POSTED_OPTIONS = ["Any time", "Past month", "Past week", "Past 24 hours"]


def next_date_posted_filter(current: str, stop_at_24hr: bool = True) -> str:
    """
    Advance the LinkedIn date-posted filter for non-stop runs.

    Empty or unknown values start at "Any time" instead of raising ValueError.
    When stop_at_24hr is True, cycling walks toward "Past 24 hours" and stays
    there rather than jumping there immediately or wrapping.
    """
    if current not in DATE_POSTED_OPTIONS:
        return DATE_POSTED_OPTIONS[0]

    next_index = DATE_POSTED_OPTIONS.index(current) + 1
    if next_index >= len(DATE_POSTED_OPTIONS):
        return DATE_POSTED_OPTIONS[-1] if stop_at_24hr else DATE_POSTED_OPTIONS[0]
    return DATE_POSTED_OPTIONS[next_index]
