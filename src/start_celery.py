import argparse
import logging
import socket

from scheduler.worker import app

DEFAULT_QUEUE = "default"

logger = logging.getLogger(__name__)


def start_worker(num_workers: int, queue: str) -> None:
    """
    Start the Celery worker with the specified number of workers on the specified queue.

    Args:
        num_workers (int): Number of worker processes
        queue (str): Queue name to listen to
    """
    logger.info(
        f"Starting Celery worker with {num_workers} workers on queue {queue}. ",
    )

    name = queue if "," not in queue else DEFAULT_QUEUE
    hostname = socket.gethostname()

    app.worker_main(
        [
            "worker",
            "--loglevel=info",
            f"--concurrency={num_workers}",
            f"-nworker_{name}_{hostname}",
            f"-Q{queue}",
        ],
    )


def start_beat() -> None:
    """Start the Celery beat scheduler."""
    logger.info("Starting Celery Beat")
    app.Beat(
        loglevel="info",
    ).run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start Celery worker or beat")
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of worker processes",
    )
    parser.add_argument(
        "--beat",
        action="store_true",
        help="Start the Celery beat scheduler",
    )
    parser.add_argument(
        "--queue",
        type=str,
        default=DEFAULT_QUEUE,
        help="Name of the queue to listen to",
    )

    args = parser.parse_args()

    if args.beat:
        start_beat()
    else:
        start_worker(args.workers, args.queue)
