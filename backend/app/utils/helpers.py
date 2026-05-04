import random
import string
from datetime import datetime, timezone


def generate_tracking_number(prefix: str = "DA") -> str:
    """Generate a unique tracking number like DA-20260504-ABCD1234."""
    date_part = datetime.now(timezone.utc).strftime("%Y%m%d")
    random_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"{prefix}-{date_part}-{random_part}"


def generate_warehouse_code(name: str) -> str:
    """Generate a short warehouse code from the warehouse name."""
    words = name.upper().split()
    if len(words) >= 2:
        base = "".join(w[0] for w in words[:3])
    else:
        base = name[:3].upper()
    suffix = "".join(random.choices(string.digits, k=3))
    return f"{base}{suffix}"


def paginate(query_result, total: int, page: int, size: int) -> dict:
    return {
        "items": query_result,
        "total": total,
        "page": page,
        "size": size,
    }
