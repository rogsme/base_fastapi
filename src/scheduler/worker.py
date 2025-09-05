import asyncio
import logging
from typing import Any, Callable, TypeVar

from celery import Celery

from constants import (
    CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND,
)

T = TypeVar("T")
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = Celery(
    __name__,
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)


@app.on_after_configure.connect
def setup_periodic_tasks(sender: Any, **kwargs: Any) -> None:  # noqa ARG001 - Celery needs both
    """Setup periodic tasks for the Celery worker with enhanced logging."""
    logger.info("Setting up periodic tasks...")

    # TODO

    logger.info("Periodic tasks setup completed")


def run_func(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """
    Run a function in an asyncio event loop to completion.

    This is necessary because Celery tasks are not async functions.
    This function converts async functions to sync functions.

    Args:
        func (Callable): The function to run.
        *args: Arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        The result of the function call.
    """
    loop = asyncio.get_event_loop()
    coro = func(*args, **kwargs)
    return loop.run_until_complete(coro)
