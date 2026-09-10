'''
CSV helpers for reading and writing job history files.
'''

import csv
import sys


def raise_csv_field_size_limit() -> None:
    '''
    Raise csv.field_size_limit to the largest value this platform allows.

    Python's CSV *reader* enforces field_size_limit (default ~128KB). The
    writer does not, so history files can contain job descriptions larger
    than the default reader limit. Call this before reading those files.
    '''
    max_int = sys.maxsize
    while True:
        try:
            csv.field_size_limit(max_int)
            return
        except OverflowError:
            max_int = int(max_int / 10)
            if max_int < 1:
                csv.field_size_limit(1_000_000)
                return
