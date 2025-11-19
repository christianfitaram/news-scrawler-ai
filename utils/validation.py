# utils/validation.py
import re
from datetime import datetime

# batch-YYYY-MM-DD (batch is numeric)
_PATTERN = r'^(\d+)-(202[5-9]|20[3-9]\d)-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$'
_rx = re.compile(_PATTERN)


def is_valid_sample(sample: str) -> bool:
    m = _rx.match(sample)
    if not m:
        return False
    _, year, month, day = m.groups()
    try:
        datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d")
        return True
    except ValueError:
        return False
