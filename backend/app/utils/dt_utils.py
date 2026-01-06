from datetime import datetime, timezone

def utc_now() -> datetime:
    """Return current UTC datetime with timezone awareness.
    
    Returns:
        datetime: Current UTC datetime with timezone info
    """
    return datetime.now(timezone.utc)
