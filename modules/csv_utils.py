'''
CSV helpers shared by the bot and CSV-backed UI.
'''

import csv
import sys


def raise_csv_field_size_limit() -> int:
    '''
    Raise Python's CSV parser field limit to the largest value supported by the
    current platform and return the limit that was applied.
    '''
    limit = sys.maxsize
    while True:
        try:
            csv.field_size_limit(limit)
            return limit
        except OverflowError:
            limit //= 10
