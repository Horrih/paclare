"""Provides logging utilities."""

import logging
import sys

RESET = "\033[0m"
CYAN = "\033[36m"
GREY = "\033[90m"
RED = "\033[31m"


_LOG_FORMAT = "%(message)s"
logging.basicConfig(format=_LOG_FORMAT, level=logging.INFO)
logger = logging.getLogger("paclare")


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
