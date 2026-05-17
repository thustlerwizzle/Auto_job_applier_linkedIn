'''
CSV helpers shared by the job history writer and UI.
'''

import csv
import sys


def raise_csv_field_size_limit(limit: int | None = None) -> int:
    '''
    Raises Python's CSV parser field size limit so large saved fields can be read.
    Returns the limit that was applied.
    '''
    field_limit = sys.maxsize if limit is None else limit
    while True:
        try:
            csv.field_size_limit(field_limit)
            return field_limit
        except OverflowError:
            field_limit //= 10
            if field_limit <= 0:
                raise
