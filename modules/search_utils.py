DATE_POSTED_FILTERS = ["Any time", "Past month", "Past week", "Past 24 hours"]


def next_date_posted_filter(current_filter: str, stop_at_24hr: bool) -> str:
    '''
    Returns the next date-posted filter for non-stop search cycling.
    '''
    try:
        current_index = DATE_POSTED_FILTERS.index(current_filter)
    except ValueError:
        current_index = -1

    next_index = current_index + 1
    if stop_at_24hr:
        return DATE_POSTED_FILTERS[min(next_index, len(DATE_POSTED_FILTERS) - 1)]
    return DATE_POSTED_FILTERS[next_index % len(DATE_POSTED_FILTERS)]
