import csv


CSV_FIELD_SIZE_LIMIT = 1_000_000


def configure_csv_field_size_limit(limit: int = CSV_FIELD_SIZE_LIMIT) -> None:
    '''
    Configure CSV readers to accept fields up to the size this app may write.
    '''
    csv.field_size_limit(limit)


def truncate_for_csv(data, max_length: int = CSV_FIELD_SIZE_LIMIT, suffix: str = "...[TRUNCATED]") -> str:
    '''
    Convert data to a CSV-safe string, truncating only when it exceeds the configured CSV field limit.
    '''
    try:
        str_data = str(data) if data is not None else ""

        if len(str_data) <= max_length:
            return str_data

        if max_length <= len(suffix):
            return suffix[:max_length]

        return str_data[:max_length - len(suffix)] + suffix
    except Exception as e:
        return f"[ERROR CONVERTING DATA: {e}]"
