import csv
import sys


def raise_csv_field_size_limit() -> None:
    '''
    Raises Python's CSV parser field size limit to the largest supported value.
    '''
    field_size_limit = sys.maxsize
    while True:
        try:
            csv.field_size_limit(field_size_limit)
            return
        except OverflowError:
            field_size_limit //= 10


def stringify_for_csv(data) -> str:
    '''
    Converts data to a string for CSV writing without dropping content.
    '''
    try:
        return str(data) if data is not None else ""
    except Exception as e:
        return f"[ERROR CONVERTING DATA: {e}]"
