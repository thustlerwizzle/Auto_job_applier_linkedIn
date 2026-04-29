import csv
import io

from modules.csv_utils import CSV_FIELD_SIZE_LIMIT, configure_csv_field_size_limit, truncate_for_csv


def test_truncate_for_csv_preserves_fields_under_configured_limit():
    value = "x" * (CSV_FIELD_SIZE_LIMIT - 1)

    assert truncate_for_csv(value) == value


def test_truncate_for_csv_only_truncates_above_configured_limit():
    value = "x" * (CSV_FIELD_SIZE_LIMIT + 10)

    result = truncate_for_csv(value)

    assert len(result) == CSV_FIELD_SIZE_LIMIT
    assert result.endswith("...[TRUNCATED]")


def test_configured_csv_reader_accepts_fields_the_bot_writes():
    configure_csv_field_size_limit()
    value = "x" * (CSV_FIELD_SIZE_LIMIT - 1)
    buffer = io.StringIO()
    csv.writer(buffer).writerow([value])

    row = next(csv.reader(io.StringIO(buffer.getvalue())))

    assert row == [value]
