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


def stringify_for_csv(data) -> str:
    '''
    Converts values for CSV writing without truncating user data.
    '''
    try:
        return str(data) if data is not None else ""
    except Exception as e:
        return f"[ERROR CONVERTING DATA: {e}]"
