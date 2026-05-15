'''
CSV helper utilities.
'''

import csv
import sys


def raise_csv_field_size_limit() -> int:
    '''
    Raises Python's CSV parser field limit as high as this platform supports.
    '''
    max_size = sys.maxsize
    while True:
        try:
            return csv.field_size_limit(max_size)
        except OverflowError:
            max_size = max_size // 10
