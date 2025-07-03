import time
from collections import defaultdict
from app.common.constant import MAX_REQUESTS, WINDOW_SECONDS

request_log = defaultdict(list)


def is_rate_limited(org_id: int, ip: str) -> bool:
    """
    Determines whether a request from a given organization and IP should be rate-limited.

    This uses a simple sliding window rate limiter based on timestamps.

    Args:
        org_id (int): Organization identifier.
        ip (str): IP address of the requester.

    Returns:
        bool: True if the request exceeds the allowed request limit, else False.
    """
    now = time.time()
    key = (org_id, ip)

    request_log[key] = [ts for ts in request_log[key] if ts > now - WINDOW_SECONDS]

    if len(request_log[key]) >= MAX_REQUESTS:
        return True

    request_log[key].append(now)
    return False
