from __future__ import annotations
import logging

import functools
import time
from typing import TYPE_CHECKING, Any

from django.db import OperationalError, close_old_connections

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger(__name__)


def retry_on_db_disconnect(max_retries: int = 5, initial_delay: int = 5, backoff_factor: int = 2) -> Callable:

    def decorator(handler: Callable) -> Callable:   
        @functools.wraps(handler)
        def wrap(*args: Any, **kwargs: Any) -> None:
            retries = 0
            current_delay = initial_delay
            while retries < max_retries:
                try:
                    return handler(*args, **kwargs)
                except OperationalError as e:
                    logger.warning("Database operational error: %s. Retrying in %d seconds...", e, current_delay)
                    close_old_connections()
                    time.sleep(current_delay)
                    retries += 1
                    current_delay *= backoff_factor
                    if retries >= max_retries:
                        raise

            return handler(*args, **kwargs)

        return wrap

    return decorator