import csv
import os
import tempfile
from contextlib import contextmanager
from typing import Iterator


def raise_csv_field_size_limit(limit: int = 1_000_000) -> None:
    """
    Raise the CSV reader field limit so large job descriptions do not crash reads.
    """
    csv.field_size_limit(limit)


@contextmanager
def csv_file_lock(csv_path: str) -> Iterator[None]:
    """
    Take an advisory lock for a CSV file using a sibling lock file.
    """
    lock_path = f"{csv_path}.lock"
    lock_dir = os.path.dirname(lock_path)
    if lock_dir:
        os.makedirs(lock_dir, exist_ok=True)

    with open(lock_path, "a+", encoding="utf-8") as lock_file:
        if os.name == "nt":
            import msvcrt

            lock_file.seek(0)
            lock_file.write("0")
            lock_file.flush()
            lock_file.seek(0)
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                lock_file.seek(0)
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def write_dict_rows_atomically(csv_path: str, fieldnames: list[str], rows: list[dict]) -> None:
    """
    Replace a CSV file with new rows without exposing a truncated partial file.
    """
    csv_dir = os.path.dirname(csv_path) or "."
    os.makedirs(csv_dir, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(prefix=".tmp-", suffix=".csv", dir=csv_dir)

    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        os.replace(temp_path, csv_path)
    except Exception:
        try:
            os.unlink(temp_path)
        except FileNotFoundError:
            pass
        raise
