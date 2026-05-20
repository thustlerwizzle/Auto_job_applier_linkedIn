import csv
import sys


def raise_csv_field_size_limit() -> int:
    """
    Raise Python's CSV parser field-size limit as high as this platform allows.

    The csv module only enforces this limit when reading. Writers can persist
    larger fields safely, so callers should not truncate history data before
    writing it.
    """
    limit = sys.maxsize
    while True:
        try:
            csv.field_size_limit(limit)
            return limit
        except OverflowError:
            limit //= 10
