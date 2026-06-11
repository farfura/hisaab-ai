import asyncio
import logging
import time
from collections.abc import Callable
from functools import lru_cache
from typing import TypeVar

from supabase import Client, create_client

from core.config import settings

logger = logging.getLogger(__name__)
T = TypeVar("T")


@lru_cache(maxsize=1)
def get_supabase() -> Client:
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in backend/.env"
        )
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


def run_with_retry(fn: Callable[[], T], *, retries: int = 3, base_delay: float = 0.5) -> T:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            return fn()
        except Exception as exc:
            last_error = exc
            if attempt == retries - 1:
                break
            delay = base_delay * (2**attempt)
            logger.warning("DB call failed (attempt %d/%d): %s", attempt + 1, retries, exc)
            time.sleep(delay)
    assert last_error is not None
    raise last_error


async def run_db(fn: Callable[[], T], *, retries: int = 3) -> T:
    return await asyncio.to_thread(run_with_retry, fn, retries=retries)


def check_db_connection() -> tuple[bool, str]:
    try:
        run_with_retry(
            lambda: get_supabase().table("users").select("id").limit(1).execute(),
            retries=2,
        )
        return True, "connected"
    except Exception as exc:
        return False, str(exc)
