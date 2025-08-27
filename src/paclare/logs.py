"""Provides logging utilities."""

import logging
import sys

RESET = "\033[0m"
CYAN = "\033[36m"
GREY = "\033[90m"
RED = "\033[31m"


_log_format = "%(message)s"
logger = logging.getLogger("paclare")


def init_logs(
    lvl: logging.DEBUG | logging.INFO | logging.WARNING | logging.ERROR,
) -> None:
    """Init the main logger."""
    logging.basicConfig(level=lvl, format=_log_format)


def print_section(text: str) -> None:
    """Print a text in highlighted color with an empty line before."""
    logger.info("\n%s%s%s", CYAN, text, RESET)


def fatal_error(text: str) -> None:
    """Print an error message and exit."""
    logger.error(
        "%sFatal error%s : %s.\nFix your configuration file.",
        RED,
        RESET,
        text,
    )
    sys.exit(0)
