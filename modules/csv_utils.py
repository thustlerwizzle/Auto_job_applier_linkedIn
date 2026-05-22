import csv
import sys


def raise_csv_field_size_limit() -> int:
    """
    Raise Python's CSV parser field limit to the largest value supported.

    The limit only affects reads. CSV writers can already emit larger fields, so
    write paths should preserve data instead of truncating it to this limit.
    """
    limit = sys.maxsize
    while True:
        try:
            csv.field_size_limit(limit)
            return limit
        except OverflowError:
            limit //= 10
