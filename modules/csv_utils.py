'''
Utilities for safely reading and writing CSV files.
'''

import csv
import sys


def raise_csv_field_size_limit() -> int:
    '''
    Raise Python's CSV parser field limit to the largest value supported by the platform.
    '''
    max_size = sys.maxsize
    while True:
        try:
            return csv.field_size_limit(max_size)
        except OverflowError:
            max_size = max_size // 10
