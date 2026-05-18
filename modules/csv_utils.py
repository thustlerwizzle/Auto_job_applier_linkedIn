'''
CSV helpers shared by the bot and the local application.
'''

import csv
import sys


def raise_csv_field_size_limit() -> int:
    '''
    Raise Python's CSV read limit as high as the platform accepts.
    '''
    field_size_limit = sys.maxsize
    while True:
        try:
            csv.field_size_limit(field_size_limit)
            return field_size_limit
        except OverflowError:
            field_size_limit = field_size_limit // 10
